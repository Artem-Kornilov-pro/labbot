"""Лимит лаб на пользователя и запись в базу."""
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bot.db import Quota  # noqa: E402

DATA = {"lab": "lab2", "name": "Иванов Иван Иванович", "group": "БИТ261", "teacher": "", "variant": 15,
        "nums": [16, 6]}


def test_limit_two_per_user(tmp_path):
    q = Quota(tmp_path / "db.sqlite", limit=2)
    assert q.reserve(1, "ivan", DATA) and q.reserve(1, "ivan", DATA)
    assert q.reserve(1, "ivan", DATA) is None
    assert q.left(1) == 0
    assert q.left(2) == 2 and q.reserve(2, None, DATA)      # у другого пользователя свой лимит
    assert q.reserve(1, "ivan", DATA, unlimited=True)       # администратор без лимита


def test_release_and_persistence(tmp_path):
    path = tmp_path / "db.sqlite"
    q = Quota(path, limit=2)
    rec = q.reserve(1, "ivan", DATA)
    q.reserve(1, "ivan", DATA)
    q.release(rec)                                          # генерация упала – лаба возвращается
    assert q.left(1) == 1
    row = Quota(path).db.execute("SELECT user_id, username, name, grp, lab, variant, nums FROM gens").fetchone()
    assert row == (1, "ivan", "Иванов Иван Иванович", "БИТ261", "lab2", 15, "16 6")


def test_concurrent_reserve_respects_limit(tmp_path):
    q = Quota(tmp_path / "db.sqlite", limit=2)
    with ThreadPoolExecutor(8) as ex:
        got = list(ex.map(lambda _: q.reserve(1, "ivan", DATA), range(20)))
    assert sum(r is not None for r in got) == 2
