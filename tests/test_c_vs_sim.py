"""Каждая программа на C компилируется без предупреждений и печатает ровно то же, что эмулятор."""
import importlib
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from labgen.labs.lab2 import part1, part2  # noqa: E402

AUTHOR = "Тестов Тест Тестович"
GCC = shutil.which("gcc")


def all_tasks():
    out = []
    for pkg in (part1, part2):
        for num in range(1, pkg.COUNT + 1):
            try:
                out.append(pkg.get(num))
            except ModuleNotFoundError:
                pass
    return out


TASKS = all_tasks()


@pytest.mark.skipif(GCC is None, reason="нужен gcc")
@pytest.mark.parametrize("task", TASKS, ids=lambda t: f"p{t.part}t{t.num:02d}")
def test_c_matches_simulation(task, tmp_path):
    src = tmp_path / "prog.c"
    exe = tmp_path / "prog"
    src.write_text(task.c_source(AUTHOR, 15), encoding="utf-8")
    cc = subprocess.run([GCC, "-Wall", "-Wextra", "-Werror", "-std=c99", "-O1", "-o", str(exe), str(src)],
                        capture_output=True, text=True)
    assert cc.returncode == 0, cc.stderr
    assert task.tests, "у задачи нет тестов"
    for tst in task.tests:
        stdin = "\n".join(tst.lines) + "\n"
        real = subprocess.run([str(exe)], input=stdin.encode(), capture_output=True, timeout=10)
        sim = task.run(tst.lines, AUTHOR)
        assert real.stdout.decode() == sim.stdout, f"тест «{tst.case}» расходится"
        assert real.returncode == 0
        assert not sim.inp, f"тест «{tst.case}»: остались неиспользованные строки ввода"
        assert sim.results, f"тест «{tst.case}»: нет результата"


@pytest.mark.parametrize("task", TASKS, ids=lambda t: f"p{t.part}t{t.num:02d}")
def test_listing_fits_page(task):
    """Строки листинга помещаются в строку отчёта (Courier 8,5 pt, 165 мм ≈ 91 символ)."""
    long = [ln for ln in task.c_source("Константинопольский Константин Константинович", 999).split("\n")
            if len(ln) > 88]
    assert not long, long
