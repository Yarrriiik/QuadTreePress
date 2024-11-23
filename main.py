"""Основная программа"""

import argparse
import os
import time
from typing import Union, Any
from work_with_images import compression_start


def check_fields(args: Any) -> bool:
    """Проверка переданных аргументов"""

    if not os.path.exists(args.file) or \
            args.file[len(args.file) - 3::] not in \
            ["jpg", "png", "jpeg"]:
        print("Такого файла c изображением не существует.")
        return False

    if args.level not in range(1, 9):
        print("Значение уровня сжатия должно быть от 1 до 8.")
        return False

    return True


def parse_args() -> Union[bool, str]:
    """Обработка параметров командной строки"""
    # Осуществляем разбор аргументов командной строки
    parser = argparse.ArgumentParser(description="Сжатие изображений на основе"
                                                 " квадродеревьев")

    parser.add_argument("-f", "--file",  dest="file", type=str,
                        help="Исходный файл изображения", required=True)

    parser.add_argument("-l", "--level", dest="level", type=int,
                        help="Уровень сжатия", required=True)

    parser.add_argument("-b", "--borders", dest="borders", action="store_true",
                        help="Отображение границ")

    parser.add_argument("-g", "--gif", dest="gif", action="store_true",
                        help="Создание gif-изображения")

    # В эту переменную попадает результат разбора аргументов командной строки.
    args = parser.parse_args()

    # Проверяем аргументы командной строки
    if check_fields(args):
        start_time = time.time()
        compression_start(args.file, args.level, args.borders, args.gif)
        end_time = time.time()
        print(f"Время выполнения программы: {end_time - start_time:.2f} секунд")

    else:
        print("Переданы неверные аргументы.")


def main():
    """Точка входа"""
    parse_args()


if __name__ == "__main__":
    main()
    #python main.py -f image.png -l 5 -b -g
