from ...core.task import Task
from ...core.cio import py_input_reals, spec_input_reals, RMAX
from ...core.omml import m, frac
from ..shared import helpers, T, alg, RMAX_DEFINE
from . import REMARK

FUNCS = helpers(ints=False, reals=True) + r'''
/* Общая часть - определитель |p q; r s| = p*s - q*r; вызывается три раза */
double det(double p, double q, double r, double s){
    return p * s - q * r;
}

/* Ввод коэффициентов q[0:5] = a, b, c, d, e, f. Возвращает 0 при конце ввода. */
int input(double q[]){
    if (!input_reals("a b c (уравнение a*x + b*y = c)", 3, -RMAX, RMAX, q)) return 0;
    return input_reals("d e f (уравнение d*x + e*y = f)", 3, -RMAX, RMAX, q + 3);
}

/* x = (ce - bf) / (ae - bd), y = (af - cd) / (ae - bd); 0 - если ae - bd = 0 */
int compute(const double q[], double *x, double *y){
    double a = q[0], b = q[1], c = q[2], d = q[3], e = q[4], f = q[5];
    double D = det(a, b, d, e);
    if (D == 0) return 0;
    *x = det(c, b, f, e) / D;
    *y = det(a, c, d, f) / D;
    return 1;
}

/* Вывод результатов */
void output(int ok, double x, double y){
    if (!ok)
        printf("\nae - bd = 0: формулы неприменимы - "
               "система не имеет единственного решения.\n");
    else
        printf("\nx = %.4f\ny = %.4f\n", x, y);
}
'''

BODY = '''    if (!input(q)) return 1;
    ok = compute(q, &x, &y);
    output(ok, x, y);
'''


def det(p, q, r, s):
    return p * s - q * r


def simulate(con):
    q = py_input_reals(con, "a b c (уравнение a*x + b*y = c)", 3, -RMAX, RMAX)
    q += py_input_reals(con, "d e f (уравнение d*x + e*y = f)", 3, -RMAX, RMAX)
    con.begin_results()
    a, b, c, d, e, f = q
    D = det(a, b, d, e)
    if D == 0:
        con.printf("\nae - bd = 0: формулы неприменимы - система не имеет единственного решения.\n")
    else:
        con.printf("\nx = %.4f\ny = %.4f\n" % (det(c, b, f, e) / D, det(a, c, d, f) / D))


def formula():
    return (m("x = ") + frac(m("ce − bf"), m("ae − bd")) + m(";    y = ") + frac(m("af − cd"), m("ae − bd")))


def formulas(rep):
    rep.math_block(formula() + m("."), rows=2)
    rep.para(REMARK, after=4)


def svyaz(rep):
    rep.fline("", formula() + m(",   ae − bd ≠ 0"))
    rep.para("(решение системы ax + by = c, dx + ey = f по правилу Крамера).", after=4)


METHOD = [
    ("Общая часть формул – определитель второго порядка – оформляется функцией det(p, q, r, s), которая "
     "вызывается три раза:", ["det(p, q, r, s) = p · s − q · r"]),
    ("Вычисление определителей и решения (при D = 0 решение по формулам не существует):",
     ["D = det(a, b, d, e)  (= ae − bd)", "x = det(c, b, f, e) / D,   y = det(a, c, d, f) / D,  если  D ≠ 0"]),
]

SPEC = (spec_input_reals("a b c (уравнение a*x + b*y = c)", ["a", "b", "c"], 3)
        + spec_input_reals("d e f (уравнение d*x + e*y = f)", ["d", "e", "f"], 3)
        + [("label", "При ae − bd = 0"),
           ("box", ["ae - bd = 0: формулы неприменимы - система не имеет единственного решения."], True),
           ("label", "Иначе"), ("box", ["x = <<x>>", "y = <<y>>"], True)])

PSEUDO = f"""
_функция_ det(p, q, r, s)
_нач_
	_возврат_ p · s − q · r
_кон_

{alg("I", 8)}
_нач_
	ввод(a, b, c, d, e, f)
	D := det(a, b, d, e)
	_если_ D = 0 _то_
		вывод(«ae - bd = 0: формулы неприменимы - система не имеет единственного решения.»)
	_иначе_
		x := det(c, b, f, e) / D; y := det(a, c, d, f) / D
		вывод(«x = », x, «y = », y)
	_всё_
_кон_
"""

TESTS = [
    T(["2 1 5", "1 -1 1"], ["2x + y = 5", "x − y = 1"], "Обычный случай: x = 2, y = 1"),
    T(["0.5 1.5 4", "3 -2 -1"], ["0.5x + 1.5y = 4", "3x − 2y = −1"], "Вещественные коэффициенты"),
    T(["1 2 3", "2 4 6"], ["x + 2y = 3", "2x + 4y = 6"], "ae − bd = 0 – единственного решения нет"),
    T(["1 2", "a 2 3", "1 2 3 4", "1 1 2", "1 -1 0"], ["1-е: 1 2 / a 2 3 / 1 2 3 4 / 1 1 2", "2-е: 1 −1 0"],
      "Недопустимые данные: мало чисел, строка, много чисел; затем x + y = 2, x − y = 0"),
]

TASK = Task(
    lab=3, part="I", num=8,
    statement="Вычислить значения по формулам: x = (ce − bf) / (ae − bd); y = (af − cd) / (ae − bd).",
    includes=["stdlib.h"], defines=RMAX_DEFINE,
    functions=FUNCS, decls="    double q[6], x = 0, y = 0;\n    int ok;\n", body=BODY, simulate=simulate,
    given=["a, b, c, d, e, f – коэффициенты системы ax + by = c, dx + ey = f."],
    result=["x, y – значения по формулам (с 4 знаками после запятой) или сообщение, что ae − bd = 0."],
    when=[f"a, b, c, d, e, f ∈ R, модуль каждого ≤ RMAX = {RMAX}."],
    svyaz=svyaz, method=METHOD, spec=SPEC, pseudo=PSEUDO, tests=TESTS, formulas=formulas,
    note="В программе коэффициенты хранятся в массиве q[0:5] = (a, b, c, d, e, f).",
    file="lab3_part1.c", lead='Вычислить значения по формулам:',
)
