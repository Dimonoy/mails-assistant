from fastapi import APIRouter, FastAPI, status
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from googleapiclient.errors import HttpError as GoogleHttpError

from mails_assistant.exception_handlers import google_service_unavailable_handler
from mails_assistant.middleware import UserIDMiddleware
from mails_assistant.routes.auth import router as auth_router
from mails_assistant.routes.gmail import router as gmail_router
from mails_assistant.routes.prompt import router as prompt_router

app = FastAPI()
router = APIRouter()
app.add_middleware(UserIDMiddleware)
app.add_middleware(SessionMiddleware, secret_key='secret_key')


@router.get('/')
async def root():
    return RedirectResponse(url='/docs', status_code=status.HTTP_302_FOUND)

app.add_exception_handler(GoogleHttpError, google_service_unavailable_handler)

app.include_router(router)
app.include_router(gmail_router)
app.include_router(prompt_router)
app.include_router(auth_router)
