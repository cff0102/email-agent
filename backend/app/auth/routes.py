# app/auth/routes.py
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Request
from app.gmail.gmail_client import get_user_messages
from app.auth.google_oauth import exchange_code_for_token, get_user_info, get_login_url
import os

router = APIRouter()

# In-memory token storage (replace with DB in prod)
user_token_store = {}
def get_user_tokens(user_email):
    return user_token_store.get(user_email)


@router.get("/auth/login")
def login():
    return RedirectResponse(get_login_url())

@router.get("/auth/callback")
def callback(request: Request, code: str):
    # 1. Exchange auth code for credentials
    creds = exchange_code_for_token(code)

    # 2. Get user email from token
    user_info = get_user_info(creds)
    user_email = user_info["email"]

    # 3. Store tokens (you can add expiration later)
    user_token_store[user_email] = {
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret
    }

    # 4. Redirect to summary endpoint or frontend dashboard
    # Option A: Redirect to backend summary (for development)
    return RedirectResponse(url=f"http://localhost:5173?user_id={user_email}")
