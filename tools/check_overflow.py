"""Рендерит отчёты всех вариантов 1..17 через LibreOffice и ищет текст за правым полем страницы."""
import subprocess
import sys
import tempfile
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from labgen.labs import lab2  # noqa: E402

LIMIT = 595 - 42.5 + 4          # A4, правое поле 15 мм, допуск 4 pt
tmp = Path(tempfile.mkdtemp())
for v in range(1, 18):
    data = lab2.generate("Константинопольский Константин Константинович", "БИТ261", "Альбатша А.", v)[2][1]
    (tmp / f"v{v:02d}.docx").write_bytes(data)
subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(tmp)] +
               [str(p) for p in sorted(tmp.glob("*.docx"))], capture_output=True)
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
