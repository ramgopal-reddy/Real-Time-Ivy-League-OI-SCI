import os
import json
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
import google.generativeai as genai
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Opportunity

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# -------------------------
# FastAPI App
# -------------------------
app = FastAPI()

Base.metadata.create_all(bind=engine)

# -------------------------
# Ivy League Opportunity URLs
# (Replace with real opportunity pages)
# -------------------------
UNIVERSITY_SITES = {
    "Harvard": "https://careers.harvard.edu/jobs",
    "Yale": "https://your-yale-opportunity-url",
    "Princeton": "https://your-princeton-url",
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
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print("Gemini Error:", e)
        return None


# -------------------------
# Scraper Function
# -------------------------
def scrape_universities():

    db: Session = SessionLocal()

    for university, url in UNIVERSITY_SITES.items():
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            # Example generic selector
            cards = soup.find_all("div")

            for card in cards[:5]:  # Limit to prevent overload
                raw_text = card.get_text(separator=" ", strip=True)

                if len(raw_text) < 50:
                    continue

                structured = analyze_with_gemini(raw_text)

                if structured:

                    exists = db.query(Opportunity).filter(
                        Opportunity.title == structured.get("title"),
                        Opportunity.university == structured.get("university")
                    ).first()

                    if not exists:
                        new_opp = Opportunity(
                            title=structured.get("title"),
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

        except Exception as e:
            print(f"Error scraping {university}: {e}")

    db.close()


# -------------------------
# Scheduler (Every 1 Hour)
# -------------------------
scheduler = BackgroundScheduler()
scheduler.add_job(scrape_universities, "interval", hours=1)
scheduler.start()


# -------------------------
# API Routes
# -------------------------
@app.get("/")
def root():
    return {"status": "Ivy League Opportunity System Running"}

@app.get("/opportunities")
def get_opportunities():
    db = SessionLocal()
    data = db.query(Opportunity).all()
    db.close()

    return data
