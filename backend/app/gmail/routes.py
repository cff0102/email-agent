from fastapi import APIRouter, Depends, HTTPException
from app.gmail.gmail_client import get_user_messages
from app.gmail.gmail_prompt_formatter import format_prompt
from app.llm.llm_client import get_llm_response  # You'll define this
from app.auth.routes import get_user_tokens  # You'll define this too
from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
import json

router = APIRouter()


def email_retriever_helper(tokens: str, max_results: int):
    emails = get_user_messages(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_uri=tokens["token_uri"],
        client_id=tokens["client_id"],
        client_secret=tokens["client_secret"],
        max_results = max_results
    )

    return emails

@router.get("/emails/summary")
def email_summary(user_id: str = Query(...)):
    # 1. Get tokens
    tokens = get_user_tokens(user_id)
    if not tokens:
        return JSONResponse({"error": "No tokens found for this user"}, status_code=401)

    # 2. Fetch emails
    emails = email_retriever_helper(tokens, max_results=50)

    # 3. Format LLM prompt
    prompt = format_prompt(emails)

    # 4. Get LLM summary
    try:
        llm_output = get_llm_response(prompt)
        print(llm_output)
        parsed = json.loads(llm_output)  # assumes the LLM response is valid JSON
        meetings = parsed.get("meetings", [])  # fallback to empty list if not present
        return JSONResponse(content={"meetings": meetings})
    except json.JSONDecodeError:
        return JSONResponse(content={"error": "Invalid JSON returned by LLM."}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@router.get("/emails/recent")
def recent_emails(user_id: str = Query(...)):
    tokens = get_user_tokens(user_id)
    if not tokens:
        return JSONResponse({"error": "No tokens found for this user"}, status_code=401)

    emails = email_retriever_helper(tokens, max_results=3)

    return JSONResponse(content=emails)
