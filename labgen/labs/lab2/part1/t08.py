from ..common import Task, Test
from ..inputs import MatrixArray
from .shared import (c_sort_col, py_find, py_sort_col, c_print_list, py_print_list, c_print_mat, py_print_mat,
                     mat_box, sort_col_method, sort_col_pseudo)
from ....docx_engine import F

IN = MatrixArray("A", "B")

C_SOLVE = f'''    /* столбцы, все элементы которых есть в массиве B */
    cnt = 0;
    for (j = 1; j <= m; j++){{
        all = 1;
        i = 1;
        while (i <= n && all){{            /* досрочный выход: элемента нет в B */
            t = 1;
            while (t <= k && B[t] != A[i][j])  /* досрочный выход при совпадении */
                t++;
            if (t > k) all = 0;
            i++;
        }}
        if (all){{                         /* все элементы есть в B - сортируем */
            cnt++;
            col[cnt] = j;
{c_sort_col("A", "j", "n", desc=True)}
        }}
    }}

    if (cnt == 0)
        printf("\\nНет столбцов, все элементы которых есть в массиве B - "
               "матрица не изменилась.\\n");
    else{{
{c_print_list("Упорядочены по убыванию столбцы: ", "col", "cnt")}
{c_print_mat("A", "n", "m", "Преобразованная матрица A:")}
    }}
'''


def simulate(con):
    n, m, A, k, B = IN.read(con)
    con.begin_results()
    cols = []
    for j in range(1, m + 1):
        if all(py_find(B, k, A[i][j]) <= k for i in range(1, n + 1)):
            cols.append(j)
            py_sort_col(A, j, n, desc=True)
    if not cols:
        con.printf("\nНет столбцов, все элементы которых есть в массиве B - матрица не изменилась.\n")
    else:
        py_print_list(con, "Упорядочены по убыванию столбцы: ", cols)
        py_print_mat(con, A, n, m, "Преобразованная матрица A:")


def svyaz(rep):
    rep.fline("", F("∀ j = {1..m}:  (∀ i = {1..n}  ∃ t ∈ [1:k]: B[t] = A[i, j])  ⇒"))
    rep.fline("", F("⇒  ∀ i = {1..n − 1}:  A'[i, j] ≥ A'[i + 1, j],"), indent=0.6)
    rep.para("где A'[1:n, j] – тот же набор элементов столбца j, переставленный по убыванию.", indent=0.6)


METHOD = [
    ("Проверка, что все элементы столбца есть в массиве B (досрочный выход из обоих циклов), и упорядочивание "
     "столбца по убыванию:",
     ["cnt = 0",
      ["для j = {1..m}",
       "all = 1;  i = 1",
       ["пока  i ≤ n  и  all = 1",
        "t = 1",
        ["пока  t ≤ k  и  B[t] ≠ A[i, j]", "t = t + 1"],
        "all = 0,  если  t > k",
        "i = i + 1"],
       "(cnt = cnt + 1,  col[cnt] = j),  если  all = 1", "упорядочить столбец j (п. 2),  если  all = 1"]]),
    ("Упорядочивание столбца j по убыванию «пузырьком» с досрочным выходом:", sort_col_method("A", desc=True)),
]

SPEC = [
    ("label", "При cnt = 0"),
    ("box", ["Нет столбцов, все элементы которых есть в массиве B - матрица не изменилась."], True),
    ("label", "Иначе"),
    ("box", ["Упорядочены по убыванию столбцы: <<col[1]>> … <<col[cnt]>>", "Преобразованная матрица A:",
             *mat_box("A")], True),
]

PSEUDO = f"""
_алг_ «Лабораторная работа №2, часть I, задание 8»
_нач_
	ввод(n, m, A[1:n, 1:m], k, B[1:k])
	вывод(A[1:n, 1:m], B[1:k])
	cnt := 0
	_цикл от_ j := 1 _до_ m
		all := 1; i := 1
		_цикл-пока_ i ≤ n _и_ all = 1
			t := 1
			_цикл-пока_ t ≤ k _и_ B[t] ≠ A[i, j]
				t := t + 1
			_кц_
			_если_ t > k _то_
				all := 0
			_всё_
			i := i + 1
		_кц_
		_если_ all = 1 _то_
			cnt := cnt + 1; col[cnt] := j
{sort_col_pseudo("A", desc=True)}
		_всё_
	_кц_
	_если_ cnt = 0 _то_
		вывод(«Нет столбцов, все элементы которых есть в массиве B - матрица не изменилась.»)
	_иначе_
		вывод(«Упорядочены по убыванию столбцы: », col[1:cnt])
		вывод(«Преобразованная матрица A:», A[1:n, 1:m])
	_всё_
_кон_
"""


def _t(mat, arr, case):
    return Test(IN.lines(mat, arr), IN.shown(mat, arr), case)


TESTS = [
    _t([[1, 5, 2], [3, 6, 9], [2, 7, 4]], [1, 2, 3, 4, 9], "Упорядочены столбцы 1 и 3 (все их элементы есть в B), 2-й – нет"),
    _t([[1, 2], [3, 4]], [1, 4], "Ни один столбец не подходит"),
    _t([[-1, 0], [5, 8]], [8, 5, 0, -1], "Подходят все столбцы"),
    Test(["1 2", "7 -7", "-0", "2", "7 -7 7", "-7 7"], ["n, m: 1 2", "строка 1: 7 -7", "k: -0 / 2", "B: 7 -7 7 / -7 7"],
         "Недопустимые данные (k = 0, лишнее число); одна строка"),
]

TASK = Task(
    part=1, num=8,
    statement=("Даны целочисленная матрица A[1:n, 1:m] и целочисленный массив B[1:k]. Упорядочить по убыванию те "
               "столбцы матрицы A, все элементы которых присутствуют в массиве B."),
    short="Упорядочивание по убыванию столбцов, все элементы которых есть в массиве",
    defines=IN.defines,
    decls=IN.decls + "    int t, p, sw, c, all, cnt, col[NMAX + 1];\n",
    c_input=IN.c_input, c_solve=C_SOLVE, simulate=simulate,
    given=IN.given,
    result=["A[1:n, 1:m] – матрица, в которой упорядочены по убыванию столбцы, все элементы которых есть в "
            "массиве B, и номера этих столбцов, или сообщение «Нет столбцов, все элементы которых есть в массиве "
            "B – матрица не изменилась»."],
    when=IN.when, svyaz=svyaz, method=METHOD, spec=IN.spec + SPEC, pseudo=PSEUDO, tests=TESTS,
)
