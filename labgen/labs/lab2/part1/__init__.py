"""Задачи части I лабы 2 (матрицы). Модуль tNN.py описывает задачу NN объектом TASK."""
import importlib

COUNT = 17


def get(num):
    return importlib.import_module(f"{__name__}.t{num:02d}").TASK
