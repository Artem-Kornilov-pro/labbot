from ..common import Task
from ..inputs import PositiveArray
from .shared import c_print_arr, py_print_arr, maker, bad_test
from ....docx_engine import F, m, nprod

IN = PositiveArray()
_t = maker(IN)

C_SOLVE = f'''    /* произведение цифр каждого элемента (досрочный выход, если встретился 0) */
    for (i = 1; i <= n; i++){{
        v = X[i];
        p = 1;
        while (v > 0 && p != 0){{
            p = p * (v % 10);
            v = v / 10;
        }}
        Y[i] = p;
    }}
{c_print_arr("\\nНовый массив Y (произведения цифр): ", "Y", "n", ind="    ")}
'''


def dprod(x):
    p = 1
    while x > 0 and p != 0:
        p *= x % 10
        x //= 10
    return p


def simulate(con):
    n, X = IN.read(con)
    con.begin_results()
    py_print_arr(con, "\nНовый массив Y (произведения цифр): ", [dprod(X[i]) for i in range(1, n + 1)])


def svyaz(rep):
    rep.fline("", F("∀ i = {1..n}:  X[i] = a[i, d[i]−1] … a[i, 1] a[i, 0],"))
    rep.fline("", m("Y[i] = ") + nprod(m("j = 0"), m("d[i] − 1"), m("a[i, j]")), indent=0.6)
    rep.para("где d[i] – число цифр X[i]; произведение цифр не превышает 9⁹ < 2³¹, поэтому помещается в int.",
             indent=0.6)


METHOD = [
    ("Для каждого элемента цифры отделяются справа и перемножаются; при встрече цифры 0 произведение уже "
     "равно нулю – досрочный выход из цикла:",
     [["для i = {1..n}",
       "v = X[i];  p = 1",
       ["пока  v > 0  и  p ≠ 0", "p = p · (v − 10 · (v \\ 10));  v = v \\ 10"],
       "Y[i] = p"]]),
]

SPEC = [("box", ["Новый массив Y (произведения цифр): <<Y[1]>> <<Y[2]>> … <<Y[n]>>"], False)]

PSEUDO = """
_алг_ «Лабораторная работа №2, часть II, задание 3»
_нач_
	ввод(n, X[1:n])
	вывод(X[1:n])
	_цикл_ _от_ i := 1 _до_ n
		v := X[i]; p := 1
		_цикл-пока_ v > 0 _и_ p ≠ 0
			p := p · (v − 10 · (v \\ 10)); v := v \\ 10
		_кц_
		Y[i] := p
	_кц_
	вывод(«Новый массив Y (произведения цифр): », Y[1:n])
_кон_
"""

TESTS = [
    _t([234, 105, 7, 999999999, 11], "Разные числа, число с нулём (произведение 0), максимальное"),
    _t([1], "Один элемент"),
    bad_test(IN, [25, 9], "Недопустимые данные: n = 0, буква, отрицательное и дробное число, мало чисел"),
]

TASK = Task(
    part=2, num=3,
    statement="Дан массив целых положительных чисел. Сформировать новый массив, содержащий произведения цифр "
              "каждого элемента исходного массива.",
    short="Произведения цифр элементов",
    defines=IN.defines, decls=IN.decls + "    int Y[KMAX + 1], v, p;\n",
    c_input=IN.c_input, c_solve=C_SOLVE, simulate=simulate,
    given=IN.given,
    result=["Y[1:n] – новый массив, Y[i] – произведение цифр элемента X[i]."],
    when=IN.when, svyaz=svyaz, method=METHOD, spec=IN.spec + SPEC, pseudo=PSEUDO, tests=TESTS,
)
