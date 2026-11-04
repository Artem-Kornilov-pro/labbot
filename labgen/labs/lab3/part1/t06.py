import math

from ...core.task import Task
from ...core.cio import py_input_int, py_input_reals, spec_input_int, spec_input_reals
from ...core.omml import m, frac, sup, supx, sub, subx
from ..shared import helpers, T, alg
from . import REMARK

NMAX = 50

FUNCS = helpers(reals=True) + r'''
/* Общая часть формулы - факториал x! (вызывается три раза) */
double fact(int x){
    double f = 1;
    int i;
    for (i = 2; i <= x; i++)
        f = f * i;
    return f;
}

/* Ввод исходных данных. Возвращает 0 при конце ввода. */
int input(int *n, int *k, double *p){
    int ok;
    if (!input_int("n", 1, NMAX, n)) return 0;
    if (!input_int("k", 1, *n, k)) return 0;
    do{
        if (!input_reals("вероятность p (0 <= p < 1)", 1, 0, 1, p)) return 0;
        ok = *p < 1;
        if (!ok) printf("Ошибка! Нужно 0 <= p < 1.\n");
    } while (!ok);
    return 1;
}

/* Вероятность Pn(k) = n! / (k! (n - k)!) * p^k * (1 - p)^(n - k) */
double compute(int n, int k, double p){
    return fact(n) / (fact(k) * fact(n - k)) * pow(p, k) * pow(1 - p, n - k);
}

/* Вывод результата */
void output(int n, int k, double r){
    printf("\nP%d(%d) = %.6g\n", n, k, r);
}
'''

BODY = '''    if (!input(&n, &k, &p)) return 1;
    r = compute(n, k, p);
    output(n, k, r);
'''


def fact(x):
    f = 1.0
    for i in range(2, x + 1):
        f = f * i
    return f


def simulate(con):
    n = py_input_int(con, "n", 1, NMAX)
    k = py_input_int(con, "k", 1, n)
    while True:
        p = py_input_reals(con, "вероятность p (0 <= p < 1)", 1, 0, 1)[0]
        if p < 1:
            break
        con.printf("Ошибка! Нужно 0 <= p < 1.\n")
    con.begin_results()
    r = fact(n) / (fact(k) * fact(n - k)) * math.pow(p, k) * math.pow(1 - p, n - k)
    con.printf("\nP%d(%d) = %.6g\n" % (n, k, r))


def formula():
    return (subx(m("P"), m("n")) + m("(k) = ") + frac(m("n!"), m("k!(n − k)!")) + m(" · ") + sup("p", "k")
            + m(" · ") + supx(m("(1 − p)"), m("n − k")))


def formulas(rep):
    rep.math_block(formula() + m(",   при  0 ≤ p < 1,  k ∈ N,  n ≥ k."), rows=2)
    rep.para(REMARK, after=4)


def svyaz(rep):
    rep.fline("", formula())
    rep.para("(формула Бернулли: вероятность ровно k успехов в n независимых испытаниях с вероятностью "
             "успеха p).", after=4)


METHOD = [
    ("Общая часть формулы – факториал – оформляется функцией fact(x), которая вызывается три раза (для n, k и "
     "n − k); факториал вычисляется в типе double:",
     ["f = 1", ["для i = {2..x}", "f = f · i"], "fact(x) = f"]),
    ("Вычисление вероятности:", ["P = fact(n) / (fact(k) · fact(n − k)) · p^k · (1 − p)^(n − k)"]),
]

SPEC = (spec_input_int("n", 1, "NMAX") + spec_input_int("k", 1, "n")
        + spec_input_reals("вероятность p (0 <= p < 1)", ["p"], 1, lo="0", hi="1",
                           extra=("При p = 1", "Ошибка! Нужно 0 <= p < 1."))
        + [("box", ["P<<n>>(<<k>>) = <<P>>"], False)])

PSEUDO = f"""
_функция_ fact(x)
_нач_
	f := 1
	_цикл от_ i := 2 _до_ x
		f := f · i
	_кц_
	_возврат_ f
_кон_

{alg("I", 6)}
_нач_
	ввод(n, k, p)
	P := fact(n) / (fact(k) · fact(n − k)) · p^k · (1 − p)^(n − k)
	вывод(«P», n, «(», k, «) = », P)
_кон_
"""

TESTS = [
    T(["5", "2", "0.5"], ["n = 5, k = 2, p = 0.5"], "Обычный случай: 10 · 0.5² · 0.5³ = 0.3125"),
    T(["10", "3", "0.2"], ["n = 10, k = 3, p = 0.2"], "Вероятность p ≠ 0.5"),
    T(["50", "50", "0.9"], ["n = 50, k = 50, p = 0.9"], "Граничный случай k = n = NMAX"),
    T(["0", "4", "0", "5", "1", "1.5", "0,3", "0.3"], ["n: 0 / 4", "k: 0 / 5 / 1", "p: 1.5 / 0,3 / 0.3"],
      "Недопустимые данные: n = 0, k вне [1; n], p вне [0; 1), запятая; затем p = 0.3"),
]

TASK = Task(
    lab=3, part="I", num=6,
    statement="Вычислить значение по формуле: Pn(k) = n! / (k!(n − k)!) · p^k · (1 − p)^(n − k), при 0 ≤ p < 1, "
              "k ∈ N, n ≥ k.",
    includes=["stdlib.h", "math.h"], defines=f"#define NMAX {NMAX}       /* наибольшее n */",
    functions=FUNCS, decls="    int n, k;\n    double p, r;\n", body=BODY, simulate=simulate,
    given=["n, k – целые числа; p – вещественное число."],
    result=["Pn(k) – значение по формуле (6 значащих цифр)."],
    when=[f"n ∈ N, n ≤ NMAX = {NMAX}; k ∈ N, k ≤ n; p ∈ R, 0 ≤ p < 1."],
    svyaz=svyaz, method=METHOD, spec=SPEC, pseudo=PSEUDO, tests=TESTS, formulas=formulas,
    file="lab3_part1.c", lead='Вычислить значение по формуле:',
)
