"""Печатает результаты тестов задач (для ручной проверки трактовок). Пример: python tools/show_tests.py 1 3"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from labgen.labs.lab2 import part1, part2  # noqa: E402

part, num = int(sys.argv[1]), int(sys.argv[2])
task = (part1 if part == 1 else part2).get(num)
for i, t in enumerate(task.tests, 1):
    con = task.run(t.lines, "Тест")
    print(f"--- тест {i}: {t.case}")
    print("    " + "\n    ".join(t.shown))
    print("  =>")
    print("    " + "\n    ".join(con.results))
