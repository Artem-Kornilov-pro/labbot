"""Отчёты генерируются для вариантов, покрывающих все задачи, и проходят проверку структуры."""
import io
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from labgen.labs import lab2  # noqa: E402

VARIANTS = list(range(1, 18))       # (v mod 17) + 1 даёт все 17 задач части I, (v mod 10) + 1 – все 10 части II


@pytest.mark.parametrize("variant", VARIANTS)
def test_report_structure(variant):
    files = lab2.generate("Иванов Иван Иванович", "БИТ261", "Петров П.П.", variant)
    names = [n for n, _ in files]
    assert names[:2] == ["lab2_part1.c", "lab2_part2.c"]
    docx = files[2][1]
    with zipfile.ZipFile(io.BytesIO(docx)) as z:
        xml = z.read("word/document.xml").decode()
        assert not [n for n in z.namelist() if n.startswith("word/media/")], "в отчёте не должно быть картинок"
    assert "TOC \\o" in xml and "PAGEREF" in xml
    assert "<m:oMath" in xml and "<wpg:wgp>" in xml
    n1, n2 = lab2.tasks_for_variant(variant)
    assert f"задание {n1}" in xml and f"задание {n2}" in xml
    assert "Иванов Иван Иванович" in xml and "БИТ261" in xml


def test_variants_cover_all_tasks():
    got = {lab2.tasks_for_variant(v) for v in VARIANTS}
    assert {a for a, _ in got} == set(range(1, 18))
    assert {b for _, b in got} == set(range(1, 11))


@pytest.mark.parametrize("variant", VARIANTS)
def test_formula_lines_fit(variant):
    """Строки формул не длиннее MATH_MAX видимых символов (иначе вылезут за поле – Word их не переносит)."""
    from labgen.docx_engine import MATH_MAX
    from labgen.labs.lab2.report import build_report
    from labgen.labs.lab2 import part1, part2
    import labgen.docx_engine as eng
    seen = []
    orig = eng.Report.finalize

    def spy(self):
        seen.extend(self.math_widths)
        return orig(self)
    eng.Report.finalize = spy
    try:
        n1, n2 = lab2.tasks_for_variant(variant)
        build_report("И И И", "", "", variant, (n1, n2), (part1.get(n1), part2.get(n2)))
    finally:
        eng.Report.finalize = orig
    long = [t for w, t in seen if w > MATH_MAX]
    assert not long, "\n".join(long)
