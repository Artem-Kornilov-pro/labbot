import math

from ...core.task import Task
from ...core.cio import py_input_int, spec_input_int
from ...core.omml import m, nsum
from ..shared import helpers, T, alg
from . import REMARK

MMAX = 1000

FUNCS = helpers() + r'''
/* Общая часть формулы - ln(k!) = ln(1) + ln(2) + ... + ln(k) (вызывается три раза) */
double lnfact(int k){
    double s = 0;
    int i;
    for (i = 2; i <= k; i++)
        s = s + log(i);
    return s;
}

/* Ввод исходных данных. Возвращает 0 при конце ввода. */
int input(int *m, int *n){
    if (!input_int("m", 0, MMAX, m)) return 0;
    return input_int("n", 0, *m, n);
}

/* Вычисление a = exp(ln(m!) - ln(n!) - ln((m - n)!)) */
double compute(int m, int n){
    return exp(lnfact(m) - lnfact(n) - lnfact(m - n));
}

/* Вывод результата */
void output(int m, int n, double a){
    printf("\na = exp(ln(%d!) - ln(%d!) - ln(%d!)) = %.10g\n", m, n, m - n, a);
}
'''

BODY = '''    if (!input(&m, &n)) return 1;
    a = compute(m, n);
    output(m, n, a);
'''


def lnfact(k):
    s = 0.0
    for i in range(2, k + 1):
        s = s + math.log(float(i))
    return s


def simulate(con):
    mm = py_input_int(con, "m", 0, MMAX)
    n = py_input_int(con, "n", 0, mm)
    con.begin_results()
    a = math.exp(lnfact(mm) - lnfact(n) - lnfact(mm - n))
    con.printf("\na = exp(ln(%d!) - ln(%d!) - ln(%d!)) = %.10g\n" % (mm, n, mm - n, a))


def formulas(rep):
    rep.math_block(m("a = exp(ln(m!) − ln(n!) − ln((m − n)!)),"))
    rep.math_block(m("где  ln(ab) = ln(a) + ln(b),   ln(k!) = ") + nsum(m("i=1"), m("k"), m("ln(i)")) + m("."),
                   rows=2)
    rep.para(REMARK, after=4)


def svyaz(rep):
    rep.fline("", m("a = exp(L(m) − L(n) − L(m − n)),  где  L(k) = ln(k!) = ") + nsum(m("i=1"), m("k"), m("ln(i)")))
    rep.para("(по свойству ln(ab) = ln(a) + ln(b) логарифм факториала – сумма логарифмов сомножителей; "
             "a равно числу сочетаний m! / (n! · (m − n)!), но факториалы не вычисляются, поэтому m может "
             "быть большим).", align=None, after=4)


METHOD = [
    ("Общая часть формулы – логарифм факториала – оформляется функцией lnfact(k), которая вызывается три раза "
     "(для m, n и m − n):",
     ["s = 0", ["для i = {2..k}", "s = s + ln(i)"], "lnfact(k) = s"]),
    ("Вычисление результата:", ["a = exp(lnfact(m) − lnfact(n) − lnfact(m − n))"]),
]

SPEC = (spec_input_int("m", 0, "MMAX") + spec_input_int("n", 0, "m")
        + [("box", ["a = exp(ln(<<m>>!) - ln(<<n>>!) - ln(<<m − n>>!)) = <<a>>"], False)])

PSEUDO = f"""
_функция_ lnfact(k)
_нач_
	s := 0
	_цикл от_ i := 2 _до_ k
		s := s + ln(i)
	_кц_
	_возврат_ s
_кон_

{alg("I", 2)}
_нач_
	ввод(m, n)
	a := exp(lnfact(m) − lnfact(n) − lnfact(m − n))
	вывод(«a = », a)
_кон_
"""

TESTS = [
    T(["5", "2"], ["m = 5", "n = 2"], "Обычный случай (5! / (2! · 3!) = 10)"),
    T(["1000", "500"], ["m = 1000", "n = 500"], "Большое m: факториалы не вычисляются, только их логарифмы"),
    T(["10", "0"], ["m = 10", "n = 0"], "Граничный случай n = 0 (ln(0!) = 0)"),
    T(["x", "1001", "7.5", "8", "9", "-1", "3"], ["m: x / 1001 / 7.5 / 8", "n: 9 / −1 / 3"],
      "Недопустимые данные: строка, вне диапазона, вещественное число, n > m"),
]

TASK = Task(
    lab=3, part="I", num=2,
    statement="Вычислить значение a = exp(ln(m!) − ln(n!) − ln((m − n)!)), где ln(ab) = ln(a) + ln(b), "
              "ln(k!) = ln(1) + ln(2) + … + ln(k).",
    includes=["math.h"], defines=f"#define MMAX {MMAX}     /* наибольшее m */",
    functions=FUNCS, decls="    int m, n;\n    double a;\n", body=BODY, simulate=simulate,
    given=["m, n – целые числа."],
    result=["a – значение по формуле (выводится с 10 значащими цифрами)."],
    when=[f"m ∈ Z, 0 ≤ m ≤ MMAX = {MMAX}; n ∈ Z, 0 ≤ n ≤ m."],
    svyaz=svyaz, method=METHOD, spec=SPEC, pseudo=PSEUDO, tests=TESTS, formulas=formulas,
    file="lab3_part1.c", lead='',
)
