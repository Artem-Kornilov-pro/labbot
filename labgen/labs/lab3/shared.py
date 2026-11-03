"""Общие фрагменты лабы 3: функции ввода на C, тесты, заголовки псевдокода."""
from ..core.cio import C_READ_LINE, C_READ_REALS, C_INPUT_INT, C_INPUT_REALS, RMAX
from ..core.task import Test

INTS = C_READ_LINE + "\n" + C_INPUT_INT
REALS = C_READ_REALS + "\n" + C_INPUT_REALS
RMAX_DEFINE = f"#define RMAX {RMAX}       /* максимальный модуль вещественного числа */"


def helpers(ints=True, reals=False):
    """Код функций ввода для программы: целые и/или вещественные числа."""
    out = []
    if ints:
        out.append(INTS)
    if reals:
        out.append(REALS)
    return "\n".join(out)


def T(lines, shown, case):
    return Test(list(lines), list(shown), case)


def alg(part, num):
    return f"_алг_ «Лабораторная работа №3, часть {part}, задание {num}»"


def fmt(x):
    """Как %g в C – для показа вещественных чисел в таблице тестов."""
    return "%g" % x
