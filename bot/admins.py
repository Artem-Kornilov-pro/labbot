"""Администраторы бота: без лимита лаб, доступ к /stats. Задаются Telegram id и/или @username."""
import os

# администраторы по умолчанию (если ADMIN_USERNAMES не задан)
DEFAULT_USERNAMES = "ArtemigKot ryplesh"


def _split(value):
    return value.replace(",", " ").split()


class Admins:
    def __init__(self, ids=(), usernames=()):
        self.ids = {int(x) for x in ids}
        self.usernames = {u.lstrip("@").lower() for u in usernames if u.lstrip("@")}

    @classmethod
    def from_env(cls, env=os.environ):
        return cls(_split(env.get("ADMIN_IDS", "")), _split(env.get("ADMIN_USERNAMES", DEFAULT_USERNAMES)))

    def __contains__(self, user):
        """user – пользователь Telegram (aiogram User) или его id."""
        if user is None:
            return False
        if isinstance(user, int):
            return user in self.ids
        return user.id in self.ids or bool(user.username) and user.username.lower() in self.usernames
