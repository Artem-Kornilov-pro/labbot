from ..common import Task
from ..inputs import PositiveArray
from .shared import c_print_arr, py_print_arr, maker, bad_test
from ....docx_engine import F, m, nsum

IN = PositiveArray()
_t = maker(IN)

C_SOLVE = f'''    /* сумма цифр каждого элемента: цифры отделяются остатком от деления на 10 */
    for (i = 1; i <= n; i++){{
        v = X[i];
        s = 0;
        while (v > 0){{
            s = s + v % 10;
            v = v / 10;
        }}
        Y[i] = s;
    }}
{c_print_arr("\\nНовый массив Y (суммы цифр): ", "Y", "n", ind="    ")}
'''


def dsum(x):
    s = 0
    while x > 0:
        s += x % 10
        x //= 10
    return s


def simulate(con):
    n, X = IN.read(con)
    con.begin_results()
    py_print_arr(con, "\nНовый массив Y (суммы цифр): ", [dsum(X[i]) for i in range(1, n + 1)])


def svyaz(rep):
    rep.fline("", F("∀ i = {1..n}:  X[i] = a[i, d[i]−1] … a[i, 1] a[i, 0],"))
    rep.fline("", m("Y[i] = ") + nsum(m("j = 0"), m("d[i] − 1"), m("a[i, j]")), indent=0.6)
    rep.para("где d[i] – число цифр элемента X[i], a[i, j] – цифра j-го разряда (справа, начиная с 0).", indent=0.6)


METHOD = [
    ("Для каждого элемента цифры отделяются справа: последняя цифра – остаток от деления на 10, отбрасывание "
     "последней цифры – целочисленное деление на 10:",
     [["для i = {1..n}",
       "v = X[i];  s = 0",
       ["пока  v > 0", "s = s + (v − 10 · (v \\ 10));  v = v \\ 10"],
       "Y[i] = s"]]),
]

SPEC = [("box", ["Новый массив Y (суммы цифр): <<Y[1]>> <<Y[2]>> … <<Y[n]>>"], False)]

PSEUDO = """
_алг_ «Лабораторная работа №2, часть II, задание 1»
_нач_
	ввод(n, X[1:n])
	вывод(X[1:n])
	_цикл_ _от_ i := 1 _до_ n
		v := X[i]; s := 0
		_цикл-пока_ v > 0
			s := s + (v − 10 · (v \\ 10)); v := v \\ 10
		_кц_
		Y[i] := s
	_кц_
	вывод(«Новый массив Y (суммы цифр): », Y[1:n])
_кон_
"""

TESTS = [
    _t([123, 5, 9999, 1000, 999999999], "Разные числа, в т.ч. с нулями и максимальное допустимое"),
    _t([7], "Один однозначный элемент"),
    bad_test(IN, [10, 205], "Недопустимые данные: n = 0, буква, отрицательное и дробное число, мало чисел"),
]

TASK = Task(
    part=2, num=1,
    statement="Дан массив целых положительных чисел. Сформировать новый массив, содержащий суммы цифр каждого "
              "элемента исходного массива.",
    short="Суммы цифр элементов",
    defines=IN.defines, decls=IN.decls + "    int Y[KMAX + 1], v, s;\n",
    c_input=IN.c_input, c_solve=C_SOLVE, simulate=simulate,
    given=IN.given,
    result=["Y[1:n] – новый массив, Y[i] – сумма цифр элемента X[i]."],
    when=IN.when, svyaz=svyaz, method=METHOD, spec=IN.spec + SPEC, pseudo=PSEUDO, tests=TESTS,
)
