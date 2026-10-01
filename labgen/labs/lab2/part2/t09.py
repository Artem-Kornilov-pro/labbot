from ..common import Task
from ..inputs import PositiveArray
from .shared import c_print_arr, py_print_arr, maker, bad_test
from ....docx_engine import F

IN = PositiveArray(z_lo=1)
_t = maker(IN)

C_SOLVE = f'''    /* первая цифра элемента: делим на 10, пока число не станет однозначным */
    cnt = 0;
    for (i = 1; i <= n; i++){{
        v = X[i];
        while (v >= 10)
            v = v / 10;
        if (v == z){{
            cnt++;
            Y[cnt] = X[i];
        }}
    }}

    if (cnt == 0)
        printf("\\nЭлементов, начинающихся с цифры %d, нет - новый массив пуст.\\n", z);
    else{{
        printf("\\nНовый массив Y (%d эл.): ", cnt);
{c_print_arr("", "Y", "cnt")}
    }}
'''


def first(x):
    while x >= 10:
        x //= 10
    return x


def simulate(con):
    n, X, z = IN.read(con)
    con.begin_results()
    Y = [X[i] for i in range(1, n + 1) if first(X[i]) == z]
    if not Y:
        con.printf("\nЭлементов, начинающихся с цифры %d, нет - новый массив пуст.\n" % z)
    else:
        con.printf("\nНовый массив Y (%d эл.): " % len(Y))
        py_print_arr(con, "", Y)


def svyaz(rep):
    rep.fline("", F("∀ i = {1..n}:  X[i] = a[i, d−1] … a[i, 0];   X[i] ∈ Y  ⇔  a[i, d−1] = Z"))


METHOD = [
    ("Для каждого элемента первая цифра получается делением на 10, пока число не станет однозначным; "
     "элементы с первой цифрой Z заносятся в новый массив:",
     ["cnt = 0",
      ["для i = {1..n}",
       "v = X[i]",
       ["пока  v ≥ 10", "v = v \\ 10"],
       "(cnt = cnt + 1,  Y[cnt] = X[i]),  если  v = Z"]]),
]

SPEC = [
    ("label", "При cnt = 0"),
    ("box", ["Элементов, начинающихся с цифры <<Z>>, нет - новый массив пуст."], True),
    ("label", "Иначе"),
    ("box", ["Новый массив Y (<<cnt>> эл.): <<Y[1]>> <<Y[2]>> … <<Y[cnt]>>"], True),
]

PSEUDO = """
_алг_ «Лабораторная работа №2, часть II, задание 9»
_нач_
	ввод(n, X[1:n], Z)
	вывод(X[1:n])
	cnt := 0
	_цикл от_ i := 1 _до_ n
		v := X[i]
		_цикл-пока_ v ≥ 10
			v := v \\ 10
		_кц_
		_если_ v = Z _то_
			cnt := cnt + 1; Y[cnt] := X[i]
		_всё_
	_кц_
	_если_ cnt = 0 _то_
		вывод(«Элементов, начинающихся с цифры », Z, «, нет - новый массив пуст.»)
	_иначе_
		вывод(«Новый массив Y (», cnt, « эл.): », Y[1:cnt])
	_всё_
_кон_
"""

TESTS = [
    _t([31, 3, 123, 300, 43], "Часть элементов начинается с 3 (в т.ч. однозначное)", z=3),
    _t([12, 21, 22], "Ни один не начинается с 9", z=9),
    _t([5, 50, 555], "Все начинаются с 5", z=5),
    bad_test(IN, [71, 17], "Недопустимые данные (в т.ч. Z = 0 и буква); Z = 7", z=7, z_bad=["0", "a"]),
]

TASK = Task(
    part=2, num=9,
    statement="Дан массив целых положительных чисел. Сформировать новый массив, состоящий из элементов исходного "
              "массива, начинающихся с заданной цифры Z.",
    short="Элементы, начинающиеся с цифры Z",
    defines=IN.defines, decls=IN.decls + "    int Y[KMAX + 1], v, cnt;\n",
    c_input=IN.c_input, c_solve=C_SOLVE, simulate=simulate,
    given=IN.given,
    result=["Y[1:cnt] – новый массив из элементов X, первая цифра которых равна Z, или сообщение «Элементов, "
            "начинающихся с цифры Z, нет – новый массив пуст»."],
    when=IN.when, svyaz=svyaz, method=METHOD, spec=IN.spec + SPEC, pseudo=PSEUDO, tests=TESTS,
)
