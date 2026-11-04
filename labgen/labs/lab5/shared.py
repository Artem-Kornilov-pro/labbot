"""Общее для лабы 5: ввод имени файла (C и Python) и «файловая система» эмулятора.

Эмулятор хранит файлы в con.files: двоичный – list[float], текстовый – bytes. Файл открывается для чтения,
если он есть; создать файл нельзя, если в имени есть каталог ('/'): в тестах каталогов нет.
"""
from ..core.cio import C_READ_STR, py_read_str

FMAX = 60
# Visual Studio по умолчанию считает fopen, sprintf, strcpy ошибкой C4996 («небезопасные функции»)
CRT = "#define _CRT_SECURE_NO_WARNINGS  /* Visual Studio: разрешить fopen, sprintf, strcpy */"

C_INPUT_NAME = r'''/* Ввод имени файла (what - какого файла). Возвращает 0 при конце ввода. */
int input_name(const char *what, char name[]){
    int r;
    do{
        printf("Введите имя %s: ", what);
        r = read_str(stdin, name, FMAX);
        if (r == -1) return 0;
        if (r <= 0) printf("Ошибка! Имя файла - от 1 до %d символов.\n", FMAX);
    } while (r <= 0);
    return 1;
}
'''

NAME_DEFINES = ("#define FMAX 60                      /* наибольшая длина имени файла, символов */\n"
                "#define NAMEB (4 * FMAX + 1)         /* байт на имя файла (UTF-8) */")

NAME_FUNCS = C_READ_STR + "\n" + C_INPUT_NAME


def py_input_name(con, what):
    while True:
        con.printf("Введите имя %s: " % what)
        r, text = py_read_str(con, FMAX)
        if r > 0:
            return text
        con.printf("Ошибка! Имя файла - от 1 до %d символов.\n" % FMAX)


def can_create(name):
    return "/" not in name


def spec_name(what, var, extra=()):
    """Окна ввода имени файла; extra – [(условие, сообщение)] – дополнительные ошибки (файл не открыт и т. п.)."""
    items = [("rep_start",),
             ("box", [f"Введите имя {what}: <{var}>"], False),
             ("label", "При пустом имени или длиннее FMAX символов"),
             ("box", ["Ошибка! Имя файла - от 1 до <<FMAX>> символов."], True)]
    for cond, msg in extra:
        items += [("label", cond), ("box", [msg], True)]
    items.append(("rep_end", f"До {var} введено верно и файл открыт"))
    return items
