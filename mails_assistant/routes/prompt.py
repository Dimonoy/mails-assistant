from typing import List
from fastapi import APIRouter, Query, Request, status
from fastapi.responses import JSONResponse
from mails_assistant.ai import OpenAILLM
from mails_assistant.utils.google import get_gmail_message_content


router = APIRouter()
openai_llm = OpenAILLM()


@router.post('/ai/prompt')
async def prompt_ai(request: Request, prompt: str, gmail_address: str, message_ids: List[str] = Query()):
    messages = []
    for message_id in message_ids:
        messages.append(get_gmail_message_content(request.session['user_id'], gmail_address, message_id))

    messages_formatted = '\n\n'.join(
        f'SUBJECT: {message["subject"]}\nSENDER: {message["sender"]}\nBODY: {message["body"]}' for message in messages
    )
    content = f"""
---
{messages_formatted}
---

Above are the messages from gmail separated by double carriage return symbol within the block starting and ending
with '---' symbol.

If asked to generated a draft, here is the output format within the '---' symbols:
---
SUBJECT: [SUBJECT]
TO: [SENDER]
BODY: [BODY]
---

User's prompt: {prompt}
    """

    detail = await openai_llm.generate_response(content)

    return JSONResponse({'detail': detail}, status_code=status.HTTP_200_OK)
