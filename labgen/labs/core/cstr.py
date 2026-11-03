"""Строки UTF-8 для лаб 4–5: функции на C (строка – массив байт, русская буква – 2 байта) и их копии на Python.

В Python строки обрабатываются посимвольно (str); C-функции дают тот же результат на байтах UTF-8.
"""

C_CHARS = r'''/* Длина в байтах символа UTF-8, который начинается в s */
int clen(const char *s){
    unsigned char c = (unsigned char)s[0];
    if (c < 0x80) return 1;
    if ((c & 0xE0) == 0xC0) return 2;
    if ((c & 0xF0) == 0xE0) return 3;
    if ((c & 0xF8) == 0xF0) return 4;
    return 1;
}

/* 1, если s начинается с русской буквы (А-Я, а-я, Ё, ё; в UTF-8 - два байта) */
int is_rus(const char *s){
    unsigned char a = (unsigned char)s[0], b = (unsigned char)s[1];
    return (a == 0xD0 && ((b >= 0x90 && b <= 0xBF) || b == 0x81))
        || (a == 0xD1 && ((b >= 0x80 && b <= 0x8F) || b == 0x91));
}

/* 1, если c - латинская буква */
int is_lat(char c){
    return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z');
}

/* 1, если c - цифра */
int is_dig(char c){
    return c >= '0' && c <= '9';
}
'''

C_EDIT = r'''/* Удаление n байт строки s, начиная с позиции pos, сдвигом влево */
void del_at(char *s, int pos, int n){
    int j = pos;
    do{
        s[j] = s[j + n];
        j++;
    } while (s[j - 1] != '\0');
}

/* Вставка строки ins в s перед позицией pos сдвигом вправо */
void ins_at(char *s, int pos, const char *ins){
    int n = (int)strlen(ins), j;
    for (j = (int)strlen(s); j >= pos; j--)
        s[j + n] = s[j];
    for (j = 0; j < n; j++)
        s[pos + j] = ins[j];
}
'''

C_CODE = r'''/* Код (номер в Unicode) символа UTF-8, который начинается в s */
int code(const char *s){
    unsigned char c = (unsigned char)s[0];
    int n = clen(s), v, i;
    if (n == 1) return c;
    v = c & (0xFF >> (n + 1));
    for (i = 1; i < n; i++)
        v = (v << 6) | ((unsigned char)s[i] & 0x3F);
    return v;
}
'''


def is_rus(ch):
    return "А" <= ch <= "я" or ch in "Ёё"


def is_lat(ch):
    return "A" <= ch <= "Z" or "a" <= ch <= "z"


def is_dig(ch):
    return "0" <= ch <= "9"


def c_str(text):
    """Текст для строкового литерала C."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def c_printf(fmt, args="", ind="    ", width=84):
    """printf с длинной строкой формата, разбитой на несколько литералов (строка листинга ≤ width символов).
    fmt – текст формата как есть (\\n – перевод строки), кавычки экранируются."""
    lit = c_str(fmt).replace("\n", "\\n")
    tail = f", {args});" if args else ");"
    one = f'{ind}printf("{lit}"{tail}'
    if len(one) <= width:
        return one
    words, parts, cur = lit.split(" "), [], ""
    room = width - len(ind) - 12
    for w in words:
        cand = (cur + " " + w) if cur else w
        if len(cand) > room and cur:
            parts.append(cur + " ")
            cur = w
        else:
            cur = cand
    parts.append(cur)
    pad = ind + " " * len("printf(")
    lines = [f'{ind}printf("{parts[0]}"'] + [f'{pad}"{p}"' for p in parts[1:]]
    if args and len(lines[-1] + tail) > width:
        lines[-1] += ","
        lines.append(f"{pad}{args});")
    else:
        lines[-1] += tail
    return "\n".join(lines)
