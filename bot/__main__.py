"""Запуск бота: python -m bot (токен – в переменной окружения BOT_TOKEN или в файле .env)."""
import asyncio
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from .blocklist import Blocklist
from .db import Quota
from .handlers import router


ROOT = Path(__file__).resolve().parents[1]


def load_env(path=ROOT / ".env"):
    """Минимальный загрузчик .env (KEY=VALUE), не перезаписывает уже заданные переменные."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


async def main():
    load_env()
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"),
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise SystemExit("Не задан BOT_TOKEN (переменная окружения или файл .env)")
    bot = Bot(token)
    dp = Dispatcher(storage=MemoryStorage())
    # попадают в обработчики аргументами quota и admins
    dp["quota"] = Quota(os.environ.get("DB_PATH", ROOT / "data" / "labbot.db"),
                        limit=int(os.environ.get("LAB_LIMIT", "2")))
    dp["admins"] = {int(x) for x in os.environ.get("ADMIN_IDS", "").replace(",", " ").split()}
    blocked = os.environ.get("BLOCKED_USERNAMES", "").replace(",", " ").split()
    if blocked:
        bl = Blocklist(blocked, os.environ.get("BLOCK_MSG", "Доступ к боту закрыт."))
        dp.message.outer_middleware(bl)
        dp.callback_query.outer_middleware(bl)
    dp.include_router(router)
    await bot.set_my_commands([
        BotCommand(command="new", description="Создать лабу"),
        BotCommand(command="cancel", description="Отменить ввод"),
        BotCommand(command="help", description="Справка"),
    ])
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
