from ...core.task import Task
from ...core.cio import py_input_reals, spec_input_reals, RMAX
from ...core.omml import m, frac, par
from ..shared import helpers, T, alg, RMAX_DEFINE
from . import REMARK

FUNCS = helpers(ints=False, reals=True) + r'''
/* Общая часть формул - u - d*v/a (вызывается два раза: f - dc/a и e - db/a) */
double g(double u, double v, double a, double d){
    return u - d * v / a;
}

/* Ввод коэффициентов q[0:5] = a, b, c, d, e, f. Возвращает 0 при конце ввода. */
int input(double q[]){
    if (!input_reals("a b c (уравнение a*x + b*y = c)", 3, -RMAX, RMAX, q)) return 0;
    return input_reals("d e f (уравнение d*x + e*y = f)", 3, -RMAX, RMAX, q + 3);
}

/* Вычисление x, y по формулам. Возвращает 1 - успешно, 0 - a = 0, -1 - e - db/a = 0 */
int compute(const double q[], double *x, double *y){
    double a = q[0], b = q[1], c = q[2], d = q[3], e = q[4], f = q[5], p, r;
    if (a == 0) return 0;
    p = g(f, c, a, d);             /* f - dc/a */
    r = g(e, b, a, d);             /* e - db/a */
    if (r == 0) return -1;
    *x = c / a - b * p / (a * r);
    *y = p / r;
    return 1;
}

/* Вывод результатов */
void output(int res, double x, double y){
    if (res == 0)
        printf("\na = 0: формулы неприменимы (деление на a).\n");
    else if (res == -1)
        printf("\ne - db/a = 0: формулы неприменимы - "
               "система не имеет единственного решения.\n");
    else
        printf("\nx = %.4f\ny = %.4f\n", x, y);
}
'''

BODY = '''    if (!input(q)) return 1;
    res = compute(q, &x, &y);
    output(res, x, y);
'''


def g(u, v, a, d):
    return u - d * v / a


def simulate(con):
    q = py_input_reals(con, "a b c (уравнение a*x + b*y = c)", 3, -RMAX, RMAX)
    q += py_input_reals(con, "d e f (уравнение d*x + e*y = f)", 3, -RMAX, RMAX)
    con.begin_results()
    a, b, c, d, e, f = q
    if a == 0:
        con.printf("\na = 0: формулы неприменимы (деление на a).\n")
        return
    p, r = g(f, c, a, d), g(e, b, a, d)
    if r == 0:
        con.printf("\ne - db/a = 0: формулы неприменимы - система не имеет единственного решения.\n")
        return
    con.printf("\nx = %.4f\ny = %.4f\n" % (c / a - b * p / (a * r), p / r))


def _p():
    return par(m("f − ") + frac(m("dc"), m("a")))


def _r():
    return par(m("e − ") + frac(m("db"), m("a")))


def formula():
    return (m("x = ") + frac(m("c"), m("a")) + m(" − ") + frac(m("b") + _p(), m("a") + _r()) + m(";    y = ")
            + frac(m("f − ") + frac(m("dc"), m("a")), m("e − ") + frac(m("db"), m("a"))))


def formulas(rep):
    rep.math_block(formula() + m("."), rows=3)
    rep.para(REMARK, after=4)


def svyaz(rep):
    rep.math_block(formula() + m(",   a ≠ 0,  e − db/a ≠ 0"), rows=3)
    rep.para("(решение системы ax + by = c, dx + ey = f методом исключения неизвестного).", after=4)


METHOD = [
    ("Общая часть формул – выражение вида u − d·v/a – оформляется функцией g(u, v, a, d), которая вызывается "
     "два раза (для f − dc/a и e − db/a):", ["g(u, v, a, d) = u − d · v / a"]),
    ("Вычисление решения (при a = 0 или e − db/a = 0 формулы неприменимы):",
     ["p = g(f, c, a, d);   r = g(e, b, a, d),  если  a ≠ 0",
      "x = c / a − b · p / (a · r);   y = p / r,  если  r ≠ 0"]),
]

SPEC = (spec_input_reals("a b c (уравнение a*x + b*y = c)", ["a", "b", "c"], 3)
        + spec_input_reals("d e f (уравнение d*x + e*y = f)", ["d", "e", "f"], 3)
        + [("label", "При a = 0"), ("box", ["a = 0: формулы неприменимы (деление на a)."], True),
           ("label", "При e − db/a = 0"),
           ("box", ["e - db/a = 0: формулы неприменимы - система не имеет единственного решения."], True),
           ("label", "Иначе"), ("box", ["x = <<x>>", "y = <<y>>"], True)])

PSEUDO = f"""
_функция_ g(u, v, a, d)
_нач_
	_возврат_ u − d · v / a
_кон_

{alg("I", 9)}
_нач_
	ввод(a, b, c, d, e, f)
	_если_ a = 0 _то_
		вывод(«a = 0: формулы неприменимы (деление на a).»)
	_иначе_
		p := g(f, c, a, d); r := g(e, b, a, d)
		_если_ r = 0 _то_
			вывод(«e - db/a = 0: формулы неприменимы - система не имеет единственного решения.»)
		_иначе_
			x := c / a − b · p / (a · r); y := p / r
			вывод(«x = », x, «y = », y)
		_всё_
	_всё_
_кон_
"""

TESTS = [
    T(["2 1 5", "1 -1 1"], ["2x + y = 5", "x − y = 1"], "Обычный случай: x = 2, y = 1"),
    T(["0.5 1.5 4", "3 -2 -1"], ["0.5x + 1.5y = 4", "3x − 2y = −1"], "Вещественные коэффициенты"),
    T(["0 1 2", "3 4 5"], ["0x + y = 2", "3x + 4y = 5"], "a = 0 – формулы неприменимы"),
    T(["1 2 3", "2 4 6"], ["x + 2y = 3", "2x + 4y = 6"], "e − db/a = 0 – единственного решения нет"),
    T(["2.5.1 1 1", "1 1 2", "1 -1 0"], ["1-е: 2.5.1 1 1 / 1 1 2", "2-е: 1 −1 0"],
      "Недопустимые данные (две точки в числе); затем x + y = 2, x − y = 0"),
]

TASK = Task(
    lab=3, part="I", num=9,
    statement="Вычислить значения по формулам: x = c/a − b(f − dc/a) / (a(e − db/a)); "
              "y = (f − dc/a) / (e − db/a).",
    includes=["stdlib.h"], defines=RMAX_DEFINE,
    functions=FUNCS, decls="    double q[6], x = 0, y = 0;\n    int res;\n", body=BODY, simulate=simulate,
    given=["a, b, c, d, e, f – коэффициенты системы ax + by = c, dx + ey = f."],
    result=["x, y – значения по формулам (с 4 знаками после запятой) или сообщение, почему формулы неприменимы."],
    when=[f"a, b, c, d, e, f ∈ R, модуль каждого ≤ RMAX = {RMAX}."],
    svyaz=svyaz, method=METHOD, spec=SPEC, pseudo=PSEUDO, tests=TESTS, formulas=formulas,
    note="В программе коэффициенты хранятся в массиве q[0:5] = (a, b, c, d, e, f).",
    file="lab3_part1.c", lead='Вычислить значения по формулам:',
)
