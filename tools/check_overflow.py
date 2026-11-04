"""Рендерит отчёты через LibreOffice и ищет текст за правым полем страницы.

python tools/check_overflow.py          – лаба 2, варианты 1..17
python tools/check_overflow.py 3 4 5    – указанные лабы, варианты, покрывающие все задания
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from labgen.registry import LABS  # noqa: E402

LIMIT = 595 - 42.5 + 4          # A4, правое поле 15 мм, допуск 4 pt
keys = sys.argv[1:] or ["2"]
tmp = Path(tempfile.mkdtemp())
for key in keys:
    lab = LABS[key]
    last = 17 if key == "2" else max(cnt for _, cnt in lab.PARTS)
    for v in range(1, last + 1):
        data = lab.generate("Константинопольский Константин Константинович", "БИТ261", "Альбатша А.", v)[-1][1]
        (tmp / f"lab{key}_v{v:02d}.docx").write_bytes(data)
subprocess.run(["soffice", f"-env:UserInstallation=file://{tmp}/profile", "--headless", "--convert-to", "pdf",
                "--outdir", str(tmp)] + [str(p) for p in sorted(tmp.glob("*.docx"))], capture_output=True)
bad = 0
for pdf in sorted(tmp.glob("*.pdf")):
    d = pymupdf.open(pdf)
    for pno, page in enumerate(d):
        for b in page.get_text("dict")["blocks"]:
            for ln in b.get("lines", []):
                if ln["bbox"][2] > LIMIT:
                    txt = "".join(s["text"] for s in ln["spans"])
                    print(f"{pdf.stem} стр.{pno}: x={ln['bbox'][2]:.0f}  {txt[:90]}")
                    bad += 1
print("pages:", {p.stem: len(pymupdf.open(p)) for p in sorted(tmp.glob('*.pdf'))})
print("overflow lines:", bad)
