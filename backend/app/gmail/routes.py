from fastapi import APIRouter, Depends, HTTPException
from app.gmail.gmail_client import get_user_messages
from app.gmail.gmail_prompt_formatter import format_prompt, format_classification_prompt
from app.llm.llm_client import get_llm_response  # You'll define this
from app.auth.routes import get_user_tokens  # You'll define this too
from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
import json
import re
from datetime import datetime

from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.crud import (
    create_email,
    get_last_email_sync,
    update_last_email_sync,
    get_emails,
    create_meeting_note,
    get_meeting_notes,
)

router = APIRouter()


def email_retriever_helper(tokens: str, max_results: int, after: int = None):
    emails = get_user_messages(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_uri=tokens["token_uri"],
        client_id=tokens["client_id"],
        client_secret=tokens["client_secret"],
        max_results=max_results,
        after=after,
    )

    return emails

@router.get("/emails/summary")
def email_summary(user_id: str = Query(...), db: Session = Depends(get_db)):
    # 1. Get tokens
    tokens = get_user_tokens(user_id)
    if not tokens:
        return JSONResponse({"error": "No tokens found for this user"}, status_code=401)

    # 2. Fetch new emails since last sync
    last_sync = get_last_email_sync(db, user_id)
    after = int(last_sync.timestamp()) if last_sync else None
    emails = email_retriever_helper(tokens, max_results=50, after=after)

    # 3. Store fetched emails in DB
    for e in emails:
        create_email(db, user_id, e)

    # 4. Build LLM prompt and call the model
    prompt = format_prompt(emails)
    try:
        llm_output = get_llm_response(prompt)
        # extract the first JSON object in the response
        match = re.search(r"\{.*\}", llm_output, re.DOTALL)
        payload = match.group(0) if match else llm_output
        parsed = json.loads(payload)
        meetings = parsed.get("meetings", [])
        # persist meeting summaries
        for m in meetings:
            create_meeting_note(db, user_id, m)
    except json.JSONDecodeError:
        return JSONResponse(content={"error": "Invalid JSON returned by LLM."}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    # 5. Update last sync timestamp only after successful processing
    update_last_email_sync(db, user_id, datetime.utcnow())
    return JSONResponse(content={"meetings": meetings})
    
@router.get("/emails/recent")
def recent_emails(user_id: str = Query(...), db: Session = Depends(get_db)):
    tokens = get_user_tokens(user_id)
    if not tokens:
        return JSONResponse({"error": "No tokens found for this user"}, status_code=401)

    last_sync = get_last_email_sync(db, user_id)
    after = int(last_sync.timestamp()) if last_sync else None
    emails = email_retriever_helper(tokens, max_results=3, after=after)

    for e in emails:
        create_email(db, user_id, e)
    update_last_email_sync(db, user_id, datetime.utcnow())

    return JSONResponse(content=emails)


@router.get("/emails")
def list_emails(user_id: str = Query(...), db: Session = Depends(get_db)):
    """
    Retrieve all stored emails for the user (newest first).
    """
    stored = get_emails(db, user_id, limit=50)
    results = [
        {
            "id": e.id,
            "subject": e.subject,
            "from": e.sender,
            "date": e.date.isoformat() if e.date else None,
            "snippet": e.snippet,
        }
        for e in stored
    ]
    return JSONResponse(content=results)


@router.post("/emails/reprocess")
def rerun_email_summary(
    user_id: str = Query(...),
    limit: int = Query(50, gt=0),
    db: Session = Depends(get_db),
):
    """
    Re-run LLM summarization on stored emails to populate meeting notes.
    """
    stored = get_emails(db, user_id, limit)
    # Build payload for LLM prompt formatter
    emails_data = [
        {
            "id": e.id,
            "subject": e.subject or "",
            "from": e.sender or "",
            "date": e.date.isoformat() if e.date else "",
            "snippet": e.snippet or "",
        }
        for e in stored
    ]
    prompt = format_prompt(emails_data)
    try:
        llm_output = get_llm_response(prompt)
        parsed = json.loads(llm_output)
        meetings = parsed.get("meetings", [])
        for m in meetings:
            create_meeting_note(db, user_id, m)
        return JSONResponse(content={"meetings": meetings})
    except json.JSONDecodeError:
        return JSONResponse(content={"error": "Invalid JSON returned by LLM."}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/meetings")
def list_meetings(user_id: str = Query(...), db: Session = Depends(get_db)):
    """
    Retrieve stored meeting summaries for the user.
    """
    notes = get_meeting_notes(db, user_id)
    results = [
        {"id": n.id, "meeting_text": n.meeting_text, "note": n.note}
        for n in notes
    ]
    return JSONResponse(content=results)


@router.post("/emails/classify")
def classify_emails(
    user_id: str = Query(...),
    limit: int = Query(50, gt=0),
    db: Session = Depends(get_db),
):
    """
    Run LLM classification on stored emails and return category lists.
    """
    stored = get_emails(db, user_id, limit)
    emails_data = [
        {
            "id": e.id,
            "subject": e.subject or "",
            "from": e.sender or "",
            "date": e.date.isoformat() if e.date else "",
            "snippet": e.snippet or "",
        }
        for e in stored
    ]
    prompt = format_classification_prompt(emails_data)
    try:
        llm_output = get_llm_response(prompt)
        # extract JSON block from LLM output
        match = re.search(r"\{.*\}", llm_output, re.DOTALL)
        payload = match.group(0) if match else llm_output
        parsed = json.loads(payload)
        return JSONResponse(content=parsed)
    except json.JSONDecodeError:
        return JSONResponse(content={"error": "Invalid JSON returned by LLM."}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
