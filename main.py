import os
import json
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from google import genai

from database import SessionLocal, engine
from models import Base, Opportunity

# -------------------------
# Load environment
# -------------------------
load_dotenv()

# -------------------------
# Gemini Setup (NEW SDK)
# -------------------------
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# -------------------------
# FastAPI App
# -------------------------
app = FastAPI()

# -------------------------
# University URLs (Use real ones)
# -------------------------
UNIVERSITY_SITES = {
    "Harvard": "https://careers.harvard.edu/jobs",
}

# -------------------------
# Gemini Structured Extraction
# -------------------------
def analyze_with_gemini(text: str):

    prompt = f"""
    Extract structured opportunity data in JSON format:

    {{
      "title": "",
      "university": "",
      "domain": "",
      "sub_domain": "",
      "deadline": "",
      "eligibility": "",
      "skills_required": [],
      "application_link": ""
    }}

    Text:
    {text}

    Return ONLY valid JSON.
    """

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )

        cleaned = response.text.strip()

        print("Gemini raw response:", cleaned)

        return json.loads(cleaned)

    except Exception as e:
        print("Gemini Error:", e)
        return None


# -------------------------
# Scraper Function
# -------------------------
def scrape_universities():

    print("Starting scrape job...")

    db: Session = SessionLocal()

    for university, url in UNIVERSITY_SITES.items():
        try:
            response = requests.get(url, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")

            # IMPORTANT: Adjust selector per site
            job_cards = soup.find_all("a")  # more realistic than generic div

            for card in job_cards[:10]:

                raw_text = card.get_text(strip=True)

                if not raw_text or len(raw_text) < 20:
                    continue

                print("Raw scraped:", raw_text)

                structured = analyze_with_gemini(raw_text)

                if not structured:
                    continue

                title = structured.get("title")

                if not title:
                    continue

                exists = db.query(Opportunity).filter(
                    Opportunity.title == title
                ).first()

                if exists:
                    continue

                new_opp = Opportunity(
                    title=title,
                    university=structured.get("university") or university,
                    domain=structured.get("domain"),
                    sub_domain=structured.get("sub_domain"),
                    deadline=structured.get("deadline"),
                    eligibility=structured.get("eligibility"),
                    skills_required=",".join(structured.get("skills_required", [])),
                    application_link=structured.get("application_link"),
                )

                db.add(new_opp)
                db.commit()

                print("Inserted:", title)

        except Exception as e:
            print(f"Error scraping {university}: {e}")

    db.close()

    print("Scrape job completed.")


# -------------------------
# Scheduler Setup
# -------------------------
scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(scrape_universities, "interval", hours=1)
    scheduler.start()
    print("Scheduler started.")


# -------------------------
# Startup Event
# -------------------------
@app.on_event("startup")
def startup():

    print("Connecting to database...")

    try:
        Base.metadata.create_all(bind=engine)
        print("Database ready.")
    except Exception as e:
        print("Database error:", e)

    start_scheduler()


# -------------------------
# API Routes
# -------------------------
@app.get("/")
def root():
    return {"status": "Ivy League Opportunity System Running"}


@app.get("/scrape-now")
def scrape_now():
    scrape_universities()
    return {"message": "Scraping executed successfully"}


@app.get("/opportunities")
def get_opportunities():
    db = SessionLocal()
    data = db.query(Opportunity).all()
    db.close()
    return data
