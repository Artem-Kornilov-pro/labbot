"""Лабораторная работа №5: «Программирование с использованием структурированных типов данных (файлы)».

Две программы: часть I (двоичный файл чисел, 12 задач), часть II (текстовый файл, построчная обработка, 9 задач).
"""
from ..core.report import LabInfo, make_generate
from . import part1, part2

LAB_NO = 5
TITLE = "Лабораторная работа №5"
PARTS = (("I", part1.COUNT), ("II", part2.COUNT))

INFO = LabInfo(
    no=LAB_NO, title=TITLE,
    goal="*ЦЕЛЬ РАБОТЫ:* Программирование с использованием структурированных типов данных (файлы).",
    parts=PARTS, intro={"I": part1.INTRO, "II": part2.INTRO},
    remark="ПРИМЕЧАНИЕ. Каждую часть оформить как отдельную программу. Задания 1 и 2 выполняются в разных "
           "программах.",
)
PKGS = (part1, part2)


def get_tasks(nums):
    return [pkg.get(n) for pkg, n in zip(PKGS, nums)]


tasks_for_variant, generate = make_generate(INFO, get_tasks)


def task_texts(nums):
    return [f"Часть {t.part}, задание {t.num}: {INFO.intro[t.part]}{t.statement}" for t in get_tasks(nums)]


def all_tasks():
    return [pkg.get(n) for pkg in PKGS for n in range(1, pkg.COUNT + 1)]
