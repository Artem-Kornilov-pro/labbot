"""Чёрный список по @username: на любое сообщение или кнопку – один ответ, обработчики не вызываются."""
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message


class Blocklist(BaseMiddleware):
    def __init__(self, usernames, text):
        self.usernames = {u.lstrip("@").lower() for u in usernames}
        self.text = text

    async def __call__(self, handler, event, data):
        user = event.from_user
        if user and user.username and user.username.lower() in self.usernames:
            if isinstance(event, CallbackQuery):
                await event.answer()
                await event.message.answer(self.text)
            elif isinstance(event, Message):
                await event.answer(self.text)
            return None
        return await handler(event, data)
