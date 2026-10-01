from ..common import Task
from ..inputs import PositiveArray
from .shared import c_print_arr, py_print_arr, maker, bad_test
from ....docx_engine import F

IN = PositiveArray()
_t = maker(IN)

C_SOLVE = f'''    /* палиндром: число равно числу, записанному в обратном порядке */
    cnt = 0;
    for (i = 1; i <= n; i++){{
        v = X[i];
        r = 0;
        while (v > 0){{
            r = r * 10 + v % 10;
            v = v / 10;
        }}
        if (r == X[i]){{
            cnt++;
            Y[cnt] = X[i];
        }}
    }}

    if (cnt == 0)
        printf("\\nПалиндромов нет - новый массив пуст.\\n");
    else{{
        printf("\\nНовый массив Y (палиндромы, %d эл.): ", cnt);
{c_print_arr("", "Y", "cnt")}
    }}
'''


def rev(x):
    r = 0
    while x > 0:
        r = r * 10 + x % 10
        x //= 10
    return r


def simulate(con):
    n, X = IN.read(con)
    con.begin_results()
    Y = [X[i] for i in range(1, n + 1) if rev(X[i]) == X[i]]
    if not Y:
        con.printf("\nПалиндромов нет - новый массив пуст.\n")
    else:
        con.printf("\nНовый массив Y (палиндромы, %d эл.): " % len(Y))
        py_print_arr(con, "", Y)


def svyaz(rep):
    rep.fline("", F("∀ i = {1..n}:  X[i] = a[i, d−1] … a[i, 0];"))
    rep.fline("", F("X[i] ∈ Y  ⇔  ∀ j = {0..d − 1}: a[i, j] = a[i, d − 1 − j]"), indent=0.6)
    rep.para("(т.е. X[i] равно числу, записанному теми же цифрами в обратном порядке).", indent=0.6)


METHOD = [
    ("Для каждого элемента строится число r из его цифр в обратном порядке; при r = X[i] элемент – палиндром:",
     ["cnt = 0",
      ["для i = {1..n}",
       "v = X[i];  r = 0",
       ["пока  v > 0", "r = r · 10 + (v − 10 · (v \\ 10));  v = v \\ 10"],
       "(cnt = cnt + 1,  Y[cnt] = X[i]),  если  r = X[i]"]]),
]

SPEC = [
    ("label", "При cnt = 0"),
    ("box", ["Палиндромов нет - новый массив пуст."], True),
    ("label", "Иначе"),
    ("box", ["Новый массив Y (палиндромы, <<cnt>> эл.): <<Y[1]>> <<Y[2]>> … <<Y[cnt]>>"], True),
]

PSEUDO = """
_алг_ «Лабораторная работа №2, часть II, задание 4»
_нач_
	ввод(n, X[1:n])
	вывод(X[1:n])
	cnt := 0
	_цикл от_ i := 1 _до_ n
		v := X[i]; r := 0
		_цикл-пока_ v > 0
			r := r · 10 + (v − 10 · (v \\ 10)); v := v \\ 10
		_кц_
		_если_ r = X[i] _то_
			cnt := cnt + 1; Y[cnt] := X[i]
		_всё_
	_кц_
	_если_ cnt = 0 _то_
		вывод(«Палиндромов нет - новый массив пуст.»)
	_иначе_
		вывод(«Новый массив Y (палиндромы, », cnt, « эл.): », Y[1:cnt])
	_всё_
_кон_
"""

TESTS = [
    _t([123321, 120, 7, 1221, 10], "Часть элементов – палиндромы (однозначные тоже)"),
    _t([12, 100, 98], "Палиндромов нет (в т.ч. 100 – число с нулями в конце)"),
    _t([11, 909, 5], "Все элементы – палиндромы"),
    bad_test(IN, [44, 45], "Недопустимые данные: n = 0, буква, отрицательное и дробное число, мало чисел"),
]

TASK = Task(
    part=2, num=4,
    statement="Дан массив целых положительных чисел. Сформировать новый массив, содержащий все элементы исходного "
              "массива, являющиеся палиндромами. Палиндромом называется число, в котором порядок следования цифр "
              "одинаковый как при чтении справа налево, так и слева направо. Например, 123321.",
    short="Палиндромы",
    defines=IN.defines, decls=IN.decls + "    int Y[KMAX + 1], v, r, cnt;\n",
    c_input=IN.c_input, c_solve=C_SOLVE, simulate=simulate,
    given=IN.given,
    result=["Y[1:cnt] – новый массив из элементов X, являющихся палиндромами (однозначные числа – палиндромы), "
            "или сообщение «Палиндромов нет – новый массив пуст»."],
    when=IN.when, svyaz=svyaz, method=METHOD, spec=IN.spec + SPEC, pseudo=PSEUDO, tests=TESTS,
)
