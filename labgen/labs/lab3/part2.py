"""Часть II лабы 3: «Дана целочисленная матрица. Вычислить значение по формуле» (min/max по строкам/столбцам).

Девять задач различаются только параметрами формулы, поэтому строятся по таблице VARIANTS:
внешняя операция и индекс, внутренняя операция, величина под знаком, квадратная ли матрица.
"""
from ..core.task import Task
from ..core.cio import py_input_int, spec_input_int
from ..lab2.common import parse_line
from ..core.omml import m, subx, absd, par, limlow, rng_bar
from .shared import helpers, T, alg

COUNT = 9
INTRO = "Дана целочисленная матрица. Вычислить значение по формуле: "
NMAX, EMAX = 9, 99

# величина под знаком: C-выражение, Python, текст для вывода, внутренний индекс доходит до «m − 1»/«n − 1»
ELEMS = {
    "adr": ("ABS(a[i][j] - a[i][j + 1])", lambda a, i, j: abs(a[i][j] - a[i][j + 1]), "|{x}[i,j] - {x}[i,j+1]|",
            "|{x}[i, j] − {x}[i, j + 1]|", True),
    "dr": ("a[i][j] - a[i][j + 1]", lambda a, i, j: a[i][j] - a[i][j + 1], "({x}[i,j] - {x}[i,j+1])",
           "({x}[i, j] − {x}[i, j + 1])", True),
    "adc": ("ABS(a[i][j] - a[i + 1][j])", lambda a, i, j: abs(a[i][j] - a[i + 1][j]), "|{x}[i,j] - {x}[i+1,j]|",
            "|{x}[i, j] − {x}[i + 1, j]|", True),
    "abs": ("ABS(a[i][j])", lambda a, i, j: abs(a[i][j]), "|{x}[i,j]|", "|{x}[i, j]|", False),
    "id": ("a[i][j]", lambda a, i, j: a[i][j], "{x}[i,j]", "{x}[i, j]", False),
}

VARIANTS = {
    1: dict(res="V", M="C", outer="min", ov="i", inner="max", elem="adr", square=False),
    2: dict(res="O", M="B", outer="min", ov="i", inner="max", elem="abs", square=True),
    3: dict(res="S", M="A", outer="max", ov="i", inner="min", elem="adr", square=False),
    4: dict(res="W", M="A", outer="max", ov="i", inner="min", elem="dr", square=False),
    5: dict(res="H", M="B", outer="min", ov="j", inner="max", elem="abs", square=False),
    6: dict(res="S", M="B", outer="min", ov="j", inner="max", elem="id", square=False),
    7: dict(res="D", M="A", outer="max", ov="i", inner="min", elem="abs", square=False),
    8: dict(res="S", M="C", outer="min", ov="j", inner="max", elem="id", square=True),
    9: dict(res="F", M="A", outer="min", ov="j", inner="max", elem="adc", square=True),
}

BASE = [[3, -1, 4, 1], [5, 9, -2, 6], [-5, 3, 5, -8]]
BASE_SQ = [[3, -1, 4], [1, -5, 9], [2, 6, -5]]
WORD = {"min": "минимум", "max": "максимум"}


class Variant:
    def __init__(self, num, res, M, outer, ov, inner, elem, square):
        self.num, self.res, self.M, self.outer, self.ov, self.inner = num, res, M, outer, ov, inner
        self.kind, self.square = elem, square
        self.iv = "j" if ov == "i" else "i"
        c_expr, self.py_elem, out_txt, doc_txt, short = ELEMS[elem]
        self.c_expr = c_expr
        x = M.lower()
        self.out_txt, self.doc_txt = out_txt.format(x=x), doc_txt.format(x=x)
        self.is_abs = "ABS" in c_expr
        # размеры: n – строки, m – столбцы; у квадратной матрицы m = n
        self.ohi = "n" if ov == "i" or square else "m"           # верхняя граница внешнего индекса
        full = "n" if (self.iv == "i" or square) else "m"
        self.ihi = f"{full} − 1" if short else full               # для документов
        self.ihi_c = f"{full} - 1" if short else full
        self.n_lo = 2 if elem == "adc" else 1
        self.m_lo = 2 if elem in ("adr", "dr") else 1
        self.dims = f"[1:n, 1:{'n' if square else 'm'}]"

    # ------------------------------------------------------------------ C
    def c_functions(self):
        M, ov, iv, op_in, op_out = self.M, self.ov, self.iv, self.inner, self.outer
        cmp_in = ">" if op_in == "max" else "<"
        cmp_out = "<" if op_out == "min" else ">"
        if self.square:
            dims = f'''    if (!input_int("порядок матрицы n", {self.n_lo}, NMAX, n)) return 0;
    *m = *n;
'''
        else:
            dims = f'''    if (!input_int("число строк n", {self.n_lo}, NMAX, n)) return 0;
    if (!input_int("число столбцов m", {self.m_lo}, NMAX, m)) return 0;
'''
        cnt_o = "n" if ov == "i" else "m"
        elem_doc = self.out_txt.replace(self.M.lower(), "a")
        return helpers() + f'''
/* Ввод размеров и элементов матрицы (построчно). Возвращает 0 при конце ввода. */
int input(int a[][NMAX + 1], int *n, int *m){{
    int i, ok;
{dims}    printf("Введите матрицу {M} построчно: в каждой строке %d целых чисел "
           "от %d до %d через пробел.\\n", *m, -EMAX, EMAX);
    for (i = 1; i <= *n; i++)
        do{{
            printf("строка %d: ", i);
            ok = read_line(&a[i][1], *m, -EMAX, EMAX);
            if (ok == -1) return 0;
            if (!ok) printf("Ошибка! Повторите ввод строки %d.\\n", i);
        }} while (!ok);
    return 1;
}}

/* Вывод матрицы */
void print_matrix(int a[][NMAX + 1], int n, int m){{
    int i, j;
    printf("\\nМатрица {M}:\\n");
    for (i = 1; i <= n; i++){{
        for (j = 1; j <= m; j++)
            printf("%5d", a[i][j]);
        printf("\\n");
    }}
}}

/* Величина под знаком {op_in}: {elem_doc} */
int elem(int a[][NMAX + 1], int i, int j){{
    return {self.c_expr};
}}

/* Внутренний {op_in} по {iv} = 1..hi при фиксированном {ov} */
int inner(int a[][NMAX + 1], int hi, int {ov}){{
    int {iv}, r;
    r = {"elem(a, i, 1)" if ov == "i" else "elem(a, 1, j)"};
    for ({iv} = 2; {iv} <= hi; {iv}++)
        if (elem(a, i, j) {cmp_in} r) r = elem(a, i, j);
    return r;
}}

/* Обработка матрицы: t[{ov}] - внутренний {op_in} ({ov} = 1..cnt, {iv} = 1..hi),
   результат - {op_out} из t[1:cnt] */
int process(int a[][NMAX + 1], int cnt, int hi, int t[]){{
    int {ov}, r;
    for ({ov} = 1; {ov} <= cnt; {ov}++)
        t[{ov}] = inner(a, hi, {ov});
    r = t[1];
    for ({ov} = 2; {ov} <= cnt; {ov}++)
        if (t[{ov}] {cmp_out} r) r = t[{ov}];
    return r;
}}

/* Вывод результатов */
void output(const int t[], int cnt, int r){{
    int k;
    printf("\\n{op_in} по {iv} величины {self.out_txt}:\\n");
    for (k = 1; k <= cnt; k++)
        printf("  {ov} = %d: %d\\n", k, t[k]);
    printf("{self.res} = {op_out} по {ov} = %d\\n", r);
}}
'''

    def c_body(self):
        cnt_o = "n" if self.ov == "i" or self.square else "m"
        return f'''    if (!input({self.M}, &n, &m)) return 1;
    print_matrix({self.M}, n, m);
    r = process({self.M}, {cnt_o}, {self.ihi_c}, t);
    output(t, {cnt_o}, r);
'''

    # ------------------------------------------------------------------ Python
    def simulate(self, con):
        M = self.M
        if self.square:
            n = py_input_int(con, "порядок матрицы n", self.n_lo, NMAX)
            mm = n
        else:
            n = py_input_int(con, "число строк n", self.n_lo, NMAX)
            mm = py_input_int(con, "число столбцов m", self.m_lo, NMAX)
        con.printf(f"Введите матрицу {M} построчно: в каждой строке %d целых чисел от %d до %d через пробел.\n"
                   % (mm, -EMAX, EMAX))
        a = [[0] * (mm + 1)]
        for i in range(1, n + 1):
            while True:
                con.printf("строка %d: " % i)
                ok, v = parse_line(con.readline(), mm, -EMAX, EMAX)
                if ok:
                    a.append([0] + v)
                    break
                con.printf("Ошибка! Повторите ввод строки %d.\n" % i)
        con.printf(f"\nМатрица {M}:\n")
        for i in range(1, n + 1):
            con.printf("".join("%5d" % a[i][j] for j in range(1, mm + 1)) + "\n")
        con.begin_results()
        ihi = {"n": n, "m": mm}[self.ihi.split()[0]] - (1 if "−" in self.ihi else 0)
        cnt = n if self.ov == "i" else mm
        pick = min if self.inner == "min" else max
        t = [0] * (cnt + 1)
        for o in range(1, cnt + 1):
            vals = [self.py_elem(a, o, k) if self.ov == "i" else self.py_elem(a, k, o) for k in range(1, ihi + 1)]
            t[o] = pick(vals)
        r = (min if self.outer == "min" else max)(t[1:])
        con.printf(f"\n{self.inner} по {self.iv} величины {self.out_txt}:\n")
        for k in range(1, cnt + 1):
            con.printf(f"  {self.ov} = %d: %d\n" % (k, t[k]))
        con.printf(f"{self.res} = {self.outer} по {self.ov} = %d\n" % r)

    # ------------------------------------------------------------------ документы
    def elem_xml(self):
        x = self.M.lower()
        e = {
            "adr": absd(subx(m(x), m("i,j")) + m(" − ") + subx(m(x), m("i,j+1"))),
            "dr": par(subx(m(x), m("i,j")) + m(" − ") + subx(m(x), m("i,j+1"))),
            "adc": absd(subx(m(x), m("i,j")) + m(" − ") + subx(m(x), m("i+1,j"))),
            "abs": absd(subx(m(x), m("i,j"))),
            "id": subx(m(x), m("i,j")),
        }[self.kind]
        return e

    def formula(self):
        inner = limlow(self.inner, rng_bar(self.iv, "1", self.ihi.replace(" ", "")), self.elem_xml())
        return m(f"{self.res} = ") + limlow(self.outer, rng_bar(self.ov, "1", self.ohi), inner)

    def statement(self):
        x = self.M.lower()
        return (f"{self.res} = {self.outer}({self.ov} = 1..{self.ohi}) {self.inner}({self.iv} = 1..{self.ihi}) "
                f"{self.doc_txt}, где {x}[i, j] – элементы матрицы {self.M}{self.dims}.")

    def formulas(self, rep):
        x = self.M.lower()
        rep.math_block(self.formula() + m(",  где  ") + subx(m(x), m("i,j")) + m(f" – элементы матрицы {self.M}")
                       + m(self.dims.replace(":", " : ") + "."), rows=2)

    def svyaz(self, rep):
        rep.fline("", self.formula())
        what = "строки" if self.ov == "i" else "столбца"
        rep.para(f"t[{self.ov}] – значение внутреннего {WORD[self.inner]}а для {what} {self.ov}, "
                 f"{self.res} – {WORD[self.outer]} из t[1:{'n' if self.ov == 'i' or self.square else 'm'}].",
                 after=4)

    def method(self):
        cnt_o = "n" if self.ov == "i" or self.square else "m"
        op_in = ">" if self.inner == "max" else "<"
        op_out = "<" if self.outer == "min" else ">"
        ij = "i, j"
        first = "elem(i, 1)" if self.ov == "i" else "elem(1, j)"
        return [
            (f"Величина под знаком {self.inner} вычисляется функцией elem(i, j):", [f"elem(i, j) = {self.doc_txt}"]),
            (f"Внутренний {WORD[self.inner]} при фиксированном {self.ov} – функция inner({self.ov}):",
             [f"r = {first}", [f"для {self.iv} = {{2..{self.ihi}}}", f"r = elem({ij}),  если  elem({ij}) {op_in} r"],
              f"inner({self.ov}) = r"]),
            (f"Обработка матрицы – функция process: внутренние {WORD[self.inner]}ы запоминаются в t, "
             f"результат – их {WORD[self.outer]}:",
             [[f"для {self.ov} = {{1..{cnt_o}}}", f"t[{self.ov}] = inner({self.ov})"], f"{self.res} = t[1]",
              [f"для {self.ov} = {{2..{cnt_o}}}", f"{self.res} = t[{self.ov}],  если  t[{self.ov}] {op_out} "
                                                  f"{self.res}"]]),
        ]

    def spec(self):
        M = self.M
        if self.square:
            dims = spec_input_int("порядок матрицы n", self.n_lo, "NMAX", "n")
        else:
            dims = spec_input_int("число строк n", self.n_lo, "NMAX", "n") + \
                spec_input_int("число столбцов m", self.m_lo, "NMAX", "m")
        mv = "n" if self.square else "m"
        cnt_o = "n" if self.ov == "i" or self.square else "m"
        return dims + [
            ("box", [f"Введите матрицу {M} построчно: в каждой строке <<{mv}>> целых чисел "
                     "от <<-EMAX>> до <<EMAX>> через пробел."], False),
            ("loop_start", "i", "1", "n"),
            ("rep_start",),
            ("box", [f"строка <<i>>: <{M}[i,1]> <{M}[i,2]> … <{M}[i,{mv}]>"], False),
            ("label", "При ошибке в строке (не числа, не то количество, вне диапазона)"),
            ("box", ["Ошибка! Повторите ввод строки <<i>>."], True),
            ("rep_end", f"До {M}[i,1:{mv}] введена верно"),
            ("loop_end",),
            ("box", [f"Матрица {M}:", f"<<{M}[1,1]>> <<{M}[1,2]>> … <<{M}[1,{mv}]>>", "…",
                     f"<<{M}[n,1]>> <<{M}[n,2]>> … <<{M}[n,{mv}]>>"], False),
            ("box", [f"{self.inner} по {self.iv} величины {self.out_txt}:",
                     f"  {self.ov} = 1: <<t[1]>>", "  …", f"  {self.ov} = <<{cnt_o}>>: <<t[{cnt_o}]>>",
                     f"{self.res} = {self.outer} по {self.ov} = <<{self.res}>>"], False),
        ]

    def pseudo(self):
        cnt_o = "n" if self.ov == "i" or self.square else "m"
        op_in = ">" if self.inner == "max" else "<"
        op_out = "<" if self.outer == "min" else ">"
        first = "elem(i, 1)" if self.ov == "i" else "elem(1, j)"
        size = "ввод(n); m := n" if self.square else "ввод(n, m)"
        return f"""
_функция_ elem(i, j)
_нач_
	_возврат_ {self.doc_txt}
_кон_

_функция_ inner({self.ov})
_нач_
	r := {first}
	_цикл от_ {self.iv} := 2 _до_ {self.ihi}
		_если_ elem(i, j) {op_in} r _то_
			r := elem(i, j)
		_всё_
	_кц_
	_возврат_ r
_кон_

_функция_ process({self.M}, t)
_нач_
	_цикл от_ {self.ov} := 1 _до_ {cnt_o}
		t[{self.ov}] := inner({self.ov})
	_кц_
	r := t[1]
	_цикл от_ {self.ov} := 2 _до_ {cnt_o}
		_если_ t[{self.ov}] {op_out} r _то_
			r := t[{self.ov}]
		_всё_
	_кц_
	_возврат_ r
_кон_

{alg("II", self.num)}
_нач_
	{size}
	ввод({self.M}[1:n, 1:{"n" if self.square else "m"}])
	вывод({self.M}[1:n, 1:{"n" if self.square else "m"}])
	{self.res} := process({self.M}, t)
	вывод(«{self.inner} по {self.iv} величины {self.out_txt}:», t[1:{cnt_o}])
	вывод(«{self.res} = {self.outer} по {self.ov} = », {self.res})
_кон_
"""

    # ------------------------------------------------------------------ тесты
    def _lines(self, mat):
        dims = [str(len(mat))] if self.square else [str(len(mat)), str(len(mat[0]))]
        return dims + [" ".join(map(str, r)) for r in mat]

    def _shown(self, mat):
        dims = f"n = {len(mat)}" if self.square else f"n = {len(mat)}, m = {len(mat[0])}"
        return [dims, f"{self.M} ="] + ["  " + " ".join(f"{v:3d}" for v in r) for r in mat]

    def tests(self):
        base = BASE_SQ if self.square else BASE
        tests = [T(self._lines(base), self._shown(base), "Обычный случай: элементы разных знаков")]
        if self.square:
            small = [[-4, 2], [7, -1]]
            tests.append(T(self._lines(small), self._shown(small), "Матрица 2×2"))
        elif self.ov == "i":
            row = [[6, -3, 8, 0, -7]]
            tests.append(T(self._lines(row), self._shown(row), "Одна строка (n = 1)"))
        else:
            col = [[4], [-9], [2]] if self.m_lo == 1 else [[4, -1], [-9, 3], [2, 2]]
            tests.append(T(self._lines(col), self._shown(col), "Один столбец (m = 1)" if self.m_lo == 1 else
                           "Два столбца"))
        same = [[5] * (len(base[0])) for _ in base]
        tests.append(T(self._lines(same), self._shown(same), "Все элементы равны"))
        # недопустимые данные: размеры, затем строки матрицы
        n, mm = len(base), len(base[0])
        rows = [" ".join(map(str, r)) for r in base]
        if self.square:
            dims = ["0", "x", "10", f"{n}.0", str(n)]
            shown_dims = f"n: 0 / x / 10 / {n}.0 / {n}"
        else:
            bad_m = str(self.m_lo - 1)
            dims = ["0", "x", str(n), bad_m, "2.5", str(mm)]
            shown_dims = f"n: 0 / x / {n};  m: {bad_m} / 2.5 / {mm}"
        r1_short = " ".join(rows[0].split()[:-1])
        lines = dims + [r1_short, rows[0].replace(rows[0].split()[0], "q", 1), rows[0],
                        rows[1] + " 0", rows[1].rsplit(" ", 1)[0] + " 100", rows[1]] + rows[2:]
        shown = [shown_dims, "строка 1: мало чисел / буква / верно", "строка 2: лишнее число / 100 / верно",
                 "далее – как в тесте 1"]
        tests.append(T(lines, shown, "Недопустимые данные: размеры вне диапазона, строка, вещественное; "
                                     "ошибки в строках матрицы"))
        return tests

    def task(self):
        decls = f"    int {self.M}[NMAX + 1][NMAX + 1], t[NMAX + 1], n, m, r;\n"
        defines = ("#define NMAX 9          /* максимальное число строк / столбцов матрицы */\n"
                   "#define EMAX 99         /* максимальный модуль элемента матрицы */")
        if self.is_abs:
            defines += "\n#define ABS(a) ((a) < 0 ? -(a) : (a))   /* модуль числа */"
        mv = "n" if self.square else "m"
        given = ([f"n, {self.M}[1:n, 1:n] – квадратная целочисленная матрица."] if self.square
                 else [f"n, m, {self.M}[1:n, 1:m] – целочисленная матрица."])
        lims = [f"n ∈ N, {self.n_lo} ≤ n ≤ NMAX = {NMAX}" + ("" if self.square else
                                                           f"; m ∈ N, {self.m_lo} ≤ m ≤ NMAX")
                + f"; {self.M}[i, j] ∈ Z, |{self.M}[i, j]| ≤ EMAX = {EMAX}."]
        cnt_o = "n" if self.ov == "i" or self.square else "m"
        what = "каждой строки" if self.ov == "i" else "каждого столбца"
        return Task(
            lab=3, part="II", num=self.num, statement=self.statement(), includes=[], defines=defines,
            functions=self.c_functions(), decls=decls, body=self.c_body(), simulate=self.simulate,
            given=given,
            result=[f"t[1:{cnt_o}] – внутренний {WORD[self.inner]} для {what}; {self.res} – значение по "
                    f"формуле."],
            when=lims, svyaz=self.svyaz, method=self.method(), spec=self.spec(), pseudo=self.pseudo(),
            tests=self.tests(), formulas=self.formulas, file="lab3_part2.c", lead="",
            note=f"Матрица хранится в массиве {self.M}[1:NMAX, 1:NMAX] (строка и столбец с номером 0 не "
                 f"используются){'; у квадратной матрицы m = n' if self.square else ''}." if mv else "",
        )


_cache = {}


def get(num):
    if num not in VARIANTS:
        raise ModuleNotFoundError(num)
    if num not in _cache:
        _cache[num] = Variant(num, **VARIANTS[num]).task()
    return _cache[num]
