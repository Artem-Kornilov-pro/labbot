"""Проверки логики бота без подключения к Telegram."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bot.handlers import norm_name, summary  # noqa: E402
from labgen.registry import LABS  # noqa: E402


def test_norm_name():
    assert norm_name("иванов иван иванович") == "Иванов Иван Иванович"
    assert norm_name("  Римский-корсаков  Николай ") == "Римский-Корсаков Николай"
    assert norm_name("Ivanov Ivan") is None
    assert norm_name("Иванов") is None
    assert norm_name("Иванов Иван Иванович Младший") is None


def test_summary_and_all_labs_generate():
    for key, lab in LABS.items():
        data = {"lab": key, "name": "Иванов Иван", "group": "", "teacher": "", "variant": 15,
                "nums": list(lab.tasks_for_variant(15))}
        text = summary(data)
        assert "Вариант: 15" in text and "<b>" in text
        files = lab.generate("Иванов Иван", "", "", 15)
        assert len(files) == 3 and all(len(b) > 1000 for _, b in files)
