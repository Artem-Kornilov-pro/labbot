from ..common import Task, Test
from ..inputs import MatrixArray
from .shared import c_find, py_find, c_print_list, py_print_list, c_print_mat, py_print_mat, mat_box
from ....docx_engine import F

IN = MatrixArray("Y", "A")

C_SOLVE = f'''    /* в каждой строке - первые минимальный и максимальный элементы */
    cnt = 0;
    rc = 0;
    for (i = 1; i <= n; i++){{
        jmin = 1;
        jmax = 1;
        for (j = 2; j <= m; j++){{
            if (Y[i][j] < Y[i][jmin]) jmin = j;
            if (Y[i][j] > Y[i][jmax]) jmax = j;
        }}
        {c_find("A", "k", "Y[i][jmin]")}
        if (t > k){{                       /* минимума нет в A - ищем максимум */
            {c_find("A", "k", "Y[i][jmax]", "s").replace(chr(10) + "        ", chr(10) + "            ")}
            if (s > k){{                   /* оба отсутствуют - обнуляем и запоминаем */
                cnt++;
                R[cnt] = Y[i][jmin];
                Y[i][jmin] = 0;
                if (jmax != jmin){{
                    cnt++;
                    R[cnt] = Y[i][jmax];
                    Y[i][jmax] = 0;
                }}
                rc++;
                row[rc] = i;
            }}
        }}
    }}

    if (rc == 0)
        printf("\\nНи в одной строке минимальный и максимальный элементы не отсутствуют "
               "оба в A - матрица не изменилась.\\n");
    else{{
        printf("\\nОбнулены минимальный и максимальный элементы в строках: ");
        for (t = 1; t <= rc; t++)
            printf("%d ", row[t]);
        printf("\\n");
{c_print_mat("Y", "n", "m", "Преобразованная матрица Y:")}
{c_print_list("Обнулённые элементы: ", "R", "cnt")}
    }}
'''


def simulate(con):
    n, m, Y, k, A = IN.read(con)
    con.begin_results()
    R, rows = [], []
    for i in range(1, n + 1):
        jmin = jmax = 1
        for j in range(2, m + 1):
            if Y[i][j] < Y[i][jmin]:
                jmin = j
            if Y[i][j] > Y[i][jmax]:
                jmax = j
        if py_find(A, k, Y[i][jmin]) > k and py_find(A, k, Y[i][jmax]) > k:
            R.append(Y[i][jmin])
            Y[i][jmin] = 0
            if jmax != jmin:
                R.append(Y[i][jmax])
                Y[i][jmax] = 0
            rows.append(i)
    if not rows:
        con.printf("\nНи в одной строке минимальный и максимальный элементы не отсутствуют оба в A - "
                   "матрица не изменилась.\n")
    else:
        py_print_list(con, "\nОбнулены минимальный и максимальный элементы в строках: ", rows)
        py_print_mat(con, Y, n, m, "Преобразованная матрица Y:")
        py_print_list(con, "Обнулённые элементы: ", R)


def svyaz(rep):
    rep.fline("1. ", F("∀ i = {1..n}:  ∃ jmin, jmax ∈ [1:m]:"))
    rep.fline("", F("∀ j = {1..m}: Y[i, jmin] ≤ Y[i, j] ≤ Y[i, jmax]"), indent=0.6)
    rep.para("(jmin, jmax – первые по порядку минимальный и максимальный элементы строки);", indent=0.6)
    rep.fline("2. ", F("(∀ t: A[t] ≠ Y[i, jmin])  и  (∀ s: A[s] ≠ Y[i, jmax])  ⇒"))
    rep.fline("", F("⇒  Y'[i, jmin] = Y'[i, jmax] = 0,"), indent=0.6)
    rep.fline("", F("Y[i, jmin], Y[i, jmax] ∈ R[1:cnt]"), indent=0.6)


METHOD = [
    ("Для каждой строки — поиск первых минимального и максимального элементов, их поиск в массиве A "
     "(досрочный выход при совпадении; максимум ищется, только если минимума нет в A), обнуление и запоминание:",
     ["cnt = 0;  rc = 0",
      ["для i = {1..n}",
       "jmin = 1;  jmax = 1",
       ["для j = {2..m}", "jmin = j,  если  Y[i, j] < Y[i, jmin]", "jmax = j,  если  Y[i, j] > Y[i, jmax]"],
       "t = 1",
       ["пока  t ≤ k  и  A[t] ≠ Y[i, jmin]", "t = t + 1"],
       "s = 1  (поиск максимума выполняется, только если  t > k)",
       ["пока  s ≤ k  и  A[s] ≠ Y[i, jmax]", "s = s + 1"],
       "(R[cnt + 1] = Y[i, jmin],  Y[i, jmin] = 0),  если  t > k  и  s > k",
       "(R[cnt + 2] = Y[i, jmax],  Y[i, jmax] = 0),  если  t > k  и  s > k",
       "(cnt = cnt + 2,  rc = rc + 1),  если  t > k  и  s > k"]]),
]

SPEC = [
    ("label", "При rc = 0"),
    ("box", ["Ни в одной строке минимальный и максимальный элементы не отсутствуют оба в A - "
             "матрица не изменилась."], True),
    ("label", "Иначе"),
    ("box", ["Обнулены минимальный и максимальный элементы в строках: <<row[1]>> … <<row[rc]>>",
             "Преобразованная матрица Y:", *mat_box("Y"), "Обнулённые элементы: <<R[1]>> <<R[2]>> … <<R[cnt]>>"],
     True),
]

PSEUDO = """
_алг_ «Лабораторная работа №2, часть I, задание 14»
_нач_
	ввод(n, m, Y[1:n, 1:m], k, A[1:k])
	вывод(Y[1:n, 1:m], A[1:k])
	cnt := 0; rc := 0
	_цикл_ _от_ i := 1 _до_ n
		jmin := 1; jmax := 1
		_цикл_ _от_ j := 2 _до_ m
			_если_ Y[i, j] < Y[i, jmin] _то_
				jmin := j
			_всё_
			_если_ Y[i, j] > Y[i, jmax] _то_
				jmax := j
			_всё_
		_кц_
		t := 1
		_цикл-пока_ t ≤ k _и_ A[t] ≠ Y[i, jmin]
			t := t + 1
		_кц_
		_если_ t > k _то_
			s := 1
			_цикл-пока_ s ≤ k _и_ A[s] ≠ Y[i, jmax]
				s := s + 1
			_кц_
			_если_ s > k _то_
				cnt := cnt + 1; R[cnt] := Y[i, jmin]; Y[i, jmin] := 0
				_если_ jmax ≠ jmin _то_
					cnt := cnt + 1; R[cnt] := Y[i, jmax]; Y[i, jmax] := 0
				_всё_
				rc := rc + 1; row[rc] := i
			_всё_
		_всё_
	_кц_
	_если_ rc = 0 _то_
		вывод(«Ни в одной строке минимальный и максимальный элементы не отсутствуют оба в A - матрица не изменилась.»)
	_иначе_
		вывод(«Обнулены минимальный и максимальный элементы в строках: », row[1:rc])
		вывод(«Преобразованная матрица Y:», Y[1:n, 1:m])
		вывод(«Обнулённые элементы: », R[1:cnt])
	_всё_
_кон_
"""


def _t(mat, arr, case):
    return Test(IN.lines(mat, arr), IN.shown(mat, arr), case)


TESTS = [
    _t([[4, -1, 8], [2, 5, 3], [0, 6, -7]], [2],
       "Строки 1 и 3: min и max отсутствуют в A – обнулены; строка 2: min = 2 есть в A"),
    _t([[1, 9], [3, 3]], [1, 3], "В каждой строке min или max есть в A – матрица не меняется"),
    _t([[5], [-2]], [0], "Один столбец: min = max – обнуляется один элемент в каждой строке"),
    Test(["1 3", "1 2 3 abc", "1 2 3", "2", "3 4"], ["n, m: 1 3", "строка 1: 1 2 3 abc / 1 2 3", "k: 2", "A: 3 4"],
         "Недопустимые данные (текст после чисел); max = 3 есть в A"),
]

TASK = Task(
    part=1, num=14,
    statement=("Даны целочисленная матрица Y[1:n, 1:m] и целочисленный массив A[1:k]. В каждой строке матрицы Y "
               "обнулить минимальный и максимальный элементы, если они оба отсутствуют в массиве A. Сохранить "
               "обнулённые элементы в новом массиве."),
    short="Обнуление минимума и максимума строк, отсутствующих в массиве",
    defines=IN.defines,
    decls=IN.decls + "    int t, s, jmin, jmax, cnt, rc, R[2 * NMAX + 1], row[NMAX + 1];\n",
    c_input=IN.c_input, c_solve=C_SOLVE, simulate=simulate,
    given=IN.given,
    result=["Y[1:n, 1:m] – матрица, в строках которой обнулены первые минимальный и максимальный элементы, если "
            "оба отсутствуют в массиве A (при m = 1 это один и тот же элемент); R[1:cnt] – массив обнулённых "
            "элементов; номера таких строк, или сообщение «Ни в одной строке минимальный и максимальный элементы "
            "не отсутствуют оба в A – матрица не изменилась»."],
    when=IN.when, svyaz=svyaz, method=METHOD, spec=IN.spec + SPEC, pseudo=PSEUDO, tests=TESTS,
)
