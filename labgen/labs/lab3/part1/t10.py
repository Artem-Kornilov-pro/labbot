import math

from ...core.task import Task
from ...core.cio import py_input_int, py_input_reals, spec_input_int, spec_input_reals, RMAX
from ...core.omml import m, frac, rad, sup, sub, nsum
from ..shared import helpers, T, alg, RMAX_DEFINE
from . import REMARK

NMAX = 20

FUNCS = helpers(reals=True) + r'''
/* Общая часть формул - среднее арифметическое n чисел x[0:n-1]
   (вызывается два раза: для чисел a[i] и для квадратов отклонений (a[i] - S)^2) */
double mean(const double x[], int n){
    double s = 0;
    int i;
    for (i = 0; i < n; i++)
        s = s + x[i];
    return s / n;
}

/* Ввод количества чисел и самих чисел. Возвращает 0 при конце ввода. */
int input(double a[], int *n){
    if (!input_int("количество чисел n", 1, NMAX, n)) return 0;
    return input_reals("числа a1 ... an через пробел", *n, -RMAX, RMAX, a);
}

/* Вычисление среднего S и среднеквадратичного отклонения sigma */
void compute(const double a[], int n, double *S, double *sigma){
    double d[NMAX];
    int i;
    *S = mean(a, n);
    for (i = 0; i < n; i++)
        d[i] = (a[i] - *S) * (a[i] - *S);
    *sigma = sqrt(mean(d, n));
}

/* Вывод результатов */
void output(double S, double sigma){
    printf("\nS = %.4f\nsigma = %.4f\n", S, sigma);
}
'''

BODY = '''    if (!input(a, &n)) return 1;
    compute(a, n, &S, &sigma);
    output(S, sigma);
'''


def mean(x):
    s = 0.0
    for v in x:
        s = s + v
    return s / len(x)


def simulate(con):
    n = py_input_int(con, "количество чисел n", 1, NMAX)
    a = py_input_reals(con, "числа a1 ... an через пробел", n, -RMAX, RMAX)
    con.begin_results()
    S = mean(a)
    sigma = math.sqrt(mean([(v - S) * (v - S) for v in a]))
    con.printf("\nS = %.4f\nsigma = %.4f\n" % (S, sigma))


def formula_s():
    return m("S = ") + frac(sub("a", "1") + m(" + ") + sub("a", "2") + m(" + … + ") + sub("a", "n"), m("n"))


def formula_sigma():
    return m("σ = ") + rad(frac(sup("(a1 − S)", "2") + m(" + ") + sup("(a2 − S)", "2") + m(" + ⋯ + ")
                                + sup("(an − S)", "2"), m("n")))


def formulas(rep):
    rep.math_block(formula_s() + m(";"), rows=2)
    rep.math_block(formula_sigma() + m("."), rows=2)
    rep.para(REMARK, after=4)


def svyaz(rep):
    rep.fline("", m("S = mean(a) = ") + frac(m("1"), m("n")) + nsum(m("i=1"), m("n"), sub("a", "i"))
              + m(",   σ = ") + rad(frac(m("1"), m("n")) + nsum(m("i=1"), m("n"), sup("(ai − S)", "2"))))


METHOD = [
    ("Общая часть формул – среднее арифметическое – оформляется функцией mean(x, n), которая вызывается два "
     "раза: для исходных чисел и для квадратов их отклонений от среднего:",
     ["s = 0", ["для i = {1..n}", "s = s + x[i]"], "mean(x, n) = s / n"]),
    ("Вычисление результатов:",
     ["S = mean(a, n)", ["для i = {1..n}", "d[i] = (a[i] − S)²"], "σ = √mean(d, n)"]),
]

SPEC = (spec_input_int("количество чисел n", 1, "NMAX", "n")
        + spec_input_reals("числа a1 ... an через пробел", ["a1", "a2", "…", "an"], "n")
        + [("box", ["S = <<S>>", "sigma = <<σ>>"], False)])

PSEUDO = f"""
_функция_ mean(x[1:n], n)
_нач_
	s := 0
	_цикл от_ i := 1 _до_ n
		s := s + x[i]
	_кц_
	_возврат_ s / n
_кон_

{alg("I", 10)}
_нач_
	ввод(n, a[1:n])
	S := mean(a, n)
	_цикл от_ i := 1 _до_ n
		d[i] := (a[i] − S)²
	_кц_
	σ := √mean(d, n)
	вывод(«S = », S, «sigma = », σ)
_кон_
"""

TESTS = [
    T(["8", "2 4 4 4 5 5 7 9"], ["n = 8", "a = 2 4 4 4 5 5 7 9"], "Обычный случай: S = 5, σ = 2"),
    T(["5", "-1.5 0 2.25 10 -3"], ["n = 5", "a = −1.5 0 2.25 10 −3"], "Отрицательные и вещественные числа"),
    T(["1", "7.5"], ["n = 1", "a = 7.5"], "Одно число – σ = 0"),
    T(["21", "2.5", "3", "1 2", "1 2 x", "1 2 3"], ["n: 21 / 2.5 / 3", "a: 1 2 / 1 2 x / 1 2 3"],
      "Недопустимые данные: n вне диапазона и вещественное, мало чисел, строка"),
]

TASK = Task(
    lab=3, part="I", num=10,
    statement="Вычислить значения по формулам: S = (a1 + a2 + … + an) / n; "
              "σ = √(((a1 − S)² + (a2 − S)² + ⋯ + (an − S)²) / n).",
    includes=["stdlib.h", "math.h"],
    defines=f"{RMAX_DEFINE}\n#define NMAX {NMAX}       /* наибольшее количество чисел */",
    functions=FUNCS, decls="    double a[NMAX], S, sigma;\n    int n;\n", body=BODY, simulate=simulate,
    given=["n – количество чисел; a1, a2, …, an – числа."],
    result=["S – среднее арифметическое, σ – среднеквадратичное отклонение (с 4 знаками после запятой)."],
    when=[f"n ∈ N, n ≤ NMAX = {NMAX}; ai ∈ R, |ai| ≤ RMAX = {RMAX}."],
    svyaz=svyaz, method=METHOD, spec=SPEC, pseudo=PSEUDO, tests=TESTS, formulas=formulas,
    note="В программе числа хранятся в массиве a[0:n−1].",
    file="lab3_part1.c", lead='Вычислить значения по формулам:',
)
