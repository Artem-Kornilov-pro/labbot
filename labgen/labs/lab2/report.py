"""Сборка отчёта по лабораторной №2: один отчёт на обе программы с подзаголовками «Программа 1/2»."""
from ...docx_engine import Report, TitleInfo, J, C

GOAL = ("*ЦЕЛЬ РАБОТЫ:* Алгоритмы с досрочным выходом из цикла. Алгоритмы обработки целых чисел.")
# вводная фраза части в практикуме (у части II она уже входит в условие: «Дан массив целых положительных чисел.»)
PREFACE = {1: "Для решения задачи необходимо использовать алгоритмы с досрочным выходом из цикла. ", 2: ""}
REQ = {
    1: ["1. Необходима проверка допустимости исходных данных.",
        "2. Необходимо использование алгоритмов с досрочным выходом из цикла. При этом используются либо "
        "цикл с предусловием, либо цикл с постусловием."],
    2: ["1. Необходима проверка допустимости исходных данных, в том числе недопустим ввод строки вместо числа.",
        "2. При вычислении результата необходимо использовать целый тип. Использование строк при решении "
        "данной задачи недопустимо."],
}


def _prog_title(t):
    return f"Программа {t.part}. Часть {'I' * t.part}, задание {t.num}"


def build_report(author, group, teacher, variant, nums, tasks, year="2026") -> bytes:
    rep = Report(TitleInfo(author=author, group=group, teacher=teacher, lab_no=2, year=year,
                           variant=f"№{variant} ({nums[0]}, {nums[1]})",
                           grade_cols=["Итог.\nпрог. 1", "Итог.\nпрог. 2"]))
    rep.title_page()
    rep.toc_placeholder()

    # ---------------------------------------------------------------- Задание
    rep.heading("Задание")
    rep.para(GOAL, align=J, after=10)
    rep.para(f"Вариант {variant}. Номера заданий определяются по формуле (остаток от деления номера варианта "
             "на количество заданий) + 1:", align=J, after=4)
    rep.para(f"– часть I: ({variant} mod 17) + 1 = {variant % 17 + 1};", indent=1)
    rep.para(f"– часть II: ({variant} mod 10) + 1 = {variant % 10 + 1}.", indent=1, after=10)
    # по методичке: задания – пунктами, текст скопирован из практикума, в конце – что они в разных программах
    for i, t in enumerate(tasks, 1):
        rep.para(f"*{i}. Часть {'I' * t.part}, задание {t.num}.* {PREFACE[t.part]}{t.statement}",
                 align=J, before=8, after=4)
        rep.para("ТРЕБОВАНИЯ К ВЫПОЛНЕНИЮ РАБОТЫ.", indent=0.6, after=2, keep=True)
        for s in REQ[t.part]:
            rep.para(s, align=J, indent=0.6, after=2)
    rep.para(f"Задания {', '.join(map(str, range(1, len(tasks))))} и {len(tasks)} выполняются в разных программах.",
             before=12)

    # ---------------------------------------------------------------- Постановка
    rep.heading("Постановка задачи")
    for t in tasks:
        rep.heading2(_prog_title(t))
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
    for t in tasks:
        rep.heading2(_prog_title(t))
        for i, (caption, items) in enumerate(t.method, 1):
            rep.para(f"*{i}.* {caption}", align=J, after=2, keep=True)
            rep.method(items)

    # ---------------------------------------------------------------- Спецификация
    rep.heading("Внешняя спецификация")
    for t in tasks:
        rep.heading2(_prog_title(t))
        rep.spec([("box", [f"Лабораторная работа № 2, часть {'I' * t.part}, задание {t.num}",
                           f"Выполнил: {author}"], False)] + t.spec)

    # ---------------------------------------------------------------- Псевдокод
    rep.heading("Описание алгоритма на псевдокоде")
    for t in tasks:
        rep.heading2(_prog_title(t))
        rep.pseudocode(t.pseudo)

    # ---------------------------------------------------------------- Листинг
    rep.heading("Листинг программы")
    for t in tasks:
        rep.heading2(f"{_prog_title(t)} (файл lab2_part{t.part}.c)")
        rep.listing(t.c_source(author, variant))

    # ---------------------------------------------------------------- Тесты
    rep.heading("Тесты")
    for t in tasks:
        rep.heading2(_prog_title(t))
        rows, runs = [], []
        for tst in t.tests:
            con = t.run(tst.lines, author)
            rows.append((tst.shown, con.results))
            runs.append(con.transcript)
        rep.tests_table(rows)
        if t.note:
            rep.para(t.note, align=J, size=12, after=6)
        rep.para(f"Распечатка работы программы {t.part} на тестах:", bold=True, before=6, after=2, keep=True)
        for i, tr in enumerate(runs, 1):
            rep.transcript(f"Тест {i}", tr)

    return rep.finalize()
