"""Часть III лабы 3: повторяющиеся элементы массива A[0:n-1], обращение к элементам через указатель.

Первая функция (общая для всех задач) – count(a, n, x): сколько раз x встречается в a[0:n-1]; ею же проверяется
«первое вхождение» (count(a, i, a[i]) = 0 – элемента нет левее). Вторая функция – по варианту: удаление сдвигом
(без дополнительного массива) или формирование нового массива B.
"""
from ..core.task import Task
from ..core.cio import py_input_int, spec_input_int
from ..lab2.common import parse_line
from .shared import helpers, T, alg

COUNT = 7
INTRO = ("Дан целочисленный массив A[0:n-1]. К элементам массива обращаться при помощи указателя. Написать "
         "программу, включающую две функции с параметрами. В первой функции необходимо подсчитать количество "
         "повторений каждого элемента массива A. Вторая функция решает следующую задачу: ")
NMAX, AMAX = 20, 999

# mode: del – удаление из A сдвигом, new – новый массив B
# cond: условие (C / Python / текст) для удаляемого (del) или включаемого в B (new) элемента
VARIANTS = {
    1: dict(mode="del", func="remove_repeated",
            text="Удалить из массива A все повторяющиеся элементы путем сдвига (дополнительный массив не "
                 "использовать).",
            what="все повторяющиеся элементы (все их экземпляры)",
            example=([1, -2, 5, 1, 0, -2, -7, 3, 5], [0, -7, 3])),
    2: dict(mode="new", func="distinct", c="count(a, i, *(a + i)) == 0",
            py=lambda a, i: a[:i].count(a[i]) == 0, doc="count(A, i, A[i]) = 0",
            text="Сформировать новый массив, содержащий все различные элементы массива A по одному разу.",
            what="первые вхождения элементов (каждое различное значение – один раз)",
            example=([2, -1, 0, 7, 2, 7, 3, 3, 2], [2, -1, 0, 7, 3])),
    3: dict(mode="new", func="repeated", c="count(a, n, *(a + i)) > 1",
            py=lambda a, i: a.count(a[i]) > 1, doc="count(A, n, A[i]) > 1",
            text="Сформировать новый массив, состоящий из элементов, которые повторяются в массиве A.",
            what="все экземпляры повторяющихся элементов",
            example=([1, 8, 5, 1, 0, 8, 7, 3, 8], [1, 8, 1, 8, 8])),
    4: dict(mode="del", func="remove_unique", c="count(a, n, *(a + i)) == 1",
            py=lambda a, i: a.count(a[i]) == 1, doc="count(A, n, A[i]) = 1",
            text="Удалить из массива A все неповторяющиеся элементы путем сдвига (дополнительный массив не "
                 "использовать).",
            what="все неповторяющиеся элементы",
            example=([1, -2, 5, 7, 1, 0, -2], [1, -2, 1, -2])),
    5: dict(mode="new", func="repeated_once", c="count(a, n, *(a + i)) > 1 && count(a, i, *(a + i)) == 0",
            py=lambda a, i: a.count(a[i]) > 1 and a[:i].count(a[i]) == 0,
            doc="count(A, n, A[i]) > 1  и  count(A, i, A[i]) = 0",
            text="Сформировать новый массив, содержащий повторяющиеся элементы массива A. Элементы в новом "
                 "массиве не должны повторяться.",
            what="повторяющиеся элементы, каждый по одному разу",
            example=([9, 1, -2, 5, -2, 1, 0, -2, 1], [1, -2])),
    6: dict(mode="new", func="unique_odd", c="count(a, n, *(a + i)) == 1 && *(a + i) % 2 != 0",
            py=lambda a, i: a.count(a[i]) == 1 and a[i] % 2 != 0,
            doc="count(A, n, A[i]) = 1  и  A[i] mod 2 ≠ 0",
            text="Сформировать новый массив, содержащий неповторяющиеся нечетные элементы массива A.",
            what="неповторяющиеся нечётные элементы",
            example=([1, -3, 5, 7, -2, 0, 0, -2, 1], [-3, 5, 7])),
    7: dict(mode="new", func="unique", c="count(a, n, *(a + i)) == 1",
            py=lambda a, i: a.count(a[i]) == 1, doc="count(A, n, A[i]) = 1",
            text="Сформировать новый массив, состоящий из элементов, которые не повторяются в массиве A.",
            what="неповторяющиеся элементы",
            example=([2, -2, 0, 4, 7, 4, 0], [2, -2, 7])),
}

COMMON = r'''
/* Ввод длины n и элементов массива A. Возвращает 0 при конце ввода. */
int input(int *a, int *n){
    int ok;
    if (!input_int("длину массива n", 1, NMAX, n)) return 0;
    do{
        printf("Введите массив A: %d целых чисел от %d до %d "
               "через пробел: ", *n, -AMAX, AMAX);
        ok = read_line(a, *n, -AMAX, AMAX);
        if (ok == -1) return 0;
        if (!ok)
            printf("Ошибка! Нужно ввести %d целых чисел от %d до %d.\n",
                   *n, -AMAX, AMAX);
    } while (!ok);
    return 1;
}

/* Вывод массива a[0:n-1] после заголовка title */
void print_array(const char *title, const int *a, int n){
    const int *p;
    printf("%s", title);
    for (p = a; p < a + n; p++)
        printf("%d ", *p);
    printf("\n");
}

/* Функция 1: количество повторений числа x в массиве a[0:n-1] */
int count(const int *a, int n, int x){
    const int *p;
    int c = 0;
    for (p = a; p < a + n; p++)
        if (*p == x) c++;
    return c;
}

/* Вывод количества повторений каждого элемента массива (по функции 1) */
void print_counts(const int *a, int n){
    int i;
    printf("A[i]:       ");
    for (i = 0; i < n; i++)
        printf("%5d", *(a + i));
    printf("\nповторений: ");
    for (i = 0; i < n; i++)
        printf("%5d", count(a, n, *(a + i)));
    printf("\n");
}
'''

FUNC2 = {
    "remove_repeated": r'''
/* Функция 2: удаление сдвигом всех повторяющихся элементов (вместе со всеми их
   экземплярами, без дополнительного массива); возвращает новую длину массива */
int remove_repeated(int *a, int n){
    int i = 0, j, k, x;
    while (i < n)
        if (count(a, n, *(a + i)) > 1){
            x = *(a + i);
            j = i;
            while (j < n)                     /* удаляем все элементы, равные x */
                if (*(a + j) == x){
                    for (k = j; k < n - 1; k++)
                        *(a + k) = *(a + k + 1);
                    n--;
                }
                else j++;
        }
        else i++;
    return n;
}
''',
    "remove_unique": r'''
/* Функция 2: удаление сдвигом всех неповторяющихся элементов (без дополнительного
   массива); возвращает новую длину массива */
int remove_unique(int *a, int n){
    int i = 0, k;
    while (i < n)
        if (count(a, n, *(a + i)) == 1){
            for (k = i; k < n - 1; k++)
                *(a + k) = *(a + k + 1);
            n--;
        }
        else i++;
    return n;
}
''',
}


def _new_func(name, cond, what):
    return f'''
/* Функция 2: новый массив b, в который входят
   {what};
   возвращает число элементов b */
int {name}(const int *a, int n, int *b){{
    int i, k = 0;
    for (i = 0; i < n; i++)
        if ({cond}){{
            *(b + k) = *(a + i);
            k++;
        }}
    return k;
}}
'''


class Variant:
    def __init__(self, num, mode, func, text, what, example, c=None, py=None, doc=None):
        self.num, self.mode, self.func, self.text, self.what, self.example = num, mode, func, text, what, example
        self.c, self.py, self.doc = c, py, doc

    # ------------------------------------------------------------------ C
    def functions(self):
        f2 = FUNC2[self.func] if self.mode == "del" else _new_func(self.func, self.c, self.what)
        out = (r'''
/* Вывод результата */
void output(const int *b, int k){
    if (k == 0)
        printf("\nНовый массив B пуст - подходящих элементов нет.\n");
    else{
        printf("\nНовый массив B (%d эл.): ", k);
        print_array("", b, k);
    }
}
''' if self.mode == "new" else r'''
/* Вывод результата */
void output(const int *a, int k){
    if (k == 0)
        printf("\nПосле удаления массив A пуст.\n");
    else{
        printf("\nМассив A после удаления (%d эл.): ", k);
        print_array("", a, k);
    }
}
''')
        return helpers() + COMMON + f2 + out

    def body(self):
        call = (f"    k = {self.func}(A, n, B);\n    output(B, k);\n" if self.mode == "new"
                else f"    k = {self.func}(A, n);\n    output(A, k);\n")
        return ('    if (!input(A, &n)) return 1;\n'
                '    print_array("\\nМассив A: ", A, n);\n'
                '    print_counts(A, n);\n' + call)

    # ------------------------------------------------------------------ Python
    def simulate(self, con):
        n = py_input_int(con, "длину массива n", 1, NMAX)
        while True:
            con.printf("Введите массив A: %d целых чисел от %d до %d через пробел: " % (n, -AMAX, AMAX))
            ok, a = parse_line(con.readline(), n, -AMAX, AMAX)
            if ok:
                break
            con.printf("Ошибка! Нужно ввести %d целых чисел от %d до %d.\n" % (n, -AMAX, AMAX))
        con.printf("\nМассив A: " + "".join(f"{v} " for v in a) + "\n")
        con.begin_results()
        con.printf("A[i]:       " + "".join("%5d" % v for v in a)
                   + "\nповторений: " + "".join("%5d" % a.count(v) for v in a) + "\n")
        if self.mode == "new":
            b = [a[i] for i in range(n) if self.py(a, i)]
            if not b:
                con.printf("\nНовый массив B пуст - подходящих элементов нет.\n")
            else:
                con.printf("\nНовый массив B (%d эл.): " % len(b) + "".join(f"{v} " for v in b) + "\n")
        else:
            if self.func == "remove_repeated":
                b = [v for v in a if a.count(v) == 1]
            else:
                b = [v for v in a if a.count(v) > 1]
            if not b:
                con.printf("\nПосле удаления массив A пуст.\n")
            else:
                con.printf("\nМассив A после удаления (%d эл.): " % len(b) + "".join(f"{v} " for v in b) + "\n")

    # ------------------------------------------------------------------ документы
    def formulas(self, rep):
        a, b = self.example
        res = "A[0:k-1]" if self.mode == "del" else "B[0:k-1]"
        rep.para(f"Пример: A[0:n-1] = {' '.join(map(str, a))}  →  {res} = {' '.join(map(str, b))}.", after=4)

    def svyaz(self, rep):
        from ..core.omml import m
        rep.fline("", m("count(x) = |{ i ∈ [0 : n − 1] :  A[i] = x }|  – число повторений x в A;"))
        if self.func == "remove_repeated":
            rep.fline("", m("A′[0:k−1] – элементы A с count(A[i]) = 1 в исходном порядке"))
        elif self.func == "remove_unique":
            rep.fline("", m("A′[0:k−1] – элементы A с count(A[i]) > 1 в исходном порядке"))
        else:
            rep.para("B[0:k−1] – элементы A[i] (i = 0, 1, …, n − 1, в исходном порядке), для которых выполнено "
                     "условие:", after=2)
            rep.fline("", m(self.doc), indent=0.6)
            if "count(A, i" in self.doc:
                rep.para("(count(A, i, A[i]) – число таких же элементов левее A[i]; 0 – первое вхождение).",
                         after=4)

    def method(self):
        items = [("Первая функция count(a, n, x) – количество повторений числа x в массиве a[0:n−1] (обход "
                  "указателем p от a до a + n − 1); она вызывается для каждого элемента:",
                  ["c = 0", ["для p = {a..a + n − 1}", "c = c + 1,  если  *p = x"], "count(a, n, x) = c"])]
        if self.func == "remove_repeated":
            items.append(("Вторая функция – удаление сдвигом: если элемент повторяется, из массива удаляются все "
                          "элементы, равные ему (у остальных значений число повторений не меняется):",
                          ["i = 0",
                           ["пока  i < n",
                            ["если  count(a, n, a[i]) > 1",
                             "x = a[i];  удалить сдвигом все a[j] = x,  j = {i..n − 1}"],
                            "иначе  i = i + 1"]]))
            items.append(("Удаление элемента a[j] сдвигом:",
                          [["для t = {j..n − 2}", "a[t] = a[t + 1]"], "n = n − 1"]))
        elif self.func == "remove_unique":
            items.append(("Вторая функция – удаление сдвигом неповторяющихся элементов (удаление такого элемента "
                          "не меняет число повторений остальных):",
                          ["i = 0",
                           ["пока  i < n",
                            ["если  count(a, n, a[i]) = 1",
                             ["для t = {i..n − 2}", "a[t] = a[t + 1]"], "n = n − 1"],
                            "иначе  i = i + 1"]]))
        else:
            short = self.doc.replace("count(A, n, A[i])", "c").replace("count(A, i, A[i])", "l").replace("A[i]", "a[i]")
            calc = "c = count(a, n, a[i])" if "c" in short.split() else ""
            if " l " in f" {short} ":
                calc = (calc + ";  " if calc else "") + "l = count(a, i, a[i])"
            items.append((f"Вторая функция – новый массив b: {self.what} (c – число повторений a[i], "
                          "l – число таких же элементов левее a[i]):",
                          ["k = 0", ["для i = {0..n − 1}", calc, f"(b[k] = a[i],  k = k + 1),  если  {short}"]]))
        return items

    def spec(self):
        res = ([("label", "При k = 0"), ("box", ["Новый массив B пуст - подходящих элементов нет."], True),
                ("label", "Иначе"), ("box", ["Новый массив B (<<k>> эл.): <<B[0]>> <<B[1]>> … <<B[k−1]>>"], True)]
               if self.mode == "new" else
               [("label", "При k = 0"), ("box", ["После удаления массив A пуст."], True),
                ("label", "Иначе"),
                ("box", ["Массив A после удаления (<<k>> эл.): <<A[0]>> <<A[1]>> … <<A[k−1]>>"], True)])
        return (spec_input_int("длину массива n", 1, "NMAX", "n") + [
            ("rep_start",),
            ("box", ["Введите массив A: <<n>> целых чисел от <<-AMAX>> до <<AMAX>> через пробел: "
                     "<A[0]> <A[1]> … <A[n−1]>"], False),
            ("label", "При ошибке ввода (не числа, не то количество, вне диапазона)"),
            ("box", ["Ошибка! Нужно ввести <<n>> целых чисел от <<-AMAX>> до <<AMAX>>."], True),
            ("rep_end", "До A[0:n−1] введён верно"),
            ("box", ["Массив A: <<A[0]>> <<A[1]>> … <<A[n−1]>>"], False),
            ("box", ["A[i]:       <<A[0]>> <<A[1]>> … <<A[n−1]>>",
                     "повторений: <<count(A[0])>> <<count(A[1])>> … <<count(A[n−1])>>"], False),
        ] + res)

    def pseudo(self):
        head = f"""
_функция_ count(a, n, x)
_нач_
	c := 0
	_цикл от_ i := 0 _до_ n − 1
		_если_ a[i] = x _то_
			c := c + 1
		_всё_
	_кц_
	_возврат_ c
_кон_
"""
        if self.func == "remove_repeated":
            f2 = """
_функция_ remove_repeated(a, n)
_нач_
	i := 0
	_цикл-пока_ i < n
		_если_ count(a, n, a[i]) > 1 _то_
			x := a[i]; j := i
			_цикл-пока_ j < n
				_если_ a[j] = x _то_
					_цикл от_ t := j _до_ n − 2
						a[t] := a[t + 1]
					_кц_
					n := n − 1
				_иначе_
					j := j + 1
				_всё_
			_кц_
		_иначе_
			i := i + 1
		_всё_
	_кц_
	_возврат_ n
_кон_
"""
        elif self.func == "remove_unique":
            f2 = """
_функция_ remove_unique(a, n)
_нач_
	i := 0
	_цикл-пока_ i < n
		_если_ count(a, n, a[i]) = 1 _то_
			_цикл от_ t := i _до_ n − 2
				a[t] := a[t + 1]
			_кц_
			n := n − 1
		_иначе_
			i := i + 1
		_всё_
	_кц_
	_возврат_ n
_кон_
"""
        else:
            cond = self.doc.replace("A[i]", "a[i]").replace("A, ", "a, ").replace("  и  ", " _и_ ")
            f2 = f"""
_функция_ {self.func}(a, n, b)
_нач_
	k := 0
	_цикл от_ i := 0 _до_ n − 1
		_если_ {cond} _то_
			b[k] := a[i]; k := k + 1
		_всё_
	_кц_
	_возврат_ k
_кон_
"""
        call = (f"k := {self.func}(A, n, B)\n\t_если_ k = 0 _то_\n\t\tвывод(«Новый массив B пуст - подходящих "
                f"элементов нет.»)\n\t_иначе_\n\t\tвывод(«Новый массив B (», k, « эл.): », B[0:k−1])\n\t_всё_"
                if self.mode == "new" else
                f"k := {self.func}(A, n)\n\t_если_ k = 0 _то_\n\t\tвывод(«После удаления массив A пуст.»)\n"
                f"\t_иначе_\n\t\tвывод(«Массив A после удаления (», k, « эл.): », A[0:k−1])\n\t_всё_")
        return head + f2 + f"""
{alg("III", self.num)}
_нач_
	ввод(n, A[0:n−1])
	вывод(«Массив A: », A[0:n−1])
	_цикл от_ i := 0 _до_ n − 1
		вывод(count(A, n, A[i]))
	_кц_
	{call}
_кон_
"""

    # ------------------------------------------------------------------ тесты
    def tests(self):
        def t(arr, case):
            return T([str(len(arr)), " ".join(map(str, arr))], [f"n = {len(arr)}", "A = " + " ".join(map(str, arr))],
                     case)
        a, _ = self.example
        bad = ["0", "21", "x", "2.5", "6", "1 2 3", "1 2 3 4 5 1000", "1 a 3 4 5 6", "4 -4 7 4 0 7"]
        return [
            t(a, "Пример из практикума"),
            t([4, -7, 0, 9, 2, 13], "Все элементы различны"),
            t([3, 3, -1, -1, 3, 5, 5], "Все элементы повторяются"),
            T(bad, ["n: 0 / 21 / x / 2.5 / 6", "A: мало чисел / 1000 / буква / 4 −4 7 4 0 7"],
              "Недопустимые данные: n вне диапазона, строка, вещественное; ошибки в массиве"),
        ]

    def task(self):
        res = ("k, A[0:k−1] – массив A после удаления: " if self.mode == "del" else "k, B[0:k−1] – новый массив: ")
        return Task(
            lab=3, part="III", num=self.num, statement=self.text, includes=[],
            defines=f"#define NMAX {NMAX}         /* максимальная длина массива */\n"
                    f"#define AMAX {AMAX}        /* максимальный модуль элемента */",
            functions=self.functions(),
            decls="    int A[NMAX], n, k;\n" + ("    int B[NMAX];\n" if self.mode == "new" else ""),
            body=self.body(), simulate=self.simulate,
            given=["n, A[0:n−1] – целочисленный массив."],
            result=["count(A[i]), i = 0, …, n − 1 – количество повторений каждого элемента массива A;",
                    res + self.what + ", в исходном порядке; или сообщение, что массив пуст."],
            when=[f"n ∈ N, n ≤ NMAX = {NMAX}; A[i] ∈ Z, |A[i]| ≤ AMAX = {AMAX}."],
            svyaz=self.svyaz, method=self.method(), spec=self.spec(), pseudo=self.pseudo(), tests=self.tests(),
            formulas=self.formulas, file="lab3_part3.c",
            note="К элементам массивов функции обращаются через указатель: запись *(a + i) означает a[i], "
                 "в функциях count и print_array указатель p пробегает от a до a + n − 1.",
        )


_cache = {}


def get(num):
    if num not in VARIANTS:
        raise ModuleNotFoundError(num)
    if num not in _cache:
        _cache[num] = Variant(num, **VARIANTS[num]).task()
    return _cache[num]
