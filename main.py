import os
import json
import feedparser
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from google import genai

from database import SessionLocal, engine
from models import Base, Opportunity

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

# -------------------------
# Official RSS Feeds
# -------------------------
RSS_FEEDS = {
    "Harvard University": "https://news.harvard.edu/gazette/feed/",
    "Yale University": "https://news.yale.edu/news-rss",
    "Cornell University": "https://news.cornell.edu/taxonomy/term/81/feed",
}

# -------------------------
# Keyword Filter
# -------------------------
OPPORTUNITY_KEYWORDS = [
    "internship", "fellowship", "research", "conference",
    "workshop", "grant", "scholarship", "competition",
    "hackathon", "apply", "applications open", "summit",
    "event", "program"
]

def is_opportunity(text: str):
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in OPPORTUNITY_KEYWORDS)

# -------------------------
# Gemini Structured Classification
# -------------------------
def analyze_with_gemini(title, description, link, university):

    prompt = f"""
    Classify and structure this academic opportunity.

    Categories allowed:
    internship, research, scholarship, fellowship,
    competition, conference, event, general

    Return JSON:

    {{
      "title": "",
      "university": "",
      "category": "",
      "domain": "",
      "sub_domain": "",
      "deadline": "",
      "eligibility": "",
      "skills_required": [],
      "application_link": ""
    }}

    Title: {title}
    Description: {description}
    Link: {link}
    University: {university}

    If this is NOT an academic opportunity, return null.

    Return ONLY valid JSON.
    """

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )

        text = response.text.strip()

        if text.lower() == "null":
            return None

        return json.loads(text)

    except Exception as e:
        print("Gemini Error:", e)
        return None


# -------------------------
# RSS Scraper
# -------------------------
def scrape_rss():

    print("Starting RSS opportunity scrape...")

    db: Session = SessionLocal()

    for university, feed_url in RSS_FEEDS.items():

        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:15]:

            title = entry.get("title", "")
            description = entry.get("summary", "")
            link = entry.get("link", "")

            combined_text = f"{title} {description}"

            if not is_opportunity(combined_text):
                continue

            exists = db.query(Opportunity).filter(
                Opportunity.title == title
            ).first()

            if exists:
                continue

            structured = analyze_with_gemini(
                title, description, link, university
            )

            if not structured:
                continue

            new_opp = Opportunity(
                title=structured.get("title"),
                university=structured.get("university") or university,
                category=structured.get("category"),
                domain=structured.get("domain"),
                sub_domain=structured.get("sub_domain"),
                deadline=structured.get("deadline"),
                eligibility=structured.get("eligibility"),
                skills_required=",".join(structured.get("skills_required", [])),
                application_link=structured.get("application_link") or link,
            )

            db.add(new_opp)
            db.commit()

            print("Inserted:", structured.get("title"))

    db.close()
    print("RSS opportunity scrape completed.")


# -------------------------
# Scheduler
# -------------------------
scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(scrape_rss, "interval", hours=1)
    scheduler.start()


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    start_scheduler()


# -------------------------
# API Routes
# -------------------------
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
