from ..common import Task
from ..inputs import PositiveArray
from .shared import c_print_arr, py_print_arr, maker, bad_test
from ....docx_engine import F

IN = PositiveArray()
_t = maker(IN)

C_SOLVE = f'''    /* обратный порядок цифр: последняя цифра v переносится в конец числа r */
    for (i = 1; i <= n; i++){{
        v = X[i];
        r = 0;
        while (v > 0){{
            r = r * 10 + v % 10;
            v = v / 10;
        }}
        X[i] = r;
    }}
{c_print_arr("\\nПреобразованный массив X: ", "X", "n", ind="    ")}
'''


def rev(x):
    r = 0
    while x > 0:
        r = r * 10 + x % 10
        x //= 10
    return r


def simulate(con):
    n, X = IN.read(con)
    con.begin_results()
    py_print_arr(con, "\nПреобразованный массив X: ", [rev(X[i]) for i in range(1, n + 1)])


def svyaz(rep):
    rep.fline("", F("∀ i = {1..n}:  X[i] = a[i, d−1] … a[i, 1] a[i, 0]  ⇒"))
    rep.fline("", F("⇒  X'[i] = a[i, 0] a[i, 1] … a[i, d−1]"), indent=0.6)
    rep.para("(ведущие нули результата отбрасываются: 120 → 21).", indent=0.6)


METHOD = [
    ("Для каждого элемента цифры отделяются справа и приписываются в конец нового числа r:",
     [["для i = {1..n}",
       "v = X[i];  r = 0",
       ["пока  v > 0", "r = r · 10 + (v − 10 · (v \\ 10));  v = v \\ 10"],
       "X[i] = r"]]),
]

SPEC = [("box", ["Преобразованный массив X: <<X[1]>> <<X[2]>> … <<X[n]>>"], False)]

PSEUDO = """
_алг_ «Лабораторная работа №2, часть II, задание 2»
_нач_
	ввод(n, X[1:n])
	вывод(X[1:n])
	_цикл от_ i := 1 _до_ n
		v := X[i]; r := 0
		_цикл-пока_ v > 0
			r := r · 10 + (v − 10 · (v \\ 10)); v := v \\ 10
		_кц_
		X[i] := r
	_кц_
	вывод(«Преобразованный массив X: », X[1:n])
_кон_
"""

TESTS = [
    _t([1623, 120, 5, 1001, 999999999], "Разные числа: с нулём в конце (120 → 21), палиндром, максимальное"),
    _t([100000000], "Число с нулями: 100000000 → 1"),
    bad_test(IN, [12, 34], "Недопустимые данные: n = 0, буква, отрицательное и дробное число, мало чисел"),
]

TASK = Task(
    part=2, num=2,
    statement="Дан массив целых положительных чисел. Для каждого элемента массива поменять порядок следования "
              "цифр на обратный.",
    short="Обратный порядок цифр",
    defines=IN.defines, decls=IN.decls + "    int v, r;\n",
    c_input=IN.c_input, c_solve=C_SOLVE, simulate=simulate,
    given=IN.given,
    result=["X[1:n] – массив, в каждом элементе которого цифры записаны в обратном порядке (ведущие нули "
            "отбрасываются)."],
    when=IN.when, svyaz=svyaz, method=METHOD, spec=IN.spec + SPEC, pseudo=PSEUDO, tests=TESTS,
)
