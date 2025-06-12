# app/auth/google_oauth.py
import os
from fastapi import Request
from urllib.parse import urlencode
import dotenv
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import requests
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials

dotenv.load_dotenv()


def get_user_info(creds: Credentials):
    authed_session = AuthorizedSession(creds)
    response = authed_session.get("https://www.googleapis.com/oauth2/v2/userinfo")
    response.raise_for_status()
    return response.json()

def get_login_url():
    params = {
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "redirect_uri": os.environ["REDIRECT_URI"],
        "response_type": "code",
        "scope": (
            "openid "
            "https://www.googleapis.com/auth/userinfo.email "
            "https://www.googleapis.com/auth/userinfo.profile "
            "https://www.googleapis.com/auth/gmail.readonly"
        ),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

def exchange_code_for_token(code: str):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.environ["GOOGLE_CLIENT_ID"],
                "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.environ["REDIRECT_URI"]],
            }
        },
        scopes=[
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid",
        ],
    )
    flow.redirect_uri = os.environ["REDIRECT_URI"]
    flow.fetch_token(code=code, include_client_id=True)
    return flow.credentials
