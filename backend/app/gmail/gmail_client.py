from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

def get_user_messages(access_token: str, refresh_token: str, token_uri: str, client_id: str, client_secret: str, max_results: int, after: int = None):
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/gmail.readonly"]
    )

    try:
        service = build('gmail', 'v1', credentials=creds)
        # Fetch messages after the last sync timestamp (epoch seconds) if provided
        if after:
            query = f"after:{after}"
            results = service.users().messages().list(userId='me', maxResults=max_results, q=query).execute()
        else:
            results = service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])

        emails = []
        for msg in messages:
            msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            payload = msg_detail.get('payload', {})
            headers = payload.get('headers', [])

            # Extract headers like Subject, From, Date
            header_dict = {h['name']: h['value'] for h in headers}
            subject = header_dict.get('Subject', '')
            sender = header_dict.get('From', '')
            date = header_dict.get('Date', '')

            snippet = msg_detail.get('snippet', '')

            emails.append({
                "id": msg['id'],
                "subject": subject,
                "from": sender,
                "date": date,
                "snippet": snippet
            })

        return emails

    except HttpError as error:
        print(f'An error occurred: {error}')
        return []
