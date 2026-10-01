from ..common import Task, Test
from ..inputs import MatrixArray
from .shared import c_find, py_find, c_print_list, py_print_list, c_print_mat, py_print_mat, mat_box
from ....docx_engine import F

IN = MatrixArray("C", "A")

C_SOLVE = f'''    /* в каждом столбце - первые максимальный и минимальный элементы и их поиск в A */
    cnt = 0;
    for (j = 1; j <= m; j++){{
        imax = 1;
        imin = 1;
        for (i = 2; i <= n; i++){{
            if (C[i][j] > C[imax][j]) imax = i;
            if (C[i][j] < C[imin][j]) imin = i;
        }}
        {c_find("A", "k", "C[imax][j]")}
        if (t <= k){{                      /* максимум есть в A - ищем минимум */
            {c_find("A", "k", "C[imin][j]", "s").replace(chr(10) + "        ", chr(10) + "            ")}
            if (s <= k){{                  /* оба есть в A - переставляем */
                c = C[imax][j];
                C[imax][j] = C[imin][j];
                C[imin][j] = c;
                cnt++;
                col[cnt] = j;
            }}
        }}
    }}

    if (cnt == 0)
        printf("\\nНи в одном столбце максимальный и минимальный элементы "
               "не присутствуют оба в A - матрица не изменилась.\\n");
    else{{
{c_print_list("Переставлены максимальный и минимальный элементы в столбцах: ", "col", "cnt")}
{c_print_mat("C", "n", "m", "Преобразованная матрица C:")}
    }}
'''


def simulate(con):
    n, m, C, k, A = IN.read(con)
    con.begin_results()
    cols = []
    for j in range(1, m + 1):
        imax = imin = 1
        for i in range(2, n + 1):
            if C[i][j] > C[imax][j]:
                imax = i
            if C[i][j] < C[imin][j]:
                imin = i
        if py_find(A, k, C[imax][j]) <= k and py_find(A, k, C[imin][j]) <= k:
            C[imax][j], C[imin][j] = C[imin][j], C[imax][j]
            cols.append(j)
    if not cols:
        con.printf("\nНи в одном столбце максимальный и минимальный элементы не присутствуют оба в A - "
                   "матрица не изменилась.\n")
    else:
        py_print_list(con, "Переставлены максимальный и минимальный элементы в столбцах: ", cols)
        py_print_mat(con, C, n, m, "Преобразованная матрица C:")


def svyaz(rep):
    rep.fline("1. ", F("∀ j = {1..m}:  ∃ imax, imin ∈ [1:n]:"))
    rep.fline("", F("∀ i = {1..n}: C[imin, j] ≤ C[i, j] ≤ C[imax, j]"), indent=0.6)
    rep.para("(imax, imin – первые по порядку максимальный и минимальный элементы столбца);", indent=0.6)
    rep.fline("2. ", F("(∃ t: A[t] = C[imax, j])  и  (∃ s: A[s] = C[imin, j])  ⇒"))
    rep.fline("", F("⇒  C'[imax, j] = C[imin, j],  C'[imin, j] = C[imax, j]"), indent=0.6)


METHOD = [
    ("Для каждого столбца — поиск первых максимального и минимального элементов, их поиск в массиве A "
     "(досрочный выход при совпадении; минимум ищется, только если найден максимум) и перестановка:",
     ["cnt = 0",
      ["для j = {1..m}",
       "imax = 1;  imin = 1",
       ["для i = {2..n}", "imax = i,  если  C[i, j] > C[imax, j]", "imin = i,  если  C[i, j] < C[imin, j]"],
       "t = 1",
       ["пока  t ≤ k  и  A[t] ≠ C[imax, j]", "t = t + 1"],
       "s = 1  (поиск минимума выполняется, только если  t ≤ k)",
       ["пока  s ≤ k  и  A[s] ≠ C[imin, j]", "s = s + 1"],
       "(C[imax, j] ↔ C[imin, j],  cnt = cnt + 1),  если  t ≤ k  и  s ≤ k"]]),
]

SPEC = [
    ("label", "При cnt = 0"),
    ("box", ["Ни в одном столбце максимальный и минимальный элементы не присутствуют оба в A - "
             "матрица не изменилась."], True),
    ("label", "Иначе"),
    ("box", ["Переставлены максимальный и минимальный элементы в столбцах: <<col[1]>> … <<col[cnt]>>",
             "Преобразованная матрица C:", *mat_box("C")], True),
]

PSEUDO = """
_алг_ «Лабораторная работа №2, часть I, задание 5»
_нач_
	ввод(n, m, C[1:n, 1:m], k, A[1:k])
	вывод(C[1:n, 1:m], A[1:k])
	cnt := 0
	_цикл_ _от_ j := 1 _до_ m
		imax := 1; imin := 1
		_цикл_ _от_ i := 2 _до_ n
			_если_ C[i, j] > C[imax, j] _то_
				imax := i
			_всё_
			_если_ C[i, j] < C[imin, j] _то_
				imin := i
			_всё_
		_кц_
		t := 1
		_цикл-пока_ t ≤ k _и_ A[t] ≠ C[imax, j]
			t := t + 1
		_кц_
		_если_ t ≤ k _то_
			s := 1
			_цикл-пока_ s ≤ k _и_ A[s] ≠ C[imin, j]
				s := s + 1
			_кц_
			_если_ s ≤ k _то_
				c := C[imax, j]; C[imax, j] := C[imin, j]; C[imin, j] := c
				cnt := cnt + 1; col[cnt] := j
			_всё_
		_всё_
	_кц_
	_если_ cnt = 0 _то_
		вывод(«Ни в одном столбце максимальный и минимальный элементы не присутствуют оба в A - матрица не изменилась.»)
	_иначе_
		вывод(«Переставлены максимальный и минимальный элементы в столбцах: », col[1:cnt])
		вывод(«Преобразованная матрица C:», C[1:n, 1:m])
	_всё_
_кон_
"""


def _t(mat, arr, case):
    return Test(IN.lines(mat, arr), IN.shown(mat, arr), case)


TESTS = [
    _t([[5, 1, 7], [-2, 4, 3], [9, 0, -1]], [9, -2, 4, 0],
       "Столбцы 1 и 2: оба (max, min) есть в A – переставлены; столбец 3: нет"),
    _t([[1, 2], [3, 4]], [3, 2], "В каждом столбце есть только один из двух – матрица не меняется"),
    _t([[6, -6], [6, 2], [-1, 2]], [6, -1, 2, -6], "Все столбцы; берутся первые max/min из равных"),
    Test(["2 1", "3", "+", "-8", "0", "2", "3 -8"],
         ["n, m: 2 1", "строки: 3 / + / -8", "k: 0 / 2", "A: 3 -8"],
         "Недопустимые данные (знак без цифр, k = 0); один столбец"),
]

TASK = Task(
    part=1, num=5,
    statement=("Даны целочисленная матрица C[1:n, 1:m] и целочисленный массив A[1:k]. В каждом столбце матрицы C "
               "переставить местами максимальный и минимальный элементы, если они оба присутствуют в массиве A."),
    short="Перестановка максимума и минимума в столбцах",
    defines=IN.defines,
    decls=IN.decls + "    int t, s, c, imax, imin, cnt, col[NMAX + 1];\n",
    c_input=IN.c_input, c_solve=C_SOLVE, simulate=simulate,
    given=IN.given,
    result=["C[1:n, 1:m] – матрица, в каждом столбце которой переставлены первые максимальный и минимальный "
            "элементы, если они оба есть в массиве A, и номера таких столбцов, или сообщение «Ни в одном столбце "
            "максимальный и минимальный элементы не присутствуют оба в A – матрица не изменилась»."],
    when=IN.when, svyaz=svyaz, method=METHOD, spec=IN.spec + SPEC, pseudo=PSEUDO, tests=TESTS,
)
