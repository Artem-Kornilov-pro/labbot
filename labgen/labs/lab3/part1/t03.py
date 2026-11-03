from ...core.task import Task
from ...core.cio import py_input_reals, spec_input_reals, RMAX
from ...core.omml import m, frac, sub, brace_rows
from ..shared import helpers, T, alg, RMAX_DEFINE
from . import REMARK

FUNCS = helpers(ints=False, reals=True) + r'''
/* Общая часть формулы - линейная интерполяция по узлам (xa, ya) и (xb, yb)
   (в программе записана два раза - для отрезков [x1; x2] и [x2; x3]) */
double lin(double xa, double ya, double xb, double yb, double x){
    return ya + (x - xa) / (xb - xa) * (yb - ya);
}

/* Ввод таблицы функции и точки x. Возвращает 0 при конце ввода. */
int input(double x[], double y[], double *t){
    int ok;
    do{
        if (!input_reals("узлы x1 x2 x3 (по возрастанию)", 3, -RMAX, RMAX, x)) return 0;
        ok = x[0] < x[1] && x[1] < x[2];
        if (!ok) printf("Ошибка! Нужно x1 < x2 < x3.\n");
    } while (!ok);
    if (!input_reals("значения y1 y2 y3", 3, -RMAX, RMAX, y)) return 0;
    do{
        if (!input_reals("точку x", 1, -RMAX, RMAX, t)) return 0;
        ok = x[0] <= *t && *t <= x[2];
        if (!ok) printf("Ошибка! Нужно %g <= x <= %g.\n", x[0], x[2]);
    } while (!ok);
    return 1;
}

/* Вычисление приближённого значения f(x) */
double compute(const double x[], const double y[], double t){
    if (t < x[1]) return lin(x[0], y[0], x[1], y[1], t);
    if (t < x[2]) return lin(x[1], y[1], x[2], y[2], t);
    return y[2];
}

/* Вывод результата */
void output(double t, double f){
    printf("\nf(%g) = %.4f\n", t, f);
}
'''

BODY = '''    if (!input(x, y, &t)) return 1;
    f = compute(x, y, t);
    output(t, f);
'''


def lin(xa, ya, xb, yb, x):
    return ya + (x - xa) / (xb - xa) * (yb - ya)


def simulate(con):
    while True:
        x = py_input_reals(con, "узлы x1 x2 x3 (по возрастанию)", 3, -RMAX, RMAX)
        if x[0] < x[1] < x[2]:
            break
        con.printf("Ошибка! Нужно x1 < x2 < x3.\n")
    y = py_input_reals(con, "значения y1 y2 y3", 3, -RMAX, RMAX)
    while True:
        t = py_input_reals(con, "точку x", 1, -RMAX, RMAX)[0]
        if x[0] <= t <= x[2]:
            break
        con.printf("Ошибка! Нужно %g <= x <= %g.\n" % (x[0], x[2]))
    con.begin_results()
    if t < x[1]:
        f = lin(x[0], y[0], x[1], y[1], t)
    elif t < x[2]:
        f = lin(x[1], y[1], x[2], y[2], t)
    else:
        f = y[2]
    con.printf("\nf(%g) = %.4f\n" % (t, f))


def _row(i, j):
    return (sub("y", i) + m(" + ") + frac(m("x − ") + sub("x", i), sub("x", j) + m(" − ") + sub("x", i))
            + m("(") + sub("y", j) + m(" − ") + sub("y", i) + m("),  если  ") + sub("x", i) + m(" ≤ x < ")
            + sub("x", j) + m(","))


def formula():
    return m("f(x) = ") + brace_rows([_row("1", "2"), _row("2", "3"),
                                      sub("y", "3") + m(",  если  x = ") + sub("x", "3") + m(".")])


def formulas(rep):
    rep.para("Функция y = f(x) задана таблицей:", after=2)
    rep.math_block(m("X: ") + sub("X", "1") + m(",  ") + sub("X", "2") + m(",  ") + sub("X", "3")
                   + m(";    Y: ") + sub("Y", "1") + m(",  ") + sub("Y", "2") + m(",  ") + sub("Y", "3"))
    rep.para("Вычислить приближенное значение f(x) в точке x1 ≤ x ≤ x3 по формуле:", after=2)
    rep.math_block(formula(), rows=5)
    rep.para(REMARK, after=4)


def svyaz(rep):
    rep.math_block(formula(), rows=5)
    rep.para("(линейная интерполяция: на каждом отрезке таблицы график заменяется отрезком прямой через два "
             "соседних узла).", after=4)


METHOD = [
    ("Общая часть формулы – значение на прямой, проходящей через узлы (xa, ya) и (xb, yb), – оформляется "
     "функцией lin(xa, ya, xb, yb, x); для отрезков [x1; x2] и [x2; x3] вызывается одна и та же функция:",
     ["lin(xa, ya, xb, yb, x) = ya + (x − xa) / (xb − xa) · (yb − ya)"]),
    ("Выбор отрезка по положению точки x:",
     ["f = lin(x1, y1, x2, y2, x),  если  x < x2",
      "f = lin(x2, y2, x3, y3, x),  если  x2 ≤ x < x3",
      "f = y3,  если  x = x3"]),
]

SPEC = (spec_input_reals("узлы x1 x2 x3 (по возрастанию)", ["x1", "x2", "x3"], 3,
                         extra=("При нарушении x1 < x2 < x3", "Ошибка! Нужно x1 < x2 < x3."))
        + spec_input_reals("значения y1 y2 y3", ["y1", "y2", "y3"], 3)
        + spec_input_reals("точку x", ["x"], 1,
                           extra=("При x < x1 или x > x3", "Ошибка! Нужно <<x1>> <= x <= <<x3>>."))
        + [("box", ["f(<<x>>) = <<f>>"], False)])

PSEUDO = f"""
_функция_ lin(xa, ya, xb, yb, x)
_нач_
	_возврат_ ya + (x − xa) / (xb − xa) · (yb − ya)
_кон_

{alg("I", 3)}
_нач_
	ввод(x1, x2, x3, y1, y2, y3, x)
	_если_ x < x2 _то_
		f := lin(x1, y1, x2, y2, x)
	_иначе_
		_если_ x < x3 _то_
			f := lin(x2, y2, x3, y3, x)
		_иначе_
			f := y3
		_всё_
	_всё_
	вывод(«f(», x, «) = », f)
_кон_
"""

TESTS = [
    T(["0 1 3", "1 3 2", "0.5"], ["X: 0 1 3", "Y: 1 3 2", "x = 0.5"], "x на первом отрезке [x1; x2]"),
    T(["0 1 3", "1 3 2", "2"], ["X: 0 1 3", "Y: 1 3 2", "x = 2"], "x на втором отрезке [x2; x3]"),
    T(["-2.5 0 4", "7 -1 3.5", "4"], ["X: −2.5 0 4", "Y: 7 −1 3.5", "x = 4"], "Граничный случай x = x3"),
    T(["1 1 2", "a b c", "0 1", "0 1 3", "1 3 2", "5", "1.5.", "1"],
      ["X: 1 1 2 / a b c / 0 1 / 0 1 3", "Y: 1 3 2", "x: 5 / 1.5. / 1"],
      "Недопустимые данные: узлы не по возрастанию, строка, мало чисел, x вне [x1; x3], x = x2"),
]

TASK = Task(
    lab=3, part="I", num=3,
    statement="Функция y = f(x) задана таблицей: X1, X2, X3; Y1, Y2, Y3. Вычислить приближенное значение f(x) "
              "в точке x1 ≤ x ≤ x3 по формуле: f(x) = y1 + (x − x1)/(x2 − x1)·(y2 − y1), если x1 ≤ x < x2; "
              "f(x) = y2 + (x − x2)/(x3 − x2)·(y3 − y2), если x2 ≤ x < x3; f(x) = y3, если x = x3.",
    includes=["stdlib.h"], defines=RMAX_DEFINE,
    functions=FUNCS, decls="    double x[3], y[3], t, f;\n", body=BODY, simulate=simulate,
    given=["x1, x2, x3 – узлы таблицы; y1, y2, y3 – значения функции в узлах; x – точка."],
    result=["f – приближённое значение функции в точке x (с 4 знаками после запятой)."],
    when=[f"xi, yi ∈ R, |xi|, |yi| ≤ RMAX = {RMAX}, x1 < x2 < x3;", "x ∈ R, x1 ≤ x ≤ x3."],
    svyaz=svyaz, method=METHOD, spec=SPEC, pseudo=PSEUDO, tests=TESTS, formulas=formulas,
    note="В программе узлы хранятся в массивах x[0:2], y[0:2] (x[0] = x1, …, x[2] = x3).",
    file="lab3_part1.c", lead='',
)
