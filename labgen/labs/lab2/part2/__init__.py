"""Задачи части II лабы 2 (обработка целых чисел). Модуль tNN.py описывает задачу NN объектом TASK."""
import importlib

COUNT = 10


def get(num):
    return importlib.import_module(f"{__name__}.t{num:02d}").TASK
