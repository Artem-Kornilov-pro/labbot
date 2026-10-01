"""Приблизительная ширина текста Times New Roman (в пунктах) без внешних шрифтов.

Нужна только для переноса строк в окнах спецификации, поэтому таблица средних ширин достаточна.
"""
# ширины в долях кегля (em) для Times New Roman
_W = {}
for ch in "ilIjt.,:;!|'[]() ":
    _W[ch] = 0.28
for ch in "fr-":
    _W[ch] = 0.33
for ch in "abcdeghknopqsuvxyz0123456789<>=+*?\"/":
    _W[ch] = 0.5
for ch in "ABCDEFGHJKLNOPQRSTUVXYZ":
    _W[ch] = 0.68
for ch in "mwMW":
    _W[ch] = 0.85
_CYR_NARROW = set("гзсэ")
_CYR_WIDE = set("жмшщыюЖМШЩЫЮ")


def char_em(ch):
    if ch in _W:
        return _W[ch]
    if "а" <= ch.lower() <= "я" or ch in "ёЁ":
        if ch in _CYR_WIDE:
            return 0.75
        if ch.isupper():
            return 0.68
        if ch in _CYR_NARROW:
            return 0.42
        return 0.5
    return 0.55


def text_width_pt(s, size):
    return sum(char_em(c) for c in s) * size
