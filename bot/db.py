"""Учёт выданных лаб в SQLite (стандартная библиотека: без сервера БД и лишних зависимостей).

Одна строка – одна сгенерированная лаба: кто (Telegram id, @username, ФИО из анкеты) и что получил.
По этой же таблице считается лимит лаб на пользователя.
"""
import sqlite3
import threading
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS gens(
    id       INTEGER PRIMARY KEY,
    user_id  INTEGER NOT NULL,
    username TEXT,
    name     TEXT NOT NULL,
    grp      TEXT,
    teacher  TEXT,
    lab      TEXT NOT NULL,
    variant  INTEGER NOT NULL,
    nums     TEXT NOT NULL,
    created  INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS gens_user ON gens(user_id);
"""


class Quota:
    def __init__(self, path, limit=2):
        self.limit = limit
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        # одно соединение на процесс; вызовы приходят из потоков asyncio.to_thread, поэтому – под блокировкой
        self.db = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(SCHEMA)
        self.lock = threading.Lock()

    def used(self, user_id):
        with self.lock:
            return self.db.execute("SELECT COUNT(*) FROM gens WHERE user_id = ?", (user_id,)).fetchone()[0]

    def left(self, user_id):
        return max(0, self.limit - self.used(user_id))

    def reserve(self, user_id, username, data, unlimited=False):
        """Занять одну лабу из лимита до генерации; None – лимит исчерпан.
        Проверка и вставка – один запрос, поэтому двойное нажатие «Сгенерировать» не обходит лимит."""
        row = (user_id, username, data["name"], data.get("group", ""), data.get("teacher", ""), data["lab"],
               data["variant"], " ".join(map(str, data["nums"])), int(time.time()))
        with self.lock:
            cur = self.db.execute(
                "INSERT INTO gens(user_id, username, name, grp, teacher, lab, variant, nums, created) "
                "SELECT ?, ?, ?, ?, ?, ?, ?, ?, ? "
                "WHERE ? OR (SELECT COUNT(*) FROM gens WHERE user_id = ?) < ?",
                row + (unlimited, user_id, self.limit))
            return cur.lastrowid if cur.rowcount else None

    def release(self, rec_id):
        """Вернуть лабу в лимит, если генерация не удалась."""
        with self.lock:
            self.db.execute("DELETE FROM gens WHERE id = ?", (rec_id,))
