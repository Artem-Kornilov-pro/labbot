from ..common import Task, Test
from ..inputs import MatrixArray
from .shared import (c_sort_row, py_sort_row, c_print_list, py_print_list, c_print_mat, py_print_mat, mat_box,
                     sort_row_method, sort_row_pseudo)
from ....docx_engine import F

IN = MatrixArray("A", "B")

C_SOLVE = f'''    /* минимальный элемент массива B */
    bmin = B[1];
    for (t = 2; t <= k; t++)
        if (B[t] < bmin) bmin = B[t];
    /* строки, содержащие bmin, упорядочиваются по возрастанию */
    cnt = 0;
    for (i = 1; i <= n; i++){{
        j = 1;
        while (j <= m && A[i][j] != bmin)  /* досрочный выход при совпадении */
            j++;
        if (j <= m){{
            cnt++;
            row[cnt] = i;
{c_sort_row("A", "i", "m")}
        }}
    }}

    printf("\\nМинимальный элемент массива B: %d.\\n", bmin);
    if (cnt == 0)
        printf("Ни одна строка не содержит этот элемент - матрица не изменилась.\\n");
    else{{
{c_print_list("Упорядочены по возрастанию строки: ", "row", "cnt")}
{c_print_mat("A", "n", "m", "Преобразованная матрица A:")}
    }}
'''


def simulate(con):
    n, m, A, k, B = IN.read(con)
    con.begin_results()
    bmin = min(B[1:k + 1])
    rows = []
    for i in range(1, n + 1):
        if bmin in A[i][1:m + 1]:
            rows.append(i)
            py_sort_row(A, i, m)
    con.printf("\nМинимальный элемент массива B: %d.\n" % bmin)
    if not rows:
        con.printf("Ни одна строка не содержит этот элемент - матрица не изменилась.\n")
    else:
        py_print_list(con, "Упорядочены по возрастанию строки: ", rows)
        py_print_mat(con, A, n, m, "Преобразованная матрица A:")


def svyaz(rep):
    rep.fline("1. ", F("bmin = min B[t],  t = {1..k}"))
    rep.fline("2. ", F("∀ i = {1..n}:  (∃ j ∈ [1:m]: A[i, j] = bmin)  ⇒"))
    rep.fline("", F("⇒  ∀ j = {1..m − 1}: A'[i, j] ≤ A'[i, j + 1],"), indent=0.6)
    rep.para("где A'[i, 1:m] – тот же набор элементов строки i, переставленный по возрастанию.", indent=0.6)


METHOD = [
    ("Поиск минимального элемента массива B:",
     ["bmin = B[1]", ["для t = {2..k}", "bmin = B[t],  если  B[t] < bmin"]]),
    ("Поиск bmin в каждой строке (досрочный выход при совпадении) и упорядочивание строки:",
     ["cnt = 0",
      ["для i = {1..n}",
       "j = 1",
       ["пока  j ≤ m  и  A[i, j] ≠ bmin", "j = j + 1"],
       "(cnt = cnt + 1,  row[cnt] = i),  если  j ≤ m", "упорядочить строку i (п. 3),  если  j ≤ m"]]),
    ("Упорядочивание строки i по возрастанию «пузырьком» с досрочным выходом:", sort_row_method("A")),
]

SPEC = [
    ("box", ["Минимальный элемент массива B: <<bmin>>."], False),
    ("label", "При cnt = 0"),
    ("box", ["Ни одна строка не содержит этот элемент - матрица не изменилась."], True),
    ("label", "Иначе"),
    ("box", ["Упорядочены по возрастанию строки: <<row[1]>> … <<row[cnt]>>", "Преобразованная матрица A:",
             *mat_box("A")], True),
]

PSEUDO = f"""
_алг_ «Лабораторная работа №2, часть I, задание 11»
_нач_
	ввод(n, m, A[1:n, 1:m], k, B[1:k])
	вывод(A[1:n, 1:m], B[1:k])
	bmin := B[1]
	_цикл от_ t := 2 _до_ k
		_если_ B[t] < bmin _то_
			bmin := B[t]
		_всё_
	_кц_
	cnt := 0
	_цикл от_ i := 1 _до_ n
		j := 1
		_цикл-пока_ j ≤ m _и_ A[i, j] ≠ bmin
			j := j + 1
		_кц_
		_если_ j ≤ m _то_
			cnt := cnt + 1; row[cnt] := i
{sort_row_pseudo("A")}
		_всё_
	_кц_
	вывод(«Минимальный элемент массива B: », bmin, «.»)
	_если_ cnt = 0 _то_
		вывод(«Ни одна строка не содержит этот элемент - матрица не изменилась.»)
	_иначе_
		вывод(«Упорядочены по возрастанию строки: », row[1:cnt])
		вывод(«Преобразованная матрица A:», A[1:n, 1:m])
	_всё_
_кон_
"""


def _t(mat, arr, case):
    return Test(IN.lines(mat, arr), IN.shown(mat, arr), case)


TESTS = [
    _t([[5, -3, 1], [4, 2, 8], [0, -3, -9]], [7, -3, 10], "Упорядочены строки 1 и 3 (содержат min B = −3)"),
    _t([[1, 2], [3, 4]], [5, 0], "min B = 0 нет в матрице – матрица не меняется"),
    _t([[9, 1], [1, 0]], [1], "Все строки содержат min B"),
    Test(["2 3", "3 1 2", "1 1 1", "1", "1 1", "1"],
                ["n, m: 2 3", "A = 3 1 2 / 1 1 1", "k: 1", "B: 1 1 / 1"],
                "Недопустимые данные (лишнее число в массиве); упорядочены обе строки"),
]

TASK = Task(
    part=1, num=11,
    statement=("Даны целочисленная матрица A[1:n, 1:m] и целочисленный массив B[1:k]. Упорядочить по возрастанию "
               "все строки матрицы, содержащие хотя бы один элемент, совпадающий с минимальным элементом массива B."),
    short="Упорядочивание строк, содержащих минимальный элемент массива",
    defines=IN.defines,
    decls=IN.decls + "    int t, p, sw, c, bmin, cnt, row[NMAX + 1];\n",
    c_input=IN.c_input, c_solve=C_SOLVE, simulate=simulate,
    given=IN.given,
    result=["bmin – минимальный элемент массива B; A[1:n, 1:m] – матрица, в которой упорядочены по возрастанию "
            "строки, содержащие bmin, и номера этих строк, или сообщение «Ни одна строка не содержит этот элемент – "
            "матрица не изменилась»."],
    when=IN.when, svyaz=svyaz, method=METHOD, spec=IN.spec + SPEC, pseudo=PSEUDO, tests=TESTS,
)
