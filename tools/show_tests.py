"""Печатает результаты тестов задачи (для ручной проверки трактовок).

Лаба 2: python tools/show_tests.py 1 3            (часть, номер задания)
Лабы 3–5: python tools/show_tests.py 3 2 4        (лаба, номер части по порядку, номер задания)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from labgen.labs.lab2 import part1, part2  # noqa: E402
from labgen.registry import LABS  # noqa: E402

args = [int(a) for a in sys.argv[1:]]
lab2 = len(args) == 2
if lab2:
    part, num = args
    task = (part1 if part == 1 else part2).get(num)
else:
    lab, part, num = args
    nums = [1] * len(LABS[str(lab)].PARTS)
    nums[part - 1] = num
    tasks = LABS[str(lab)].get_tasks(nums)
    task = tasks[min(part - 1, len(tasks) - 1)]          # у лабы 4 одна программа на все пункты
for i, t in enumerate(task.tests, 1):
    con = task.run(t.lines if lab2 else t, "Тест")
    print(f"--- тест {i}: {t.case}")
    print("    " + "\n    ".join(t.shown))
    print("  =>")
    print("    " + "\n    ".join(con.results))
