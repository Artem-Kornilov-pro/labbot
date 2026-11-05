"""Лабораторная работа №4: «Обработка символьных строк».

Одна программа из трёх подпрограмм: выделение подстрок (п. 1, 12 вариантов), поиск подстроки (п. 2, 10 вариантов),
преобразование строки, которой принадлежит найденная подстрока (п. 3, 11 вариантов). Ввод данных, анализ
существования результатов и вывод – в главной программе. Строки – UTF-8 (русская буква – 2 байта).
"""
from ..core.task import Task, Test
from ..core.report import LabInfo, make_generate
from ..core.cio import C_READ_LINE, C_INPUT_INT, C_READ_STR, py_input_int, py_read_str, spec_input_int
from ..core.cstr import C_CHARS, C_EDIT, C_CODE, c_printf
from .pieces import EXTRACT, FIND, TRANSFORM, H

LAB_NO = 4
TITLE = "Лабораторная работа №4"
PARTS = (("1", len(EXTRACT)), ("2", len(FIND)), ("3", len(TRANSFORM)))
KMAX, LMAX = 10, 80

INTRO = ("Дано k литерных строк. Каждая строка содержит латинские и русские буквы, цифры, а также все возможные "
         "разделители. Требуется:")
NOTE1 = ("ПРИМЕЧАНИЕ. Пробел считать буквой. Каждую подстроку печатать с новой строки. Пустые подстроки не "
         "выделять и не печатать.")
REMARK = ("ЗАМЕЧАНИЕ. Все части оформить как подпрограммы в одной программе. Ввод данных, анализ существования "
          "результатов и их вывод оформить в главной программе. Если выполнение какого-либо задания невозможно, "
          "то необходимо вывести соответствующее сообщение.")

INFO = LabInfo(no=LAB_NO, title=TITLE, goal="*ЦЕЛЬ РАБОТЫ:* Обработка символьных строк.", parts=PARTS,
               part_word="пункт", remark=REMARK)

DEFINES = ("#define KMAX 10                      /* наибольшее число строк */\n"
           "#define LMAX 80                      /* наибольшая длина строки, символов */\n"
           "#define SMAX (4 * LMAX + 1)          /* байт на строку: символ UTF-8 - до 4 байт */\n"
           "#define PMAX (KMAX * (LMAX / 2 + 1)) /* наибольшее число подстрок всех строк */")

# консоль Windows по умолчанию в кодировке 866: без переключения на UTF-8 русские буквы с клавиатуры
# не распознаются (программа работает с UTF-8), а русский текст выводится нечитаемым
WIN_PRELUDE = "#ifdef _WIN32\n#include <windows.h>               /* SetConsoleCP: консоль Windows в UTF-8 */\n#endif"
WIN_SETUP = """#ifdef _WIN32
    SetConsoleCP(CP_UTF8);               /* ввод и вывод консоли Windows - в UTF-8 */
    SetConsoleOutputCP(CP_UTF8);
#endif
"""

C_INPUT_STR = r'''/* Ввод строки номер num с повтором, если она длиннее LMAX символов.
   Возвращает 0 при конце ввода. */
int input_str(int num, char s[]){
    int r;
    do{
        printf("Введите строку %d: ", num);
        r = read_str(stdin, s, LMAX);
        if (r == -1) return 0;
        if (r == -2)
            printf("Ошибка! Строка длиннее %d символов, повторите ввод.\n", LMAX);
    } while (r < 0);
    return 1;
}
'''

# ------------------------------------------------------------------ тестовые строки для каждого правила п. 1
# rich – подстроки с цифрами, скобками, пробелами в конце (подходят почти все условия п. 2);
# poor – подстроки без цифр; none – подстрок нет
SAMPLES = {
    1: (["Счёт {12(3)45 apple}, {  x7 } и {Дом 2024}{}", "Без 777 here; {abc}"],
        ["Слова {abc} и {Дом}", "{ее}"], ["Нет скобок: 12 (3) 45", "{} и {"]),
    2: (["Код <12(3)45 apple> и <  x7 >, <Дом 2024><>", "Без 777 here; <abc>"],
        ["Слова <abc> и <Дом>", "<ее>"], ["Нет: 12 > 5 < 3", "<> и <"]),
    3: (["x*12(3)45 apple*  x7 **Дом 2024*end", "1*abc*"], ["a*abc*Дом*b", "**ее*"],
        ["нет звёздочек 12 (3)", "*только одна"]),
    4: (["x+12(3)45 apple-  x7 /Дом 2024*end", "1-abc+"], ["a+abc-Дом/b", "*ее/"],
        ["нет знаков 12 (3)", "+только один"]),
    5: (["x.12(3)45 apple.  x7 ..Дом 2024.end", "1.abc."], ["a.abc.Дом.b", "..ее."],
        ["нет точек, 12 (3)", "... и"]),
    6: (["x12(3)45y;Дом;z 77,1w", "q(ё)r 2!"], ["a;Дом;b", "c-ё-d"], ["12 34", "Дом, 1"]),
    7: (["а12(3)45б;Dog;в 77,1г", "д(x)е 2!"], ["а;Dog;б", "в-x-г"], ["12 34", "Dog, 1"]),
    8: (["12(3)45 apple.  x7 .Дом 2024", "abc..1"], ["abc.Дом", "ее"], ["...", ""]),
    9: (["12(3)45 apple,  x7 ;Дом 2024", "abc:1."], ["abc;Дом", "ее"], [".,;:", ""]),
    10: (["12(3)45 apple[  x7 ]Дом 2024", "abc[1]"], ["abc[Дом]", "ее"], ["[][]", ""]),
    11: (["12 apple(  x7 ;Дом 2024", "abc!1"], ["abc;xyz", "Дом-ее"], ["Дом;(;)", "ёж-ёж"]),
    12: (["12 яблоко(  ж7 ;Dom 2024", "абв!1"], ["абв;где", "Dog-ее"], ["abc;(;)", "xy-zz"]),
}

# ведущие пробелы – чтобы было видно преобразование «удалить пробелы в начале строки»
# (в правилах 1–7 пробелы в начале строки не входят в подстроки)
SAMPLES = {k: ((["  " + r[0], *r[1:]] if k <= 7 else r), ["  " + p[0], *p[1:]], n)
           for k, (r, p, n) in SAMPLES.items()}


def _q(s):
    return f"«{s}»"


class Program:
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c
        self.ex, self.fi, self.tr = EXTRACT[a], FIND[b], TRANSFORM[c]

    # ------------------------------------------------------------------ C
    def functions(self):
        deps = set(self.fi.deps) | set(self.tr.deps)
        parts = [C_READ_LINE, C_INPUT_INT, C_READ_STR, C_INPUT_STR, C_CHARS]
        if "code" in deps:
            parts.append(C_CODE)
        if "edit" in deps:
            parts.append(C_EDIT)
        parts += [H[d] for d in ("nchars", "ndig", "has", "nlet", "ldig", "tdig", "tsp") if d in deps]
        parts += [self.ex.c, self.fi.c, self.tr.c]
        return "\n".join(parts)

    def body(self):
        l1, l2 = self.ex.label, self.fi.label
        return f'''    if (!input_int("число строк k", 1, KMAX, &k)) return 1;
    for (i = 0; i < k; i++)
        if (!input_str(i + 1, s[i])) return 1;

    /* 1. выделение подстрок из каждой строки */
{c_printf(f"{chr(10)}Подстроки ({l1}):{chr(10)}")}
    total = 0;
    for (i = 0; i < k; i++){{
        cnt = extract(s[i], p + total, len + total);
        if (cnt == 0) printf("Строка %d: подстрок нет\\n", i + 1);
        else printf("Строка %d:\\n", i + 1);
        for (t = total; t < total + cnt; t++){{
            ln[t] = i;
            printf("  \\"%.*s\\"\\n", len[t], p[t]);
        }}
        total = total + cnt;
    }}

    /* 2. поиск подстроки и 3. преобразование строки, которой она принадлежит */
    if (total == 0)
        printf("\\nПодстрок нет - поиск и преобразование невозможны.\\n");
    else{{
        f = find(p, len, total);
        if (f < 0)
{c_printf(f"{chr(10)}Поиск ({l2}): подстрока не найдена - преобразование невозможно.{chr(10)}", ind="            ")}
        else{{
            i = ln[f];
{c_printf(f'{chr(10)}Поиск ({l2}): "%.*s" (строка %d){chr(10)}', "len[f], p[f], i + 1", ind="            ")}
            printf("Исходная строка %d: \\"%s\\"\\n", i + 1, s[i]);
{self.c_transform()}
        }}
    }}
'''

    def c_transform(self):
        if not self.tr.fail:          # преобразование выполнимо всегда
            return ('            transform(s[i]);\n'
                    '            printf("Преобразованная строка: \\"%s\\"\\n", s[i]);')
        return ('            if (transform(s[i]))\n'
                '                printf("Преобразованная строка: \\"%s\\"\\n", s[i]);\n'
                '            else\n'
                + c_printf(f"Преобразование невозможно: {self.tr.fail}.\n", ind="                "))

    # ------------------------------------------------------------------ Python
    def simulate(self, con):
        k = py_input_int(con, "число строк k", 1, KMAX)
        s = []
        for i in range(1, k + 1):
            while True:
                con.printf("Введите строку %d: " % i)
                r, text = py_read_str(con, LMAX)
                if r >= 0:
                    s.append(text)
                    break
                con.printf("Ошибка! Строка длиннее %d символов, повторите ввод.\n" % LMAX)
        con.begin_results()
        con.printf(f"\nПодстроки ({self.ex.label}):\n")
        subs, ln = [], []
        for i, line in enumerate(s):
            got = self.ex.py(line)
            con.printf("Строка %d: подстрок нет\n" % (i + 1) if not got else "Строка %d:\n" % (i + 1))
            for q in got:
                con.printf(f'  "{q}"\n')
            subs += got
            ln += [i] * len(got)
        if not subs:
            con.printf("\nПодстрок нет - поиск и преобразование невозможны.\n")
            return
        f = self.fi.py(subs)
        if f < 0:
            con.printf(f"\nПоиск ({self.fi.label}): подстрока не найдена - преобразование невозможно.\n")
            return
        i = ln[f]
        con.printf(f'\nПоиск ({self.fi.label}): "{subs[f]}" (строка {i + 1})\n')
        con.printf(f'Исходная строка {i + 1}: "{s[i]}"\n')
        ok, new = self.tr.py(s[i])
        if ok:
            con.printf(f'Преобразованная строка: "{new}"\n')
        else:
            con.printf(f"Преобразование невозможно: {self.tr.fail or '-'}.\n")

    # ------------------------------------------------------------------ документы
    def items(self):
        return [f"1. Выделить из каждой строки и напечатать подстроки: {self.ex.text}.",
                "2. Среди выделенных подстрок найти подстроку (если таких подстрок несколько, выбирается первая "
                f"из них): {self.fi.text}.",
                "3. Преобразовать исходную строку, которой принадлежит найденная подстрока, следующим образом: "
                f"{self.tr.text}."]

    def formulas(self, rep):
        it = self.items()
        rep.para(it[0], align=None, indent=0.6, after=2)
        rep.para(NOTE1, indent=0.6, after=2)
        rep.para(it[1], indent=0.6, after=2)
        rep.para(it[2], indent=0.6, after=4)

    def svyaz(self, rep):
        rep.para(f"P[0:total−1] – все подстроки строк s[1:k], {self.ex.text} (по порядку строк и позиций); "
                 "ln[t] – номер строки, которой принадлежит подстрока P[t];", after=2)
        rep.para(f"f – номер первой из подстрок P, удовлетворяющих условию п. 2 ({self.fi.label}); "
                 "f не существует, если таких подстрок нет;", after=2)
        rep.para(f"s′[ln[f]] – строка s[ln[f]], преобразованная так: {self.tr.text}.", after=4)

    def method(self):
        main = ("Главная программа: ввод k и строк; для каждой строки – выделение подстрок (их начала p, длины "
                "len и номера строк ln собираются в общие массивы) и вывод; анализ существования результатов: "
                "при total = 0 поиск невозможен, при f = −1 невозможно преобразование:",
                ["total = 0", ["для i = {1..k}", "cnt = extract(s[i], p + total, len + total)",
                               "ln[t] = i,  t = {total..total + cnt − 1};   total = total + cnt"],
                 "f = find(p, len, total),  если  total > 0",
                 "transform(s[ln[f]]),  если  f ≥ 0"])
        return [self.ex.method, self.fi.method, self.tr.method, main]

    def spec(self):
        l1, l2 = self.ex.label, self.fi.label
        out = spec_input_int("число строк k", 1, "KMAX", "k") + [
            ("loop_start", "i", "1", "k"),
            ("rep_start",),
            ("box", ["Введите строку <<i>>: <s[i]>"], False),
            ("label", "При длине строки больше LMAX символов"),
            ("box", ["Ошибка! Строка длиннее <<LMAX>> символов, повторите ввод."], True),
            ("rep_end", "До L(s[i]) ≤ LMAX"),
            ("loop_end",),
            ("box", [f"Подстроки ({l1}):"], False),
            ("loop_start", "i", "1", "k"),
            ("label", "Если в строке нет подстрок"),
            ("box", ["Строка <<i>>: подстрок нет"], True),
            ("label", "Иначе"),
            ("box", ["Строка <<i>>:", '  "<<подстрока 1>>"', "  …", '  "<<подстрока cnt>>"'], True),
            ("loop_end",),
            ("label", "При total = 0"),
            ("box", ["Подстрок нет - поиск и преобразование невозможны."], True),
            ("label", "При f = −1"),
            ("box", [f"Поиск ({l2}): подстрока не найдена - преобразование невозможно."], True),
            ("label", "Иначе"),
            ("box", [f'Поиск ({l2}): "<<P[f]>>" (строка <<j>>)', 'Исходная строка <<j>>: "<<s[j]>>"'], True),
        ]
        if self.tr.fail:
            out += [("label", "Если преобразование невозможно"),
                    ("box", [f"Преобразование невозможно: {self.tr.fail}."], True), ("label", "Иначе")]
        out.append(("box", ['Преобразованная строка: "<<s′[j]>>"'], bool(self.tr.fail)))
        return out

    def pseudo(self):
        return (self.ex.pseudo + self.fi.pseudo + self.tr.pseudo + f"""
_алг_ «Лабораторная работа №4, задания {self.a}, {self.b}, {self.c}»
_нач_
	ввод(k, s[1:k])
	total := 0
	_цикл от_ i := 1 _до_ k
		cnt := extract(s[i], p + total, len + total)
		вывод(«Строка », i, «: », подстроки p[total : total + cnt − 1])
		_цикл от_ t := total _до_ total + cnt − 1
			ln[t] := i
		_кц_
		total := total + cnt
	_кц_
	_если_ total = 0 _то_
		вывод(«Подстрок нет - поиск и преобразование невозможны.»)
	_иначе_
		f := find(p, len, total)
		_если_ f = −1 _то_
			вывод(«Поиск: подстрока не найдена - преобразование невозможно.»)
		_иначе_
			j := ln[f]
			вывод(«Поиск: », p[f], «(строка », j, «)»)
			вывод(«Исходная строка », j, «: », s[j])
{self.pseudo_transform()}
		_всё_
	_всё_
_кон_
""")

    def pseudo_transform(self):
        if not self.tr.fail:
            return "\t\t\ttransform(s[j])\n\t\t\tвывод(«Преобразованная строка: », s[j])"
        return ("\t\t\t_если_ transform(s[j]) = 1 _то_\n\t\t\t\tвывод(«Преобразованная строка: », s[j])\n"
                f"\t\t\t_иначе_\n\t\t\t\tвывод(«Преобразование невозможно: {self.tr.fail}.»)\n\t\t\t_всё_")

    def tests(self):
        rich, poor, none = SAMPLES[self.a]

        def t(lines, case):
            return Test([str(len(lines)), *lines], [f"k = {len(lines)}", *[_q(x) for x in lines]], case)
        long_line = "Д" * (LMAX + 1)
        bad = Test(["0", "11", "два", "2.0", "2", long_line, *rich],
                   ["k: 0 / 11 / два / 2.0 / 2", f"строка 1: {LMAX + 1} символ «Д» / {_q(rich[0])}", _q(rich[1])],
                   "Недопустимые данные: k вне диапазона, строка, вещественное; строка длиннее LMAX")
        return [t(rich, "Подстроки с цифрами, скобками и пробелами"),
                t(poor, "Подстроки без цифр"),
                t(none, "Подстрок нет – поиск и преобразование невозможны"),
                bad]

    def task(self):
        it = self.items()
        return Task(
            lab=LAB_NO, part="", num=f"{self.a}, {self.b}, {self.c}",
            statement=" ".join([INTRO, it[0], NOTE1, it[1], it[2]]), lead=INTRO, formulas=self.formulas,
            includes=["string.h"] if "edit" in self.tr.deps else [], defines=DEFINES,
            functions=self.functions(),
            decls="    char s[KMAX][SMAX], *p[PMAX];\n    int len[PMAX], ln[PMAX], k, i, t, cnt, total, f;\n",
            body=self.body(), simulate=self.simulate,
            given=["k – число строк; s[1:k] – строки, содержащие латинские и русские буквы, цифры и разделители."],
            result=[f"1) подстроки каждой строки, {self.ex.text} (каждая – с новой строки, в кавычках), или "
                    "сообщение, что подстрок нет;",
                    f"2) {self.fi.label} (первая из таких) и номер её строки, или сообщение, что такой "
                    "подстроки нет;",
                    f"3) строка, которой принадлежит найденная подстрока, после преобразования ({self.tr.text})"
                    + (", или сообщение, что преобразование невозможно." if self.tr.fail else ".")],
            when=[f"k ∈ N, k ≤ KMAX = {KMAX}; длина каждой строки – не более LMAX = {LMAX} символов;",
                  "пробел считается буквой при выделении подстрок и подсчёте букв (примечание к п. 1);",
                  "русские буквы – А–Я, а–я, Ё, ё; латинские – A–Z, a–z."],
            svyaz=self.svyaz, method=self.method(), spec=self.spec(), pseudo=self.pseudo(), tests=self.tests(),
            note="Строки хранятся в кодировке UTF-8 (русская буква занимает 2 байта), поэтому длины подстрок "
                 "в программе – в байтах, а символы перебираются с шагом clen(s + i). В Windows программа "
                 "переключает консоль в UTF-8 (SetConsoleCP), чтобы русские буквы вводились и выводились верно.",
            file="lab4.c", prelude=WIN_PRELUDE, setup=WIN_SETUP,
        )


_cache = {}


def get_tasks(nums):
    a, b, c = nums
    if (a, b, c) not in _cache:
        if a not in EXTRACT or b not in FIND or c not in TRANSFORM:
            raise ModuleNotFoundError(nums)
        _cache[(a, b, c)] = Program(a, b, c).task()
    return [_cache[(a, b, c)]]


tasks_for_variant, generate = make_generate(INFO, get_tasks)


def task_texts(nums):
    p = Program(*nums)
    return [f"Пункт {k}, задание {n}: {t}" for k, n, t in zip((1, 2, 3), nums, [x[3:] for x in p.items()])]


def all_tasks():
    """Программы, в которых встречается каждая подпрограмма каждого пункта (варианты 1..12)."""
    return [get_tasks(tasks_for_variant(v))[0] for v in range(1, 13)]
