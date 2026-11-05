"""Описание задачи лаб 3–5: программа на C из функций, эмулятор, разделы отчёта, тесты."""
from dataclasses import dataclass, field

from .cio import Console, EndOfInput


@dataclass
class Test:
    lines: list                 # строки ввода с клавиатуры
    shown: list                 # как показать исходные данные в таблице тестов
    case: str                   # проверяемый случай
    files: dict = field(default_factory=dict)   # входные файлы {имя: bytes}, существующие до запуска


@dataclass
class Task:
    lab: int
    part: str                   # «I», «II», «III»; «» – лаба из одной программы (лаба 4)
    num: object                 # номер задания (у лабы 4 – строка «3, 5, 7»)
    statement: str              # условие (как в практикуме), простым текстом
    includes: list              # заголовочные файлы, кроме stdio.h
    defines: str                # #define
    functions: str              # вспомогательные функции и функции задачи (до main)
    decls: str                  # объявления переменных main
    body: str                   # тело main после заголовка
    simulate: object            # fn(con) – то же, что main после заголовка (Python)
    given: list                 # Дано
    result: list                # Результат
    when: list                  # При
    svyaz: object               # fn(rep) – пункт «Связь»
    method: list                # пункты метода: (заголовок, items)
    spec: list                  # окна спецификации (без заголовка программы)
    pseudo: str                 # псевдокод
    tests: list = field(default_factory=list)
    note: str = ""              # пояснение под таблицей тестов
    formulas: object = None     # fn(rep) – формулы условия в разделе «Задание» (лаба 3, часть I)
    file: str = ""              # имя файла программы
    lead: object = None         # текст условия в отчёте, если формулы условия выводятся formulas (иначе statement)
    prelude: str = ""           # строки до #include (например, _CRT_SECURE_NO_WARNINGS для Visual Studio)
    setup: str = ""             # операторы в начале main до заголовка (например, настройка консоли Windows)

    @property
    def title(self):
        part = f", часть {self.part}" if self.part else ""
        word = "задания" if isinstance(self.num, str) else "задание"
        return f"Лабораторная работа № {self.lab}{part}, {word} {self.num}"

    def c_source(self, author, variant):
        inc = "".join(f"#include <{h}>\n" for h in self.includes)
        head = self.title.replace("№ ", "№")
        pre = f"{self.prelude}\n" if self.prelude else ""
        return (f"/* {head}.\n   Вариант {variant}. Выполнил: {author} */\n{pre}"
                f"#include <stdio.h>\n{inc}{self.defines}\n\n{self.functions.strip(chr(10))}\n\n"
                f"int main(){{\n{self.decls}\n{self.setup}"
                f'    printf("{self.title}\\n"\n'
                f'           "Выполнил: {author}\\n\\n");\n\n'
                f"{self.body.rstrip()}\n    return 0;\n}}\n")

    def run(self, test_or_lines, author):
        tst = test_or_lines if isinstance(test_or_lines, Test) else Test(list(test_or_lines), [], "")
        con = Console(tst.lines, tst.files)
        con.printf(f"{self.title}\nВыполнил: {author}\n\n")
        try:
            self.simulate(con)
        except EndOfInput:
            pass
        return con
