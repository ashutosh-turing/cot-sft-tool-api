from sqlalchemy import Column, Integer, String, Text
from backend.db import Base

class Problem(Base):
    __tablename__ = "problems"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(String, unique=True, index=True)
    title = Column(String)
    problem_link = Column(String)
    response_links = Column(Text)  
    scraped_json = Column(Text)  # stores JSON as string
