from ..common import Task
from ..inputs import PositiveArray
from .shared import c_print_arr, py_print_arr, maker, bad_test
from ....docx_engine import F

IN = PositiveArray(z_lo=0)
_t = maker(IN)

C_SOLVE = f'''    /* количество цифр z в каждом элементе; элементы с такой цифрой - в Y */
    total = 0;
    cnt = 0;
    for (i = 1; i <= n; i++){{
        v = X[i];
        c = 0;
        while (v > 0){{
            if (v % 10 == z) c++;
            v = v / 10;
        }}
        total = total + c;
        if (c > 0){{
            cnt++;
            Y[cnt] = X[i];
        }}
    }}

    printf("\\nЦифра %d встречается в элементах массива %d раз(а).\\n", z, total);
    if (cnt == 0)
        printf("Элементов, содержащих цифру %d, нет - новый массив пуст.\\n", z);
    else{{
        printf("Новый массив Y (%d эл.): ", cnt);
{c_print_arr("", "Y", "cnt")}
    }}
'''


def count(x, z):
    c = 0
    while x > 0:
        c += x % 10 == z
        x //= 10
    return c


def simulate(con):
    n, X, z = IN.read(con)
    con.begin_results()
    cs = [count(X[i], z) for i in range(1, n + 1)]
    Y = [X[i] for i in range(1, n + 1) if cs[i - 1] > 0]
    con.printf("\nЦифра %d встречается в элементах массива %d раз(а).\n" % (z, sum(cs)))
    if not Y:
        con.printf("Элементов, содержащих цифру %d, нет - новый массив пуст.\n" % z)
    else:
        con.printf("Новый массив Y (%d эл.): " % len(Y))
        py_print_arr(con, "", Y)


def svyaz(rep):
    rep.fline("1. ", F("∀ i = {1..n}:  X[i] = a[i, d[i]−1] … a[i, 0];"))
    rep.fline("", F("c[i] = |{ j : a[i, j] = Z }|  – количество цифр Z в X[i];"), indent=0.6)
    rep.fline("2. ", F("total = c[1] + c[2] + … + c[n];   X[i] ∈ Y  ⇔  c[i] > 0"))


METHOD = [
    ("Для каждого элемента цифры отделяются справа и сравниваются с Z; подсчитывается общее количество, "
     "элементы, содержащие Z, заносятся в новый массив:",
     ["total = 0;  cnt = 0",
      ["для i = {1..n}",
       "v = X[i];  c = 0",
       ["пока  v > 0", "c = c + 1,  если  v − 10 · (v \\ 10) = Z", "v = v \\ 10"],
       "total = total + c",
       "(cnt = cnt + 1,  Y[cnt] = X[i]),  если  c > 0"]]),
]

SPEC = [
    ("box", ["Цифра <<Z>> встречается в элементах массива <<total>> раз(а)."], False),
    ("label", "При cnt = 0"),
    ("box", ["Элементов, содержащих цифру <<Z>>, нет - новый массив пуст."], True),
    ("label", "Иначе"),
    ("box", ["Новый массив Y (<<cnt>> эл.): <<Y[1]>> <<Y[2]>> … <<Y[cnt]>>"], True),
]

PSEUDO = """
_алг_ «Лабораторная работа №2, часть II, задание 7»
_нач_
	ввод(n, X[1:n], Z)
	вывод(X[1:n])
	total := 0; cnt := 0
	_цикл_ _от_ i := 1 _до_ n
		v := X[i]; c := 0
		_цикл-пока_ v > 0
			_если_ v − 10 · (v \\ 10) = Z _то_
				c := c + 1
			_всё_
			v := v \\ 10
		_кц_
		total := total + c
		_если_ c > 0 _то_
			cnt := cnt + 1; Y[cnt] := X[i]
		_всё_
	_кц_
	вывод(«Цифра », Z, « встречается в элементах массива », total, « раз(а).»)
	_если_ cnt = 0 _то_
		вывод(«Элементов, содержащих цифру », Z, «, нет - новый массив пуст.»)
	_иначе_
		вывод(«Новый массив Y (», cnt, « эл.): », Y[1:cnt])
	_всё_
_кон_
"""

TESTS = [
    _t([1223, 45, 2, 222, 31], "Цифра 2 встречается несколько раз, в т.ч. многократно в одном числе", z=2),
    _t([100, 7, 2050], "Цифра 0 (нули внутри и в конце числа)", z=0),
    _t([13, 57, 9], "Цифры 2 нет ни в одном элементе", z=2),
    bad_test(IN, [55, 15], "Недопустимые данные (в т.ч. Z = 10 и Z = −1); цифра 5", z=5, z_bad=["10", "-1"]),
]

TASK = Task(
    part=2, num=7,
    statement="Дан массив целых положительных чисел. Посчитать, сколько раз в элементах исходного массива "
              "встречается заданная цифра Z. Сформировать новый массив, состоящий из элементов, содержащих хотя бы "
              "одну такую цифру.",
    short="Подсчёт цифры Z и элементы с ней",
    defines=IN.defines, decls=IN.decls + "    int Y[KMAX + 1], v, c, total, cnt;\n",
    c_input=IN.c_input, c_solve=C_SOLVE, simulate=simulate,
    given=IN.given,
    result=["total – количество цифр Z во всех элементах массива; Y[1:cnt] – новый массив из элементов, содержащих "
            "цифру Z, или сообщение «Элементов, содержащих цифру Z, нет – новый массив пуст»."],
    when=IN.when, svyaz=svyaz, method=METHOD, spec=IN.spec + SPEC, pseudo=PSEUDO, tests=TESTS,
)
