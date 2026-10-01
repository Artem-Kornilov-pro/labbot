"""Общие фрагменты задач части II: вывод массивов и построение тестов."""
from ..common import Test
from ..inputs import PositiveArray


def c_print_arr(title, arr, cnt, ind="        "):
    return f'''{ind}printf("{title}");
{ind}for (i = 1; i <= {cnt}; i++)
{ind}    printf("%d ", {arr}[i]);
{ind}printf("\\n");'''


def py_print_arr(con, title, values):
    con.printf(title + "".join(f"{v} " for v in values) + "\n")


def maker(inp: PositiveArray):
    def _t(arr, case, z=None):
        return Test(inp.lines(arr, z), inp.shown(arr, z), case)
    return _t


def bad_test(inp: PositiveArray, good, case, z=None, z_bad=None):
    """Тест с недопустимыми данными: n = 0, буквы; массив с отрицательным, дробным, неполный; затем верный."""
    lines = ["0", "x", str(len(good)), "-5 " + " ".join(map(str, good[1:])), "3.5 " + " ".join(map(str, good[1:])),
             " ".join(map(str, good[:-1])) or "q", " ".join(map(str, good))]
    shown = ["n: 0 / x / " + str(len(good)), "X: с −5 / с 3.5 / не хватает чисел / " + " ".join(map(str, good))]
    if z is not None:
        lines += list(z_bad or []) + [str(z)]
        shown += ["Z: " + " / ".join(list(z_bad or []) + [str(z)])]
    return Test(lines, shown, case)
