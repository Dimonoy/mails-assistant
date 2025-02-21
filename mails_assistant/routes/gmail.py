from typing import List
from fastapi import APIRouter, Query, Request, status
from fastapi.responses import JSONResponse

from mails_assistant.utils import get_gmail_messages, get_gmail_message_content, get_gmail_labels as _get_gmail_labels

router = APIRouter()


@router.get('/gmail/mails')
async def get_gmail_mails(
    request: Request,
    gmail_address: str,
    labels: List[str] = Query(default=['INBOX']),
    max_results: int = 3,
):
    messages = get_gmail_messages(request.session['user_id'], gmail_address, labels, max_results)
    messages = messages.get('messages', [])
    detail = {'mails': []}

    for message in messages:
        message_id = message['id']
        detail['mails'].append(get_gmail_message_content(request.session['user_id'], gmail_address, message_id))

    return JSONResponse({'detail': detail}, status_code=status.HTTP_200_OK)


@router.get('/gmail/labels')
async def get_gmail_labels(request: Request, gmail_address: str):
    detail = _get_gmail_labels(request.session['user_id'], gmail_address)

    return JSONResponse({'detail': detail}, status_code=status.HTTP_200_OK)
