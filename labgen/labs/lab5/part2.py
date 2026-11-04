"""Часть II лабы 5: текстовый файл, созданный в «Блокноте», читается построчно; каждая строка преобразуется,
записывается в новый текстовый файл, затем строки выходного файла выводятся на экран.

Строки – UTF-8 (как сохраняет «Блокнот»); символы '\\r' (конец строки Windows) отбрасываются при чтении.
"""
from ..core.task import Task, Test
from ..core.cio import TextFile
from ..core.cstr import C_CHARS, C_EDIT, is_rus, is_lat, is_dig
from .shared import NAME_DEFINES, NAME_FUNCS, py_input_name, can_create, spec_name

COUNT = 9
INTRO = ("Создать текстовый файл средствами редактора (т.е. в «Блокноте»). Прочитать этот файл построчно и "
         "произвести в каждой строке следующие действия: ")
OUTRO = ("Записать каждую полученную строку в новый текстовый файл и вывести полученные строки из файла на экран. "
         "Имена входного и выходного файла задаются пользователем.")
LMAX = 80

DEFINES = ("#define LMAX 80                      /* наибольшая длина строки файла, символов */\n"
           "#define SMAX (4 * LMAX + 1)          /* байт на строку: символ UTF-8 - до 4 байт */\n"
           "#define OMAX (12 * LMAX + 1)         /* байт на строку результата (3 * LMAX симв.) */\n"
           + NAME_DEFINES)

C_LOW = r'''/* 1, если s начинается со строчной русской буквы (а-я, ё; в UTF-8 - два байта) */
int is_rus_low(const char *s){
    unsigned char a = (unsigned char)s[0], b = (unsigned char)s[1];
    return (a == 0xD0 && b >= 0xB0 && b <= 0xBF)
        || (a == 0xD1 && ((b >= 0x80 && b <= 0x8F) || b == 0x91));
}
'''

C_PRINT = r'''/* Вывод на экран строк текстового файла name */
void print_file(const char *name){
    FILE *f = fopen(name, "r");
    char s[OMAX];
    if (f == NULL) return;
    printf("\nСодержимое файла \"%s\":\n", name);
    while (read_str(f, s, 3 * LMAX) != -1)
        printf("%s\n", s);
    fclose(f);
}
'''


def _sort_keep(s, pred, reverse=False):
    vals = sorted((c for c in s if pred(c)), reverse=reverse)
    it = iter(vals)
    return "".join(next(it) if pred(c) else c for c in s)


def _zeros(s):
    out = []
    for i, c in enumerate(s):
        out.append(c)
        if is_lat(c) and i + 1 < len(s) and is_lat(s[i + 1]):
            out.append("00")
    return "".join(out)


def _after_digits(s):
    out, i = [], 0
    while i < len(s):
        if is_dig(s[i]):
            j = i
            while j < len(s) and is_dig(s[j]):
                j += 1
            out.append(s[i:j] + ("A" if j - i >= 2 else ""))
            i = j
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def _swap_pairs(s):
    return "".join(s[i + 1] + s[i] if i + 1 < len(s) else s[i] for i in range(0, len(s), 2))


def _lower_rus(c):
    return "а" <= c <= "я" or c == "ё"


_DEL = '''    int i = 0;
    while (s[i] != '\\0')
        if ({cond})
            del_at(s, i, {n});            /* удаление сдвигом влево */
        else
            i++;
'''

# номер: текст, тело C-функции transform, Python, нужен ли C_EDIT / C_LOW, псевдокод, пункты метода
VARIANTS = {
    1: ("заменить каждую цифру соответствующей ей латинской буквой (‘0’ на ‘A’, ‘1’ на ‘B’ и т.д.)", '''    int i;
    for (i = 0; s[i] != '\\0'; i++)
        if (is_dig(s[i]))
            s[i] = (char)('A' + (s[i] - '0'));
''', lambda s: "".join(chr(ord("A") + int(c)) if is_dig(c) else c for c in s), (),
        "_цикл от_ i := 1 _до_ L(s)\n\t\t_если_ цифра(s[i]) _то_\n\t\t\ts[i] := буква с номером s[i]\n\t\t_всё_\n\t_кц_",
        [["для i = {1..L}", "s[i] = 'A' + (s[i] − '0'),  если  цифра(s[i])"]]),
    2: ("упорядочить все латинские буквы по возрастанию, сохранив расположение остальных символов (например, "
        "строка ‘1c2a3b’ преобразуется в строку ‘1a2b3c’)", '''    int i, j;
    char c;
    for (i = 0; s[i] != '\\0'; i++)      /* сортировка обменами только латинских букв */
        if (is_lat(s[i]))
            for (j = i + 1; s[j] != '\\0'; j++)
                if (is_lat(s[j]) && s[j] < s[i]){
                    c = s[i];
                    s[i] = s[j];
                    s[j] = c;
                }
''', lambda s: _sort_keep(s, is_lat), (),
        "_цикл от_ i := 1 _до_ L(s)\n\t\t_если_ лат(s[i]) _то_\n\t\t\t_цикл от_ j := i + 1 _до_ L(s)\n"
        "\t\t\t\t_если_ лат(s[j]) _и_ s[j] < s[i] _то_\n\t\t\t\t\ts[i] ↔ s[j]\n\t\t\t\t_всё_\n\t\t\t_кц_\n"
        "\t\t_всё_\n\t_кц_",
        [["для i = {1..L}, если  лат(s[i])", ["для j = {i + 1..L}", "s[i] ↔ s[j],  если  лат(s[j])  и  s[j] < s[i]"]]]),
    3: ("удалить путем сдвига все четные цифры", _DEL.format(cond="is_dig(s[i]) && (s[i] - '0') % 2 == 0", n=1),
        lambda s: "".join(c for c in s if not (is_dig(c) and int(c) % 2 == 0)), ("edit",),
        "i := 1\n\t_цикл-пока_ i ≤ L(s)\n\t\t_если_ цифра(s[i]) _и_ s[i] чётная _то_\n\t\t\tудалить(s, i)\n"
        "\t\t_иначе_\n\t\t\ti := i + 1\n\t\t_всё_\n\t_кц_",
        ["i = 1", ["пока  i ≤ L", "удалить(s, i),  если  цифра(s[i])  и  s[i] ⋮ 2", "i = i + 1,  иначе"]]),
    4: ("вставить два нуля между каждыми двумя соседними латинскими буквами", '''    int i = 0;
    while (s[i] != '\\0')
        if (is_lat(s[i]) && is_lat(s[i + 1])){
            ins_at(s, i + 1, "00");     /* вставка сдвигом вправо */
            i = i + 3;
        }
        else
            i++;
''', _zeros, ("edit",),
        "i := 1\n\t_цикл-пока_ i ≤ L(s)\n\t\t_если_ лат(s[i]) _и_ лат(s[i + 1]) _то_\n"
        "\t\t\tвставить(s, i + 1, «00»); i := i + 3\n\t\t_иначе_\n\t\t\ti := i + 1\n\t\t_всё_\n\t_кц_",
        ["i = 1", ["пока  i ≤ L", "(вставить(s, i + 1, '00'),  i = i + 3),  если  лат(s[i])  и  лат(s[i + 1])",
                   "i = i + 1,  иначе"]]),
    5: ("упорядочить все цифры по убыванию (например, строка ‘1c2a3b’ преобразуется в строку ‘3c2a1b’)", '''    int i, j;
    char c;
    for (i = 0; s[i] != '\\0'; i++)      /* сортировка обменами только цифр */
        if (is_dig(s[i]))
            for (j = i + 1; s[j] != '\\0'; j++)
                if (is_dig(s[j]) && s[j] > s[i]){
                    c = s[i];
                    s[i] = s[j];
                    s[j] = c;
                }
''', lambda s: _sort_keep(s, is_dig, reverse=True), (),
        "_цикл от_ i := 1 _до_ L(s)\n\t\t_если_ цифра(s[i]) _то_\n\t\t\t_цикл от_ j := i + 1 _до_ L(s)\n"
        "\t\t\t\t_если_ цифра(s[j]) _и_ s[j] > s[i] _то_\n\t\t\t\t\ts[i] ↔ s[j]\n\t\t\t\t_всё_\n\t\t\t_кц_\n"
        "\t\t_всё_\n\t_кц_",
        [["для i = {1..L}, если  цифра(s[i])", ["для j = {i + 1..L}",
                                                "s[i] ↔ s[j],  если  цифра(s[j])  и  s[j] > s[i]"]]]),
    6: ("удалить путем сдвига все строчные русские буквы", _DEL.format(cond="is_rus_low(s + i)", n=2),
        lambda s: "".join(c for c in s if not _lower_rus(c)), ("edit", "low"),
        "i := 1\n\t_цикл-пока_ i ≤ L(s)\n\t\t_если_ s[i] – строчная русская буква _то_\n\t\t\tудалить(s, i)\n"
        "\t\t_иначе_\n\t\t\ti := i + 1\n\t\t_всё_\n\t_кц_",
        ["i = 1", ["пока  i ≤ L", "удалить(s, i),  если  s[i] ∈ {'а'..'я', 'ё'}", "i = i + 1,  иначе"]]),
    7: ("вставить букву 'A' после двух или более следующих подряд цифр", '''    int i = 0, j;
    while (s[i] != '\\0')
        if (is_dig(s[i])){
            j = i;
            while (is_dig(s[j]))        /* конец группы цифр */
                j++;
            if (j - i >= 2){
                ins_at(s, j, "A");      /* вставка сдвигом вправо */
                j++;
            }
            i = j;
        }
        else
            i++;
''', _after_digits, ("edit",),
        "i := 1\n\t_цикл-пока_ i ≤ L(s)\n\t\t_если_ цифра(s[i]) _то_\n\t\t\tj := i\n"
        "\t\t\t_цикл-пока_ цифра(s[j])\n\t\t\t\tj := j + 1\n\t\t\t_кц_\n"
        "\t\t\t_если_ j − i ≥ 2 _то_\n\t\t\t\tвставить(s, j, «A»); j := j + 1\n\t\t\t_всё_\n\t\t\ti := j\n"
        "\t\t_иначе_\n\t\t\ti := i + 1\n\t\t_всё_\n\t_кц_",
        ["i = 1", ["пока  i ≤ L",
                   ["если  цифра(s[i])", "j = i;   j = j + 1,  пока  цифра(s[j])",
                    "(вставить(s, j, 'A'),  j = j + 1),  если  j − i ≥ 2", "i = j"],
                   "i = i + 1,  иначе"]]),
    8: ("переставить все символы в строке в обратной последовательности", '''    int i = 0, n = (int)strlen(s), d;
    while (s[i] != '\\0'){        /* байты каждого символа UTF-8 - в обратном порядке */
        d = clen(s + i);
        rev(s, i, i + d - 1);
        i = i + d;
    }
    rev(s, 0, n - 1);             /* затем вся строка: символы снова читаются верно */
''', lambda s: s[::-1], ("rev",),
        "_цикл от_ i := 1 _до_ L(s) / 2\n\t\ts[i] ↔ s[L(s) − i + 1]\n\t_кц_",
        [["для i = {1..L / 2}", "s[i] ↔ s[L − i + 1]"]]),
    9: ("поменять местами каждую пару расположенных подряд символов (при нечетной длине строки последний символ "
        "оставить на месте). (Например, строка ‘1c2a3b0’ преобразуется в строку ‘c1a2b30’)", '''    char t[SMAX];
    int i = 0, k = 0, d1, d2, j;
    while (s[i] != '\\0'){
        d1 = clen(s + i);
        d2 = s[i + d1] != '\\0' ? clen(s + i + d1) : 0;   /* 0 - у символа нет пары */
        for (j = 0; j < d2; j++)                       /* сначала второй символ пары */
            t[k++] = s[i + d1 + j];
        for (j = 0; j < d1; j++)                       /* затем первый */
            t[k++] = s[i + j];
        i = i + d1 + d2;
    }
    t[k] = '\\0';
    strcpy(s, t);
''', _swap_pairs, (),
        "i := 1\n\t_цикл-пока_ i < L(s)\n\t\ts[i] ↔ s[i + 1]; i := i + 2\n\t_кц_",
        ["i = 1", ["пока  i < L", "s[i] ↔ s[i + 1];   i = i + 2"]]),
}

C_REV = r'''/* Перестановка байт s[a..b] в обратном порядке */
void rev(char *s, int a, int b){
    char c;
    while (a < b){
        c = s[a];
        s[a] = s[b];
        s[b] = c;
        a++;
        b--;
    }
}
'''

BODY = r'''    do{
        if (!input_name("входного файла", in)) return 1;
        f = fopen(in, "r");
        if (f == NULL) printf("Ошибка! Не удалось открыть файл \"%s\".\n", in);
    } while (f == NULL);
    do{
        g = NULL;
        if (!input_name("выходного файла", out)){
            fclose(f);
            return 1;
        }
        if (strcmp(in, out) == 0)
            printf("Ошибка! Выходной файл должен отличаться от входного.\n");
        else{
            g = fopen(out, "w");
            if (g == NULL) printf("Ошибка! Не удалось создать файл \"%s\".\n", out);
        }
    } while (g == NULL);

    /* построчная обработка: каждая полученная строка записывается в выходной файл */
    printf("\n");
    while ((r = read_str(f, s, LMAX)) != -1){
        num++;
        if (r == -2)
            printf("Строка %d длиннее %d символов - пропущена.\n", num, LMAX);
        else{
            transform(s);
            fprintf(g, "%s\n", s);
        }
    }
    fclose(f);
    fclose(g);
    printf("Прочитано строк: %d.\n", num);
    print_file(out);
'''


class Variant:
    def __init__(self, num, text, c_body, py, deps, pseudo, items):
        self.num, self.text, self.c_body, self.py, self.deps = num, text, c_body, py, deps
        self.pseudo_body, self.items = pseudo, items

    def functions(self):
        from ..lab4.pieces import comment
        parts = [NAME_FUNCS, C_CHARS]
        if "low" in self.deps:
            parts.append(C_LOW)
        if "edit" in self.deps:
            parts.append(C_EDIT)
        if "rev" in self.deps:
            parts.append(C_REV)
        parts.append(comment(f"Преобразование строки s: {self.text}") + f"void transform(char *s){{\n{self.c_body}}}\n")
        parts.append(C_PRINT)
        return "\n".join(parts)

    def simulate(self, con):
        while True:
            src = py_input_name(con, "входного файла")
            if src in con.files:
                break
            con.printf(f'Ошибка! Не удалось открыть файл "{src}".\n')
        while True:
            dst = py_input_name(con, "выходного файла")
            if dst == src:
                con.printf("Ошибка! Выходной файл должен отличаться от входного.\n")
            elif not can_create(dst):
                con.printf(f'Ошибка! Не удалось создать файл "{dst}".\n')
            else:
                break
        con.begin_results()
        con.printf("\n")
        f, out, num = TextFile(con.files[src]), b"", 0
        while True:
            r, s = f.read_str(LMAX)
            if r == -1:
                break
            num += 1
            if r == -2:
                con.printf("Строка %d длиннее %d символов - пропущена.\n" % (num, LMAX))
            else:
                out += (self.py(s) + "\n").encode("utf-8")
        con.files[dst] = out
        con.printf("Прочитано строк: %d.\n" % num)
        con.printf(f'\nСодержимое файла "{dst}":\n')
        g = TextFile(con.files[dst])
        while True:
            r, s = g.read_str(3 * LMAX)
            if r == -1:
                break
            con.printf(s + "\n")

    # ------------------------------------------------------------------ документы
    def svyaz(self, rep):
        rep.para("in[1:N] – строки входного файла (N – число строк), out[1:N′] – строки выходного файла:", after=2)
        rep.para(f"out[j] = T(in[i]), где T – преобразование «{self.text}»; строки длиннее LMAX символов "
                 "пропускаются (N′ ≤ N); на экран выводятся строки out[1:N′], прочитанные из выходного файла.",
                 after=4)

    def method(self):
        return [
            ("Открытие файлов: входной – для чтения (fopen(in, \"r\")), выходной – для записи (fopen(out, \"w\")); "
             "при ошибке имя вводится заново, выходной файл должен отличаться от входного.", []),
            ("Построчное чтение – функция read_str(f, s, LMAX): символы читаются до '\\n' или конца файла, '\\r' "
             "(конец строки Windows) отбрасывается; строка длиннее LMAX символов пропускается.", []),
            ("Преобразование строки – функция transform(s) (лат(c), цифра(c) – латинская буква / цифра; "
             "удалить(s, i) – удаление символа сдвигом влево, вставить(s, i, t) – вставка t перед i-м символом "
             "сдвигом вправо; L – длина строки в символах):", self.items),
            ("Каждая полученная строка записывается в выходной файл (fprintf); после закрытия файлов выходной файл "
             "открывается для чтения, и его строки выводятся на экран (функция print_file).", []),
        ]

    def spec(self):
        return (spec_name("входного файла", "in",
                          [("Если файл не найден", 'Ошибка! Не удалось открыть файл "<<in>>".')])
                + spec_name("выходного файла", "out",
                            [("Если out = in", "Ошибка! Выходной файл должен отличаться от входного."),
                             ("Если файл не удалось создать", 'Ошибка! Не удалось создать файл "<<out>>".')])
                + [("loop_start", "i", "1", "N"), ("label", "Если строка длиннее LMAX символов"),
                   ("box", ["Строка <<i>> длиннее <<LMAX>> символов - пропущена."], True), ("loop_end",),
                   ("box", ["Прочитано строк: <<N>>."], False),
                   ("box", ['Содержимое файла "<<out>>":', "<<out[1]>>", "…", "<<out[N′]>>"], False)])

    def pseudo(self):
        return f"""
_функция_ transform(s)
_нач_
	{self.pseudo_body}
_кон_

_алг_ «Лабораторная работа №5, часть II, задание {self.num}»
_нач_
	ввод(in); открыть файл in для чтения
	ввод(out); открыть файл out для записи
	num := 0
	_цикл-пока_ из файла in прочитана строка s
		num := num + 1
		_если_ L(s) > LMAX _то_
			вывод(«Строка », num, « длиннее LMAX символов - пропущена.»)
		_иначе_
			transform(s); записать s в файл out
		_всё_
	_кц_
	закрыть файлы in и out
	вывод(«Прочитано строк: », num)
	открыть файл out для чтения
	_цикл-пока_ из файла out прочитана строка s
		вывод(s)
	_кц_
	закрыть файл out
_кон_
"""

    def tests(self):
        def show(name, data):
            lines = data.decode("utf-8").replace("\r", "␍").split("\n")
            if lines and lines[-1] == "":
                lines = lines[:-1]
            return [f"файл {name}:"] + [f"  «{x}»" if len(x) <= 40 else f"  «{x[:12]}…» ({len(x)} символов)"
                                        for x in lines]
        f1 = "1c2a3b\nПривет, World 2024!\n  b9a 7 ёж Ёж 100\nlast 12345 zz\n".encode("utf-8")
        f2 = ("1c2a3b0\r\n\r\n" + "x" * (LMAX + 1) + "\r\nЁлка 42 ab").encode("utf-8")
        f3 = "1c2a3b\nHello мир 99\n".encode("utf-8")
        return [
            Test(["input.txt", "out.txt"], show("input.txt", f1) + ["выходной файл: out.txt"],
                 "Строки с цифрами, латинскими и русскими буквами", {"input.txt": f1}),
            Test(["текст.txt", "результат.txt"], show("текст.txt", f2) + ["выходной файл: результат.txt"],
                 "Файл из «Блокнота» Windows (\\r\\n), пустая строка, строка длиннее LMAX, нет '\\n' в конце",
                 {"текст.txt": f2}),
            Test(["", "нет.txt", "in.txt", "in.txt", "нет/out.txt", "out.txt"],
                 ["входной: (пусто) / нет.txt / in.txt", "выходной: in.txt / нет/out.txt / out.txt"]
                 + show("in.txt", f3)[1:],
                 "Недопустимые имена: пустое, файла нет, выходной = входной, каталога нет", {"in.txt": f3}),
        ]

    def task(self):
        return Task(
            lab=5, part="II", num=self.num, statement=f"{self.text}. {OUTRO}", includes=["string.h"],
            defines=DEFINES, functions=self.functions(),
            decls="    char in[NAMEB], out[NAMEB], s[SMAX];\n    FILE *f, *g;\n    int r, num = 0;\n",
            body=BODY, simulate=self.simulate,
            given=["in – имя входного текстового файла (создан в «Блокноте»); out – имя выходного файла; "
                   "строки файла in."],
            result=[f"файл out: каждая строка файла in, преобразованная так: {self.text};",
                    "строки файла out на экране."],
            when=[f"длина строки входного файла – не более LMAX = {LMAX} символов (более длинные строки "
                  "пропускаются с сообщением); out ≠ in; имена файлов – от 1 до FMAX = 60 символов;",
                  "текст в кодировке UTF-8 (русская буква – 2 байта), конец строки – '\\n' или '\\r\\n'."],
            svyaz=self.svyaz, method=self.method(), spec=self.spec(), pseudo=self.pseudo(), tests=self.tests(),
            file="lab5_part2.c",
            note="В таблице тестов «␍» – символ '\\r' (конец строки Windows). Файлы создаются в текущей папке "
                 "программы.",
        )


_cache = {}


def get(num):
    if num not in VARIANTS:
        raise ModuleNotFoundError(num)
    if num not in _cache:
        _cache[num] = Variant(num, *VARIANTS[num]).task()
    return _cache[num]
