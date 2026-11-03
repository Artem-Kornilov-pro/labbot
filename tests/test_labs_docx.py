"""Лабы 3–5: отчёты для вариантов, покрывающих все задания, проходят проверку структуры и оформления."""
import io
import re
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import labgen.docx_engine as eng  # noqa: E402
from labgen.registry import LABS  # noqa: E402

NEW = {k: lab for k, lab in LABS.items() if hasattr(lab, "all_tasks")}


def covering_variants(lab):
    """Варианты 1..N, где N – наибольшее число заданий в части: (v mod K) + 1 перебирает все задания."""
    return range(1, max(cnt for _, cnt in lab.PARTS) + 1)


CASES = [(k, v) for k, lab in NEW.items() for v in covering_variants(lab)]


@pytest.mark.parametrize("key", NEW)
def test_variants_cover_all_tasks(key):
    lab = NEW[key]
    got = [lab.tasks_for_variant(v) for v in covering_variants(lab)]
    for i, (_, cnt) in enumerate(lab.PARTS):
        assert {g[i] for g in got} == set(range(1, cnt + 1))


@pytest.mark.parametrize("key,variant", CASES)
def test_report_structure_and_formula_width(key, variant):
    lab = NEW[key]
    seen = []
    orig = eng.Report.finalize

    def spy(self):
        seen.extend(self.math_widths)
        return orig(self)
    eng.Report.finalize = spy
    try:
        files = lab.generate("Иванов Иван Иванович", "БИТ261", "Петров П.П.", variant)
    finally:
        eng.Report.finalize = orig
    names = [n for n, _ in files]
    assert names[-1].startswith(f"Лаба{lab.LAB_NO}_вариант{variant}_") and names[-1].endswith(".docx")
    assert all(n.endswith(".c") for n in names[:-1])
    with zipfile.ZipFile(io.BytesIO(files[-1][1])) as z:
        xml = z.read("word/document.xml").decode()
        assert not [n for n in z.namelist() if n.startswith("word/media/")], "в отчёте не должно быть картинок"
    assert "TOC \\o" in xml and "PAGEREF" in xml
    assert "<m:oMath" in xml and "<wpg:wgp>" in xml
    assert "Иванов Иван Иванович" in xml and "БИТ261" in xml
    long = [t for w, t in seen if w > eng.MATH_MAX]
    assert not long, "\n".join(long)


PSEUDO_WORDS = {"алг", "нач", "кон", "функция", "возврат", "цикл от", "до", "цикл-пока", "кц", "если", "то",
                "иначе", "всё", "и", "или", "не"}


@pytest.mark.parametrize("task", [t for lab in NEW.values() for t in lab.all_tasks()],
                         ids=lambda t: f"lab{t.lab}-{t.part or 'x'}-{str(t.num).replace(', ', '.')}")
def test_text_markup_is_intended(task):
    """В абзацах отчёта «*…*» – жирный, «_…_» – подчёркнутый: в псевдокоде и текстах не должно быть
    случайных пар звёздочек и подчёркиваний (например, *(a + i) или имён вида make_new_array)."""
    texts = [task.lead if task.lead is not None else task.statement, *task.given, *task.result, *task.when,
             task.note, *[c for c, _ in task.method]]
    for s in texts:
        assert not re.search(r"\*[^*]+\*", s or ""), s
        assert not re.search(r"_[^_\s][^_]*_", s or ""), s
    for line in task.pseudo.split("\n"):
        assert not re.search(r"\*[^*]+\*", line), line
        for mt in re.findall(r"_([^_\s][^_]*)_", line):
            assert mt in PSEUDO_WORDS, f"случайное подчёркивание «{mt}» в строке: {line}"
