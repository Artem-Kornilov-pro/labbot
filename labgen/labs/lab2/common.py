"""Общая часть лабораторной №2: C-каркас, ввод данных (C + эмулятор на Python), окна спецификации.

Программа на C и эмулятор обязаны печатать байт в байт одно и то же — это проверяет tests/test_c_vs_sim.py.
Массивы и матрицы нумеруются с 1 (как в псевдокоде и отчёте).
"""
from dataclasses import dataclass, field

NMAX = 9                  # максимальное число строк / столбцов матрицы
KMAX = 20                 # максимальная длина массива
EMAX = 99                 # максимальный модуль элемента матрицы
AMAX = 999999999          # максимальный модуль элемента массива (часть I) / элемента (часть II)

# ====================================================================== C
C_READ_LINE = r'''/* Читает одну строку ввода и разбирает в ней ровно cnt целых чисел из [lo; hi].
   Строка читается посимвольно, число собирается из цифр (без строк и scanf).
   Возвращает 1 - строка корректна, 0 - ошибка (строка уже дочитана до конца),
   -1 - конец ввода. */
int read_line(int a[], int cnt, int lo, int hi){
    int ch, cntr = 0, ok = 1, sign, digits;
    long long v;
    ch = getchar();
    if (ch == EOF) return -1;
    while (ch != '\n' && ch != EOF && ok){   /* досрочный выход при первой ошибке */
        if (ch == ' ' || ch == '\t' || ch == '\r')
            ch = getchar();
        else{
            sign = 1;
            if (ch == '-' || ch == '+'){
                if (ch == '-') sign = -1;
                ch = getchar();
            }
            v = 0;
            digits = 0;
            while (ch >= '0' && ch <= '9'){
                if (v < 10000000000LL) v = v * 10 + (ch - '0');
                digits++;
                ch = getchar();
            }
            v = v * sign;
            if (digits == 0
                || (ch != ' ' && ch != '\t' && ch != '\r' && ch != '\n' && ch != EOF)
                || cntr >= cnt || v < lo || v > hi)
                ok = 0;
            else{
                a[cntr] = (int)v;
                cntr++;
            }
        }
    }
    while (ch != '\n' && ch != EOF) ch = getchar();   /* дочитываем строку */
    return ok && cntr == cnt;
}
'''


def c_read_int(var, prompt, lo, hi, err):
    """Ввод одного числа с повтором. prompt/err — C-строки с %d для lo/hi, переданные как есть."""
    return f'''    do{{
        printf("{prompt}", {lo}, {hi});
        ok = read_line(&{var}, 1, {lo}, {hi});
        if (ok == -1) return 1;
        if (!ok) printf("{err}\\n", {lo}, {hi});
    }} while (!ok);
'''


def c_read_matrix(name, n, m):
    return f'''    printf("Введите матрицу {name} построчно: в каждой строке %d целых чисел "
           "от %d до %d через пробел.\\n", {m}, -EMAX, EMAX);
    for (i = 1; i <= {n}; i++)
        do{{
            printf("строка %d: ", i);
            ok = read_line(&{name}[i][1], {m}, -EMAX, EMAX);
            if (ok == -1) return 1;
            if (!ok) printf("Ошибка! Повторите ввод строки %d.\\n", i);
        }} while (!ok);
'''


def c_read_array(name, k, lo, hi, what):
    return f'''    do{{
        printf("Введите {what} {name}: %d целых чисел от %d до %d через пробел: ",
               {k}, {lo}, {hi});
        ok = read_line(&{name}[1], {k}, {lo}, {hi});
        if (ok == -1) return 1;
        if (!ok)
            printf("Ошибка! Нужно ввести %d целых чисел от %d до %d.\\n",
                   {k}, {lo}, {hi});
    }} while (!ok);
'''


def c_print_matrix(name, n, m, title):
    return f'''    printf("{title}\\n");
    for (i = 1; i <= {n}; i++){{
        for (j = 1; j <= {m}; j++)
            printf("%5d", {name}[i][j]);
        printf("\\n");
    }}
'''


def c_print_array(name, k, title, fmt="%d "):
    return f'''    printf("{title}");
    for (i = 1; i <= {k}; i++)
        printf("{fmt}", {name}[i]);
    printf("\\n");
'''


def c_program(header_comment, defines, decls, body, author, lab_title):
    return f'''/* {header_comment} */
#include <stdio.h>
{defines}
{C_READ_LINE}
int main(){{
{decls}
    printf("{lab_title}\\n"
           "Выполнил: {author}\\n\\n");

{body}
    return 0;
}}
'''


# ====================================================================== эмулятор
class EndOfInput(Exception):
    pass


class Console:
    """Эмуляция консоли: stdout программы и распечатка с эхом введённых строк."""

    def __init__(self, lines):
        self.inp = list(lines)
        self.out = []
        self.tr = []
        self.res_from = None

    def printf(self, s):
        self.out.append(s)
        self.tr.append(s)

    def readline(self):
        if not self.inp:
            raise EndOfInput
        line = self.inp.pop(0)
        self.tr.append(line + "\n")
        return line

    def begin_results(self):
        self.res_from = len(self.out)

    @property
    def stdout(self):
        return "".join(self.out)

    @property
    def transcript(self):
        return "".join(self.tr)

    @property
    def results(self):
        text = "".join(self.out[self.res_from:]) if self.res_from is not None else ""
        return [ln.rstrip() for ln in text.split("\n") if ln.strip()]


def parse_line(s, cnt, lo, hi):
    """Точная копия read_line() из C. Возвращает (ok, values)."""
    i, n, ok, vals = 0, len(s), True, []
    sep = " \t\r"
    while i < n and ok:
        ch = s[i]
        if ch in sep:
            i += 1
            continue
        sign = 1
        if ch in "+-":
            sign = -1 if ch == "-" else 1
            i += 1
        v, digits = 0, 0
        while i < n and "0" <= s[i] <= "9":
            if v < 10000000000:
                v = v * 10 + ord(s[i]) - 48
            digits += 1
            i += 1
        v *= sign
        nxt = s[i] if i < n else "\n"
        if digits == 0 or nxt not in sep + "\n" or len(vals) >= cnt or v < lo or v > hi:
            ok = False
        else:
            vals.append(v)
    return ok and len(vals) == cnt, vals


def cfmt(fmt, *args):
    """printf для используемых форматов (%d, %5d)."""
    return fmt % args


def py_read_int(con, prompt, lo, hi, err):
    while True:
        con.printf(prompt % (lo, hi))
        ok, v = parse_line(con.readline(), 1, lo, hi)
        if ok:
            return v[0]
        con.printf(err % (lo, hi) + "\n")


def py_read_matrix(con, name, n, m):
    con.printf(f"Введите матрицу {name} построчно: в каждой строке %d целых чисел от %d до %d через пробел.\n"
               % (m, -EMAX, EMAX))
    mat = [[0] * (m + 1)]
    for i in range(1, n + 1):
        while True:
            con.printf("строка %d: " % i)
            ok, v = parse_line(con.readline(), m, -EMAX, EMAX)
            if ok:
                mat.append([0] + v)
                break
            con.printf("Ошибка! Повторите ввод строки %d.\n" % i)
    return mat


def py_read_array(con, name, k, lo, hi, what):
    while True:
        con.printf(f"Введите {what} {name}: %d целых чисел от %d до %d через пробел: " % (k, lo, hi))
        ok, v = parse_line(con.readline(), k, lo, hi)
        if ok:
            return [0] + v
        con.printf("Ошибка! Нужно ввести %d целых чисел от %d до %d.\n" % (k, lo, hi))


def py_print_matrix(con, mat, n, m, title):
    con.printf(title + "\n")
    for i in range(1, n + 1):
        con.printf("".join("%5d" % mat[i][j] for j in range(1, m + 1)) + "\n")


def py_print_array(con, arr, k, title, fmt="%d "):
    con.printf(title + "".join(fmt % arr[i] for i in range(1, k + 1)) + "\n")


# ====================================================================== описание задачи
@dataclass
class Test:
    lines: list            # строки ввода
    shown: list            # как показать исходные данные в таблице тестов
    case: str              # проверяемый случай


@dataclass
class Task:
    """Описание одной задачи лабы 2 (часть I или II)."""
    part: int
    num: int
    statement: str                 # текст условия (как в практикуме)
    short: str                     # краткое название для подзаголовков
    defines: str                   # #define для C
    decls: str                     # объявления переменных C
    c_input: str                   # ввод (C)
    c_solve: str                   # обработка и вывод (C)
    simulate: object               # fn(con) — ввод + обработка (Python)
    given: list                    # Дано
    result: list                   # Результат
    when: list                     # При
    svyaz: object                  # fn(rep) — пункт «Связь»
    method: list                   # пункты метода: (заголовок, items)
    spec: list                     # окна спецификации
    pseudo: str                    # псевдокод
    tests: list = field(default_factory=list)
    note: str = ""

    def c_source(self, author, variant):
        body = self.c_input + "\n" + self.c_solve
        title = f"Лабораторная работа № 2, часть {'I' * self.part}, задание {self.num}"
        return c_program(f"Лабораторная работа №2, часть {'I' * self.part}, задание {self.num}.\n"
                         f"   Вариант {variant}. Выполнил: {author}",
                         self.defines, self.decls, body, author, title)

    def run(self, lines, author):
        con = Console(lines)
        title = f"Лабораторная работа № 2, часть {'I' * self.part}, задание {self.num}"
        con.printf(f"{title}\nВыполнил: {author}\n\n")
        try:
            self.simulate(con)
        except EndOfInput:
            pass
        return con
