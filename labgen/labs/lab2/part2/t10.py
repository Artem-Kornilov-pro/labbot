from ..common import Task
from ..inputs import PositiveArray
from .shared import c_print_arr, py_print_arr, maker, bad_test
from ....docx_engine import F, m, sup

IN = PositiveArray()
_t = maker(IN)

C_SOLVE = f'''    /* циклический сдвиг цифр влево: первая цифра становится последней */
    for (i = 1; i <= n; i++){{
        p = 1;                          /* p = 10^(d-1), d - число цифр */
        v = X[i];
        while (v >= 10){{
            p = p * 10;
            v = v / 10;
        }}
        X[i] = (X[i] % p) * 10 + X[i] / p;
    }}
{c_print_arr("\\nПреобразованный массив X: ", "X", "n", ind="    ")}
'''


def shift(x):
    p, v = 1, x
    while v >= 10:
        p *= 10
        v //= 10
    return (x % p) * 10 + x // p


def simulate(con):
    n, X = IN.read(con)
    con.begin_results()
    py_print_arr(con, "\nПреобразованный массив X: ", [shift(X[i]) for i in range(1, n + 1)])


def svyaz(rep):
    rep.fline("", F("∀ i = {1..n}:  X[i] = a[i, d−1] a[i, d−2] … a[i, 0]  ⇒"))
    rep.fline("", F("⇒  X'[i] = a[i, d−2] … a[i, 0] a[i, d−1],"), indent=0.6)
    rep.fline("", m("X'[i] = (X[i] mod ") + sup("10", "d−1") + m(") · 10 + X[i] \\ ") + sup("10", "d−1"),
              indent=0.6)
    rep.para("(если вторая цифра 0, результат короче: 1023 → 231).", indent=0.6)


METHOD = [
    ("Для каждого элемента находится p = 10^(d−1), затем первая цифра (X[i] \\ p) переносится в конец, "
     "а остаток от деления на p сдвигается на разряд влево:",
     [["для i = {1..n}",
       "p = 1;  v = X[i]",
       ["пока  v ≥ 10", "p = p · 10;  v = v \\ 10"],
       "X[i] = (X[i] − p · (X[i] \\ p)) · 10 + X[i] \\ p"]]),
]

SPEC = [("box", ["Преобразованный массив X: <<X[1]>> <<X[2]>> … <<X[n]>>"], False)]

PSEUDO = """
_алг_ «Лабораторная работа №2, часть II, задание 10»
_нач_
	ввод(n, X[1:n])
	вывод(X[1:n])
	_цикл от_ i := 1 _до_ n
		p := 1; v := X[i]
		_цикл-пока_ v ≥ 10
			p := p · 10; v := v \\ 10
		_кц_
		X[i] := (X[i] − p · (X[i] \\ p)) · 10 + X[i] \\ p
	_кц_
	вывод(«Преобразованный массив X: », X[1:n])
_кон_
"""

TESTS = [
    _t([1623, 1023, 8, 90, 999999999], "Пример из условия (1623 → 6231), ноль второй цифрой, однозначное"),
    _t([100], "Число 100 → 1 (ведущие нули отбрасываются)"),
    bad_test(IN, [12, 345], "Недопустимые данные: n = 0, буква, отрицательное и дробное число, мало чисел"),
]

TASK = Task(
    part=2, num=10,
    statement="Дан массив целых положительных чисел. Для каждого элемента массива произвести циклическую "
              "перестановку цифр на одну цифру влево. Например, 1623-> 6231.",
    short="Циклический сдвиг цифр влево",
    defines=IN.defines, decls=IN.decls + "    int v, p;\n",
    c_input=IN.c_input, c_solve=C_SOLVE, simulate=simulate,
    given=IN.given,
    result=["X[1:n] – массив, в каждом элементе которого цифры циклически сдвинуты на одну влево (первая цифра "
            "стала последней; если вторая цифра равна 0, число становится короче)."],
    when=IN.when, svyaz=svyaz, method=METHOD, spec=IN.spec + SPEC, pseudo=PSEUDO, tests=TESTS,
)
