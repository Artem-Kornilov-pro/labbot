from ..common import Task, Test
from ..inputs import MatrixArray
from .shared import c_find, py_find, c_print_list, py_print_list, c_print_mat, py_print_mat, mat_box
from ....docx_engine import F

IN = MatrixArray("X", "Z")

C_SOLVE = f'''    /* обнуление элементов X, которых нет в массиве Z, с запоминанием в R */
    cnt = 0;
    for (i = 1; i <= n; i++)
        for (j = 1; j <= m; j++){{
            {c_find("Z", "k", "X[i][j]").replace(chr(10) + "        ", chr(10) + "            ")}
            if (t > k){{
                cnt++;
                R[cnt] = X[i][j];
                X[i][j] = 0;
            }}
        }}

    if (cnt == 0)
        printf("\\nВсе элементы матрицы есть в массиве Z - обнулений нет.\\n");
    else{{
        printf("\\nОбнулено элементов: %d.\\n", cnt);
{c_print_mat("X", "n", "m", "Преобразованная матрица X:")}
{c_print_list("Обнулённые элементы: ", "R", "cnt")}
    }}
'''


def simulate(con):
    n, m, X, k, Z = IN.read(con)
    con.begin_results()
    R = []
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if py_find(Z, k, X[i][j]) > k:
                R.append(X[i][j])
                X[i][j] = 0
    if not R:
        con.printf("\nВсе элементы матрицы есть в массиве Z - обнулений нет.\n")
    else:
        con.printf("\nОбнулено элементов: %d.\n" % len(R))
        py_print_mat(con, X, n, m, "Преобразованная матрица X:")
        py_print_list(con, "Обнулённые элементы: ", R)


def svyaz(rep):
    rep.fline("", F("∀ i = {1..n},  ∀ j = {1..m}:  (∀ t = {1..k}: Z[t] ≠ X[i, j])  ⇒"))
    rep.fline("", F("⇒  X'[i, j] = 0,  X[i, j] ∈ R[1:cnt]"), indent=0.6)


METHOD = [
    ("Для каждого элемента — поиск в массиве Z (досрочный выход при совпадении); отсутствующий элемент "
     "запоминается в массиве R и обнуляется:",
     ["cnt = 0",
      ["для i = {1..n},  j = {1..m}",
       "t = 1",
       ["пока  t ≤ k  и  Z[t] ≠ X[i, j]", "t = t + 1"],
       "(cnt = cnt + 1,  R[cnt] = X[i, j],  X[i, j] = 0),  если  t > k"]]),
]

SPEC = [
    ("label", "При cnt = 0"),
    ("box", ["Все элементы матрицы есть в массиве Z - обнулений нет."], True),
    ("label", "Иначе"),
    ("box", ["Обнулено элементов: <<cnt>>.", "Преобразованная матрица X:", *mat_box("X"),
             "Обнулённые элементы: <<R[1]>> <<R[2]>> … <<R[cnt]>>"], True),
]

PSEUDO = """
_алг_ «Лабораторная работа №2, часть I, задание 12»
_нач_
	ввод(n, m, X[1:n, 1:m], k, Z[1:k])
	вывод(X[1:n, 1:m], Z[1:k])
	cnt := 0
	_цикл_ _от_ i := 1 _до_ n
		_цикл_ _от_ j := 1 _до_ m
			t := 1
			_цикл-пока_ t ≤ k _и_ Z[t] ≠ X[i, j]
				t := t + 1
			_кц_
			_если_ t > k _то_
				cnt := cnt + 1; R[cnt] := X[i, j]; X[i, j] := 0
			_всё_
		_кц_
	_кц_
	_если_ cnt = 0 _то_
		вывод(«Все элементы матрицы есть в массиве Z - обнулений нет.»)
	_иначе_
		вывод(«Обнулено элементов: », cnt, «.»)
		вывод(«Преобразованная матрица X:», X[1:n, 1:m])
		вывод(«Обнулённые элементы: », R[1:cnt])
	_всё_
_кон_
"""


def _t(mat, arr, case):
    return Test(IN.lines(mat, arr), IN.shown(mat, arr), case)


TESTS = [
    _t([[1, 5, 2], [8, 1, -4]], [1, 2], "Обнулены элементы, отсутствующие в Z; они запомнены"),
    _t([[3, 3], [4, 0]], [0, 3, 4], "Все элементы есть в Z – обнулений нет"),
    _t([[6, -6]], [5], "Нет ни одного элемента из Z – обнулена вся матрица"),
    Test(["1 1", "7", "3", "7 8", "7 8 9 10", "7 8 9"], ["n, m: 1 1", "X = 7", "k: 3",
                                                                "Z: 7 8 / 7 8 9 10 / 7 8 9"],
                "Недопустимые данные (мало и много чисел в массиве); обнулений нет"),
]

TASK = Task(
    part=1, num=12,
    statement=("Даны целочисленная матрица X[1:n, 1:m] и целочисленный массив Z[1:k]. Обнулить элементы матрицы X, "
               "которых нет в массиве Z, и запомнить обнулённые элементы."),
    short="Обнуление элементов, отсутствующих в массиве",
    defines=IN.defines,
    decls=IN.decls + "    int t, cnt, R[NMAX * NMAX + 1];\n",
    c_input=IN.c_input, c_solve=C_SOLVE, simulate=simulate,
    given=IN.given,
    result=["X[1:n, 1:m] – матрица, в которой обнулены элементы, отсутствующие в массиве Z; R[1:cnt] – массив "
            "обнулённых элементов (в порядке просмотра по строкам), или сообщение «Все элементы матрицы есть в "
            "массиве Z – обнулений нет»."],
    when=IN.when, svyaz=svyaz, method=METHOD, spec=IN.spec + SPEC, pseudo=PSEUDO, tests=TESTS,
)
