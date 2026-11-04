from ...core.task import Task
from ...core.cio import py_input_reals, spec_input_reals, RMAX
from ...core.omml import m, frac, sub, absd, par
from ..shared import helpers, T, alg, RMAX_DEFINE
from . import REMARK

FUNCS = helpers(ints=False, reals=True) + r'''
/* Общая часть формулы - произведение разностей (a - b)(c - d); вызывается два раза */
double mult(double a, double b, double c, double d){
    return (a - b) * (c - d);
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

/* Площадь S = |(x1 - x3)(y2 - y3) - (x2 - x3)(y1 - y3)| / 2 */
double compute(const double x[], const double y[]){
    return fabs(mult(x[0], x[2], y[1], y[2]) - mult(x[1], x[2], y[0], y[2])) / 2;
}

/* Вывод результата */
void output(double s){
    printf("\nS = %.4f\n", s);
    if (s == 0) printf("Точки лежат на одной прямой - треугольник вырожден.\n");
}
'''

BODY = '''    if (!input(x, y)) return 1;
    s = compute(x, y);
    output(s);
'''


def mult(a, b, c, d):
    return (a - b) * (c - d)


def simulate(con):
    x, y = [], []
    for i in range(1, 4):
        p = py_input_reals(con, f"координаты точки P{i} (x{i} y{i})", 2, -RMAX, RMAX)
        x.append(p[0])
        y.append(p[1])
    con.begin_results()
    s = abs(mult(x[0], x[2], y[1], y[2]) - mult(x[1], x[2], y[0], y[2])) / 2
    con.printf("\nS = %.4f\n" % s)
    if s == 0:
        con.printf("Точки лежат на одной прямой - треугольник вырожден.\n")


def _d(a, b):
    return par(sub(a[0], a[1]) + m(" − ") + sub(b[0], b[1]))


def formula():
    return m("S = ") + frac(m("1"), m("2")) + absd(_d("x1", "x3") + _d("y2", "y3") + m(" − ")
                                                  + _d("x2", "x3") + _d("y1", "y3"))


def formulas(rep):
    rep.math_block(formula(), rows=2)
    rep.para(REMARK, after=4)


def svyaz(rep):
    rep.fline("", formula() + m(","))
    rep.fline("где  ", m("P1(x1, y1),  P2(x2, y2),  P3(x3, y3) – вершины треугольника"), indent=0.6)


METHOD = [
    ("Общая часть формулы – произведение двух разностей – оформляется функцией mult(a, b, c, d), которая "
     "вызывается два раза:", ["mult(a, b, c, d) = (a − b) · (c − d)"]),
    ("Вычисление площади:", ["S = |mult(x1, x3, y2, y3) − mult(x2, x3, y1, y3)| / 2"]),
]

SPEC = (spec_input_reals("координаты точки P1 (x1 y1)", ["x1", "y1"], 2)
        + spec_input_reals("координаты точки P2 (x2 y2)", ["x2", "y2"], 2)
        + spec_input_reals("координаты точки P3 (x3 y3)", ["x3", "y3"], 2)
        + [("box", ["S = <<S>>"], False), ("label", "При S = 0"),
           ("box", ["Точки лежат на одной прямой - треугольник вырожден."], True)])

PSEUDO = f"""
_функция_ mult(a, b, c, d)
_нач_
	_возврат_ (a − b) · (c − d)
_кон_

{alg("I", 4)}
_нач_
	ввод(x1, y1, x2, y2, x3, y3)
	S := |mult(x1, x3, y2, y3) − mult(x2, x3, y1, y3)| / 2
	вывод(«S = », S)
	_если_ S = 0 _то_
		вывод(«Точки лежат на одной прямой - треугольник вырожден.»)
	_всё_
_кон_
"""

TESTS = [
    T(["0 0", "4 0", "0 3"], ["P1(0, 0), P2(4, 0), P3(0, 3)"], "Прямоугольный треугольник (S = 4 · 3 / 2)"),
    T(["1.5 -2", "3 4.5", "-1 2"], ["P1(1.5, −2), P2(3, 4.5), P3(−1, 2)"],
      "Вещественные координаты, обход по часовой стрелке (модуль)"),
    T(["0 0", "1 1", "2 2"], ["P1(0, 0), P2(1, 1), P3(2, 2)"], "Точки на одной прямой – S = 0"),
    T(["1 x", "1", "1 2 3", "1001 0", "0 0", "4 0", "0 3,5", "0 3"],
      ["P1: 1 x / 1 / 1 2 3 / 1001 0 / 0 0", "P2: 4 0", "P3: 0 3,5 / 0 3"],
      "Недопустимые данные: строка, мало и много чисел, вне диапазона, запятая вместо точки"),
]

TASK = Task(
    lab=3, part="I", num=4,
    statement="Вычислить площадь треугольника с вершинами в точках P1(x1, y1), P2(x2, y2), P3(x3, y3) по "
              "формуле: S = ½·|(x1 − x3)(y2 − y3) − (x2 − x3)(y1 − y3)|.",
    includes=["stdlib.h", "math.h"], defines=RMAX_DEFINE,
    functions=FUNCS, decls="    double x[3], y[3], s;\n", body=BODY, simulate=simulate,
    given=["x1, y1, x2, y2, x3, y3 – координаты вершин треугольника P1, P2, P3."],
    result=["S – площадь треугольника (с 4 знаками после запятой); при S = 0 – сообщение о том, что точки "
            "лежат на одной прямой."],
    when=[f"xi, yi ∈ R, |xi|, |yi| ≤ RMAX = {RMAX}."],
    svyaz=svyaz, method=METHOD, spec=SPEC, pseudo=PSEUDO, tests=TESTS, formulas=formulas,
    note="В программе координаты хранятся в массивах x[0:2], y[0:2] (x[0] = x1, …, y[2] = y3).",
    file="lab3_part1.c", lead='Вычислить площадь треугольника с вершинами в точках P1(x1, y1), P2(x2, y2), P3(x3, y3) по формуле:',
)
