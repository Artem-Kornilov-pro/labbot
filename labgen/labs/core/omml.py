"""Дополнительные конструкции формул Word (OMML) поверх docx_engine: индексы, корень, модуль, min/max с пределом."""
from ...docx_engine import m, frac, sup, nsum, bar, brace as brace_rows  # noqa: F401


def sub(base, s):
    """base с нижним индексом s (строки текста)."""
    return f'<m:sSub><m:e>{m(base)}</m:e><m:sub>{m(s)}</m:sub></m:sSub>'


def subx(base_xml, sub_xml):
    return f'<m:sSub><m:e>{base_xml}</m:e><m:sub>{sub_xml}</m:sub></m:sSub>'


def supx(base_xml, sup_xml):
    return f'<m:sSup><m:e>{base_xml}</m:e><m:sup>{sup_xml}</m:sup></m:sSup>'


def rad(inner):
    return f'<m:rad><m:radPr><m:degHide m:val="1"/></m:radPr><m:deg/><m:e>{inner}</m:e></m:rad>'


def delim(inner, beg="(", end=")"):
    return (f'<m:d><m:dPr><m:begChr m:val="{beg}"/><m:endChr m:val="{end}"/></m:dPr>'
            f'<m:e>{inner}</m:e></m:d>')


def absd(inner):
    return delim(inner, "|", "|")


def par(inner):
    return delim(inner)


def limlow(op, lim_xml, body_xml):
    """min/max с пределом под знаком: «min» и область изменения индекса снизу."""
    return (f'<m:func><m:fName><m:limLow><m:e>{m(op)}</m:e><m:lim>{lim_xml}</m:lim></m:limLow></m:fName>'
            f'<m:e>{body_xml}</m:e></m:func>')


def rng_bar(var, a, b):
    """«i = 1,n̄» – область изменения индекса с чертой (как в методичке)."""
    return m(f"{var}=") + bar(m(f"{a},{b}"))
