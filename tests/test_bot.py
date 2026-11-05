"""Проверки логики бота без подключения к Telegram."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bot.handlers import limit_msg, norm_name, summary  # noqa: E402
from labgen.registry import LABS  # noqa: E402


def test_norm_name():
    assert norm_name("иванов иван иванович") == "Иванов Иван Иванович"
    assert norm_name("  Римский-корсаков  Николай ") == "Римский-Корсаков Николай"
    assert norm_name("Ivanov Ivan") is None
    assert norm_name("Иванов") is None
    assert norm_name("Иванов Иван Иванович Младший") is None


def test_limit_message():
    assert "получили 6 лаб." in limit_msg(6)
    assert "получили 2 лабы." in limit_msg(2)
    assert "получили 1 лабу." in limit_msg(1)
    assert "получили 11 лаб." in limit_msg(11)


def test_default_limit_is_ten(tmp_path):
    from bot.db import Quota
    assert Quota(tmp_path / "db.sqlite").limit == 10


def test_summary_and_all_labs_generate():
    for key, lab in LABS.items():
        data = {"lab": key, "name": "Иванов Иван", "group": "", "teacher": "", "variant": 15,
                "nums": list(lab.tasks_for_variant(15))}
        text = summary(data)
        assert "Вариант: 15" in text and "<b>" in text
        files = lab.generate("Иванов Иван", "", "", 15)
        assert len(files) == len(lab.PARTS) + 1 or len(files) == 2      # программы + отчёт (лаба 4 – одна программа)
        assert files[-1][0].endswith(".docx") and all(len(b) > 1000 for _, b in files)


def test_blocklist():
    import asyncio
    from unittest.mock import AsyncMock
    from aiogram.types import Message, User
    from bot.blocklist import Blocklist

    bl = Blocklist(["@The_S4CRED"], "закрыто")

    def msg(username):
        m = Message.model_construct(from_user=User(id=1, is_bot=False, first_name="x", username=username))
        object.__setattr__(m, "answer", AsyncMock())
        return m

    handler = AsyncMock(return_value="ok")
    blocked = msg("the_s4cred")
    assert asyncio.run(bl(handler, blocked, {})) is None
    blocked.answer.assert_awaited_once_with("закрыто")
    handler.assert_not_awaited()
    assert asyncio.run(bl(handler, msg("someone"), {})) == "ok"
    assert asyncio.run(bl(handler, msg(None), {})) == "ok"


def test_admins_by_id_and_username():
    from aiogram.types import User
    from bot.admins import Admins

    def u(uid, username=None):
        return User(id=uid, is_bot=False, first_name="x", username=username)
    admins = Admins.from_env({})                      # по умолчанию – ArtemigKot и ryplesh
    assert u(1, "ArtemigKot") in admins and u(2, "RYPLESH") in admins
    assert u(3, "someone") not in admins and u(4) not in admins and None not in admins
    admins = Admins.from_env({"ADMIN_IDS": "5, 6", "ADMIN_USERNAMES": "@Boss"})
    assert u(5) in admins and 6 in admins and u(7, "boss") in admins and u(8, "ArtemigKot") not in admins


def test_stats_xlsx(tmp_path):
    import io
    from openpyxl import load_workbook
    from bot.db import Quota
    from bot.stats import build_xlsx
    q = Quota(tmp_path / "db.sqlite")
    base = {"name": "Иванов Иван", "group": "БИТ261", "teacher": "", "variant": 15}
    q.reserve(1, "ivan", {**base, "lab": "3", "nums": [6, 7, 2]})
    q.reserve(1, "ivan", {**base, "lab": "4", "nums": [4, 6, 5]})
    q.reserve(2, None, {**base, "name": "Петров Пётр", "lab": "4", "nums": [1, 2, 3]})
    wb = load_workbook(io.BytesIO(build_xlsx(q.rows(), q.limit)))
    assert wb.sheetnames == ["Сводка", "Пользователи", "Выдачи"]
    summary = {r[0]: r[1] for r in wb["Сводка"].iter_rows(values_only=True) if r[0]}
    assert summary["Всего выдано лаб"] == 3 and summary["Пользователей"] == 2 and summary["Лаба 4"] == 2
    users = list(wb["Пользователи"].iter_rows(min_row=2, values_only=True))
    assert users[0][:5] == (1, "@ivan", "Иванов Иван", "БИТ261", 2)
    assert wb["Выдачи"].max_row == 4
    assert build_xlsx([], 10)                        # пустая база – таблица всё равно строится
