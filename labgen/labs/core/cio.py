"""Ввод данных для лаб 3–5: функции на C и их точные копии на Python.

Целые числа читаются read_line() из лабы 2 (посимвольно, строка вместо числа и дробь вместо целого – ошибка),
вещественные – read_reals() (цифры и дробная часть через точку), строки – read_str() (UTF-8, длина в символах).
"""
from ..lab2.common import C_READ_LINE, Console as _Console, EndOfInput, parse_line  # noqa: F401

RMAX = 1000                # максимальный модуль вещественного числа на входе

# ====================================================================== C
C_READ_REALS = r'''/* Читает одну строку ввода и разбирает в ней ровно cnt вещественных чисел из [lo; hi].
   Число: необязательный знак, цифры и необязательная дробная часть через точку (-12.5).
   Возвращает 1 - строка корректна, 0 - ошибка, -1 - конец ввода. */
int read_reals(double a[], int cnt, double lo, double hi){
    char buf[32];
    int ch, cntr = 0, ok = 1, len, digits, frac;
    double v;
    ch = getchar();
    if (ch == EOF) return -1;
    while (ch != '\n' && ch != EOF && ok){   /* досрочный выход при первой ошибке */
        if (ch == ' ' || ch == '\t' || ch == '\r')
            ch = getchar();
        else{
            len = 0;
            digits = 0;
            frac = 1;
            if (ch == '-' || ch == '+'){
                buf[len++] = (char)ch;
                ch = getchar();
            }
            while (ch >= '0' && ch <= '9' && len < 30){
                buf[len++] = (char)ch;
                digits++;
                ch = getchar();
            }
            if (ch == '.' && digits > 0){
                buf[len++] = '.';
                ch = getchar();
                frac = 0;
                while (ch >= '0' && ch <= '9' && len < 30){
                    buf[len++] = (char)ch;
                    frac++;
                    ch = getchar();
                }
            }
            buf[len] = '\0';
            if (digits == 0 || frac == 0 || cntr >= cnt
                || (ch != ' ' && ch != '\t' && ch != '\r' && ch != '\n' && ch != EOF))
                ok = 0;
            else{
                v = strtod(buf, NULL);
                if (v < lo || v > hi) ok = 0;
                else{
                    a[cntr] = v;
                    cntr++;
                }
            }
        }
    }
    while (ch != '\n' && ch != EOF) ch = getchar();   /* дочитываем строку */
    return ok && cntr == cnt;
}
'''

C_INPUT_INT = r'''/* Ввод целого числа из [lo; hi] с повтором при ошибке. Возвращает 0 при конце ввода. */
int input_int(const char *name, int lo, int hi, int *x){
    int ok;
    do{
        printf("Введите %s (целое число от %d до %d): ", name, lo, hi);
        ok = read_line(x, 1, lo, hi);
        if (ok == -1) return 0;
        if (!ok) printf("Ошибка! Нужно ввести целое число от %d до %d.\n", lo, hi);
    } while (!ok);
    return 1;
}
'''

C_INPUT_REALS = r'''/* Ввод cnt вещественных чисел из [lo; hi] одной строкой с повтором при ошибке.
   Возвращает 0 при конце ввода. */
int input_reals(const char *what, int cnt, double lo, double hi, double a[]){
    int ok;
    do{
        printf("Введите %s: ", what);
        ok = read_reals(a, cnt, lo, hi);
        if (ok == -1) return 0;
        if (!ok)
            printf("Ошибка! Нужно чисел: %d, каждое от %g до %g "
                   "(дробная часть - через точку).\n", cnt, lo, hi);
    } while (!ok);
    return 1;
}
'''

C_READ_STR = r'''/* Читает из f строку до '\n' или конца файла в s (без '\n' и '\r').
   Возвращает длину строки в символах (UTF-8), -1 - конец файла,
   -2 - строка длиннее lmax символов (остаток строки пропускается). */
int read_str(FILE *f, char s[], int lmax){
    int ch, chars = 0, bytes = 0;
    ch = getc(f);
    if (ch == EOF) return -1;
    while (ch != '\n' && ch != EOF){
        if (ch != '\r'){
            if ((ch & 0xC0) != 0x80) chars++;     /* первый байт очередного символа */
            if (chars <= lmax && bytes < 4 * lmax){
                s[bytes] = (char)ch;
                bytes++;
            }
        }
        ch = getc(f);
    }
    s[bytes] = '\0';
    return chars > lmax ? -2 : chars;
}
'''


# ====================================================================== Python
class Console(_Console):
    """Консоль лабы 2 + виртуальные файлы: {имя: bytes} (текстовые) или {имя: list[float]} (двоичные)."""

    def __init__(self, lines, files=None):
        super().__init__(lines)
        self.files = dict(files or {})


def parse_reals(s, cnt, lo, hi):
    """Точная копия read_reals() из C. Возвращает (ok, values)."""
    i, n, ok, vals = 0, len(s), True, []
    sep = " \t\r"
    while i < n and ok:
        ch = s[i]
        if ch in sep:
            i += 1
            continue
        buf, digits, frac = "", 0, 1
        if ch in "+-":
            buf += ch
            i += 1
        while i < n and "0" <= s[i] <= "9" and len(buf) < 30:
            buf += s[i]
            digits += 1
            i += 1
        if i < n and s[i] == "." and digits > 0:
            buf += "."
            i += 1
            frac = 0
            while i < n and "0" <= s[i] <= "9" and len(buf) < 30:
                buf += s[i]
                frac += 1
                i += 1
        nxt = s[i] if i < n else "\n"
        if digits == 0 or frac == 0 or len(vals) >= cnt or nxt not in sep + "\n":
            ok = False
        else:
            v = float(buf)
            if v < lo or v > hi:
                ok = False
            else:
                vals.append(v)
    return ok and len(vals) == cnt, vals


def py_input_int(con, name, lo, hi):
    while True:
        con.printf("Введите %s (целое число от %d до %d): " % (name, lo, hi))
        ok, v = parse_line(con.readline(), 1, lo, hi)
        if ok:
            return v[0]
        con.printf("Ошибка! Нужно ввести целое число от %d до %d.\n" % (lo, hi))


def py_input_reals(con, what, cnt, lo, hi):
    while True:
        con.printf("Введите %s: " % what)
        ok, v = parse_reals(con.readline(), cnt, lo, hi)
        if ok:
            return v
        con.printf("Ошибка! Нужно чисел: %d, каждое от %g до %g (дробная часть - через точку).\n" % (cnt, lo, hi))


def str_from_bytes(raw, lmax):
    """Копия read_str() для уже прочитанной строки (bytes без '\\n'): (длина или -2, текст)."""
    raw = raw.replace(b"\r", b"")
    chars = sum(1 for b in raw if b & 0xC0 != 0x80)
    if chars > lmax:
        return -2, ""
    return chars, raw.decode("utf-8", "replace")


def py_read_str(con, lmax):
    """read_str(stdin, …): строка с клавиатуры."""
    return str_from_bytes(con.readline().encode("utf-8"), lmax)


class TextFile:
    """Чтение текстового файла эмулятора построчно, как read_str(f, …)."""

    def __init__(self, data: bytes):
        self.data, self.pos = data, 0

    def read_str(self, lmax):
        if self.pos >= len(self.data):
            return -1, ""
        end = self.data.find(b"\n", self.pos)
        if end < 0:
            end = len(self.data)
        raw = self.data[self.pos:end]
        self.pos = end + 1
        return str_from_bytes(raw, lmax)


# ====================================================================== спецификация
def shown(v):
    """Как значение выглядит в окне спецификации: число – как есть, имя (NMAX, n) – <<NMAX>> (выводится его
    значение)."""
    v = str(v)
    return v if v.lstrip("-").isdigit() else f"<<{v}>>"


def spec_input_int(name, lo, hi, var=None):
    """name – как величина названа в приглашении («длину массива n»), var – её обозначение («n»)."""
    var = var or name
    return [
        ("rep_start",),
        ("box", [f"Введите {name} (целое число от {shown(lo)} до {shown(hi)}): <{var}>"], False),
        ("label", f"При {var} ∉ Z или {var} < {lo} или {var} > {hi}"),
        ("box", [f"Ошибка! Нужно ввести целое число от {shown(lo)} до {shown(hi)}."], True),
        ("rep_end", f"До {var} ∈ Z и {lo} ≤ {var} ≤ {hi}"),
    ]


def spec_input_reals(what, names, cnt, lo="-RMAX", hi="RMAX", extra=None):
    """extra: (условие ошибки, текст сообщения) – дополнительная проверка введённых чисел."""
    items = [
        ("rep_start",),
        ("box", [f"Введите {what}: " + " ".join(f"<{n}>" for n in names)], False),
        ("label", "При ошибке ввода (не числа, не то количество, вне диапазона)"),
        ("box", [f"Ошибка! Нужно чисел: {shown(cnt)}, каждое от {shown(lo)} до {shown(hi)} (дробная часть - "
                 "через точку)."], True),
    ]
    if extra:
        items += [("label", extra[0]), ("box", [extra[1]], True)]
    items.append(("rep_end", f"До {', '.join(names)} введены верно"))
    return items
