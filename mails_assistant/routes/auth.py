from fastapi import APIRouter, status, HTTPException, Request
from fastapi.responses import JSONResponse
from google_auth_oauthlib.flow import Flow

from mails_assistant import DATA_PATH, GOOGLE_CREDENTIALS_FILE, SCOPES
from mails_assistant.utils import check_google_credentials, save_google_credentials

router = APIRouter()


@router.post('/auth/google')
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

    return JSONResponse({'authorization_url': authorization_url}, status_code=status.HTTP_200_OK)



@router.post('/auth/google/callback')
async def auth_google_callback(request: Request):
    flow = Flow.from_client_secrets_file(
        str(DATA_PATH / GOOGLE_CREDENTIALS_FILE),
        scopes=SCOPES,
        state=request.query_params.get('state')
    )
    flow.redirect_uri = 'http://127.0.0.1:8000/auth/google/callback'
    flow.fetch_token(code=request.query_params.get('code'))

    save_google_credentials(flow.credentials, request.session['user_id'])

    return JSONResponse({'message': 'Authentication successful'}, status_code=status.HTTP_201_CREATED)
