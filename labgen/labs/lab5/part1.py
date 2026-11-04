"""Часть I лабы 5: двоичный файл действительных чисел, вводимых с клавиатуры; чтение файла и вычисление.

Двенадцать задач различаются условием отбора чисел (положительные, отрицательные, с чётными/нечётными номерами,
все) и вычисляемой величиной (min, max, сумма, произведение, среднее, количество, max/min по модулю).
"""
from ..core.task import Task, Test
from ..core.cio import (C_READ_LINE, C_INPUT_INT, C_READ_REALS, C_INPUT_REALS, RMAX, py_input_int,
                        py_input_reals, spec_input_int, spec_input_reals)
from .shared import NAME_DEFINES, NAME_FUNCS, CRT, py_input_name, can_create, spec_name

COUNT = 12
INTRO = "Создать файл для хранения действительных чисел, вводимых с клавиатуры. Прочитать этот файл и вычислить: "
NMAX = 50

# фильтр: C-условие, Python, текст для «Связи», сообщение «нет чисел» («» – подходящие числа есть всегда)
FILTERS = {
    "pos": ("x > 0", lambda i, x: x > 0, "xi > 0", "Положительных чисел в файле нет"),
    "neg": ("x < 0", lambda i, x: x < 0, "xi < 0", "Отрицательных чисел в файле нет"),
    "even": ("i % 2 == 0", lambda i, x: i % 2 == 0, "i mod 2 = 0", "Чисел с чётными номерами в файле нет"),
    # первое число всегда имеет нечётный номер – результат существует при любом n ≥ 1
    "odd": ("i % 2 == 1", lambda i, x: i % 2 == 1, "i mod 2 = 1", ""),
    "all": (None, lambda i, x: True, "", ""),
}
# величина: начальное значение r, C-обновление, псевдокод, формула для «Связи»
AGGS = {
    "min": ("0", "if (cnt == 0 || x < *r) *r = x;", "_если_ cnt = 0 _или_ x < r _то_ r := x _всё_", "min"),
    "max": ("0", "if (cnt == 0 || x > *r) *r = x;", "_если_ cnt = 0 _или_ x > r _то_ r := x _всё_", "max"),
    "sum": ("0", "*r = *r + x;", "r := r + x", "∑"),
    "prod": ("1", "*r = *r * x;", "r := r · x", "∏"),
    "mean": ("0", "*r = *r + x;", "r := r + x", "mean"),
    "count": ("0", "", "", "count"),
    "maxabs": ("0", "if (cnt == 0 || fabs(x) > fabs(*r)) *r = x;",
               "_если_ cnt = 0 _или_ |x| > |r| _то_ r := x _всё_", "maxabs"),
    "minabs": ("0", "if (cnt == 0 || fabs(x) < fabs(*r)) *r = x;",
               "_если_ cnt = 0 _или_ |x| < |r| _то_ r := x _всё_", "minabs"),
}

VARIANTS = {
    1: ("минимальное положительное число", "pos", "min", "Минимальное положительное число"),
    2: ("сумму положительных чисел", "pos", "sum", "Сумма положительных чисел"),
    3: ("произведение отрицательных чисел", "neg", "prod", "Произведение отрицательных чисел"),
    4: ("среднее арифметическое положительных чисел", "pos", "mean", "Среднее арифметическое положительных чисел"),
    5: ("максимальное среди отрицательных чисел", "neg", "max", "Максимальное среди отрицательных чисел"),
    6: ("среднее арифметическое отрицательных чисел", "neg", "mean", "Среднее арифметическое отрицательных чисел"),
    7: ("минимальное число среди чисел с четными номерами", "even", "min",
         "Минимальное среди чисел с чётными номерами"),
    8: ("количество положительных чисел", "pos", "count", "Количество положительных чисел"),
    9: ("максимальное по абсолютной величине", "all", "maxabs", "Максимальное по абсолютной величине число"),
    10: ("максимальное число среди чисел с нечетными номерами", "odd", "max",
          "Максимальное среди чисел с нечётными номерами"),
    11: ("произведение положительных чисел", "pos", "prod", "Произведение положительных чисел"),
    12: ("минимальное по абсолютной величине число", "all", "minabs", "Минимальное по абсолютной величине число"),
}

DEFINES = (f"#define NMAX {NMAX}                      /* наибольшее количество чисел */\n"
           f"#define RMAX {RMAX}                    /* максимальный модуль числа */\n" + NAME_DEFINES)

COMMON = r'''
/* Создание двоичного файла name: n чисел вводятся с клавиатуры и сразу записываются
   в файл. Возвращает 1 - файл создан, 0 - конец ввода, -1 - файл не удалось создать */
int create_file(const char *name){
    FILE *f;
    char what[16];
    double x;
    int n, i;
    f = fopen(name, "wb");
    if (f == NULL) return -1;
    if (!input_int("количество чисел n", 1, NMAX, &n)){
        fclose(f);
        return 0;
    }
    for (i = 1; i <= n; i++){
        sprintf(what, "x%d", i);
        if (!input_reals(what, 1, -RMAX, RMAX, &x)){
            fclose(f);
            return 0;
        }
        fwrite(&x, sizeof(double), 1, f);
    }
    fclose(f);
    return 1;
}

/* Вывод чисел, прочитанных из двоичного файла name */
void print_file(const char *name){
    FILE *f = fopen(name, "rb");
    double x;
    if (f == NULL) return;
    printf("\nЧисла из файла \"%s\":", name);
    while (fread(&x, sizeof(double), 1, f) == 1)
        printf(" %g", x);
    printf("\n");
    fclose(f);
}
'''


class Variant:
    def __init__(self, num, text, filt, agg, cap):
        self.num, self.text, self.filt, self.agg, self.cap = num, text, filt, agg, cap
        self.f_c, self.f_py, self.f_doc, self.none = FILTERS[filt]
        self.init, self.upd, self.upd_ps, self.op = AGGS[agg]

    # ------------------------------------------------------------------ C
    def functions(self):
        idx = self.filt in ("even", "odd")
        decl = "    int i = 0, cnt = 0;\n" if idx else "    int cnt = 0;\n"
        step = "        i++;\n" if idx else ""
        upd = f"{self.upd}\n" if self.upd else ""
        if self.f_c:
            loop = f"{step}        if ({self.f_c}){{\n" + (f"            {upd}" if upd else "") + \
                "            cnt++;\n        }\n"
        else:
            loop = f"{step}        {upd}        cnt++;\n"
        mean = "    if (cnt > 0) *r = *r / cnt;\n" if self.agg == "mean" else ""
        if self.agg == "count":
            out = f'''/* Вывод результата */
void output(int cnt){{
    printf("\\n{self.cap}: %d\\n", cnt);
}}
'''
        else:
            none = f'''        printf("\\n{self.none} - результат не существует.\\n");\n''' if self.none else ""
            out = f'''/* Вывод результата: cnt - сколько чисел участвовало в вычислении */
void output(int cnt, double r){{
''' + (f"    if (cnt == 0)\n{none}    else\n        printf(\"\\n{self.cap}: %g\\n\", r);\n" if self.none else
       f"    if (cnt > 0) printf(\"\\n{self.cap}: %g\\n\", r);\n") + "}\n"
        proc = f'''
/* Чтение двоичного файла name и вычисление:
   {self.text}.
   Возвращает количество чисел, участвовавших в вычислении (r - результат) */
int process(const char *name, double *r){{
    FILE *f = fopen(name, "rb");
    double x;
{decl}    *r = {self.init};
    if (f == NULL) return 0;
    while (fread(&x, sizeof(double), 1, f) == 1){{
{loop}    }}
    fclose(f);
{mean}    return cnt;
}}

'''
        return "\n".join([C_READ_LINE, C_INPUT_INT, C_READ_REALS, C_INPUT_REALS, NAME_FUNCS]) + COMMON + proc + out

    def body(self):
        call = "    output(cnt);\n" if self.agg == "count" else "    output(cnt, r);\n"
        return f'''    do{{
        if (!input_name("двоичного файла", name)) return 1;
        res = create_file(name);
        if (res == 0) return 1;
        if (res == -1) printf("Ошибка! Не удалось создать файл \\"%s\\".\\n", name);
    }} while (res == -1);
    print_file(name);
    cnt = process(name, &r);
{call}'''

    # ------------------------------------------------------------------ Python
    def simulate(self, con):
        while True:
            name = py_input_name(con, "двоичного файла")
            if can_create(name):
                break
            con.printf(f'Ошибка! Не удалось создать файл "{name}".\n')
        n = py_input_int(con, "количество чисел n", 1, NMAX)
        xs = [py_input_reals(con, f"x{i}", 1, -RMAX, RMAX)[0] for i in range(1, n + 1)]
        con.files[name] = xs
        con.begin_results()
        con.printf(f'\nЧисла из файла "{name}":' + "".join(" %g" % x for x in con.files[name]) + "\n")
        r = 1.0 if self.agg == "prod" else 0.0
        cnt = 0
        for i, x in enumerate(con.files[name], 1):
            if not self.f_py(i, x):
                continue
            a = self.agg
            if (a == "min" and (cnt == 0 or x < r)) or (a == "max" and (cnt == 0 or x > r)) \
                    or (a == "maxabs" and (cnt == 0 or abs(x) > abs(r))) \
                    or (a == "minabs" and (cnt == 0 or abs(x) < abs(r))):
                r = x
            elif a in ("sum", "mean"):
                r = r + x
            elif a == "prod":
                r = r * x
            cnt += 1
        if self.agg == "mean" and cnt > 0:
            r = r / cnt
        if self.agg == "count":
            con.printf(f"\n{self.cap}: %d\n" % cnt)
        elif cnt == 0:
            if self.none:
                con.printf(f"\n{self.none} - результат не существует.\n")
        else:
            con.printf(f"\n{self.cap}: %g\n" % r)

    # ------------------------------------------------------------------ документы
    def relation(self):
        f = f",  {self.f_doc}" if self.f_doc else ""
        rng = f"i = 1..n{f}"
        return {
            "min": f"r = min {{ xi :  {rng} }}", "max": f"r = max {{ xi :  {rng} }}",
            "sum": f"r = ∑ xi,  {rng}", "prod": f"r = ∏ xi,  {rng}",
            "mean": f"r = (∑ xi) / cnt,  {rng},  cnt – число таких xi",
            "count": f"cnt = |{{ i ∈ [1 : n] :  {self.f_doc} }}|",
            "maxabs": "r = xk:  |xk| = max |xi|,  i = 1..n  (k – наименьший такой номер)",
            "minabs": "r = xk:  |xk| = min |xi|,  i = 1..n  (k – наименьший такой номер)",
        }[self.agg]

    def svyaz(self, rep):
        from ..core.omml import m
        rep.para("Файл name после создания содержит числа x1, x2, …, xn в порядке ввода (тип double, двоичный "
                 "вид); при чтении i – номер числа в файле:", after=2)
        rep.fline("", m(self.relation()))
        if self.none and self.agg != "count":
            rep.para("Результат не существует, если в файле нет чисел, удовлетворяющих условию.", after=4)

    def method(self):
        upd = {
            "min": "r = x,  если  cnt = 0  или  x < r", "max": "r = x,  если  cnt = 0  или  x > r",
            "sum": "r = r + x", "prod": "r = r · x", "mean": "r = r + x", "count": "",
            "maxabs": "r = x,  если  cnt = 0  или  |x| > |r|", "minabs": "r = x,  если  cnt = 0  или  |x| < |r|",
        }[self.agg]
        body = [upd, "cnt = cnt + 1"] if upd else ["cnt = cnt + 1"]
        cond = self.f_doc.replace("xi", "x")
        loop = ["пока  из файла прочитано число x"] + (["i = i + 1"] if self.filt in ("even", "odd") else []) + \
            ([[f"если  {cond}"] + body] if cond else body)
        items = [f"cnt = 0;  r = {self.init}" + (";  i = 0" if self.filt in ("even", "odd") else ""), loop]
        if self.agg == "mean":
            items.append("r = r / cnt,  если  cnt > 0")
        return [
            ("Создание файла – функция create_file: файл открывается для записи в двоичном режиме (fopen(name, "
             "\"wb\")); каждое введённое число сразу записывается в файл функцией fwrite; затем файл закрывается.",
             []),
            ("Вывод чисел из файла – функция print_file: файл открывается для чтения (\"rb\"), числа читаются "
             "функцией fread до конца файла.", []),
            (f"Вычисление – функция process: файл читается ещё раз, по числам x вычисляется {self.text} "
             "(cnt – сколько чисел участвовало):", items),
        ]

    def spec(self):
        res = [("box", [f"{self.cap}: <<cnt>>"], False)] if self.agg == "count" else (
            [("label", "При cnt = 0"), ("box", [f"{self.none} - результат не существует."], True),
             ("label", "Иначе"), ("box", [f"{self.cap}: <<r>>"], True)] if self.none else
            [("box", [f"{self.cap}: <<r>>"], False)])
        return (spec_name("двоичного файла", "name",
                          [("Если файл не удалось создать", 'Ошибка! Не удалось создать файл "<<name>>".')])
                + spec_input_int("количество чисел n", 1, "NMAX", "n")
                + [("loop_start", "i", "1", "n")] + spec_input_reals("x<<i>>", ["xi"], 1) + [("loop_end",)]
                + [("box", ['Числа из файла "<<name>>": <<x1>> <<x2>> … <<xn>>'], False)] + res)

    def pseudo(self):
        idx = self.filt in ("even", "odd")
        cond = self.f_doc.replace("xi", "x").replace("i mod 2 = 0", "i чётно").replace("i mod 2 = 1", "i нечётно")
        upd = self.upd_ps
        inner = (f"\t\t_если_ {cond} _то_\n" + (f"\t\t\t{upd}\n" if upd else "") + "\t\t\tcnt := cnt + 1\n\t\t_всё_\n"
                 if cond else (f"\t\t{upd}\n" if upd else "") + "\t\tcnt := cnt + 1\n")
        res = (f"\tвывод(«{self.cap}: », cnt)" if self.agg == "count" else
               f"\t_если_ cnt = 0 _то_\n\t\tвывод(«{self.none} - результат не существует.»)\n"
               f"\t_иначе_\n\t\tвывод(«{self.cap}: », r)\n\t_всё_" if self.none else
               f"\tвывод(«{self.cap}: », r)")
        return f"""
_функция_ create_file(name)
_нач_
	открыть файл name для записи (двоичный)
	ввод(n)
	_цикл от_ i := 1 _до_ n
		ввод(x); записать x в файл
	_кц_
	закрыть файл
_кон_

_функция_ print_file(name)
_нач_
	открыть файл name для чтения (двоичный)
	_цикл-пока_ из файла прочитано число x
		вывод(x)
	_кц_
	закрыть файл
_кон_

_функция_ process(name, r)
_нач_
	открыть файл name для чтения (двоичный)
	cnt := 0; r := {self.init}{"; i := 0" if idx else ""}
	_цикл-пока_ из файла прочитано число x
{"		i := i + 1" + chr(10) if idx else ""}{inner}	_кц_
	закрыть файл
{"	_если_ cnt > 0 _то_ r := r / cnt _всё_" + chr(10) if self.agg == "mean" else ""}	_возврат_ cnt
_кон_

_алг_ «Лабораторная работа №5, часть I, задание {self.num}»
_нач_
	ввод(name)
	create_file(name)
	print_file(name)
	cnt := process(name, r)
{res}
_кон_
"""

    # ------------------------------------------------------------------ тесты
    def tests(self):
        def t(xs, case, name="data.bin", pre=()):
            lines = [*pre, name, str(len(xs)), *("%g" % x for x in xs)]
            return Test(lines, [f"имя файла: {name}", f"n = {len(xs)}", "x: " + " ".join("%g" % x for x in xs)],
                        case)
        none = {"pos": [-1.5, 0, -3], "neg": [2, 0, 4.5], "even": [5.5], "odd": [0, -4, 4], "all": [0, -4, 4]}
        case2 = {"pos": "Положительных чисел нет", "neg": "Отрицательных чисел нет", "even": "Одно число (n = 1)",
                 "odd": "Ноль и числа, равные по модулю", "all": "Ноль и числа, равные по модулю"}
        bad = Test(["", "нет/data.bin", "числа.bin", "0", "51", "x", "3", "abc", "1,5", "1001", "1.5", "-2", "4"],
                   ["имя: (пусто) / нет/data.bin / числа.bin", "n: 0 / 51 / x / 3", "x1: abc / 1,5 / 1001 / 1.5",
                    "x2 = −2, x3 = 4"],
                   "Недопустимые данные: пустое имя, файл не создаётся (нет каталога), n и числа с ошибками")
        return [t([3.5, -2, 0, 7.25, -0.5, 10], "Числа разных знаков, вещественные"),
                t(none[self.filt], case2[self.filt]),
                t([-8, 2.5, -1, 4, -0.25, 6, 9, -3], "Восемь чисел, чередование знаков", name="nums.dat"),
                bad]

    def task(self):
        return Task(
            lab=5, part="I", num=self.num, statement=self.text + ".",
            includes=["stdlib.h"] + (["math.h"] if "abs" in self.agg else []), defines=DEFINES,
            functions=self.functions(), decls="    char name[NAMEB];\n    double r;\n    int res, cnt;\n",
            body=self.body(), simulate=self.simulate,
            given=["name – имя двоичного файла; n – количество чисел; x1, x2, …, xn – действительные числа, "
                   "вводимые с клавиатуры и записываемые в файл."],
            result=["файл name с числами x1, …, xn; числа, прочитанные из файла;",
                    f"{self.cap.lower() if self.agg != 'count' else 'количество положительных чисел cnt'}"
                    + (" – или сообщение, что подходящих чисел нет." if self.none and self.agg != "count" else ".")],
            when=[f"n ∈ N, n ≤ NMAX = {NMAX}; xi ∈ R, |xi| ≤ RMAX = {RMAX} (дробная часть – через точку);",
                  "имя файла – от 1 до FMAX = 60 символов; числа хранятся в файле в двоичном виде (тип double)."],
            svyaz=self.svyaz, method=self.method(), spec=self.spec(), pseudo=self.pseudo(), tests=self.tests(),
            file="lab5_part1.c", prelude=CRT,
            note="Числа выводятся в формате %g (до 6 значащих цифр). Файл создаётся в текущей папке программы.",
        )


_cache = {}


def get(num):
    if num not in VARIANTS:
        raise ModuleNotFoundError(num)
    if num not in _cache:
        _cache[num] = Variant(num, *VARIANTS[num]).task()
    return _cache[num]
