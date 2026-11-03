import math

from ...core.task import Task
from ...core.cio import py_input_reals, spec_input_reals, RMAX
from ...core.omml import m, rad, sup, par
from ..shared import helpers, T, alg, RMAX_DEFINE
from . import REMARK

FUNCS = helpers(ints=False, reals=True) + r'''
/* Общая часть - длина отрезка между (x1, y1) и (x2, y2); вызывается три раза */
double L(double x1, double y1, double x2, double y2){
    return sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2));
}

/* Ввод координат вершин P1, P2, P3. Возвращает 0 при конце ввода. */
int input(double x[], double y[]){
    const char *what[3] = {"координаты точки P1 (x1 y1)", "координаты точки P2 (x2 y2)",
                           "координаты точки P3 (x3 y3)"};
    double p[2];
    int i;
    for (i = 0; i < 3; i++){
        if (!input_reals(what[i], 2, -RMAX, RMAX, p)) return 0;
        x[i] = p[0];
        y[i] = p[1];
    }
    return 1;
}

/* Длины сторон d[0] = |P1P2|, d[1] = |P2P3|, d[2] = |P1P3|; возвращает периметр */
double compute(const double x[], const double y[], double d[]){
    d[0] = L(x[0], y[0], x[1], y[1]);
    d[1] = L(x[1], y[1], x[2], y[2]);
    d[2] = L(x[0], y[0], x[2], y[2]);
    return d[0] + d[1] + d[2];
}

/* Вывод результатов */
void output(const double d[], double p){
    printf("\n|P1P2| = %.4f, |P2P3| = %.4f, |P1P3| = %.4f\n", d[0], d[1], d[2]);
    printf("P = %.4f\n", p);
}
'''

BODY = '''    if (!input(x, y)) return 1;
    p = compute(x, y, d);
    output(d, p);
'''


def L(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))


def simulate(con):
    x, y = [], []
    for i in range(1, 4):
        p = py_input_reals(con, f"координаты точки P{i} (x{i} y{i})", 2, -RMAX, RMAX)
        x.append(p[0])
        y.append(p[1])
    con.begin_results()
    d = [L(x[0], y[0], x[1], y[1]), L(x[1], y[1], x[2], y[2]), L(x[0], y[0], x[2], y[2])]
    con.printf("\n|P1P2| = %.4f, |P2P3| = %.4f, |P1P3| = %.4f\n" % tuple(d))
    con.printf("P = %.4f\n" % (d[0] + d[1] + d[2]))


def formula():
    return m("L(x1, y1, x2, y2) = ") + rad(sup("(x1 − x2)", "2") + m(" + ") + sup("(y1 − y2)", "2"))


def formulas(rep):
    rep.para("Использовать для вычисления длин сторон треугольника формулу:", after=2)
    rep.math_block(formula(), rows=2)
    rep.para(REMARK, after=4)


def svyaz(rep):
    rep.fline("", m("P = L(x1, y1, x2, y2) + L(x2, y2, x3, y3) + L(x1, y1, x3, y3),"))
    rep.fline("", m("где  ") + formula(), indent=0.6)


METHOD = [
    ("Общая часть – длина отрезка по координатам концов – оформляется функцией L(x1, y1, x2, y2), которая "
     "вызывается три раза (для каждой стороны):", ["L = " + "√((x1 − x2)² + (y1 − y2)²)"]),
    ("Вычисление периметра:", ["P = L(x1, y1, x2, y2) + L(x2, y2, x3, y3) + L(x1, y1, x3, y3)"]),
]

SPEC = (spec_input_reals("координаты точки P1 (x1 y1)", ["x1", "y1"], 2)
        + spec_input_reals("координаты точки P2 (x2 y2)", ["x2", "y2"], 2)
        + spec_input_reals("координаты точки P3 (x3 y3)", ["x3", "y3"], 2)
        + [("box", ["|P1P2| = <<d1>>, |P2P3| = <<d2>>, |P1P3| = <<d3>>", "P = <<P>>"], False)])

PSEUDO = f"""
_функция_ L(x1, y1, x2, y2)
_нач_
	_возврат_ √((x1 − x2)² + (y1 − y2)²)
_кон_

{alg("I", 5)}
_нач_
	ввод(x1, y1, x2, y2, x3, y3)
	d1 := L(x1, y1, x2, y2); d2 := L(x2, y2, x3, y3); d3 := L(x1, y1, x3, y3)
	P := d1 + d2 + d3
	вывод(«|P1P2| = », d1, «, |P2P3| = », d2, «, |P1P3| = », d3)
	вывод(«P = », P)
_кон_
"""

TESTS = [
    T(["0 0", "3 0", "0 4"], ["P1(0, 0), P2(3, 0), P3(0, 4)"], "Египетский треугольник 3–4–5, P = 12"),
    T(["-1.5 2", "2.5 -1", "4 3"], ["P1(−1.5, 2), P2(2.5, −1), P3(4, 3)"], "Вещественные координаты"),
    T(["2 2", "2 2", "2 2"], ["P1 = P2 = P3 = (2, 2)"], "Все вершины совпадают – P = 0"),
    T(["0", "0 0 0", "q 1", "0 0", "3 0", "0 4"], ["P1: 0 / 0 0 0 / q 1 / 0 0", "P2: 3 0", "P3: 0 4"],
      "Недопустимые данные: мало и много чисел, строка"),
]

TASK = Task(
    lab=3, part="I", num=5,
    statement="Вычислить периметр треугольника с вершинами в точках P1(x1, y1), P2(x2, y2), P3(x3, y3). "
              "Использовать для вычисления длин сторон треугольника формулу: "
              "L(x1, y1, x2, y2) = √((x1 − x2)² + (y1 − y2)²).",
    includes=["stdlib.h", "math.h"], defines=RMAX_DEFINE,
    functions=FUNCS, decls="    double x[3], y[3], d[3], p;\n", body=BODY, simulate=simulate,
    given=["x1, y1, x2, y2, x3, y3 – координаты вершин треугольника P1, P2, P3."],
    result=["|P1P2|, |P2P3|, |P1P3| – длины сторон; P – периметр треугольника (с 4 знаками после запятой)."],
    when=[f"xi, yi ∈ R, |xi|, |yi| ≤ RMAX = {RMAX}."],
    svyaz=svyaz, method=METHOD, spec=SPEC, pseudo=PSEUDO, tests=TESTS, formulas=formulas,
    note="В программе координаты хранятся в массивах x[0:2], y[0:2], длины сторон – в d[0:2].",
    file="lab3_part1.c", lead='Вычислить периметр треугольника с вершинами в точках P1(x1, y1), P2(x2, y2), P3(x3, y3).',
)
