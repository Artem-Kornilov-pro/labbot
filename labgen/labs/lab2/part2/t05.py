from ..common import Task
from ..inputs import PositiveArray
from .shared import c_print_arr, py_print_arr, maker, bad_test
from ....docx_engine import F

IN = PositiveArray()
_t = maker(IN)

C_SOLVE = f'''    /* произведение первой и последней цифр каждого элемента */
    for (i = 1; i <= n; i++){{
        last = X[i] % 10;
        v = X[i];
        while (v >= 10)                 /* до первой цифры */
            v = v / 10;
        Y[i] = v * last;
    }}
{c_print_arr("\\nНовый массив Y (произведения первой и последней цифр): ", "Y", "n", ind="    ")}
'''


def fl(x):
    last = x % 10
    while x >= 10:
        x //= 10
    return x * last


def simulate(con):
    n, X = IN.read(con)
    con.begin_results()
    py_print_arr(con, "\nНовый массив Y (произведения первой и последней цифр): ", [fl(X[i]) for i in range(1, n + 1)])


def svyaz(rep):
    rep.fline("", F("∀ i = {1..n}:  X[i] = a[i, d[i]−1] … a[i, 0],"))
    rep.fline("", F("Y[i] = a[i, d[i]−1] · a[i, 0]"), indent=0.6)
    rep.para("(для однозначного числа первая и последняя цифры совпадают: Y[i] = X[i]²).", indent=0.6)


METHOD = [
    ("Для каждого элемента последняя цифра – остаток от деления на 10, первая – результат деления на 10, "
     "пока число не станет однозначным:",
     [["для i = {1..n}",
       "last = X[i] − 10 · (X[i] \\ 10);  v = X[i]",
       ["пока  v ≥ 10", "v = v \\ 10"],
       "Y[i] = v · last"]]),
]

SPEC = [("box", ["Новый массив Y (произведения первой и последней цифр): <<Y[1]>> <<Y[2]>> … <<Y[n]>>"], False)]

PSEUDO = """
_алг_ «Лабораторная работа №2, часть II, задание 5»
_нач_
	ввод(n, X[1:n])
	вывод(X[1:n])
	_цикл_ _от_ i := 1 _до_ n
		last := X[i] − 10 · (X[i] \\ 10); v := X[i]
		_цикл-пока_ v ≥ 10
			v := v \\ 10
		_кц_
		Y[i] := v · last
	_кц_
	вывод(«Новый массив Y (произведения первой и последней цифр): », Y[1:n])
_кон_
"""

TESTS = [
    _t([1623, 50, 7, 999999999, 101], "Разные числа: с нулём в конце (0), однозначное (7·7), максимальное"),
    _t([38], "Один двузначный элемент"),
    bad_test(IN, [21, 3], "Недопустимые данные: n = 0, буква, отрицательное и дробное число, мало чисел"),
]

TASK = Task(
    part=2, num=5,
    statement="Дан массив целых положительных чисел. Сформировать новый массив, каждый элемент которого равен "
              "произведению первой и последней цифры соответствующего элемента исходного массива.",
    short="Произведение первой и последней цифр",
    defines=IN.defines, decls=IN.decls + "    int Y[KMAX + 1], v, last;\n",
    c_input=IN.c_input, c_solve=C_SOLVE, simulate=simulate,
    given=IN.given,
    result=["Y[1:n] – новый массив, Y[i] – произведение первой и последней цифр элемента X[i]."],
    when=IN.when, svyaz=svyaz, method=METHOD, spec=IN.spec + SPEC, pseudo=PSEUDO, tests=TESTS,
)
