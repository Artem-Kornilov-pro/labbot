"""Реестр лабораторных работ, которые умеет генерировать бот.

Чтобы добавить новую лабу, создайте пакет labgen/labs/labN с тем же интерфейсом, что у lab2
(LAB_NO, TITLE, PARTS, tasks_for_variant, task_texts, generate), и добавьте его в LABS.
"""
from .labs import lab2

LABS = {
    "2": lab2,
}
