"""Статистика бота для команды /stats: Excel-таблица по базе выданных лаб.

Листы: «Сводка» (итоги, по лабам, по дням), «Пользователи», «Выдачи» (все сгенерированные лабы).
"""
import io
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

MSK = timezone(timedelta(hours=3))      # время в таблице – московское (без перехода на летнее время)
COLS = ("id", "user_id", "username", "name", "grp", "teacher", "lab", "variant", "nums", "created")


def _dt(ts):
    return datetime.fromtimestamp(ts, MSK).replace(tzinfo=None)


def _lab(key):
    key = str(key)
    return f"Лаба {key[3:] if key.startswith('lab') else key}"


def _sheet(wb, title, header, rows, widths, first=False):
    ws = wb.active if first else wb.create_sheet()
    ws.title = title
    ws.append(header)
    for c in ws[1]:
        c.font = Font(bold=True)
    for r in rows:
        ws.append(list(r))
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"
    return ws


def summary(rows, limit):
    users = {r["user_id"] for r in rows}
    return {"total": len(rows), "users": len(users), "limit": limit,
            "today": sum(1 for r in rows if _dt(r["created"]).date() == datetime.now(MSK).date())}


def build_xlsx(rows, limit) -> bytes:
    """rows – словари с полями COLS (как в таблице gens)."""
    rows = sorted(rows, key=lambda r: r["created"])
    s = summary(rows, limit)
    wb = Workbook()

    # ---------------------------------------------------------------- Сводка
    ws = _sheet(wb, "Сводка", ["Показатель", "Значение"], [
        ("Сформировано", datetime.now(MSK).strftime("%d.%m.%Y %H:%M") + " (МСК)"),
        ("Всего выдано лаб", s["total"]),
        ("Из них сегодня", s["today"]),
        ("Пользователей", s["users"]),
        ("Лимит лаб на пользователя", limit),
    ], [32, 22], first=True)
    by_lab = Counter(r["lab"] for r in rows)
    lab_users = defaultdict(set)
    for r in rows:
        lab_users[r["lab"]].add(r["user_id"])
    ws.append([])
    ws.append(["Лаба", "Выдано", "Пользователей"])
    for c in ws[ws.max_row]:
        c.font = Font(bold=True)
    for lab in sorted(by_lab, key=lambda k: str(k)):
        ws.append([_lab(lab), by_lab[lab], len(lab_users[lab])])
    ws.append([])
    ws.append(["Дата", "Выдано"])
    for c in ws[ws.max_row]:
        c.font = Font(bold=True)
    by_day = Counter(_dt(r["created"]).date() for r in rows)
    for day in sorted(by_day, reverse=True):
        ws.append([day, by_day[day]])
        ws.cell(ws.max_row, 1).number_format = "DD.MM.YYYY"

    # ---------------------------------------------------------------- Пользователи
    per_user = defaultdict(list)
    for r in rows:
        per_user[r["user_id"]].append(r)
    urows = []
    for uid, rs in per_user.items():
        last = rs[-1]
        urows.append((uid, "@" + last["username"] if last["username"] else "", last["name"], last["grp"] or "",
                      len(rs), ", ".join(sorted({_lab(x["lab"]) for x in rs})), _dt(rs[0]["created"]),
                      _dt(last["created"])))
    urows.sort(key=lambda u: (-u[4], u[7]))
    ws = _sheet(wb, "Пользователи", ["Telegram id", "Username", "ФИО", "Группа", "Выдано лаб", "Лабы", "Первая",
                                     "Последняя"], urows, [14, 18, 34, 12, 11, 30, 17, 17])
    for row in ws.iter_rows(min_row=2, min_col=7, max_col=8):
        for c in row:
            c.number_format = "DD.MM.YYYY HH:MM"

    # ---------------------------------------------------------------- Выдачи
    grows = [(i, _dt(r["created"]), r["user_id"], "@" + r["username"] if r["username"] else "", r["name"],
              r["grp"] or "", r["teacher"] or "", _lab(r["lab"]), r["variant"], r["nums"])
             for i, r in enumerate(rows, 1)]
    ws = _sheet(wb, "Выдачи", ["№", "Время (МСК)", "Telegram id", "Username", "ФИО", "Группа", "Преподаватель",
                               "Лаба", "Вариант", "Задания"], grows, [6, 17, 14, 18, 34, 12, 22, 9, 9, 12])
    for row in ws.iter_rows(min_row=2, min_col=2, max_col=2):
        for c in row:
            c.number_format = "DD.MM.YYYY HH:MM"

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
