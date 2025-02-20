import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from ._logger import logger


class UserIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == '/auth/google':
            await self.set_user_id(request)

        response = await call_next(request)
        return response

    async def set_user_id(self, request: Request):
        logger.debug('Settings user ID...')

        if not (user_id := request.session.get('user_id')):
            user_id = str(uuid.uuid4())
            request.session['user_id'] = user_id

            logger.debug(f'User ID was set: {user_id}')

        logger.debug(f'User ID already exists: {user_id}')
