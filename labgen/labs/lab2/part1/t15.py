from ..common import Task, Test
from ..inputs import MatrixArray
from .shared import (c_find, py_find, c_sort_row, py_sort_row, c_print_list, py_print_list, c_print_mat,
                     py_print_mat, mat_box, sort_row_method, sort_row_pseudo)
from ....docx_engine import F, m, nsum

IN = MatrixArray("Q", "Z")

C_SOLVE = f'''    /* для каждой строки: сумма элементов и её поиск в массиве Z */
    cnt = 0;
    for (i = 1; i <= n; i++){{
        sum = 0;
        for (j = 1; j <= m; j++)
            sum = sum + Q[i][j];
        {c_find("Z", "k", "sum")}
        if (t <= k){{                      /* сумма есть в Z - сортируем строку */
            cnt++;
            row[cnt] = i;
{c_sort_row("Q", "i", "m", desc=True)}
        }}
    }}

    if (cnt == 0)
        printf("\\nСумма ни одной строки не совпадает с элементами Z - "
               "матрица не изменилась.\\n");
    else{{
{c_print_list("Упорядочены по убыванию строки: ", "row", "cnt")}
{c_print_mat("Q", "n", "m", "Преобразованная матрица Q:")}
    }}
'''


def simulate(con):
    n, m_, Q, k, Z = IN.read(con)
    con.begin_results()
    rows = []
    for i in range(1, n + 1):
        if py_find(Z, k, sum(Q[i][1:m_ + 1])) <= k:
            rows.append(i)
            py_sort_row(Q, i, m_, desc=True)
    if not rows:
        con.printf("\nСумма ни одной строки не совпадает с элементами Z - матрица не изменилась.\n")
    else:
        py_print_list(con, "Упорядочены по убыванию строки: ", rows)
        py_print_mat(con, Q, n, m_, "Преобразованная матрица Q:")


def svyaz(rep):
    rep.fline("1. ", F("∀ i = {1..n}:  s[i] = ") + nsum(m("j = 1"), m("m"), m("Q[i, j]")))
    rep.fline("2. ", F("∀ i = {1..n}:  (∃ t ∈ [1:k]: Z[t] = s[i])  ⇒"))
    rep.fline("", F("⇒  ∀ j = {1..m − 1}: Q'[i, j] ≥ Q'[i, j + 1],"), indent=0.6)
    rep.para("где Q'[i, 1:m] – тот же набор элементов строки i, переставленный по убыванию.", indent=0.6)


METHOD = [
    ("Сумма каждой строки, её поиск в массиве Z (досрочный выход при совпадении) и упорядочивание строки:",
     ["cnt = 0",
      ["для i = {1..n}",
       "s = 0",
       ["для j = {1..m}", "s = s + Q[i, j]"],
       "t = 1",
       ["пока  t ≤ k  и  Z[t] ≠ s", "t = t + 1"],
       "(cnt = cnt + 1,  row[cnt] = i),  если  t ≤ k", "упорядочить строку i (п. 2),  если  t ≤ k"]]),
    ("Упорядочивание строки i по убыванию «пузырьком» с досрочным выходом:", sort_row_method("Q", desc=True)),
]

SPEC = [
    ("label", "При cnt = 0"),
    ("box", ["Сумма ни одной строки не совпадает с элементами Z - матрица не изменилась."], True),
    ("label", "Иначе"),
    ("box", ["Упорядочены по убыванию строки: <<row[1]>> … <<row[cnt]>>", "Преобразованная матрица Q:",
             *mat_box("Q")], True),
]

PSEUDO = f"""
_алг_ «Лабораторная работа №2, часть I, задание 15»
_нач_
	ввод(n, m, Q[1:n, 1:m], k, Z[1:k])
	вывод(Q[1:n, 1:m], Z[1:k])
	cnt := 0
	_цикл от_ i := 1 _до_ n
		sum := 0
		_цикл от_ j := 1 _до_ m
			sum := sum + Q[i, j]
		_кц_
		t := 1
		_цикл-пока_ t ≤ k _и_ Z[t] ≠ sum
			t := t + 1
		_кц_
		_если_ t ≤ k _то_
			cnt := cnt + 1; row[cnt] := i
{sort_row_pseudo("Q", desc=True)}
		_всё_
	_кц_
	_если_ cnt = 0 _то_
		вывод(«Сумма ни одной строки не совпадает с элементами Z - матрица не изменилась.»)
	_иначе_
		вывод(«Упорядочены по убыванию строки: », row[1:cnt])
		вывод(«Преобразованная матрица Q:», Q[1:n, 1:m])
	_всё_
_кон_
"""


def _t(mat, arr, case):
    return Test(IN.lines(mat, arr), IN.shown(mat, arr), case)


TESTS = [
    _t([[1, 5, 3], [2, 2, 2], [-4, 0, 9]], [9, 5], "Упорядочены строки 1 и 3 (суммы 9 и 5 есть в Z)"),
    _t([[1, 2], [3, 4]], [0, 10], "Ни одна сумма не совпадает – матрица не меняется"),
    _t([[-3, 3, 7], [0, 0, 0]], [7, 0], "Подходят все строки"),
    Test(["1 4", "1 2 3 4", "1", "10.0", "10"], ["n, m: 1 4", "Q = 1 2 3 4", "k: 1", "Z: 10.0 / 10"],
         "Недопустимые данные (дробная запись числа); сумма 10 есть в Z"),
]

TASK = Task(
    part=1, num=15,
    statement=("Даны целочисленная матрица Q[1:n, 1:m] и целочисленный массив Z[1:k]. Упорядочить по убыванию те "
               "строки матрицы Q, сумма элементов которых совпадает с одним из элементов массива Z."),
    short="Упорядочивание по убыванию строк, сумма которых есть в массиве",
    defines=IN.defines,
    decls=IN.decls + "    int t, p, sw, c, sum, cnt, row[NMAX + 1];\n",
    c_input=IN.c_input, c_solve=C_SOLVE, simulate=simulate,
    given=IN.given,
    result=["Q[1:n, 1:m] – матрица, в которой упорядочены по убыванию строки, сумма элементов которых совпадает "
            "с одним из элементов Z, и номера этих строк, или сообщение «Сумма ни одной строки не совпадает с "
            "элементами Z – матрица не изменилась»."],
    when=IN.when, svyaz=svyaz, method=METHOD, spec=IN.spec + SPEC, pseudo=PSEUDO, tests=TESTS,
)
