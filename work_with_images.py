"""
Модуль для создания изображений
"""

import os

from PIL import Image, ImageDraw

from tree import QuadTree, MAX_DEPTH


class CreatorGifImages:
    """
    Класс, отвечающий за сохранение Gif-изображений
    """

    def __init__(self) -> None:
        """
        Конструктор класса, который будет сохранять гифки
        :return: None
        """
        self.frames = []
        self.frames_count = 0
        self.gif_number = 1

        self.__path = self.create_path()

    @property
    def path(self):
        """
        Получение пути к gif изображению.
        :return: путь к изображению
        """
        return self.__path

    def create_path(self) -> str:
        """
        Метод создания пути к гифке
        :return: путь к гифке
        """
        directory = "gif"

        # Если папки .gif нет, то создаём её
        if not os.path.exists(directory):
            os.mkdir(directory)

        path = f"{directory}\\gif{self.gif_number}.gif"
        while os.path.exists(path):
            self.gif_number += 1
            path = f"{directory}\\gif{self.gif_number}.gif"
        return path


def add_img_to_gif(image: Image,
                   gif: CreatorGifImages) -> None:
    """
    Добавляет один кадр к гифке
    :param image: Добавляемый кадр к гифке
    :param gif: экземпляр класса CreatorGifImages
    :return: None
    """
    gif.frames_count += 1
    gif.frames.append(image)



def create_gif(gif: CreatorGifImages) -> None:
    """
    Метод сохранения гифки в директорию
    :param gif: Класс gif изображения
    :return: None
    """
    print("Gif-изображение создаётся...")

    gif.frames[0].save(gif.path, save_all=True,
                       append_images=gif.frames[1:],
                       optimize=True,
                       duration=800,
                       loop=1)

    print("Gif-изображение было сохранено в директорию gif")

    gif.frames[0].close()
    gif.frames.clear()
    gif.frames_count = 0
    gif.gif_number += 1



def create_image(quadtree: QuadTree, level: int,
                 borders: bool) -> Image:
    """
    Создание изображения на основе квадродерева
    :param quadtree: Квадродерево
    :param level: Уровень глубины
    :param borders: Нужны ли границы
    :return: Готовое изображение
    """
    # Создаём пустой холст изображения
    image = Image.new('RGB', (quadtree.width, quadtree.height))

    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, quadtree.width, quadtree.height), (0, 0, 0))
    leaf_nodes = quadtree.get_leaf_nodes(level)

    for node in leaf_nodes:
        if borders:
            draw.rectangle(node.border_box, node.average_color,
                           outline=(0, 0, 0))
        else:
            draw.rectangle(node.border_box, node.average_color)

    return image


def compression_start(file: str, level: int, borders: bool,
                      gif: bool) -> None:
    """
    Начало сжатия
    :param file: Путь к файлу
    :param level: Уровень глубины
    :param borders: Отображение границ
    :param gif: Нужно ли создавать gif изображение
    :return: None
    """
    original_image = Image.open(file)
    quadtree = QuadTree(original_image)

    file_name = file[:-4]
    file_extension = file[len(file) - 3::]

    result_image = create_image(quadtree, level, borders)
    result_image.save(f"{file_name}_quadtree.{file_extension}")
    print("Изображение создано.")

    if gif:
        gif = CreatorGifImages()

        for value in range(MAX_DEPTH + 1):
            new_img = create_image(quadtree, value, borders)
            add_img_to_gif(new_img, gif)

        create_gif(gif)
