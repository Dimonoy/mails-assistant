from fastapi import Request, HTTPException, status
from googleapiclient.errors import HttpError as GoogleHttpError


async def google_service_unavailable_handler(request: Request, exc: GoogleHttpError):
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f'Something wrong with Google: {exc.content}'
    )
