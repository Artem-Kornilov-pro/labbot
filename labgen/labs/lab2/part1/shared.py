"""Общие фрагменты задач части I: сортировка «пузырьком» с досрочным выходом, поиск в массиве, вывод матрицы."""
from ..common import py_print_matrix

ABS_DEFINE = "\n#define ABS(a) ((a) < 0 ? -(a) : (a))   /* модуль числа */"


def c_find(arr, k, val, idx="t"):
    """Поиск val в arr[1:k] с досрочным выходом; после цикла idx > k - не найден."""
    return f'''{idx} = 1;
        while ({idx} <= {k} && {arr}[{idx}] != {val})    /* досрочный выход при совпадении */
            {idx}++;'''


def py_find(arr, k, val):
    t = 1
    while t <= k and arr[t] != val:
        t += 1
    return t


def c_sort_col(M, j, n, desc=False, ind="            "):
    op = "<" if desc else ">"
    return f'''{ind}p = {n};
{ind}sw = 1;
{ind}while (sw){{             /* выход, если за проход не было обменов */
{ind}    sw = 0;
{ind}    for (i = 1; i < p; i++)
{ind}        if ({M}[i][{j}] {op} {M}[i + 1][{j}]){{
{ind}            c = {M}[i][{j}];
{ind}            {M}[i][{j}] = {M}[i + 1][{j}];
{ind}            {M}[i + 1][{j}] = c;
{ind}            sw = 1;
{ind}        }}
{ind}    p--;
{ind}}}'''


def c_sort_row(M, i, m, desc=False, ind="            "):
    op = "<" if desc else ">"
    return f'''{ind}p = {m};
{ind}sw = 1;
{ind}while (sw){{             /* выход, если за проход не было обменов */
{ind}    sw = 0;
{ind}    for (j = 1; j < p; j++)
{ind}        if ({M}[{i}][j] {op} {M}[{i}][j + 1]){{
{ind}            c = {M}[{i}][j];
{ind}            {M}[{i}][j] = {M}[{i}][j + 1];
{ind}            {M}[{i}][j + 1] = c;
{ind}            sw = 1;
{ind}        }}
{ind}    p--;
{ind}}}'''


def py_sort_col(M, j, n, desc=False):
    col = sorted((M[i][j] for i in range(1, n + 1)), reverse=desc)
    for i in range(1, n + 1):
        M[i][j] = col[i - 1]


def py_sort_row(M, i, m, desc=False):
    M[i][1:m + 1] = sorted(M[i][1:m + 1], reverse=desc)


def c_print_list(title, arr, cnt):
    return f'''        printf("{title}");
        for (t = 1; t <= {cnt}; t++)
            printf("%d ", {arr}[t]);
        printf("\\n");'''


def py_print_list(con, title, values):
    con.printf(title + "".join(f"{v} " for v in values) + "\n")


def c_print_mat(M, rows, cols, title, ind="        "):
    return f'''{ind}printf("{title}\\n");
{ind}for (i = 1; i <= {rows}; i++){{
{ind}    for (j = 1; j <= {cols}; j++)
{ind}        printf("%5d", {M}[i][j]);
{ind}    printf("\\n");
{ind}}}'''


def py_print_mat(con, M, rows, cols, title):
    py_print_matrix(con, M, rows, cols, title)


def sort_col_method(M, desc=False):
    op = "<" if desc else ">"
    return ["p = n;  sw = 1",
            ["пока  sw = 1", "sw = 0",
             ["для i = {1..p − 1}", f"({M}[i, j] ↔ {M}[i + 1, j],  sw = 1),  если  {M}[i, j] {op} {M}[i + 1, j]"],
             "p = p − 1"]]


def sort_row_method(M, desc=False):
    op = "<" if desc else ">"
    return ["p = m;  sw = 1",
            ["пока  sw = 1", "sw = 0",
             ["для j = {1..p − 1}", f"({M}[i, j] ↔ {M}[i, j + 1],  sw = 1),  если  {M}[i, j] {op} {M}[i, j + 1]"],
             "p = p − 1"]]


def sort_col_pseudo(M, desc=False, ind=3):
    op = "<" if desc else ">"
    T = "\t" * ind
    return (f"{T}p := n; sw := 1\n"
            f"{T}_цикл-пока_ sw = 1\n"
            f"{T}\tsw := 0\n"
            f"{T}\t_цикл_ _от_ i := 1 _до_ p − 1\n"
            f"{T}\t\t_если_ {M}[i, j] {op} {M}[i + 1, j] _то_\n"
            f"{T}\t\t\tc := {M}[i, j]; {M}[i, j] := {M}[i + 1, j]; {M}[i + 1, j] := c; sw := 1\n"
            f"{T}\t\t_всё_\n"
            f"{T}\t_кц_\n"
            f"{T}\tp := p − 1\n"
            f"{T}_кц_")


def sort_row_pseudo(M, desc=False, ind=3):
    op = "<" if desc else ">"
    T = "\t" * ind
    return (f"{T}p := m; sw := 1\n"
            f"{T}_цикл-пока_ sw = 1\n"
            f"{T}\tsw := 0\n"
            f"{T}\t_цикл_ _от_ j := 1 _до_ p − 1\n"
            f"{T}\t\t_если_ {M}[i, j] {op} {M}[i, j + 1] _то_\n"
            f"{T}\t\t\tc := {M}[i, j]; {M}[i, j] := {M}[i, j + 1]; {M}[i, j + 1] := c; sw := 1\n"
            f"{T}\t\t_всё_\n"
            f"{T}\t_кц_\n"
            f"{T}\tp := p − 1\n"
            f"{T}_кц_")


def mat_box(M, rows="n", cols="m"):
    return [f"<<{M}[1,1]>> … <<{M}[1,{cols}]>>", "…", f"<<{M}[{rows},1]>> … <<{M}[{rows},{cols}]>>"]
