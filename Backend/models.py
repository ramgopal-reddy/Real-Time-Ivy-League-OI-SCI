from sqlalchemy import Column, Integer, String, Text
from database import Base

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    university = Column(String, index=True)
    category = Column(String)   # NEW
    domain = Column(String)
    sub_domain = Column(String)
    deadline = Column(String)
    eligibility = Column(Text)
    skills_required = Column(Text)
    application_link = Column(String)
