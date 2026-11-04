from ...core.task import Task
from ...core.cio import py_input_int, spec_input_int
from ...core.omml import m, frac, sup
from ..shared import helpers, T, alg
from . import REMARK

KMAX = 9

FUNCS = helpers() + r'''
/* Общая часть формулы - факториал x! (вызывается два раза) */
long long fact(int x){
    long long f = 1;
    int i;
    for (i = 2; i <= x; i++)
        f = f * i;
    return f;
}

/* Ввод исходных данных. Возвращает 0 при конце ввода. */
int input(int *k){
    return input_int("k", 0, KMAX, k);
}

/* f(k) = (2k + 1)!! = (2k + 1)! / (2^k * k!) */
long long compute(int k){
    long long p2 = 1;
    int i;
    for (i = 1; i <= k; i++)
        p2 = p2 * 2;
    return fact(2 * k + 1) / (p2 * fact(k));
}

/* Вывод результата */
void output(int k, long long f){
    printf("\nf(%d) = %d!! = %d! / (2^%d * %d!) = %lld\n",
           k, 2 * k + 1, 2 * k + 1, k, k, f);
}
'''

BODY = '''    if (!input(&k)) return 1;
    f = compute(k);
    output(k, f);
'''


def fact(x):
    f = 1
    for i in range(2, x + 1):
        f *= i
    return f


def simulate(con):
    k = py_input_int(con, "k", 0, KMAX)
    con.begin_results()
    f = fact(2 * k + 1) // (2 ** k * fact(k))
    con.printf("\nf(%d) = %d!! = %d! / (2^%d * %d!) = %d\n" % (k, 2 * k + 1, 2 * k + 1, k, k, f))


def formula():
    return m("f(k) = (2k + 1)!! = ") + frac(m("(2k + 1)!"), sup("2", "k") + m(" · k!"))


def formulas(rep):
    rep.math_block(formula() + m("."), rows=2)
    rep.para(REMARK, after=4)


def svyaz(rep):
    rep.fline("", formula() + m(" = 1 · 3 · 5 · … · (2k + 1)"))


METHOD = [
    ("Общая часть формулы – факториал – оформляется функцией fact(x), которая вызывается два раза "
     "(для 2k + 1 и k):", ["f = 1", ["для i = {2..x}", "f = f · i"], "fact(x) = f"]),
    ("Вычисление степени двойки и результата (деление нацело: (2k + 1)!! – целое):",
     ["p2 = 1", ["для i = {1..k}", "p2 = p2 · 2"], "f = fact(2k + 1) / (p2 · fact(k))"]),
]

SPEC = spec_input_int("k", 0, "KMAX") + [("box", ["f(<<k>>) = <<2k + 1>>!! = <<2k + 1>>! / (2^<<k>> * <<k>>!) = "
                                                  "<<f>>"], False)]

PSEUDO = f"""
_функция_ fact(x)
_нач_
	f := 1
	_цикл от_ i := 2 _до_ x
		f := f · i
	_кц_
	_возврат_ f
_кон_

{alg("I", 7)}
_нач_
	ввод(k)
	p2 := 1
	_цикл от_ i := 1 _до_ k
		p2 := p2 · 2
	_кц_
	f := fact(2k + 1) / (p2 · fact(k))
	вывод(«f(», k, «) = », f)
_кон_
"""

TESTS = [
    T(["3"], ["k = 3"], "Обычный случай: 7!! = 1 · 3 · 5 · 7 = 105"),
    T(["9"], ["k = 9"], "Наибольшее k: 19! ещё помещается в long long"),
    T(["0"], ["k = 0"], "Граничный случай k = 0: 1!! = 1"),
    T(["три", "10", "2.0", "-1", "4"], ["k: три / 10 / 2.0 / −1 / 4"],
      "Недопустимые данные: строка, вне диапазона, вещественное число; затем k = 4"),
]

TASK = Task(
    lab=3, part="I", num=7,
    statement="Вычислить значение по формуле: f(k) = (2k + 1)!! = (2k + 1)! / (2^k · k!).",
    includes=[], defines=f"#define KMAX {KMAX}        /* наибольшее k: 19! помещается в long long */",
    functions=FUNCS, decls="    int k;\n    long long f;\n", body=BODY, simulate=simulate,
    given=["k – целое число."],
    result=["f(k) = (2k + 1)!! – произведение нечётных чисел от 1 до 2k + 1."],
    when=[f"k ∈ Z, 0 ≤ k ≤ KMAX = {KMAX} ((2k + 1)! должен помещаться в тип long long)."],
    svyaz=svyaz, method=METHOD, spec=SPEC, pseudo=PSEUDO, tests=TESTS, formulas=formulas,
    file="lab3_part1.c", lead='Вычислить значение по формуле:',
)
