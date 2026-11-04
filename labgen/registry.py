"""Реестр лабораторных работ, которые умеет генерировать бот.

Чтобы добавить новую лабу, создайте пакет labgen/labs/labN с тем же интерфейсом, что у lab2/lab3
(LAB_NO, TITLE, PARTS, tasks_for_variant, task_texts, generate), и добавьте его в LABS.
Лабы 3–5 собраны на общем каркасе labgen/labs/core (функции all_tasks() – для проверок).
"""
from .labs import lab2, lab3

LABS = {
    "2": lab2,
    "3": lab3,
}
