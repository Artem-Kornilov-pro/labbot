"""Лабораторная работа №2: «Алгоритмы с досрочным выходом из цикла. Алгоритмы обработки целых чисел».

Две программы: часть I (матрицы, 17 задач) и часть II (цифры чисел, 10 задач).
"""
from . import part1, part2
from .report import build_report

LAB_NO = 2
TITLE = "Лабораторная работа №2"
PARTS = (("I", part1.COUNT), ("II", part2.COUNT))


def tasks_for_variant(variant: int):
    """Номера заданий по методичке: (вариант mod число_заданий) + 1."""
    return variant % part1.COUNT + 1, variant % part2.COUNT + 1


def task_texts(nums):
    t1, t2 = part1.get(nums[0]), part2.get(nums[1])
    return [f"Часть I, задание {nums[0]}: {t1.statement}", f"Часть II, задание {nums[1]}: {t2.statement}"]


def surname(author):
    return author.split()[0] if author.split() else "student"


def generate(author, group, teacher, variant, nums=None, year=None):
    """Возвращает список (имя_файла, bytes): две программы на C и отчёт .docx."""
    import datetime
    year = year or str(datetime.date.today().year)
    nums = tuple(nums or tasks_for_variant(variant))
    t1, t2 = part1.get(nums[0]), part2.get(nums[1])
    files = [
        ("lab2_part1.c", t1.c_source(author, variant).encode("utf-8")),
        ("lab2_part2.c", t2.c_source(author, variant).encode("utf-8")),
    ]
    docx = build_report(author, group, teacher, variant, nums, (t1, t2), year=year)
    files.append((f"Лаба2_вариант{variant}_{surname(author)}.docx", docx))
    return files
