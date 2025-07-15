from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db import Base

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey('problems.id'))
    reviewer = Column(String)
    status = Column(String)         # e.g., "approved", "changes_requested"
    feedback = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    problem = relationship("Problem")
