"""Сборка отчёта по лабам 3–5 (разделы и оформление – как у лабы 2, по методичке)."""
import datetime
from dataclasses import dataclass, field

from ...docx_engine import Report, TitleInfo, J


@dataclass
class LabInfo:
    no: int
    title: str                      # «Лабораторная работа №3»
    goal: str                       # цель работы (с разметкой *…*)
    parts: tuple                    # ((имя части, число заданий), …)
    part_word: str = "часть"        # как называть часть в разделе «Задание»
    intro: dict = field(default_factory=dict)   # часть -> вводная фраза перед условием
    req: dict = field(default_factory=dict)     # часть -> требования к выполнению
    remark: str = ""                # замечание в конце раздела «Задание»


def caption(t, i, many):
    what = f"Часть {t.part}, задание {t.num}" if t.part else f"Задания {t.num}"
    return f"Программа {i}. {what}" if many else f"Программа. {what}"


def surname(author):
    return author.split()[0] if author.split() else "student"


def build_report(info: LabInfo, author, group, teacher, variant, nums, tasks, year=None) -> bytes:
    year = year or str(datetime.date.today().year)
    many = len(tasks) > 1
    caps = [caption(t, i, many) for i, t in enumerate(tasks, 1)]
    grade = [f"Итог.\nпрог. {i}" for i in range(1, len(tasks) + 1)] if many else ["Итог.\nоценка"]
    rep = Report(TitleInfo(author=author, group=group, teacher=teacher, lab_no=info.no, year=year,
                           variant=f"№{variant} ({', '.join(map(str, nums))})", grade_cols=grade))
    rep.title_page()
    rep.toc_placeholder()

    # ---------------------------------------------------------------- Задание
    rep.heading("Задание")
    rep.para(info.goal, align=J, after=10)
    rep.para(f"Вариант {variant}. Номера заданий определяются по формуле (остаток от деления номера варианта "
             "на количество заданий) + 1:", align=J, after=4)
    for k, ((name, cnt), n) in enumerate(zip(info.parts, nums)):
        end = "." if k == len(nums) - 1 else ";"
        rep.para(f"– {info.part_word} {name}: ({variant} mod {cnt}) + 1 = {n}{end}", indent=1,
                 after=10 if end == "." else 0)
    for i, t in enumerate(tasks, 1):
        head = f"*{i}. Часть {t.part}, задание {t.num}.* " if t.part else ""
        text = t.statement if t.lead is None else t.lead
        rep.para(f"{head}{info.intro.get(t.part, '')}{text}", align=J, before=8, after=4)
        if t.formulas:
            t.formulas(rep)
        req = info.req.get(t.part, [])
        if req:
            rep.para("ТРЕБОВАНИЯ К ВЫПОЛНЕНИЮ РАБОТЫ.", indent=0.6, after=2, keep=True)
            for s in req:
                rep.para(s, align=J, indent=0.6, after=2)
    if info.remark:
        rep.para(info.remark, align=J, before=12)

    # ---------------------------------------------------------------- Постановка
    rep.heading("Постановка задачи")
    for t, cap in zip(tasks, caps):
        rep.heading2(cap)
        rep.para("_Дано:_", after=4, keep=True)
        for s in t.given:
            rep.para(s, align=J)
        rep.para("_Результат:_", before=8, after=4, keep=True)
        for s in t.result:
            rep.para(s, align=J)
        rep.para("_При:_", before=8, after=4, keep=True)
        for s in t.when:
            rep.para(s, align=J)
        rep.para("_Связь:_", before=8, after=6, keep=True)
        t.svyaz(rep)

    # ---------------------------------------------------------------- Метод
    rep.heading("Метод решения задачи")
    for t, cap in zip(tasks, caps):
        rep.heading2(cap)
        for i, (cap_m, items) in enumerate(t.method, 1):
            rep.para(f"*{i}.* {cap_m}", align=J, after=2, keep=True)
            if items:
                rep.method(items)

    # ---------------------------------------------------------------- Спецификация
    rep.heading("Внешняя спецификация")
    for t, cap in zip(tasks, caps):
        rep.heading2(cap)
        rep.spec([("box", [t.title, f"Выполнил: {author}"], False)] + t.spec)

    # ---------------------------------------------------------------- Псевдокод
    rep.heading("Описание алгоритма на псевдокоде")
    for t, cap in zip(tasks, caps):
        rep.heading2(cap)
        rep.pseudocode(t.pseudo)

    # ---------------------------------------------------------------- Листинг
    rep.heading("Листинг программы")
    for t, cap in zip(tasks, caps):
        rep.heading2(f"{cap} (файл {t.file})")
        rep.listing(t.c_source(author, variant))

    # ---------------------------------------------------------------- Тесты
    rep.heading("Тесты")
    for i, (t, cap) in enumerate(zip(tasks, caps), 1):
        rep.heading2(cap)
        rows, runs = [], []
        for tst in t.tests:
            con = t.run(tst, author)
            rows.append((tst.shown, con.results))
            runs.append(con.transcript)
        rep.tests_table(rows)
        if t.note:
            rep.para(t.note, align=J, size=12, after=6)
        what = f"программы {i}" if many else "программы"
        rep.para(f"Распечатка работы {what} на тестах:", bold=True, before=6, after=2, keep=True)
        for k, tr in enumerate(runs, 1):
            rep.transcript(f"Тест {k}", tr)

    return rep.finalize()


def make_generate(info: LabInfo, get_tasks):
    """generate(author, group, teacher, variant, nums=None, year=None) -> [(имя файла, bytes)] для пакета лабы."""
    def tasks_for_variant(variant):
        return tuple(variant % cnt + 1 for _, cnt in info.parts)

    def generate(author, group, teacher, variant, nums=None, year=None):
        nums = tuple(nums or tasks_for_variant(variant))
        tasks = get_tasks(nums)
        files = [(t.file, t.c_source(author, variant).encode("utf-8")) for t in tasks]
        docx = build_report(info, author, group, teacher, variant, nums, tasks, year=year)
        files.append((f"Лаба{info.no}_вариант{variant}_{surname(author)}.docx", docx))
        return files

    return tasks_for_variant, generate
