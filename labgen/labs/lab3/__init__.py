"""Лабораторная работа №3: «Использование функций».

Три программы: часть I (общая часть формулы – функция, 10 задач), часть II (min/max по матрице, 9 задач),
часть III (повторяющиеся элементы массива, обращение через указатель, 7 задач).
"""
from ..core.report import LabInfo, make_generate
from . import part1, part2, part3

LAB_NO = 3
TITLE = "Лабораторная работа №3"
PARTS = (("I", part1.COUNT), ("II", part2.COUNT), ("III", part3.COUNT))

REQ = ["1. Необходима проверка допустимости исходных данных, в том числе недопустим ввод строки вместо числа "
       "и вещественного числа вместо целого.",
       "2. При решении задачи необходимо оформить как отдельные функции ввод данных, вывод результатов, "
       "обработку массива."]

INFO = LabInfo(
    no=LAB_NO, title=TITLE, goal="*ЦЕЛЬ РАБОТЫ:* Использование функций.", parts=PARTS,
    intro={"I": part1.INTRO, "II": part2.INTRO, "III": part3.INTRO},
    req={"I": REQ, "II": REQ, "III": REQ},
    remark="ЗАМЕЧАНИЕ. Каждую часть оформить как отдельную программу. Задания 1, 2 и 3 выполняются "
           "в разных программах.",
)
PKGS = (part1, part2, part3)


def get_tasks(nums):
    return [pkg.get(n) for pkg, n in zip(PKGS, nums)]


tasks_for_variant, generate = make_generate(INFO, get_tasks)


def task_texts(nums):
    return [f"Часть {t.part}, задание {t.num}: {INFO.intro[t.part]}{t.statement}" for t in get_tasks(nums)]


def all_tasks():
    return [pkg.get(n) for pkg in PKGS for n in range(1, pkg.COUNT + 1)]
