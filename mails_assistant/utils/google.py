import re
import base64
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

from bs4 import BeautifulSoup
from fastapi import HTTPException, status
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from mails_assistant import DATA_PATH, GOOGLE_TOKENS_DIR, SCOPES


def convert_user_id_to_google_token_file(user_id: str) -> str:
    token_file = f'{user_id}-google-token.json'
    return token_file


def check_google_credentials(user_id: str) -> bool:
    google_token_path = _get_google_token_path(user_id)

    return google_token_path.exists()


def save_google_credentials(credentials: Credentials, user_id: str) -> None:
    google_token_path = _get_google_token_path(user_id)

    with open(google_token_path, 'w') as google_token:
        google_token.write(credentials.to_json())


def get_google_credentials(user_id: str) -> Credentials:
    do_google_credentials_exist = check_google_credentials(user_id)
    if not do_google_credentials_exist:
        HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Please, give us permissions to use your gmail through the google authentication.'
        )

    google_token_path = _get_google_token_path(user_id)

    return Credentials.from_authorized_user_file(google_token_path, SCOPES)


def get_gmail_messages(user_id: str, gmail_address: str, labels: List[str], max_results: int) -> Dict:
    google_service = build('gmail', 'v1', credentials=get_google_credentials(user_id))
    labels = list(map(lambda label: label.upper(), labels))

    return google_service.users().messages().list(
        userId=gmail_address, labelIds=labels, maxResults=max_results
    ).execute()


@lru_cache(maxsize=1024)
def get_gmail_message_content(user_id: str, gmail_address: str, message_id: str) -> Dict:
    google_service = build('gmail', 'v1', credentials=get_google_credentials(user_id))
    message = google_service.users().messages().get(userId=gmail_address, id=message_id, format='full').execute()
    
    payload = message['payload']
    headers = payload['headers']
    
    subject = next(header['value'] for header in headers if header['name'] == 'Subject')
    sender = next(header['value'] for header in headers if header['name'] == 'From')
    sendee = next(header['value'] for header in headers if header['name'] == 'To')
    
    parts = payload.get('parts', [])
    body = ''
    
    if 'data' in payload['body']:
        body = payload['body'].get('data', '')
    elif parts:
        for part in parts:
            if part['mimeType'] == 'text/plain':
                body = part['body'].get('data', '')
                break
    
    body = base64.urlsafe_b64decode(body).decode('utf-8')
    soup = BeautifulSoup(body, 'html.parser')
    
    return {
        'message_id': message_id,
        'subject': subject,
        'sender': sender,
        'sendee': sendee,
        'body': re.sub(r'\s+', ' ', soup.get_text().replace('\n', '').replace('\t', '')).strip()
    }


def get_gmail_labels(user_id: str, gmail_address: str) -> Dict:
    google_service = build('gmail', 'v1', credentials=get_google_credentials(user_id))
    labels = google_service.users().labels().list(userId=gmail_address).execute()

    return labels


def _get_google_token_path(user_id: str) -> Path:
    google_token_file = convert_user_id_to_google_token_file(user_id)
    google_token_path = DATA_PATH / GOOGLE_TOKENS_DIR / google_token_file

    return google_token_path
