"""Подпрограммы лабы 4: выделение подстрок (12), поиск подстроки (10), преобразование строки (11).

Каждая подпрограмма: текст из практикума, функция на C, копия на Python, псевдокод, пункт метода.
В псевдокоде: лат(c), рус(c), цифра(c) – c латинская буква / русская буква / цифра; «*» – символ.
Пробел считается буквой (примечание к п. 1) при выделении подстрок и подсчёте букв в п. 2.
"""
from ..core.cstr import is_rus, is_lat, is_dig


def comment(text, width=84):
    """Комментарий C /* … */ из текста, разбитого на строки не длиннее width."""
    words, lines, cur = text.split(" "), [], "/*"
    for w in words:
        if len(cur) + 1 + len(w) > width - 3 and cur.strip() not in ("/*", ""):
            lines.append(cur)
            cur = "  "
        cur += " " + w
    lines.append(cur + " */")
    return "\n".join(lines) + "\n"


class Piece:
    def __init__(self, num, text, c, py, pseudo, method, deps=(), label=None, fail=None, svyaz=""):
        self.num, self.text, self.c, self.py, self.pseudo, self.method = num, text, c, py, pseudo, method
        self.deps, self.label, self.fail, self.svyaz = tuple(deps), label or text, fail, svyaz


# ====================================================================== 1. выделение подстрок
def _sp(pred):
    return lambda ch: pred(ch) or ch == " "


EX_DEF = {
    1: ("заключенные в фигурные скобки", "pair", "{}", None, None, "в фигурных скобках"),
    2: ("расположенные между знаками '<' и '>'", "pair", "<>", None, None, "между '<' и '>'"),
    3: ("ограниченные с обеих сторон одной или несколькими звездочками", "bounded",
        "s[i] == '*'", lambda c: c == "*", "s[i] = «*»", "между звездочками"),
    4: ("ограниченные с обеих сторон знаками '+', '-', '*', '/'", "bounded",
        "s[i] == '+' || s[i] == '-' || s[i] == '*' || s[i] == '/'", lambda c: c in "+-*/",
        "s[i] ∈ {«+», «-», «*», «/»}", "между знаками + - * /"),
    5: ("ограниченные с обеих сторон одной или несколькими точками", "bounded",
        "s[i] == '.'", lambda c: c == ".", "s[i] = «.»", "между точками"),
    6: ("ограниченные с обеих сторон одной или несколькими латинскими буквами", "bounded",
        "is_lat(s[i]) || s[i] == ' '", _sp(is_lat), "лат(s[i]) _или_ s[i] = « »", "между латинскими буквами"),
    7: ("ограниченные с обеих сторон одной или несколькими русскими буквами", "bounded",
        "is_rus(s + i) || s[i] == ' '", _sp(is_rus), "рус(s[i]) _или_ s[i] = « »", "между русскими буквами"),
    8: ("не содержащие точек", "split", "s[i] == '.'", lambda c: c == ".", "s[i] = «.»", "без точек"),
    9: ("не содержащие символов '.', ',', ';', ':'", "split",
        "s[i] == '.' || s[i] == ',' || s[i] == ';' || s[i] == ':'", lambda c: c in ".,;:",
        "s[i] ∈ {«.», «,», «;», «:»}", "без символов . , ; :"),
    10: ("не содержащие квадратных скобок", "split", "s[i] == '[' || s[i] == ']'", lambda c: c in "[]",
         "s[i] ∈ {«[», «]»}", "без квадратных скобок"),
    11: ("содержащие только латинские буквы и цифры", "split",
         "!(is_lat(s[i]) || is_dig(s[i]) || s[i] == ' ')", lambda c: not (is_lat(c) or is_dig(c) or c == " "),
         "_не_ (лат(s[i]) _или_ цифра(s[i]) _или_ s[i] = « »)", "из латинских букв и цифр"),
    12: ("содержащие только русские буквы и цифры", "split",
         "!(is_rus(s + i) || is_dig(s[i]) || s[i] == ' ')", lambda c: not (is_rus(c) or is_dig(c) or c == " "),
         "_не_ (рус(s[i]) _или_ цифра(s[i]) _или_ s[i] = « »)", "из русских букв и цифр"),
}

_ADD = '''            p[cnt] = s + start;
            len[cnt] = i - start;
            cnt++;'''


def _ex_c(num, text, kind, arg):
    head = comment(f"1. Выделить из строки s подстроки, {text}. p[] - начала подстрок, len[] - их длины в "
                   "байтах; возвращает число подстрок")
    if kind == "pair":
        o, c = arg
        return head + f'''int extract(char *s, char *p[], int len[]){{
    int i = 0, start = -1, cnt = 0;
    while (s[i] != '\\0'){{
        if (s[i] == '{o}')
            start = i + 1;              /* подстрока - после открывающего знака */
        else if (s[i] == '{c}'){{
            if (start >= 0 && i > start){{  /* пустые подстроки не выделяются */
    {_ADD.replace(chr(10), chr(10) + "    ")}
            }}
            start = -1;
        }}
        i = i + clen(s + i);
    }}
    return cnt;
}}
'''
    bounded = kind == "bounded"
    tail = "" if bounded else f'''    if (i > start){{                    /* последняя подстрока - до конца строки */
{_ADD.replace("            ", "        ")}
    }}
'''
    return head + f'''int extract(char *s, char *p[], int len[]){{
    int i = 0, start = {"-1" if bounded else "0"}, cnt = 0, d;
    while (s[i] != '\\0'){{
        d = clen(s + i);
        if ({arg}){{
            if ({"start >= 0 && " if bounded else ""}i > start){{
    {_ADD.replace(chr(10), chr(10) + "    ")}
            }}
            start = i + d;
        }}
        i = i + d;
    }}
{tail}    return cnt;
}}
'''


def _ex_py(kind, arg, pred):
    def run(s):
        out = []
        if kind == "pair":
            o, c = arg
            start = None
            for i, ch in enumerate(s):
                if ch == o:
                    start = i + 1
                elif ch == c:
                    if start is not None and i > start:
                        out.append(s[start:i])
                    start = None
            return out
        start = None if kind == "bounded" else 0
        for i, ch in enumerate(s):
            if pred(ch):
                if start is not None and i > start:
                    out.append(s[start:i])
                start = i + 1
        if kind == "split" and len(s) > start:
            out.append(s[start:])
        return out
    return run


def _ex_pseudo(kind, arg, cond):
    if kind == "pair":
        o, c = arg
        return f"""
_функция_ extract(s, p, len)
_нач_
	start := −1; cnt := 0
	_цикл от_ i := 1 _до_ L(s)
		_если_ s[i] = «{o}» _то_
			start := i + 1
		_иначе_
			_если_ s[i] = «{c}» _то_
				_если_ start ≥ 0 _и_ i > start _то_
					p[cnt] := start; len[cnt] := i − start; cnt := cnt + 1
				_всё_
				start := −1
			_всё_
		_всё_
	_кц_
	_возврат_ cnt
_кон_
"""
    bounded = kind == "bounded"
    tail = ("" if bounded else "\t_если_ L(s) + 1 > start _то_\n"
            "\t\tp[cnt] := start; len[cnt] := L(s) + 1 − start; cnt := cnt + 1\n\t_всё_\n")
    return f"""
_функция_ extract(s, p, len)
_нач_
	start := {"−1" if bounded else "1"}; cnt := 0
	_цикл от_ i := 1 _до_ L(s)
		_если_ {cond} _то_
			_если_ {"start ≥ 0 _и_ " if bounded else ""}i > start _то_
				p[cnt] := start; len[cnt] := i − start; cnt := cnt + 1
			_всё_
			start := i + 1
		_всё_
	_кц_
{tail}	_возврат_ cnt
_кон_
"""


def _ex_method(kind, arg, cond):
    cond_m = cond.replace("_или_", "или").replace("_не_", "не").replace("«", "'").replace("»", "'")
    if kind == "pair":
        o, c = arg
        return ("Выделение подстрок – функция extract(s, p, len): подстрока начинается после открывающего знака "
                f"«{o}» и заканчивается перед ближайшим закрывающим «{c}»; пустые подстроки не выделяются "
                "(L – длина строки):",
                ["start = −1;  cnt = 0",
                 ["для i = {1..L}",
                  f"start = i + 1,  если  s[i] = '{o}'",
                  [f"если  s[i] = '{c}'", ["если  start ≥ 0  и  i > start", "p[cnt] = start;  len[cnt] = i − start;  cnt = cnt + 1"], "start = −1"]]])
    if kind == "bounded":
        return ("Выделение подстрок – функция extract(s, p, len): разделитель – символ, для которого "
                f"{cond_m}; подстрока – участок между двумя разделителями (участки до первого и после "
                "последнего разделителя не ограничены с обеих сторон), пустые подстроки не выделяются:",
                ["start = −1;  cnt = 0",
                 ["для i = {1..L}",
                  ["если  s[i] – разделитель",
                   ["если  start ≥ 0  и  i > start", "p[cnt] = start;  len[cnt] = i − start;  cnt = cnt + 1"],
                   "start = i + 1"]]])
    return ("Выделение подстрок – функция extract(s, p, len): разделитель – символ, для которого "
            f"{cond_m}; подстроки – непустые участки строки между разделителями, от начала строки до первого "
            "разделителя и от последнего разделителя до конца строки:",
            ["start = 1;  cnt = 0",
             ["для i = {1..L}",
              ["если  s[i] – разделитель",
               ["если  i > start", "p[cnt] = start;  len[cnt] = i − start;  cnt = cnt + 1"],
               "start = i + 1"]],
             ["если  L + 1 > start", "p[cnt] = start;  len[cnt] = L + 1 − start;  cnt = cnt + 1"]])


EXTRACT = {}
for _n, (_text, _kind, _c, _py, _doc, _short) in EX_DEF.items():
    _arg = _c if _kind != "pair" else tuple(_c)
    EXTRACT[_n] = Piece(_n, _text, _ex_c(_n, _text, _kind, _arg), _ex_py(_kind, _arg, _py),
                        _ex_pseudo(_kind, _arg, _doc), _ex_method(_kind, _arg, _doc or ""), label=_short)

# ====================================================================== 2. поиск подстроки
H = {
    "nchars": r'''/* Число символов в подстроке q длиной n байт */
int nchars(const char *q, int n){
    int i, c = 0;
    for (i = 0; i < n; i++)
        if (((unsigned char)q[i] & 0xC0) != 0x80) c++;
    return c;
}
''',
    "ndig": r'''/* Число цифр в подстроке q длиной n байт */
int ndig(const char *q, int n){
    int i, c = 0;
    for (i = 0; i < n; i++)
        if (is_dig(q[i])) c++;
    return c;
}
''',
    "has": r'''/* 1, если символ ch есть в подстроке q длиной n байт (досрочный выход) */
int has(const char *q, int n, char ch){
    int i = 0;
    while (i < n && q[i] != ch)
        i++;
    return i < n;
}
''',
    "nlet": r'''/* Число латинских и русских букв в подстроке q длиной n байт (пробел - буква) */
int nlet(const char *q, int n){
    int i = 0, c = 0;
    while (i < n){
        if (is_lat(q[i]) || is_rus(q + i) || q[i] == ' ') c++;
        i = i + clen(q + i);
    }
    return c;
}
''',
    "ldig": r'''/* Число цифр в начале подстроки q длиной n байт */
int ldig(const char *q, int n){
    int i = 0;
    while (i < n && is_dig(q[i]))
        i++;
    return i;
}
''',
    "tdig": r'''/* Число цифр в конце подстроки q длиной n байт */
int tdig(const char *q, int n){
    int i = n;
    while (i > 0 && is_dig(q[i - 1]))
        i--;
    return n - i;
}
''',
    "tsp": r'''/* Число пробелов в конце подстроки q длиной n байт */
int tsp(const char *q, int n){
    int i = n;
    while (i > 0 && q[i - 1] == ' ')
        i--;
    return n - i;
}
''',
}


def _letters(q):
    return sum(1 for ch in q if is_lat(ch) or is_rus(ch) or ch == " ")


def _lead(q):
    n = 0
    while n < len(q) and is_dig(q[n]):
        n += 1
    return n


def _trail(q, pred):
    n = 0
    while n < len(q) and pred(q[len(q) - 1 - n]):
        n += 1
    return n


def _first(subs, ok):
    return next((t for t, q in enumerate(subs) if ok(q)), -1)


def _best(subs, val, better):
    """Первая подстрока с наилучшим ненулевым значением val (better(v, bv) – v лучше bv)."""
    best, bv = -1, None
    for t, q in enumerate(subs):
        v = val(q)
        if v > 0 and (best < 0 or better(v, bv)):
            best, bv = t, v
    return best


def _fn(sig, body):
    return comment(f"2. Найти подстроку: {sig}; возвращает её номер или -1") + \
        f"int find(char *p[], const int len[], int total){{\n{body}}}\n"


FI_DEF = {
    1: ("самую длинную", ["nchars"], '''    int t, best = 0;
    for (t = 1; t < total; t++)
        if (nchars(p[t], len[t]) > nchars(p[best], len[best])) best = t;
    return best;
''', lambda subs: max(range(len(subs)), key=lambda t: (len(subs[t]), -t)),
        "best := 0\n\t_цикл от_ t := 1 _до_ total − 1\n\t\t_если_ L(p[t]) > L(p[best]) _то_\n\t\t\tbest := t\n"
        "\t\t_всё_\n\t_кц_\n\t_возврат_ best",
        ("самая длинная подстрока (L – число символов; при равенстве остаётся первая):",
         ["best = 0", ["для t = {1..total − 1}", "best = t,  если  L(p[t]) > L(p[best])"]]),
        "самая длинная подстрока"),
    2: ("самую короткую", ["nchars"], '''    int t, best = 0;
    for (t = 1; t < total; t++)
        if (nchars(p[t], len[t]) < nchars(p[best], len[best])) best = t;
    return best;
''', lambda subs: min(range(len(subs)), key=lambda t: (len(subs[t]), t)),
        "best := 0\n\t_цикл от_ t := 1 _до_ total − 1\n\t\t_если_ L(p[t]) < L(p[best]) _то_\n\t\t\tbest := t\n"
        "\t\t_всё_\n\t_кц_\n\t_возврат_ best",
        ("самая короткая подстрока (L – число символов; при равенстве остаётся первая):",
         ["best = 0", ["для t = {1..total − 1}", "best = t,  если  L(p[t]) < L(p[best])"]]),
        "самая короткая подстрока"),
    3: ("содержащую цифры и круглые скобки", ["ndig", "has"], '''    int t = 0;
    while (t < total && !(ndig(p[t], len[t]) > 0 && has(p[t], len[t], '(')
                          && has(p[t], len[t], ')')))
        t++;                            /* досрочный выход на первой подходящей */
    return t < total ? t : -1;
''', lambda subs: _first(subs, lambda q: any(is_dig(c) for c in q) and "(" in q and ")" in q),
        "t := 0\n\t_цикл-пока_ t < total _и_ _не_ (D(p[t]) > 0 _и_ «(» ∈ p[t] _и_ «)» ∈ p[t])\n\t\tt := t + 1\n"
        "\t_кц_\n\t_если_ t < total _то_ _возврат_ t _иначе_ _возврат_ −1 _всё_",
        ("первая подстрока, в которой есть цифры и обе круглые скобки (D – число цифр; досрочный выход):",
         ["t = 0", ["пока  t < total  и  не (D(p[t]) > 0  и  '(' ∈ p[t]  и  ')' ∈ p[t])", "t = t + 1"],
          "find = t,  если  t < total;   иначе  find = −1"]),
        "подстрока с цифрами и круглыми скобками"),
    4: ("содержащую максимальное (но не нулевое) число цифр", ["ndig"], '''    int t, v, best = -1, bv = 0;
    for (t = 0; t < total; t++){
        v = ndig(p[t], len[t]);
        if (v > bv){
            bv = v;
            best = t;
        }
    }
    return best;
''', lambda subs: _best(subs, lambda q: sum(is_dig(c) for c in q), lambda v, b: v > b),
        "best := −1; bv := 0\n\t_цикл от_ t := 0 _до_ total − 1\n\t\t_если_ D(p[t]) > bv _то_\n"
        "\t\t\tbv := D(p[t]); best := t\n\t\t_всё_\n\t_кц_\n\t_возврат_ best",
        ("подстрока с наибольшим ненулевым числом цифр D (при равенстве – первая):",
         ["best = −1;  bv = 0", ["для t = {0..total − 1}", "(bv = D(p[t]),  best = t),  если  D(p[t]) > bv"]]),
        "подстрока с наибольшим числом цифр"),
    5: ("содержащую минимальное (но не нулевое) число латинских и русских букв", ["nlet"],
        '''    int t, v, best = -1, bv = 0;
    for (t = 0; t < total; t++){
        v = nlet(p[t], len[t]);
        if (v > 0 && (best < 0 || v < bv)){
            bv = v;
            best = t;
        }
    }
    return best;
''', lambda subs: _best(subs, _letters, lambda v, b: v < b),
        "best := −1\n\t_цикл от_ t := 0 _до_ total − 1\n\t\t_если_ B(p[t]) > 0 _и_ (best < 0 _или_ B(p[t]) < bv) "
        "_то_\n\t\t\tbv := B(p[t]); best := t\n\t\t_всё_\n\t_кц_\n\t_возврат_ best",
        ("подстрока с наименьшим ненулевым числом букв B (латинские, русские и пробел; при равенстве – первая):",
         ["best = −1", ["для t = {0..total − 1}",
                        ["если  B(p[t]) > 0  и  (best < 0  или  B(p[t]) < bv)", "bv = B(p[t]);  best = t"]]]),
        "подстрока с наименьшим числом букв"),
    6: ("содержащую символ с минимальным кодом", [], '''    int t, i, c, best = 0, bc = code(p[0]);
    for (t = 0; t < total; t++)
        for (i = 0; i < len[t]; i = i + clen(p[t] + i)){
            c = code(p[t] + i);
            if (c < bc){
                bc = c;
                best = t;
            }
        }
    return best;
''', lambda subs: min(range(len(subs)), key=lambda t: (min(ord(c) for c in subs[t]), t)),
        "best := 0; bc := код(p[0][1])\n\t_цикл от_ t := 0 _до_ total − 1\n\t\t_цикл от_ i := 1 _до_ L(p[t])\n"
        "\t\t\t_если_ код(p[t][i]) < bc _то_\n\t\t\t\tbc := код(p[t][i]); best := t\n\t\t\t_всё_\n\t\t_кц_\n"
        "\t_кц_\n\t_возврат_ best",
        ("подстрока, содержащая символ с наименьшим кодом (код символа UTF-8 – его номер в Unicode, функция "
         "code; при равенстве – первая):",
         ["best = 0;  bc = код(p[0][1])",
          ["для t = {0..total − 1},  i = {1..L(p[t])}", "(bc = код(p[t][i]),  best = t),  если  код(p[t][i]) < bc"]]),
        "подстрока с символом минимального кода"),
    7: ("начинающуюся с наибольшего (но не нулевого) числа цифр", ["ldig"], '''    int t, v, best = -1, bv = 0;
    for (t = 0; t < total; t++){
        v = ldig(p[t], len[t]);
        if (v > bv){
            bv = v;
            best = t;
        }
    }
    return best;
''', lambda subs: _best(subs, _lead, lambda v, b: v > b),
        "best := −1; bv := 0\n\t_цикл от_ t := 0 _до_ total − 1\n\t\t_если_ Н(p[t]) > bv _то_\n"
        "\t\t\tbv := Н(p[t]); best := t\n\t\t_всё_\n\t_кц_\n\t_возврат_ best",
        ("подстрока, начинающаяся с наибольшего ненулевого числа цифр Н (цифры подряд с начала подстроки):",
         ["best = −1;  bv = 0", ["для t = {0..total − 1}", "(bv = Н(p[t]),  best = t),  если  Н(p[t]) > bv"]]),
        "подстрока с наибольшим числом цифр в начале"),
    8: ("заканчивающуюся минимальным (но не нулевым) числом цифр", ["tdig"], '''    int t, v, best = -1, bv = 0;
    for (t = 0; t < total; t++){
        v = tdig(p[t], len[t]);
        if (v > 0 && (best < 0 || v < bv)){
            bv = v;
            best = t;
        }
    }
    return best;
''', lambda subs: _best(subs, lambda q: _trail(q, is_dig), lambda v, b: v < b),
        "best := −1\n\t_цикл от_ t := 0 _до_ total − 1\n\t\t_если_ К(p[t]) > 0 _и_ (best < 0 _или_ К(p[t]) < bv) "
        "_то_\n\t\t\tbv := К(p[t]); best := t\n\t\t_всё_\n\t_кц_\n\t_возврат_ best",
        ("подстрока, заканчивающаяся наименьшим ненулевым числом цифр К (цифры подряд в конце подстроки):",
         ["best = −1", ["для t = {0..total − 1}",
                        ["если  К(p[t]) > 0  и  (best < 0  или  К(p[t]) < bv)", "bv = К(p[t]);  best = t"]]]),
        "подстрока с наименьшим числом цифр в конце"),
    9: ("начинающуюся с четного (но не нулевого) числа цифр", ["ldig"], '''    int t = 0;
    while (t < total && (ldig(p[t], len[t]) == 0 || ldig(p[t], len[t]) % 2 != 0))
        t++;                            /* досрочный выход на первой подходящей */
    return t < total ? t : -1;
''', lambda subs: _first(subs, lambda q: _lead(q) > 0 and _lead(q) % 2 == 0),
        "t := 0\n\t_цикл-пока_ t < total _и_ (Н(p[t]) = 0 _или_ Н(p[t]) нечётно)\n\t\tt := t + 1\n\t_кц_\n"
        "\t_если_ t < total _то_ _возврат_ t _иначе_ _возврат_ −1 _всё_",
        ("первая подстрока, начинающаяся с чётного ненулевого числа цифр Н (досрочный выход):",
         ["t = 0", ["пока  t < total  и  (Н(p[t]) = 0  или  Н(p[t]) ⋮̸ 2)", "t = t + 1"],
          "find = t,  если  t < total;   иначе  find = −1"]),
        "подстрока с чётным числом цифр в начале"),
    10: ("заканчивающуюся нечетным числом пробелов", ["tsp"], '''    int t = 0;
    while (t < total && tsp(p[t], len[t]) % 2 == 0)
        t++;                            /* досрочный выход на первой подходящей */
    return t < total ? t : -1;
''', lambda subs: _first(subs, lambda q: _trail(q, lambda c: c == " ") % 2 == 1),
         "t := 0\n\t_цикл-пока_ t < total _и_ П(p[t]) чётно\n\t\tt := t + 1\n\t_кц_\n"
         "\t_если_ t < total _то_ _возврат_ t _иначе_ _возврат_ −1 _всё_",
         ("первая подстрока, заканчивающаяся нечётным числом пробелов П (пробелы подряд в конце; досрочный выход):",
          ["t = 0", ["пока  t < total  и  П(p[t]) ⋮ 2", "t = t + 1"],
           "find = t,  если  t < total;   иначе  find = −1"]),
         "подстрока с нечётным числом пробелов в конце"),
}

FIND = {}
for _n, (_text, _deps, _body, _py, _ps, _meth, _label) in FI_DEF.items():
    _deps = list(_deps) + (["code"] if _n == 6 else [])
    FIND[_n] = Piece(_n, _text, _fn(_text, _body), _py, f"\n_функция_ find(p, len, total)\n_нач_\n\t{_ps}\n_кон_\n",
                     ("Поиск подстроки – функция find(p, len, total): " + _meth[0], _meth[1]), deps=_deps,
                     label=_label)

# ====================================================================== 3. преобразование строки


def _first_digit(s):
    return next((i for i, c in enumerate(s) if is_dig(c)), -1)


def _last_digit(s):
    return max((i for i, c in enumerate(s) if is_dig(c)), default=-1)


def _ins_after_first(s):
    i = _first_digit(s)
    return (False, s) if i < 0 else (True, s[:i + 1] + "..." + s[i + 1:])


def _ins_before_last(s):
    j = _last_digit(s)
    return (False, s) if j < 0 else (True, s[:j] + "***" + s[j:])


def _tr(sig, body):
    return comment(f"3. Преобразовать строку s: {sig}; возвращает 1 - выполнено, 0 - невозможно") + \
        f"int transform(char *s){{\n{body}}}\n"


_SHIFT_DEL = '''    int i = 0;
    while (s[i] != '\\0')
        if ({cond})
            del_at(s, i, 1);            /* удаление сдвигом влево */
        else
            i++;
    return 1;
'''

TR_DEF = {
    1: ("удалить путем сдвига все латинские буквы", ["edit"], _SHIFT_DEL.format(cond="is_lat(s[i])"),
        lambda s: (True, "".join(c for c in s if not is_lat(c))),
        "i := 1\n\t_цикл-пока_ i ≤ L(s)\n\t\t_если_ лат(s[i]) _то_\n\t\t\tудалить(s, i)\n\t\t_иначе_\n"
        "\t\t\ti := i + 1\n\t\t_всё_\n\t_кц_",
        ["i = 1", ["пока  i ≤ L", "удалить(s, i),  если  лат(s[i])", "i = i + 1,  иначе"]]),
    2: ("удалить путем сдвига все символы, отличные от русских букв", ["edit"], '''    int i = 0;
    while (s[i] != '\\0')
        if (is_rus(s + i))
            i = i + 2;                  /* русская буква - 2 байта */
        else
            del_at(s, i, clen(s + i));  /* удаление символа сдвигом влево */
    return 1;
''', lambda s: (True, "".join(c for c in s if is_rus(c))),
        "i := 1\n\t_цикл-пока_ i ≤ L(s)\n\t\t_если_ рус(s[i]) _то_\n\t\t\ti := i + 1\n\t\t_иначе_\n"
        "\t\t\tудалить(s, i)\n\t\t_всё_\n\t_кц_",
        ["i = 1", ["пока  i ≤ L", "i = i + 1,  если  рус(s[i])", "удалить(s, i),  иначе"]]),
    3: ("удалить пробелы, расположенные в начале строки", ["edit"], '''    int n = 0;
    while (s[n] == ' ')
        n++;
    if (n > 0)
        del_at(s, 0, n);                /* сдвиг строки влево на n позиций */
    return 1;
''', lambda s: (True, s.lstrip(" ")),
        "n := 0\n\t_цикл-пока_ s[n + 1] = « »\n\t\tn := n + 1\n\t_кц_\n\tудалить первые n символов строки s",
        ["n = 0", ["пока  s[n + 1] = ' '", "n = n + 1"], "s = s[n + 1 : L]  (сдвиг влево на n)"]),
    4: ("удалить путем сдвига все четные цифры", ["edit"],
        _SHIFT_DEL.format(cond="is_dig(s[i]) && (s[i] - '0') % 2 == 0"),
        lambda s: (True, "".join(c for c in s if not (is_dig(c) and int(c) % 2 == 0))),
        "i := 1\n\t_цикл-пока_ i ≤ L(s)\n\t\t_если_ цифра(s[i]) _и_ s[i] чётная _то_\n\t\t\tудалить(s, i)\n"
        "\t\t_иначе_\n\t\t\ti := i + 1\n\t\t_всё_\n\t_кц_",
        ["i = 1", ["пока  i ≤ L", "удалить(s, i),  если  цифра(s[i])  и  s[i] ⋮ 2", "i = i + 1,  иначе"]]),
    5: ("заменить каждую цифру на две точки", ["edit"], '''    int i = 0;
    while (s[i] != '\\0')
        if (is_dig(s[i])){
            s[i] = '.';
            ins_at(s, i, ".");          /* вторая точка - вставка сдвигом вправо */
            i = i + 2;
        }
        else
            i++;
    return 1;
''', lambda s: (True, "".join(".." if is_dig(c) else c for c in s)),
        "i := 1\n\t_цикл-пока_ i ≤ L(s)\n\t\t_если_ цифра(s[i]) _то_\n\t\t\ts[i] := «.»; вставить(s, i, «.»); "
        "i := i + 2\n\t\t_иначе_\n\t\t\ti := i + 1\n\t\t_всё_\n\t_кц_",
        ["i = 1", ["пока  i ≤ L", "(s[i] = '.',  вставить(s, i, '.'),  i = i + 2),  если  цифра(s[i])",
                   "i = i + 1,  иначе"]]),
    6: ("заменить все цифры на латинские буквы с соответствующим номером в алфавите ('0' на 'A', '1' на 'B', "
        "'2' на 'C' и т. д.)", [], '''    int i;
    for (i = 0; s[i] != '\\0'; i++)
        if (is_dig(s[i]))
            s[i] = (char)('A' + (s[i] - '0'));
    return 1;
''', lambda s: (True, "".join(chr(ord("A") + int(c)) if is_dig(c) else c for c in s)),
        "_цикл от_ i := 1 _до_ L(s)\n\t\t_если_ цифра(s[i]) _то_\n\t\t\ts[i] := буква с номером s[i]\n"
        "\t\t_всё_\n\t_кц_",
        [["для i = {1..L}", "s[i] = 'A' + (s[i] − '0'),  если  цифра(s[i])"]]),
    7: ("заменить каждую русскую букву на две такие же буквы", ["edit"], '''    char b[3];
    int i = 0;
    b[2] = '\\0';
    while (s[i] != '\\0')
        if (is_rus(s + i)){
            b[0] = s[i];                /* русская буква - 2 байта */
            b[1] = s[i + 1];
            ins_at(s, i, b);            /* вставка копии сдвигом вправо */
            i = i + 4;
        }
        else
            i++;
    return 1;
''', lambda s: (True, "".join(c * 2 if is_rus(c) else c for c in s)),
        "i := 1\n\t_цикл-пока_ i ≤ L(s)\n\t\t_если_ рус(s[i]) _то_\n\t\t\tвставить(s, i, s[i]); i := i + 2\n"
        "\t\t_иначе_\n\t\t\ti := i + 1\n\t\t_всё_\n\t_кц_",
        ["i = 1", ["пока  i ≤ L", "(вставить(s, i, s[i]),  i = i + 2),  если  рус(s[i])", "i = i + 1,  иначе"]]),
    8: ("вставить цифру '0' после каждой цифры '1'", ["edit"], '''    int i = 0;
    while (s[i] != '\\0')
        if (s[i] == '1'){
            ins_at(s, i + 1, "0");      /* вставка сдвигом вправо */
            i = i + 2;
        }
        else
            i++;
    return 1;
''', lambda s: (True, s.replace("1", "10")),
        "i := 1\n\t_цикл-пока_ i ≤ L(s)\n\t\t_если_ s[i] = «1» _то_\n\t\t\tвставить(s, i + 1, «0»); i := i + 2\n"
        "\t\t_иначе_\n\t\t\ti := i + 1\n\t\t_всё_\n\t_кц_",
        ["i = 1", ["пока  i ≤ L", "(вставить(s, i + 1, '0'),  i = i + 2),  если  s[i] = '1'", "i = i + 1,  иначе"]]),
    9: ("вставить три звездочки перед каждой цифрой", ["edit"], '''    int i = 0;
    while (s[i] != '\\0')
        if (is_dig(s[i])){
            ins_at(s, i, "***");        /* вставка сдвигом вправо */
            i = i + 4;
        }
        else
            i++;
    return 1;
''', lambda s: (True, "".join("***" + c if is_dig(c) else c for c in s)),
        "i := 1\n\t_цикл-пока_ i ≤ L(s)\n\t\t_если_ цифра(s[i]) _то_\n\t\t\tвставить(s, i, «три звёздочки»); "
        "i := i + 4\n\t\t_иначе_\n\t\t\ti := i + 1\n\t\t_всё_\n\t_кц_",
        ["i = 1", ["пока  i ≤ L", "(вставить(s, i, '∗∗∗'),  i = i + 4),  если  цифра(s[i])", "i = i + 1,  иначе"]]),
    10: ("вставить три точки после первой цифры", ["edit"], '''    int i = 0;
    while (s[i] != '\\0' && !is_dig(s[i]))
        i++;                            /* досрочный выход на первой цифре */
    if (s[i] == '\\0') return 0;
    ins_at(s, i + 1, "...");
    return 1;
''', _ins_after_first,
         "i := 1\n\t_цикл-пока_ i ≤ L(s) _и_ _не_ цифра(s[i])\n\t\ti := i + 1\n\t_кц_\n"
         "\t_если_ i > L(s) _то_ _возврат_ 0 _всё_\n\tвставить(s, i + 1, «...»)",
         ["i = 1", ["пока  i ≤ L  и  не цифра(s[i])", "i = i + 1"],
          "вставить(s, i + 1, '...'),  если  i ≤ L", "иначе – преобразование невозможно"],
         "в строке нет цифр"),
    11: ("вставить три звездочки перед последней цифрой", ["edit"], '''    int i, last = -1;
    for (i = 0; s[i] != '\\0'; i++)
        if (is_dig(s[i])) last = i;
    if (last < 0) return 0;
    ins_at(s, last, "***");
    return 1;
''', _ins_before_last,
         "last := 0\n\t_цикл от_ i := 1 _до_ L(s)\n\t\t_если_ цифра(s[i]) _то_\n\t\t\tlast := i\n\t\t_всё_\n\t_кц_\n"
         "\t_если_ last = 0 _то_ _возврат_ 0 _всё_\n\tвставить(s, last, «три звёздочки»)",
         ["last = 0", ["для i = {1..L}", "last = i,  если  цифра(s[i])"],
          "вставить(s, last, '∗∗∗'),  если  last > 0", "иначе – преобразование невозможно"],
         "в строке нет цифр"),
}

TRANSFORM = {}
for _n, (_text, _deps, _body, _py, _ps, _items, *_fail) in TR_DEF.items():
    TRANSFORM[_n] = Piece(_n, _text, _tr(_text, _body), _py,
                          f"\n_функция_ transform(s)\n_нач_\n\t{_ps}\n\t_возврат_ 1\n_кон_\n",
                          ("Преобразование строки – функция transform(s) (удалить(s, i) – удаление символа "
                           "сдвигом влево, вставить(s, i, t) – вставка t перед i-м символом сдвигом вправо):",
                           _items),
                          deps=_deps, fail=_fail[0] if _fail else None)
