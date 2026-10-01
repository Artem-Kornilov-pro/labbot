"""Диалог бота: лаба → ФИО → группа → преподаватель → вариант → подтверждение → файлы."""
import asyncio
import html
import logging
import re

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from labgen.registry import LABS
from .db import Quota
from .keyboards import confirm_kb, labs_kb, skip_kb, start_kb
from .states import Form

router = Router()
log = logging.getLogger(__name__)

NAME_WORD = re.compile(r"^[А-ЯЁа-яё]+(?:-[А-ЯЁа-яё]+)?$")
GROUP_RE = re.compile(r"^[\wА-ЯЁа-яё\-. ]{1,20}$")
MAX_VARIANT = 999
# одновременно генерируется не больше нескольких отчётов, чтобы не перегружать сервер
GEN_LIMIT = asyncio.Semaphore(4)

HELP = ("Я собираю лабораторную работу по варианту: программы на C и отчёт .docx, оформленный по методичке "
        "(титульный лист, содержание, постановка, метод, спецификация, псевдокод, листинг, тесты).\n\n"
        "Всё генерируется по заранее подготовленным шаблонам – без ИИ.\n\n"
        "Команды:\n/new – создать лабу\n/cancel – отменить ввод\n/help – эта справка")


def norm_name(text):
    words = text.split()
    if not 2 <= len(words) <= 3 or not all(NAME_WORD.match(w) for w in words):
        return None
    return " ".join("-".join(p[:1].upper() + p[1:].lower() for p in w.split("-")) for w in words)


def lab_of(data):
    return LABS[data["lab"]]


def summary(data):
    lab = lab_of(data)
    nums = data["nums"]
    head = [f"<b>{html.escape(lab.TITLE)}</b>",
            f"Студент: {html.escape(data['name'])}",
            f"Группа: {html.escape(data.get('group') or '—')}",
            f"Преподаватель: {html.escape(data.get('teacher') or '—')}",
            f"Вариант: {data['variant']}  →  задания: {', '.join(map(str, nums))}"]
    tasks = [html.escape(t) for t in lab.task_texts(nums)]
    return "\n".join(head) + "\n\n" + "\n\n".join(tasks)


# ------------------------------------------------------------------ команды
async def quota_line(user_id, quota: Quota, admins):
    if user_id in admins:
        return ""
    return f"\n\nДоступно лаб: {await asyncio.to_thread(quota.left, user_id)} из {quota.limit}."


@router.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext, quota: Quota, admins: set):
    await state.clear()
    await msg.answer("Привет! " + HELP + await quota_line(msg.from_user.id, quota, admins), reply_markup=start_kb())


@router.message(Command("help"))
async def cmd_help(msg: Message, quota: Quota, admins: set):
    await msg.answer(HELP + await quota_line(msg.from_user.id, quota, admins), reply_markup=start_kb())


@router.message(Command("cancel"))
async def cmd_cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Отменено. Чтобы начать заново – /new.", reply_markup=start_kb())


LIMIT_MSG = "Лимит исчерпан: вы уже получили {limit} лабы. Больше сгенерировать нельзя."


async def begin(msg: Message, state: FSMContext, user_id, quota: Quota, admins):
    """Начало анкеты – только если лимит лаб не исчерпан (чтобы не заполнять её зря)."""
    await state.clear()
    if user_id not in admins and await asyncio.to_thread(quota.left, user_id) == 0:
        await msg.answer(LIMIT_MSG.format(limit=quota.limit))
        return
    await state.set_state(Form.lab)
    await msg.answer("Выберите лабораторную работу:", reply_markup=labs_kb())


@router.message(Command("new"))
async def cmd_new(msg: Message, state: FSMContext, quota: Quota, admins: set):
    await begin(msg, state, msg.from_user.id, quota, admins)


@router.callback_query(F.data == "new")
async def cb_new(cb: CallbackQuery, state: FSMContext, quota: Quota, admins: set):
    await begin(cb.message, state, cb.from_user.id, quota, admins)
    await cb.answer()


# ------------------------------------------------------------------ шаги анкеты
@router.callback_query(Form.lab, F.data.startswith("lab:"))
async def cb_lab(cb: CallbackQuery, state: FSMContext):
    key = cb.data.split(":", 1)[1]
    if key not in LABS:
        await cb.answer("Такой лабы нет", show_alert=True)
        return
    await state.update_data(lab=key)
    await state.set_state(Form.name)
    await cb.message.answer(f"{LABS[key].TITLE}.\n\nВведите ФИО полностью (например: Иванов Иван Иванович):")
    await cb.answer()


@router.message(Form.name, F.text)
async def step_name(msg: Message, state: FSMContext):
    name = norm_name(msg.text)
    if not name:
        await msg.answer("Не похоже на ФИО. Нужно 2–3 слова русскими буквами, например: Иванов Иван Иванович")
        return
    await state.update_data(name=name)
    await state.set_state(Form.group)
    await msg.answer("Введите группу (например, БИТ261):", reply_markup=skip_kb("group"))


@router.message(Form.group, F.text)
async def step_group(msg: Message, state: FSMContext):
    text = msg.text.strip()
    if not GROUP_RE.match(text):
        await msg.answer("Название группы – до 20 символов (буквы, цифры, дефис). Попробуйте ещё раз:",
                         reply_markup=skip_kb("group"))
        return
    await state.update_data(group=text)
    await ask_teacher(msg, state)


@router.callback_query(Form.group, F.data == "skip:group")
async def skip_group(cb: CallbackQuery, state: FSMContext):
    await state.update_data(group="")
    await ask_teacher(cb.message, state)
    await cb.answer()


async def ask_teacher(msg: Message, state: FSMContext):
    await state.set_state(Form.teacher)
    await msg.answer("Введите преподавателя (например, Альбатша А.):", reply_markup=skip_kb("teacher"))


@router.message(Form.teacher, F.text)
async def step_teacher(msg: Message, state: FSMContext):
    text = " ".join(msg.text.split())
    if not 2 <= len(text) <= 60:
        await msg.answer("Слишком длинно или пусто (до 60 символов). Попробуйте ещё раз:",
                         reply_markup=skip_kb("teacher"))
        return
    await state.update_data(teacher=text)
    await ask_variant(msg, state)


@router.callback_query(Form.teacher, F.data == "skip:teacher")
async def skip_teacher(cb: CallbackQuery, state: FSMContext):
    await state.update_data(teacher="")
    await ask_variant(cb.message, state)
    await cb.answer()


async def ask_variant(msg: Message, state: FSMContext):
    await state.set_state(Form.variant)
    await msg.answer(f"Введите номер варианта (целое число от 1 до {MAX_VARIANT}):")


@router.message(Form.variant, F.text)
async def step_variant(msg: Message, state: FSMContext):
    text = msg.text.strip()
    if not text.isdigit() or not 1 <= int(text) <= MAX_VARIANT:
        await msg.answer(f"Нужно целое число от 1 до {MAX_VARIANT}.")
        return
    data = await state.get_data()
    variant = int(text)
    nums = list(lab_of(data).tasks_for_variant(variant))
    await state.update_data(variant=variant, nums=nums)
    await show_confirm(msg, state)


async def show_confirm(msg: Message, state: FSMContext):
    await state.set_state(Form.confirm)
    data = await state.get_data()
    await msg.answer(summary(data) + "\n\nВсё верно?", reply_markup=confirm_kb(), parse_mode="HTML")


@router.callback_query(Form.confirm, F.data == "manual")
async def cb_manual(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lab = lab_of(data)
    parts = ", ".join(f"часть {name}: 1–{cnt}" for name, cnt in lab.PARTS)
    await state.set_state(Form.manual)
    await cb.message.answer(f"Введите номера заданий через пробел ({parts}). Например: "
                            + " ".join(str(n) for n in data["nums"]))
    await cb.answer()


@router.message(Form.manual, F.text)
async def step_manual(msg: Message, state: FSMContext):
    data = await state.get_data()
    lab = lab_of(data)
    toks = msg.text.split()
    ok = len(toks) == len(lab.PARTS) and all(t.isdigit() for t in toks) and \
        all(1 <= int(t) <= cnt for t, (_, cnt) in zip(toks, lab.PARTS))
    if not ok:
        parts = ", ".join(f"часть {name}: 1–{cnt}" for name, cnt in lab.PARTS)
        await msg.answer(f"Нужно {len(lab.PARTS)} числа через пробел ({parts}).")
        return
    await state.update_data(nums=[int(t) for t in toks])
    await show_confirm(msg, state)


# ------------------------------------------------------------------ генерация
@router.callback_query(Form.confirm, F.data == "gen")
async def cb_generate(cb: CallbackQuery, state: FSMContext, quota: Quota, admins: set):
    await state.set_state(Form.generating)      # повторное нажатие «Сгенерировать» сюда уже не попадёт
    data = await state.get_data()
    lab = lab_of(data)
    user = cb.from_user
    await cb.answer()
    rec = await asyncio.to_thread(quota.reserve, user.id, user.username, data, user.id in admins)
    if rec is None:
        await state.clear()
        await cb.message.answer(LIMIT_MSG.format(limit=quota.limit))
        return
    wait = await cb.message.answer("⏳ Собираю программы и отчёт…")
    try:
        async with GEN_LIMIT:
            files = await asyncio.to_thread(lab.generate, data["name"], data.get("group", ""),
                                            data.get("teacher", ""), data["variant"], tuple(data["nums"]))
    except Exception:
        log.exception("ошибка генерации: %s", data)
        await asyncio.to_thread(quota.release, rec)
        await state.set_state(Form.confirm)
        await wait.edit_text("❌ Не удалось сгенерировать лабу (лимит не потрачен). Попробуйте ещё раз "
                             "или сообщите автору бота.", reply_markup=confirm_kb())
        return
    for name, content in files:
        await cb.message.answer_document(BufferedInputFile(content, filename=name))
    await wait.edit_text(
        "✅ Готово! Программы на C и отчёт выше.\n\n"
        "В Word при открытии отчёта согласитесь обновить поля – номера страниц в содержании станут точными.",
    )
    await state.clear()
    if user.id in admins:
        await cb.message.answer("Создать ещё одну лабу?", reply_markup=start_kb())
        return
    left = await asyncio.to_thread(quota.left, user.id)
    if left:
        await cb.message.answer(f"Можно сгенерировать ещё лаб: {left}.", reply_markup=start_kb())
    else:
        await cb.message.answer(f"Это была последняя лаба из {quota.limit} доступных.")


@router.message(F.text)
async def fallback(msg: Message):
    await msg.answer("Чтобы создать лабу, нажмите кнопку или отправьте /new.", reply_markup=start_kb())
