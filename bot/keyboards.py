from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from labgen.registry import LABS


def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📝 Создать лабу", callback_data="new")]])


def labs_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=lab.TITLE, callback_data=f"lab:{key}")] for key, lab in LABS.items()
    ])


def skip_kb(what):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Пропустить", callback_data=f"skip:{what}")]])


def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Сгенерировать", callback_data="gen")],
        [InlineKeyboardButton(text="✏️ Изменить номера заданий", callback_data="manual")],
        [InlineKeyboardButton(text="↩️ Начать заново", callback_data="new")],
    ])
