from sqlalchemy.orm import Session
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from app.database.models import Email, EmailSync, MeetingNote
import uuid

def get_last_email_sync(db: Session, user_id: str):
    """
    Retrieve the last sync timestamp for a given user.
    """
    sync = db.query(EmailSync).filter(EmailSync.user_id == user_id).first()
    return sync.last_sync if sync else None

def update_last_email_sync(db: Session, user_id: str, last_sync: datetime):
    """
    Update or create the last sync timestamp for a given user.
    """
    sync = db.query(EmailSync).filter(EmailSync.user_id == user_id).first()
    if sync:
        sync.last_sync = last_sync
    else:
        sync = EmailSync(user_id=user_id, last_sync=last_sync)
        db.add(sync)
    db.commit()
    db.refresh(sync)
    return sync

def create_email(db: Session, user_id: str, email_data: dict):
    """
    Store a single email in the database if it does not already exist.
    """
    existing = db.query(Email).filter(Email.id == email_data["id"]).first()
    if existing:
        return existing

    date_str = email_data.get("date")
    try:
        dt = parsedate_to_datetime(date_str) if date_str else None
        if dt and dt.tzinfo:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    except Exception:
        dt = None

    email = Email(
        id=email_data["id"],
        user_id=user_id,
        subject=email_data.get("subject", ""),
        sender=email_data.get("from", ""),
        date=dt,
        snippet=email_data.get("snippet", "")
    )
    db.add(email)
    db.commit()
    db.refresh(email)
    return email

def get_emails(db: Session, user_id: str, limit: int = None):
    """
    Retrieve stored emails for a user, newest first.
    """
    query = db.query(Email).filter(Email.user_id == user_id).order_by(Email.date.desc())
    if limit:
        query = query.limit(limit)
    return query.all()

def create_meeting_note(db: Session, user_id: str, meeting_text: str):
    """
    Store a meeting summary text if not already present.
    """
    existing = db.query(MeetingNote).filter(
        MeetingNote.user_id == user_id,
        MeetingNote.meeting_text == meeting_text
    ).first()
    if existing:
        return existing
    note = MeetingNote(
        id=str(uuid.uuid4()),
        user_id=user_id,
        meeting_text=meeting_text,
        note=""
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

def get_meeting_notes(db: Session, user_id: str):
    """
    Retrieve stored meeting summaries for a user.
    """
    return db.query(MeetingNote).filter(MeetingNote.user_id == user_id).order_by(MeetingNote.meeting_text).all()