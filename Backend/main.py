import os
import json
import time
import re
import feedparser
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from google import genai

from database import SessionLocal, engine
from models import Base, Opportunity

# =============================
# ENV SETUP
# =============================
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

# =============================
# RSS FEEDS (Official Only)
# =============================
RSS_FEEDS = {
    "Harvard University": "https://news.harvard.edu/gazette/feed/",
    "Yale University": "https://news.yale.edu/news-rss",
    "Cornell University": "https://news.cornell.edu/taxonomy/term/81/feed",
}

# =============================
# KEYWORDS FILTER
# =============================
OPPORTUNITY_KEYWORDS = [
    "internship", "fellowship", "research", "conference",
    "workshop", "grant", "scholarship", "competition",
    "hackathon", "apply", "applications open", "summit",
    "event", "program"
]

def is_opportunity(text: str):
    text = text.lower()

    APPLICATION_KEYWORDS = [
        "applications open",
        "apply now",
        "call for applications",
        "deadline",
        "submit application",
        "open for applications",
        "now accepting applications",
        "register now"
    ]

    return any(keyword in text for keyword in APPLICATION_KEYWORDS)




# =============================
# SIMPLE RULE CATEGORY
# =============================
def classify_category(text):
    text = text.lower()

    if "internship" in text:
        return "internship"
    if "fellowship" in text:
        return "fellowship"
    if "research" in text:
        return "research"
    if "scholarship" in text:
        return "scholarship"
    if "conference" in text:
        return "conference"
    if "competition" in text:
        return "competition"
    if "event" in text or "workshop" in text:
        return "event"

    return "general"

# =============================
# GEMINI CONFIG
# =============================
GEMINI_CALL_LIMIT = 5
gemini_calls_made = 0

def analyze_with_gemini(title, description, link, university):

    global gemini_calls_made

    if gemini_calls_made >= GEMINI_CALL_LIMIT:
        print("Gemini call limit reached for this scrape.")
        return None

    prompt = f"""
    Extract structured academic opportunity details.

    Return JSON only:

    {{
      "domain": "",
      "sub_domain": "",
      "deadline": "",
      "eligibility": "",
      "skills_required": []
    }}

    Title: {title}
    Description: {description}
    Link: {link}
    University: {university}

    If not enough information, return empty fields.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        gemini_calls_made += 1

        text = response.text.strip()

        return json.loads(text)

    except Exception as e:
        print("Gemini Error:", e)
        time.sleep(5)
        return None

# =============================
# DEADLINE REGEX
# =============================
def extract_deadline(text):
    match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}", text)
    if match:
        return match.group(0)
    return None

# =============================
# RSS SCRAPER
# =============================
def scrape_rss():

    global gemini_calls_made
    gemini_calls_made = 0

    print("Starting RSS opportunity scrape...")

    db: Session = SessionLocal()

    for university, feed_url in RSS_FEEDS.items():

        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:15]:

            title = entry.get("title", "")
            description = entry.get("summary", "")
            link = entry.get("link", "")

            combined = f"{title} {description}"

            if not is_opportunity(combined):
                continue

            exists = db.query(Opportunity).filter(
                Opportunity.title == title
            ).first()

            if exists:
                continue

            category = classify_category(combined)
            deadline = extract_deadline(combined)

            structured = analyze_with_gemini(
                title, description, link, university
            )

            if structured is None:
                structured = {
                    "domain": "General",
                    "sub_domain": "General",
                    "deadline": deadline,
                    "eligibility": None,
                    "skills_required": []
                }

            new_opp = Opportunity(
                title=title,
                university=university,
                category=category,
                domain=structured.get("domain"),
                sub_domain=structured.get("sub_domain"),
                deadline=structured.get("deadline") or deadline,
                eligibility=structured.get("eligibility"),
                skills_required=",".join(structured.get("skills_required", [])),
                application_link=link,
            )

            db.add(new_opp)
            db.commit()

            print("Inserted:", title)

    db.close()
    print("RSS opportunity scrape completed.")

# =============================
# SCHEDULER
# =============================
scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(scrape_rss, "interval", hours=1)
    scheduler.start()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    start_scheduler()

# =============================
# ROUTES
# =============================
@app.get("/")
def root():
    return {"status": "Ivy League Opportunity Intelligence Running"}

@app.get("/scrape-now")
def scrape_now():
    scrape_rss()
    return {"message": "RSS scraping executed successfully"}

@app.get("/opportunities")
def get_opportunities():
    db = SessionLocal()
    data = db.query(Opportunity).all()
    db.close()
    return data
