"""Типовые наборы входных данных лабы 2: код ввода на C, эмулятор, окна спецификации, «Дано»/«При», тесты."""
from .common import (EMAX, AMAX, KMAX, NMAX, c_read_array, c_read_matrix, c_print_matrix, c_print_array,
                     py_read_array, py_read_matrix, py_print_matrix, py_print_array, parse_line)

DEFINES_P1 = ("#define NMAX 9          /* максимальное число строк / столбцов матрицы */\n"
              "#define KMAX 20         /* максимальная длина массива */\n"
              "#define EMAX 99         /* максимальный модуль элемента матрицы */\n"
              "#define AMAX 999999999  /* максимальный модуль элемента массива */")
DEFINES_P2 = ("#define KMAX 20         /* максимальная длина массива */\n"
              "#define AMAX 999999999  /* максимальное значение элемента массива */")


# ------------------------------------------------------------------ C / Python: размеры
def _c_dims(nv, mv, mname, dims):
    return f'''    do{{
        printf("Введите число строк и столбцов матрицы {mname} "
               "(два целых числа от 1 до %d): ", NMAX);
        ok = read_line({dims}, 2, 1, NMAX);
        if (ok == -1) return 1;
        if (!ok)
            printf("Ошибка! Нужно ввести два целых числа от 1 до %d.\\n", NMAX);
    }} while (!ok);
    {nv} = {dims}[0];
    {mv} = {dims}[1];
'''


def _py_dims(con, mname):
    while True:
        con.printf(f"Введите число строк и столбцов матрицы {mname} (два целых числа от 1 до %d): " % NMAX)
        ok, v = parse_line(con.readline(), 2, 1, NMAX)
        if ok:
            return v
        con.printf("Ошибка! Нужно ввести два целых числа от 1 до %d.\n" % NMAX)


def _c_len(kv, aname, what):
    return f'''    do{{
        printf("Введите длину {what} {aname} (целое число от 1 до %d): ", KMAX);
        ok = read_line(&{kv}, 1, 1, KMAX);
        if (ok == -1) return 1;
        if (!ok) printf("Ошибка! Нужно ввести целое число от 1 до %d.\\n", KMAX);
    }} while (!ok);
'''


def _py_len(con, aname, what):
    while True:
        con.printf(f"Введите длину {what} {aname} (целое число от 1 до %d): " % KMAX)
        ok, v = parse_line(con.readline(), 1, 1, KMAX)
        if ok:
            return v[0]
        con.printf("Ошибка! Нужно ввести целое число от 1 до %d.\n" % KMAX)


# ------------------------------------------------------------------ спецификация
def _spec_dims(mname, nv, mv):
    return [
        ("rep_start",),
        ("box", [f"Введите число строк и столбцов матрицы {mname} (два целых числа от 1 до <<NMAX>>): "
                 f"<{nv}> <{mv}>"], False),
        ("label", f"При ошибке ввода ({nv}, {mv} ∉ Z или вне [1; NMAX])"),
        ("box", ["Ошибка! Нужно ввести два целых числа от 1 до <<NMAX>>."], True),
        ("rep_end", f"До {nv}, {mv} ∈ Z и 1 ≤ {nv}, {mv} ≤ NMAX"),
    ]


def _spec_matrix(mname, nv, mv):
    return [
        ("box", [f"Введите матрицу {mname} построчно: в каждой строке <<{mv}>> целых чисел "
                 f"от <<-EMAX>> до <<EMAX>> через пробел."], False),
        ("rep_start",),
        ("box", [f"строка <<i>>: <{mname}[i,1]> <{mname}[i,2]> … <{mname}[i,{mv}]>"], False),
        ("label", "При ошибке в строке (не числа, не то количество, вне диапазона)"),
        ("box", ["Ошибка! Повторите ввод строки <<i>>."], True),
        ("rep_end", f"До строка введена верно; для i = 1, …, {nv}"),
    ]


def _spec_len(kv, aname, what):
    return [
        ("rep_start",),
        ("box", [f"Введите длину {what} {aname} (целое число от 1 до <<KMAX>>): <{kv}>"], False),
        ("label", f"При {kv} ∉ Z или {kv} < 1 или {kv} > KMAX"),
        ("box", ["Ошибка! Нужно ввести целое число от 1 до <<KMAX>>."], True),
        ("rep_end", f"До {kv} ∈ Z и 1 ≤ {kv} ≤ KMAX"),
    ]


def _spec_array(aname, kv, lo, hi, what):
    return [
        ("rep_start",),
        ("box", [f"Введите {what} {aname}: <<{kv}>> целых чисел от <<{lo}>> до <<{hi}>> через пробел: "
                 f"<{aname}[1]> <{aname}[2]> … <{aname}[{kv}]>"], False),
        ("label", "При ошибке ввода"),
        ("box", [f"Ошибка! Нужно ввести <<{kv}>> целых чисел от <<{lo}>> до <<{hi}>>."], True),
        ("rep_end", f"До {aname}[1:{kv}] введён верно"),
    ]


def spec_print_matrix(mname, nv, mv, title):
    return [("box", [title, f"<<{mname}[1,1]>> <<{mname}[1,2]>> … <<{mname}[1,{mv}]>>", "…",
                     f"<<{mname}[{nv},1]>> <<{mname}[{nv},2]>> … <<{mname}[{nv},{mv}]>>"], False)]


# ------------------------------------------------------------------ наборы
class MatrixArray:
    """Матрица M[1:n, 1:m] и массив K[1:k] (большинство задач части I)."""

    def __init__(self, mname, aname):
        self.M, self.K = mname, aname
        self.defines = DEFINES_P1
        self.decls = (f"    int n, m, k, i, j, ok, nm[2];\n"
                      f"    int {mname}[NMAX + 1][NMAX + 1], {aname}[KMAX + 1];\n")
        self.c_input = (_c_dims("n", "m", mname, "nm") + c_read_matrix(mname, "n", "m")
                        + _c_len("k", aname, "массива") + c_read_array(aname, "k", "-AMAX", "AMAX", "массив")
                        + c_print_matrix(mname, "n", "m", f"\\nИсходная матрица {mname}:")
                        + c_print_array(aname, "k", f"Массив {aname}: "))
        self.given = [f"n, m, {mname}[1:n, 1:m] – матрица; k, {aname}[1:k] – массив."]
        self.when = [f"n, m ∈ N, n ≤ NMAX, m ≤ NMAX, NMAX = {NMAX}; {mname}[i, j] ∈ Z, "
                     f"|{mname}[i, j]| ≤ EMAX = {EMAX};",
                     f"k ∈ N, k ≤ KMAX = {KMAX}; {aname}[t] ∈ Z, |{aname}[t]| ≤ AMAX = {AMAX}."]
        self.pseudo_in = f"ввод(n, m, {mname}[1:n, 1:m], k, {aname}[1:k])"
        self.spec = (_spec_dims(mname, "n", "m") + _spec_matrix(mname, "n", "m") + _spec_len("k", aname, "массива")
                     + _spec_array(aname, "k", "-AMAX", "AMAX", "массив")
                     + spec_print_matrix(mname, "n", "m", f"Исходная матрица {mname}:")
                     + [("box", [f"Массив {aname}: <<{aname}[1]>> <<{aname}[2]>> … <<{aname}[k]>>"], False)])

    def read(self, con):
        n, m = _py_dims(con, self.M)
        mat = py_read_matrix(con, self.M, n, m)
        k = _py_len(con, self.K, "массива")
        arr = py_read_array(con, self.K, k, -AMAX, AMAX, "массив")
        py_print_matrix(con, mat, n, m, f"\nИсходная матрица {self.M}:")
        py_print_array(con, arr, k, f"Массив {self.K}: ")
        return n, m, mat, k, arr

    def lines(self, mat, arr):
        return [f"{len(mat)} {len(mat[0])}", *[" ".join(map(str, r)) for r in mat], str(len(arr)),
                " ".join(map(str, arr))]

    def shown(self, mat, arr):
        return [f"n = {len(mat)}, m = {len(mat[0])}", f"{self.M} =", *["  " + " ".join(f"{v:3d}" for v in r)
                                                                     for r in mat],
                f"k = {len(arr)}", f"{self.K} = {' '.join(map(str, arr))}"]


class MatrixOnly:
    """Только матрица M[1:n, 1:m]."""

    def __init__(self, mname):
        self.M = mname
        self.defines = DEFINES_P1
        self.decls = f"    int n, m, i, j, ok, nm[2];\n    int {mname}[NMAX + 1][NMAX + 1];\n"
        self.c_input = (_c_dims("n", "m", mname, "nm") + c_read_matrix(mname, "n", "m")
                        + c_print_matrix(mname, "n", "m", f"\\nИсходная матрица {mname}:"))
        self.given = [f"n, m, {mname}[1:n, 1:m] – матрица."]
        self.when = [f"n, m ∈ N, n ≤ NMAX, m ≤ NMAX, NMAX = {NMAX}; {mname}[i, j] ∈ Z, "
                     f"|{mname}[i, j]| ≤ EMAX = {EMAX}."]
        self.pseudo_in = f"ввод(n, m, {mname}[1:n, 1:m])"
        self.spec = (_spec_dims(mname, "n", "m") + _spec_matrix(mname, "n", "m")
                     + spec_print_matrix(mname, "n", "m", f"Исходная матрица {mname}:"))

    def read(self, con):
        n, m = _py_dims(con, self.M)
        mat = py_read_matrix(con, self.M, n, m)
        py_print_matrix(con, mat, n, m, f"\nИсходная матрица {self.M}:")
        return n, m, mat

    def lines(self, mat):
        return [f"{len(mat)} {len(mat[0])}", *[" ".join(map(str, r)) for r in mat]]

    def shown(self, mat):
        return [f"n = {len(mat)}, m = {len(mat[0])}", f"{self.M} =",
                *["  " + " ".join(f"{v:3d}" for v in r) for r in mat]]


class TwoMatrices:
    """Матрицы A[1:n, 1:m] и B[1:x, 1:y] (задача 7)."""

    def __init__(self):
        self.defines = DEFINES_P1
        self.decls = ("    int n, m, x, y, p, q, i, j, ok, nm[2];\n"
                      "    int A[NMAX + 1][NMAX + 1], B[NMAX + 1][NMAX + 1], C[NMAX + 1][NMAX + 1];\n")
        self.c_input = (_c_dims("n", "m", "A", "nm") + c_read_matrix("A", "n", "m")
                        + _c_dims("x", "y", "B", "nm") + c_read_matrix("B", "x", "y")
                        + c_print_matrix("A", "n", "m", "\\nИсходная матрица A:")
                        + c_print_matrix("B", "x", "y", "Исходная матрица B:"))
        self.given = ["n, m, A[1:n, 1:m] – первая матрица; x, y, B[1:x, 1:y] – вторая матрица."]
        self.when = [f"n, m, x, y ∈ N, n, m, x, y ≤ NMAX, NMAX = {NMAX};",
                     f"A[i, j], B[i, j] ∈ Z, |A[i, j]|, |B[i, j]| ≤ EMAX = {EMAX}."]
        self.pseudo_in = "ввод(n, m, A[1:n, 1:m], x, y, B[1:x, 1:y])"
        self.spec = (_spec_dims("A", "n", "m") + _spec_matrix("A", "n", "m")
                     + _spec_dims("B", "x", "y") + _spec_matrix("B", "x", "y")
                     + spec_print_matrix("A", "n", "m", "Исходная матрица A:")
                     + spec_print_matrix("B", "x", "y", "Исходная матрица B:"))

    def read(self, con):
        n, m = _py_dims(con, "A")
        a = py_read_matrix(con, "A", n, m)
        x, y = _py_dims(con, "B")
        b = py_read_matrix(con, "B", x, y)
        py_print_matrix(con, a, n, m, "\nИсходная матрица A:")
        py_print_matrix(con, b, x, y, "Исходная матрица B:")
        return n, m, a, x, y, b

    def lines(self, a, b):
        return [f"{len(a)} {len(a[0])}", *[" ".join(map(str, r)) for r in a],
                f"{len(b)} {len(b[0])}", *[" ".join(map(str, r)) for r in b]]

    def shown(self, a, b):
        return [f"n = {len(a)}, m = {len(a[0])}", "A =", *["  " + " ".join(f"{v:3d}" for v in r) for r in a],
                f"x = {len(b)}, y = {len(b[0])}", "B =", *["  " + " ".join(f"{v:3d}" for v in r) for r in b]]


class PositiveArray:
    """Часть II: массив целых положительных чисел X[1:n] (и при need_z — цифра Z)."""

    def __init__(self, z_lo=None):
        self.z_lo = z_lo
        self.defines = DEFINES_P2
        z = ", z" if z_lo is not None else ""
        self.decls = f"    int n, i, ok{z};\n    int X[KMAX + 1];\n"
        self.c_input = (_c_len("n", "X", "массива")
                        + c_read_array("X", "n", "1", "AMAX", "массив"))
        if z_lo is not None:
            self.c_input += f'''    do{{
        printf("Введите цифру Z (целое число от %d до 9): ", {z_lo});
        ok = read_line(&z, 1, {z_lo}, 9);
        if (ok == -1) return 1;
        if (!ok) printf("Ошибка! Нужно ввести одну цифру от %d до 9.\\n", {z_lo});
    }} while (!ok);
'''
        self.c_input += c_print_array("X", "n", "\\nИсходный массив X: ")
        self.given = ["n, X[1:n] – массив целых положительных чисел" + ("; Z – заданная цифра." if z else ".")]
        self.when = [f"n ∈ N, n ≤ KMAX = {KMAX}; X[i] ∈ N, X[i] ≤ AMAX = {AMAX}"
                     + (f"; Z ∈ Z, {z_lo} ≤ Z ≤ 9." if z else ".")]
        self.pseudo_in = "ввод(n, X[1:n]" + (", Z)" if z else ")")
        self.spec = (_spec_len("n", "X", "массива") + _spec_array("X", "n", "1", "AMAX", "массив"))
        if z:
            self.spec += [
                ("rep_start",),
                ("box", [f"Введите цифру Z (целое число от {z_lo} до 9): <Z>"], False),
                ("label", f"При Z ∉ Z или Z < {z_lo} или Z > 9"),
                ("box", [f"Ошибка! Нужно ввести одну цифру от {z_lo} до 9."], True),
                ("rep_end", f"До Z ∈ Z и {z_lo} ≤ Z ≤ 9"),
            ]
        self.spec += [("box", ["Исходный массив X: <<X[1]>> <<X[2]>> … <<X[n]>>"], False)]

    def read(self, con):
        n = _py_len(con, "X", "массива")
        arr = py_read_array(con, "X", n, 1, AMAX, "массив")
        z = None
        if self.z_lo is not None:
            while True:
                con.printf("Введите цифру Z (целое число от %d до 9): " % self.z_lo)
                ok, v = parse_line(con.readline(), 1, self.z_lo, 9)
                if ok:
                    z = v[0]
                    break
                con.printf("Ошибка! Нужно ввести одну цифру от %d до 9.\n" % self.z_lo)
        py_print_array(con, arr, n, "\nИсходный массив X: ")
        return (n, arr, z) if self.z_lo is not None else (n, arr)

    def lines(self, arr, z=None):
        return [str(len(arr)), " ".join(map(str, arr))] + ([str(z)] if z is not None else [])

    def shown(self, arr, z=None):
        return [f"n = {len(arr)}", "X = " + " ".join(map(str, arr))] + ([f"Z = {z}"] if z is not None else [])
