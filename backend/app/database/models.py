from sqlalchemy import Column, String, Text, DateTime, Boolean
from app.db import Base

class Email(Base):
    __tablename__ = "emails"
    id = Column(String, primary_key=True)  # Gmail Message ID
    user_id = Column(String, index=True)
    subject = Column(String)
    sender = Column(String)
    date = Column(DateTime)
    snippet = Column(Text)
    processed = Column(Boolean, default=False)  # True if LLM processed

class MeetingNote(Base):
    __tablename__ = "meeting_notes"
    id = Column(String, primary_key=True)
    user_id = Column(String)
    meeting_text = Column(Text)
    note = Column(Text)
