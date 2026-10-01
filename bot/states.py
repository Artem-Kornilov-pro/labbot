from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    lab = State()
    name = State()
    group = State()
    teacher = State()
    variant = State()
    confirm = State()
    manual = State()
    generating = State()
