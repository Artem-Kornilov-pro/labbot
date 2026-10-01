from ..common import Task, Test
from ..inputs import MatrixArray
from .shared import c_find, py_find, c_print_list, py_print_list
from ....docx_engine import F

IN = MatrixArray("Z", "F")

C_SOLVE = f'''    /* в каждом столбце - первый отрицательный элемент, затем элементы после него */
    cnt = 0;
    for (j = 1; j <= m; j++){{
        i = 1;
        while (i <= n && Z[i][j] >= 0)  /* досрочный выход на первом отрицательном */
            i++;
        for (i = i + 1; i <= n; i++){{
            {c_find("F", "k", "Z[i][j]").replace(chr(10) + "        ", chr(10) + "            ")}
            if (t > k){{                   /* элемента нет в F - заносим в Q */
                cnt++;
                Q[cnt] = Z[i][j];
            }}
        }}
    }}

    if (cnt == 0)
        printf("\\nПодходящих элементов нет - массив Q пуст.\\n");
    else{{
        printf("\\nМассив Q (%d эл.): ", cnt);
{c_print_list("", "Q", "cnt")}
    }}
'''


def simulate(con):
    n, m, Z, k, Fa = IN.read(con)
    con.begin_results()
    Q = []
    for j in range(1, m + 1):
        i = 1
        while i <= n and Z[i][j] >= 0:
            i += 1
        for i2 in range(i + 1, n + 1):
            if py_find(Fa, k, Z[i2][j]) > k:
                Q.append(Z[i2][j])
    if not Q:
        con.printf("\nПодходящих элементов нет - массив Q пуст.\n")
    else:
        con.printf("\nМассив Q (%d эл.): " % len(Q))
        py_print_list(con, "", Q)


def svyaz(rep):
    rep.fline("1. ", F("∀ j = {1..m}:  ∃ ineg[j] ∈ [1:n]:  Z[ineg[j], j] < 0,"))
    rep.fline("", F("∀ i = {1..ineg[j] − 1}: Z[i, j] ≥ 0"), indent=0.6)
    rep.fline("2. ", F("Q[1:cnt]:  Z[i, j] ∈ Q  ⇔"))
    rep.fline("", F("⇔  i > ineg[j]  и  ∀ t = {1..k}: F[t] ≠ Z[i, j]"), indent=0.6)
    rep.para("(элементы заносятся по столбцам, в каждом столбце – сверху вниз).", indent=0.6)


METHOD = [
    ("Для каждого столбца — поиск первого отрицательного элемента (досрочный выход), затем для каждого "
     "элемента ниже него поиск в массиве F (досрочный выход при совпадении):",
     ["cnt = 0",
      ["для j = {1..m}",
       "i = 1",
       ["пока  i ≤ n  и  Z[i, j] ≥ 0", "i = i + 1"],
       ["для s = {i + 1..n}",
        "t = 1",
        ["пока  t ≤ k  и  F[t] ≠ Z[s, j]", "t = t + 1"],
        "(cnt = cnt + 1,  Q[cnt] = Z[s, j]),  если  t > k"]]]),
]

SPEC = [
    ("label", "При cnt = 0"),
    ("box", ["Подходящих элементов нет - массив Q пуст."], True),
    ("label", "Иначе"),
    ("box", ["Массив Q (<<cnt>> эл.): <<Q[1]>> <<Q[2]>> … <<Q[cnt]>>"], True),
]

PSEUDO = """
_алг_ «Лабораторная работа №2, часть I, задание 13»
_нач_
	ввод(n, m, Z[1:n, 1:m], k, F[1:k])
	вывод(Z[1:n, 1:m], F[1:k])
	cnt := 0
	_цикл_ _от_ j := 1 _до_ m
		i := 1
		_цикл-пока_ i ≤ n _и_ Z[i, j] ≥ 0
			i := i + 1
		_кц_
		_цикл_ _от_ s := i + 1 _до_ n
			t := 1
			_цикл-пока_ t ≤ k _и_ F[t] ≠ Z[s, j]
				t := t + 1
			_кц_
			_если_ t > k _то_
				cnt := cnt + 1; Q[cnt] := Z[s, j]
			_всё_
		_кц_
	_кц_
	_если_ cnt = 0 _то_
		вывод(«Подходящих элементов нет - массив Q пуст.»)
	_иначе_
		вывод(«Массив Q (», cnt, « эл.): », Q[1:cnt])
	_всё_
_кон_
"""


def _t(mat, arr, case):
    return Test(IN.lines(mat, arr), IN.shown(mat, arr), case)


TESTS = [
    _t([[1, -2, 3], [-4, 5, 6], [7, 8, -9], [2, 5, 1]], [5],
       "Столбцы 1 и 2: элементы после первого отрицательного, кроме 5 (есть в F); в столбце 3 – после −9"),
    _t([[1, 2], [3, 4]], [0], "Отрицательных нет – массив Q пуст"),
    _t([[-1, 5], [2, -3], [2, 9]], [2, 9], "Все элементы после отрицательных есть в F – массив Q пуст"),
    Test(["2 1", "-5", "-6", "1", "1  2", "0"], ["n, m: 2 1", "Z = -5 / -6", "k: 1", "F: 1  2 / 0"],
         "Недопустимые данные (два числа вместо одного); Q = −6"),
]

TASK = Task(
    part=1, num=13,
    statement=("Даны целочисленная матрица Z[1:n, 1:m] и целочисленный массив F[1:k]. Сформировать массив Q, "
               "состоящий из элементов столбцов матрицы Z, расположенных после первого отрицательного элемента "
               "каждого столбца этой матрицы и отсутствующих в массиве F."),
    short="Массив из элементов после первого отрицательного в столбцах",
    defines=IN.defines,
    decls=IN.decls + "    int t, cnt, Q[NMAX * NMAX + 1];\n",
    c_input=IN.c_input, c_solve=C_SOLVE, simulate=simulate,
    given=IN.given,
    result=["Q[1:cnt] – массив из элементов столбцов матрицы Z, расположенных после первого отрицательного "
            "элемента своего столбца и отсутствующих в массиве F, или сообщение «Подходящих элементов нет – "
            "массив Q пуст»."],
    when=IN.when, svyaz=svyaz, method=METHOD, spec=IN.spec + SPEC, pseudo=PSEUDO, tests=TESTS,
)
