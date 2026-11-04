from ...core.task import Task
from ...core.cio import py_input_int, spec_input_int
from ...core.omml import m, frac
from ..shared import helpers, T, alg
from . import REMARK

NMAX = 20

FUNCS = helpers() + r'''
/* Общая часть формулы - факториал x! (вызывается три раза) */
long long fact(int x){
    long long f = 1;
    int i;
    for (i = 2; i <= x; i++)
        f = f * i;
    return f;
}

/* Ввод исходных данных. Возвращает 0 при конце ввода. */
int input(int *n, int *k){
    if (!input_int("n", 0, NMAX, n)) return 0;
    return input_int("k", 0, *n, k);
}

/* Вычисление a = n! / (k! * (n - k)!) */
long long compute(int n, int k){
    return fact(n) / (fact(k) * fact(n - k));
}

/* Вывод результата */
void output(int n, int k, long long a){
    printf("\na = %d! / (%d! * %d!) = %lld\n", n, k, n - k, a);
}
'''

BODY = '''    if (!input(&n, &k)) return 1;
    a = compute(n, k);
    output(n, k, a);
'''


def fact(x):
    f = 1
    for i in range(2, x + 1):
        f *= i
    return f


def simulate(con):
    n = py_input_int(con, "n", 0, NMAX)
    k = py_input_int(con, "k", 0, n)
    con.begin_results()
    con.printf("\na = %d! / (%d! * %d!) = %d\n" % (n, k, n - k, fact(n) // (fact(k) * fact(n - k))))


def formula():
    return m("a = ") + frac(m("n!"), m("k! · (n − k)!"))


def formulas(rep):
    rep.math_block(formula(), rows=2)
    rep.para(REMARK, align=None, after=4)


def svyaz(rep):
    rep.fline("", formula() + m(",  где  x! = 1 · 2 · … · x,  0! = 1"))


METHOD = [
    ("Общая часть формулы – факториал – оформляется функцией fact(x), которая вызывается три раза "
     "(для n, k и n − k):",
     ["f = 1", ["для i = {2..x}", "f = f · i"], "fact(x) = f"]),
    ("Вычисление результата (деление нацело: число сочетаний – целое):",
     ["a = fact(n) / (fact(k) · fact(n − k))"]),
]

SPEC = (spec_input_int("n", 0, "NMAX") + spec_input_int("k", 0, "n")
        + [("box", ["a = <<n>>! / (<<k>>! * <<n − k>>!) = <<a>>"], False)])

PSEUDO = f"""
_функция_ fact(x)
_нач_
	f := 1
	_цикл от_ i := 2 _до_ x
		f := f · i
	_кц_
	_возврат_ f
_кон_

{alg("I", 1)}
_нач_
	ввод(n, k)
	a := fact(n) / (fact(k) · fact(n − k))
	вывод(«a = », n, «! / (», k, «! * », n − k, «!) = », a)
_кон_
"""

TESTS = [
    T(["5", "2"], ["n = 5", "k = 2"], "Обычный случай"),
    T(["20", "10"], ["n = 20", "k = 10"], "Наибольшее n (20! помещается в long long)"),
    T(["6", "0"], ["n = 6", "k = 0"], "Граничный случай k = 0 (0! = 1)"),
    T(["abc", "21", "4.5", "6", "7", "2,5", "3"], ["n: abc / 21 / 4.5 / 6", "k: 7 / 2,5 / 3"],
      "Недопустимые данные: строка, вне диапазона, вещественное число, k > n"),
]

TASK = Task(
    lab=3, part="I", num=1,
    statement="Вычислить значение a = n! / (k! · (n − k)!).",
    includes=[], defines=f"#define NMAX {NMAX}       /* наибольшее n: 20! помещается в long long */",
    functions=FUNCS, decls="    int n, k;\n    long long a;\n", body=BODY, simulate=simulate,
    given=["n, k – целые числа."],
    result=["a – значение по формуле (число сочетаний из n по k)."],
    when=[f"n ∈ Z, 0 ≤ n ≤ NMAX = {NMAX} (20! – наибольший факториал, помещающийся в тип long long);",
          "k ∈ Z, 0 ≤ k ≤ n."],
    svyaz=svyaz, method=METHOD, spec=SPEC, pseudo=PSEUDO, tests=TESTS, formulas=formulas,
    file="lab3_part1.c", lead='',
)
