import re
import base64
from pathlib import Path

from bs4 import BeautifulSoup
from fastapi import HTTPException, status
from google.oauth2.credentials import Credentials

from src import DATA_PATH, GOOGLE_TOKENS_DIR, SCOPES
from src._logger import logger


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


def get_message_content(service, user_id, msg_id):
    message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
    
    payload = message['payload']
    headers = payload['headers']
    
    logger.debug(payload)
    
    subject = next(header['value'] for header in headers if header['name'] == 'Subject')
    sender = next(header['value'] for header in headers if header['name'] == 'From')
    
    parts = payload.get('parts', [])
    body = ''
    
    if 'body' in payload:
        body = payload['body'].get('data', '')
    elif parts:
        for part in parts:
            if part['mimeType'] == 'text/plain':
                body = part['body'].get('data', '')
                break
    
    body = base64.urlsafe_b64decode(body).decode('utf-8')
    soup = BeautifulSoup(body)
    
    return {
        'subject': subject,
        'sender': sender,
        'body': re.sub('\s+', ' ', soup.get_text().replace('\n', '').replace('\t', '')).strip()
    }


def _get_google_token_path(user_id: str) -> Path:
    google_token_file = convert_user_id_to_google_token_file(user_id)
    google_token_path = DATA_PATH / GOOGLE_TOKENS_DIR / google_token_file

    return google_token_path
