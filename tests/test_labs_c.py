"""Лабы 3–5: каждая программа компилируется без предупреждений и печатает ровно то же, что эмулятор.

Программа запускается в отдельной папке: входные файлы теста создаются до запуска (лаба 5).
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from labgen.registry import LABS  # noqa: E402

AUTHOR = "Тестов Тест Тестович"
GCC = shutil.which("gcc")
# без слияния умножения и сложения (FMA): иначе последний бит вещественных вычислений C и Python может различаться
CFLAGS = ["-Wall", "-Wextra", "-Werror", "-std=c99", "-O1", "-ffp-contract=off"]

TASKS = [t for lab in LABS.values() if hasattr(lab, "all_tasks") for t in lab.all_tasks()]


def tid(t):
    return f"lab{t.lab}-{t.part or 'x'}-{str(t.num).replace(', ', '.')}"


def compile_task(task, tmp_path):
    src = tmp_path / "prog.c"
    exe = tmp_path / "prog"
    src.write_text(task.c_source(AUTHOR, 15), encoding="utf-8")
    cc = subprocess.run([GCC, *CFLAGS, "-o", str(exe), str(src), "-lm"], capture_output=True, text=True)
    assert cc.returncode == 0, cc.stderr
    return exe


def run_c(exe, tst, cwd):
    for name, data in tst.files.items():
        (cwd / name).write_bytes(data)
    stdin = "\n".join(tst.lines) + "\n"
    return subprocess.run([str(exe)], input=stdin.encode(), capture_output=True, timeout=10, cwd=cwd)


@pytest.mark.skipif(GCC is None, reason="нужен gcc")
@pytest.mark.parametrize("task", TASKS, ids=tid)
def test_c_matches_simulation(task, tmp_path):
    exe = compile_task(task, tmp_path)
    assert task.tests, "у задачи нет тестов"
    for i, tst in enumerate(task.tests):
        cwd = tmp_path / f"run{i}"
        cwd.mkdir()
        real = run_c(exe, tst, cwd)
        sim = task.run(tst, AUTHOR)
        assert real.stdout.decode() == sim.stdout, f"тест «{tst.case}» расходится"
        assert real.returncode == 0, f"тест «{tst.case}»: код возврата {real.returncode}"
        assert not sim.inp, f"тест «{tst.case}»: остались неиспользованные строки ввода"
        assert sim.results, f"тест «{tst.case}»: нет результата"


@pytest.mark.parametrize("task", TASKS, ids=tid)
def test_listing_fits_page(task):
    """Строки листинга помещаются в строку отчёта (Courier 8,5 pt, 165 мм ≈ 91 символ)."""
    long = [ln for ln in task.c_source("Константинопольский Константин Константинович", 999).split("\n")
            if len(ln) > 88]
    assert not long, long
