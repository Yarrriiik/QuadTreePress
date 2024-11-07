"""Реализация квадродерева"""

import threading
from typing import Optional, Union
from PIL import Image

MAX_DEPTH = 8  # Максимальная глубина узла
ERROR_THRESHOLD = 13  # Порог значения


class Point:
    """Класс точки."""

    def __init__(self, x_coordinate: int, y_coordinate: int) -> None:
        """
        Конструктор класса точки.
        :param x_coordinate: Координата x
        :param y_coordinate: Координата y
        :return: None
        """
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate

    def __eq__(self, another: "Point") -> bool:
        """
        Сравнение двух точек.
        :param another: Точка для сравнения
        :return: Результат сравнения
        """
        return self.x_coordinate == another.y_coordinate and \
            self.y_coordinate == another.y_coordinate

    def __repr__(self) -> str:
        """
        Строковое представление точки.
        :return: Cтроковое представление точки
        """
        return f"Точка: ({self.x_coordinate}, {self.y_coordinate})"


def weighted_average(hist: list[int]) -> Union[int, float]:
    """
    Возвращает взвешенное среднее значение цвета и
    ошибку из гистограммы пикселей.
    :param hist: список количества пикселей для каждого диапазона.
    :return: взвешенное среднее значение цвета и ошибку
    """
    total = sum(hist)
    value, error = 0, 0
    if total > 0:
        # Формула для взвешенного среднего значения
        # предполагает умножение каждого щначения на его вес
        # (количество пикселей с этим значением), а затем деление
        # общего произведения на общее количество пикселей.
        value = sum(i * x for i, x in enumerate(hist)) / total
        # Формула для ошибки рассчитывает среднеквадратичное отклонение
        # каждого значения от взвешенного среднего значения.
        error = sum(x * (value - i) ** 2 for i, x in enumerate(hist)) / total
        error = error ** 0.5
    return value, error


def color_from_histogram(hist: list[int]) -> Union[tuple[int], float]:
    """
    Возвращает средний цвет RGB из заданной гистограммы
    количества цветов пикселей.
    :param hist: список количества пикселей для каждого диапазона.
    :return: Cредний цвет и ошибку.
    """
    red, red_error = weighted_average(hist[:256])
    green, green_error = weighted_average(hist[256:512])
    blue, blue_error = weighted_average(hist[512:768])
    error = red_error * 0.2989 + green_error * 0.5870 + blue_error * 0.1140
    return (int(red), int(green), int(blue)), error


class QuadtreeNode:
    """
    Класс, отвечающий за узел квадродерева,
    который содержит секцию изображения и информацию о ней.
    """

    def __init__(self, image: Image, border_box: tuple[int],
                 depth: int) -> None:
        """
        Конструктор класса.
        :param image: изображение
        :param border_box: координатная область
        :param depth: глубина
        :return: None
        """
        self.__border_box = border_box  # регион копирования
        self.__depth = depth
        self.__childrens = None  # top left,top right,bottom left,bottom right
        self.__is_leaf = False
        self.node_points = []

        left_right = self.__border_box[0] + (self.__border_box[2] -
                                             self.__border_box[0]) / 2
        top_bottom = self.__border_box[1] + (self.__border_box[3] -
                                             self.__border_box[1]) / 2

        self.__node_center_point = Point(left_right, top_bottom)

        # Обрезка части изображения по координатам
        image = image.crop(border_box)
        # Метод histogram возвращает список количества пикселей
        # для каждого диапазона, присутствующего на изображении.
        # В списке будут объединены все подсчеты для каждого диапазона.
        # Для RGB изображения для каждого цвета будет возвращен
        # список количества пикселей, суммарно 768.
        # Другими словами, метод дает информацию о том, сколько красных,
        # зелёных и синих пикселей присутствует в изображении для каждых
        # 256 типо красного, 256 типов зеленого и 256 синего.
        hist = image.histogram()
        self.__average_color, self.__error = color_from_histogram(
            hist)  # (r, g, b), error

    @property
    def depth(self) -> int:
        """
        Возвращает значение глубины.
        :return: Значение глубины.
        """
        return self.__depth

    @property
    def node_center_point(self) -> Point:
        """
        Возвращает координаты центральной точки узла.
        :return: Координаты центральной точки.
        """
        return self.__node_center_point

    @property
    def error(self) -> float:
        """
        Возвращает значения ошибки.
        :return: Значение ошибки.
        """
        return self.__error

    @property
    def average_color(self) -> tuple[int, int, int]:
        """
        Возвращает значения цвета
        :return: Значение цвета.
        """
        return self.__average_color

    @property
    def childrens(self) -> Optional[list]:
        """
        Возвращение дочерних узлов.
        :return: Список с дочерними узлами.
        """
        return self.__childrens

    @property
    def border_box(self) -> tuple[int]:
        """
        Возвращает координаты граничных точек.
        :return: Координаты точек.
        """
        return self.__border_box

    @property
    def is_leaf(self) -> bool:
        """
        Является ли узел листом или нет.
        :return: Логическое значение
        """
        return self.__is_leaf

    @is_leaf.setter
    def is_leaf(self, value: bool) -> None:
        """
        Квадрант становится листом.
        :param value: Булевое значение
        :return: None
        """
        self.__is_leaf = value

    def __repr__(self) -> str:
        """
        Строковое представление узла
        :return: строковое представление узла.
        """
        return f"Узел дерева: {self.__border_box}"

    def split(self, image: Image) -> None:
        """
        Разбивает данную секцию изображения на четыре равных блока.
        :param image: Изображение
        :return: None
        """

        left, top, right, bottom = self.__border_box

        top_left = QuadtreeNode(image, (
            left, top, self.__node_center_point.x_coordinate,
            self.__node_center_point.y_coordinate),
                                self.__depth + 1)
        top_right = QuadtreeNode(image, (
            self.__node_center_point.x_coordinate, top, right,
            self.__node_center_point.y_coordinate),
                                 self.__depth + 1)
        bottom_left = QuadtreeNode(image,
                                   (left,
                                    self.__node_center_point.y_coordinate,
                                    self.__node_center_point.x_coordinate,
                                    bottom),
                                   self.__depth + 1)
        bottom_right = QuadtreeNode(image,
                                    (self.__node_center_point.x_coordinate,
                                     self.__node_center_point.y_coordinate,
                                     right, bottom),
                                    self.__depth + 1)

        self.__childrens = [top_left, top_right, bottom_left, bottom_right]

    def insert_point(self, point: Point) -> "function":
        """
        Вставка точки в подходящий узел
        :param point: Точка, которая должна быть вставлена
        :return: None или рекурсивный вызов функции.
        """
        if self.childrens is not None:
            if point.x_coordinate < self.__node_center_point.x_coordinate \
                    and \
                    point.y_coordinate < \
                    self.__node_center_point.y_coordinate:
                return self.childrens[0].insert_point(point)

            if point.x_coordinate >= self.__node_center_point.x_coordinate \
                    and \
                    point.y_coordinate < \
                    self.__node_center_point.y_coordinate:
                return self.childrens[1].insert_point(point)

            if point.x_coordinate < self.__node_center_point.x_coordinate \
                    and \
                    point.y_coordinate >= \
                    self.__node_center_point.y_coordinate:
                self.childrens[2].insert_point(point)

            if point.x_coordinate >= self.__node_center_point.x_coordinate \
                    and \
                    point.y_coordinate >= \
                    self.__node_center_point.y_coordinate:
                self.childrens[3].insert_point(point)

        self.node_points.append(point)

    def find_node(self, point, search_list: list = None) ->list["QuadtreeNode",
                                                                list]:
        """
        Возвращает узел, содержащий точку и путь до узла.
        :param point: искомая точка
        :param search_list: список узлов
        :return: узел и список узлов
        """
        if not search_list:
            search_list = []

        search_list.append(self)

        if self.childrens is not None:
            if point.x_coordinate < self.__node_center_point.x_coordinate \
                    and \
                    point.y_coordinate < \
                    self.__node_center_point.y_coordinate:
                if self.childrens[0] is not None:
                    return self.childrens[0].find_node(point,search_list)

            elif point.x_coordinate >= self.__node_center_point.x_coordinate \
                    and \
                    point.y_coordinate < \
                    self.__node_center_point.y_coordinate:
                if self.childrens[1] is not None:
                    return self.childrens[1].find_node(point, search_list)

            elif point.x_coordinate < self.__node_center_point.x_coordinate \
                    and \
                    point.y_coordinate >= \
                    self.__node_center_point.y_coordinate:
                if self.childrens[2] is not None:
                    return self.childrens[2].find_node(point, search_list)

            elif point.x_coordinate >= self.__node_center_point.x_coordinate \
                    and \
                    point.y_coordinate >= \
                    self.__node_center_point.y_coordinate:
                if self.childrens[3] is not None:
                    return self.childrens[3].find_node(point, search_list)

        return self, search_list

    def remove_point(self, delete_point: Point) -> None:
        """
        Удаление точки.
        :param delete_point: Удаляемая точка.
        :return: None
        """
        current_node, _ = self.find_node(delete_point)

        if current_node is not None:
            for point in current_node.node_points:
                if point == delete_point:
                    current_node.node_points.remove(point)

    def find_node_contain_point(self, search_point: Point) -> "QuadtreeNode":
        """
        Возвращает узел, который содержит точку.
        :param search_point: Искомая точка
        :return: Необходимый узел.
        """
        current_node, _ = self.find_node(search_point)
        return current_node


class QuadTree:
    """Класс квадродерева."""

    def __init__(self, image: Image) -> None:
        """
        Конструктор класса
        :param image: исходное изображение.
        :return: None
        """
        self.__width, self.__height = image.size
        self.__root = QuadtreeNode(image, image.getbbox(), 0)

        # остлеживает максимальную глубину, достигнутую рекурсией
        self.__max_depth = 0
        self.__build_tree(image, self.__root)

    @property
    def width(self) -> int:
        """
        Возвращает ширину исходного изображения
        :return: ширина исходного изображения
        """
        return self.__width

    @property
    def height(self) -> int:
        """
        Возвращает высоту исходного изображения
        :return: высота изображения
        """
        return self.__height

    @property
    def max_depth(self) -> int:
        """
        Возвращает максимальную глубину, достигнутую рекурсией.
        :return: Значение максимальной глубины.
        """
        return self.__max_depth

    @property
    def root(self) -> QuadtreeNode:
        """
        Возвращает корневой узел
        :return: высота изображения
        """
        return self.__root

    def __build_tree(self, image: Image, node: QuadtreeNode) -> None:
        """
        Рекурсивно добавляет узлы, пока не будет достигнута макс. глубина
        :param image: исходное изображение
        :param node: узел
        :return: None
        """
        if (node.depth >= MAX_DEPTH) or (node.error <= ERROR_THRESHOLD):
            if node.depth > self.__max_depth:
                self.__max_depth = node.depth
            node.is_leaf = True
            return None

        node.split(image)

        threads = []
        for child in node.childrens:
            thread = threading.Thread(target=self.__build_tree,
                                      args=(image, child))

            thread.start()
            threads.append(thread)

        for process in threads:
            process.join()

        return None

    def get_leaf_nodes(self, depth: int) -> list:
        """
        Получаем листья дерева.
        :param depth: Значение глубины рекурсии.
        :return: Список листьев
        """

        if depth > self.__max_depth:
            raise ValueError('Дана глубина больше, чем высота деревьев')

        leaf_nodes = []

        # рекурсивный поиск по квадродереву
        self.get_leaf_nodes_recursion(self.__root, depth, leaf_nodes)

        return leaf_nodes

    def get_leaf_nodes_recursion(self, node: QuadtreeNode, depth: int,
                                 leaf_nodes: list) -> None:
        """
        Рекурсивно получает листовые узлы в зависимости от того,
        является ли узел листом или достигнута заданная глубина.
        :param node: Узел
        :param depth: значение глубины
        :param leaf_nodes: Список листьев
        :return:
        """
        if node.is_leaf is True or node.depth == depth:
            leaf_nodes.append(node)
        elif node.childrens is not None:
            for child in node.childrens:
                self.get_leaf_nodes_recursion(child, depth, leaf_nodes)
