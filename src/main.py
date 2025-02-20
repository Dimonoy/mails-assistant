from fastapi import FastAPI, HTTPException, Request, status
from starlette.middleware.sessions import SessionMiddleware
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src import DATA_PATH, GOOGLE_CREDENTIALS_FILE, SCOPES
from src._utils import get_message_content, save_google_credentials, check_google_credentials, get_google_credentials
from src._middleware import UserIDMiddleware

app = FastAPI()
app.add_middleware(UserIDMiddleware)
app.add_middleware(SessionMiddleware, secret_key='secret_key')


@app.get('/')
async def root():
    return {'Hello': 'World!'}


@app.get('/auth/google')
async def auth_google(request: Request):
    do_credentials_exist = check_google_credentials(request.session['user_id'])
    if do_credentials_exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Already authorized.')
    
    flow = Flow.from_client_secrets_file(
        str(DATA_PATH / GOOGLE_CREDENTIALS_FILE),
        scopes=SCOPES
    )
    flow.redirect_uri = 'http://127.0.0.1:8000/auth/google/callback'
    authorization_url, _ = flow.authorization_url(prompt='consent')

    return {'authorization_url': authorization_url}


@app.get('/auth/google/callback')
async def auth_google_callback(request: Request):
    flow = Flow.from_client_secrets_file(
        str(DATA_PATH / GOOGLE_CREDENTIALS_FILE),
        scopes=SCOPES,
        state=request.query_params.get('state')
    )
    flow.redirect_uri = 'http://127.0.0.1:8000/auth/google/callback'
    flow.fetch_token(code=request.query_params.get('code'))

    save_google_credentials(flow.credentials, request.session['user_id'])

    return {'message': 'Authentication successful'}


@app.get('/gmails')
async def get_gmails(request: Request):
    try:
        google_service = build('gmail', 'v1', credentials=get_google_credentials(request.session['user_id']))
        results = google_service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=3).execute()
        messages = results.get('messages', [])
        response = {'mails': []}

        for message in messages:
            msg_id = message['id']
            response['mails'].append(get_message_content(google_service, 'me', msg_id))

        return {'detail': response}

    except HttpError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Something wrong with Google: {error.content}'
        )
