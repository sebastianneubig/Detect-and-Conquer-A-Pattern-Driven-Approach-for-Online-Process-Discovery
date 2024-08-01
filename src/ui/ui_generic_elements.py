import faulthandler
import math
import sys
import typing
from random import uniform
from typing import Callable, List

from PyQt5.QtCore import QRectF, QPointF, Qt, QPropertyAnimation, QObject, pyqtProperty, QTimer, pyqtSignal, QLineF
from PyQt5.QtGui import QColor, QBrush, QPen, QPainter, QPainterPath, QPolygonF, QTransform
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsRectItem, \
    QGraphicsLineItem, QGraphicsPathItem, QGraphicsScene, QPushButton, QGraphicsProxyWidget, QWidget, \
    QGraphicsPolygonItem

import uuid

# Constants
ELEMENT_WIDTH: int = 50
ELEMENT_HEIGHT: int = 50
LINE_ANIMATION_DURATION: int = 1000

# Style Constants
ELLIPSE_SIZE: int = 10
ELLIPSE_OFFSET: int = 5
ELLIPSE_BRUSH_COLOR: QColor = QColor(Qt.red)
LINE_PEN_COLOR: QColor = QColor(Qt.black)
LINE_PEN_WIDTH: int = 2
ITEM_SELECTED_COLOR: str = 'lightgrey'
ITEM_ORIGINAL_COLOR: str = '#FFFFFF'
ITEM_PEN_COLOR: str = '#000000'
ITEM_PEN_WIDTH: int = 3
ITEM_SELECTED_PEN_WIDTH: int = 4
BUTTON_STYLE: str = """
    QPushButton {
        background-color: white;
        border: 1px solid black;
        border-radius: 7px;
        font-size: 10px;
        padding: 10px;
        color: black;
    }
    QPushButton:hover {
        background-color: #f0f0f0;
        border: 2px solid grey;
    }
"""
BUTTON_SIZE: int = 15
BUTTON_OFFSET_X_ADD: int = 5
BUTTON_OFFSET_X_REMOVE: int = -20
BUTTON_OFFSET_Y: int = -40


# EllipseElementWrapper Class
class EllipseElementWrapper(QObject):
    def __init__(self, ellipse: QGraphicsEllipseItem):
        super().__init__()
        self._ellipse = ellipse

    def get_pos(self) -> QPointF:
        return self._ellipse.pos()

    def set_pos(self, pos: QPointF) -> None:
        self._ellipse.setPos(pos)

    pos = pyqtProperty(QPointF, get_pos, set_pos)


class CustomLineItem(QGraphicsPathItem):
    def __init__(self, start_item: QGraphicsItem, end_item: QGraphicsItem, scene: QGraphicsScene):
        super().__init__()
        self.ANIMATION_FLAG: bool = False
        self.start_item = start_item
        self.end_item = end_item
        self.num_breaks = 2
        self.ellipse = QGraphicsEllipseItem(-10, -10, ELLIPSE_SIZE, ELLIPSE_SIZE)
        self.ellipse.setBrush(ELLIPSE_BRUSH_COLOR)
        self.arrow_head = QGraphicsPolygonItem()
        self.arrow_head.setBrush(QBrush(Qt.blue))
        scene.addItem(self.arrow_head)
        self.id: str = str(uuid.uuid4())
        self.update_position({})
        pen = QPen(Qt.black, 2)
        self.setPen(pen)
        self.setZValue(-1)
        self.arrow_head.setZValue(0)

    def check_parents(self, start_item: QGraphicsItem, end_item: QGraphicsItem) -> bool:
        return self.start_item == start_item and self.end_item == end_item

    def update_position(self, event: object) -> None:
        path = self.calculate_manhattan_path(self.num_breaks)
        self.setPath(path)
        self.update_arrow_head()

    def calculate_manhattan_path(self, num_breaks: int) -> QPainterPath:
        start_pos = self.get_intersection_with_edge(self.start_item, self.end_item)
        end_pos = self.get_intersection_with_edge(self.end_item, self.start_item)
        path = QPainterPath(start_pos)

        if num_breaks > 0:
            delta_x = (end_pos.x() - start_pos.x()) / (num_breaks + 1)
            delta_y = (end_pos.y() - start_pos.y()) / (num_breaks + 1)
            current_pos = start_pos
            for i in range(1, num_breaks + 1):
                if i % 2 != 0:
                    current_pos.setX(start_pos.x() + i * delta_x)
                else:
                    current_pos.setY(start_pos.y() + (i // 2) * delta_y)
                path.lineTo(current_pos)
            if num_breaks % 2 == 0:
                current_pos.setY(end_pos.y())
            else:
                current_pos.setX(end_pos.x())
            path.lineTo(current_pos)
        path.lineTo(end_pos)
        return path

    def get_intersection_with_edge(self, source_item: QGraphicsItem, target_item: QGraphicsItem) -> QPointF:
        source_rect = source_item.sceneBoundingRect()
        target_rect = target_item.sceneBoundingRect()
        source_center = source_rect.center()
        target_center = target_rect.center()

        line = QLineF(source_center, target_center)
        intersections = []

        edges = [
            QLineF(source_rect.topLeft(), source_rect.topRight()),  # Top edge
            QLineF(source_rect.topRight(), source_rect.bottomRight()),  # Right edge
            QLineF(source_rect.bottomRight(), source_rect.bottomLeft()),  # Bottom edge
            QLineF(source_rect.bottomLeft(), source_rect.topLeft())  # Left edge
        ]

        for edge in edges:
            intersection_point = QPointF()
            if line.intersect(edge, intersection_point) == QLineF.BoundedIntersection:
                intersections.append(intersection_point)

        if intersections:
            return intersections[0]
        print("Fallback to center in get_intersection_with_edge()")
        return source_center  # Fallback to center if no intersection found

    def update_arrow_head(self) -> None:
        path = self.path()
        if path.isEmpty():
            return

        end_point: QPointF = path.elementAt(path.elementCount() - 1)
        prev_point: QPointF = path.elementAt(path.elementCount() - 2)

        line = QLineF(prev_point.x, prev_point.y, end_point.x, end_point.y)
        angle = line.angle()

        arrow_size = 10
        arrow_points = [
            QPointF(0, 0),
            QPointF(-arrow_size, arrow_size / 2),
            QPointF(-arrow_size, -arrow_size / 2)
        ]

        arrow_polygon = QPolygonF(arrow_points)
        transform = QTransform()
        transform.translate(end_point.x, end_point.y)
        transform.rotate(-angle)
        arrow_polygon = transform.map(arrow_polygon)

        self.arrow_head.setPolygon(arrow_polygon)
        self.arrow_head.setRotation(-angle)
        self.arrow_head.setPos(end_point.x, end_point.y)
        self.update()
        self.arrow_head.update()

    def run_animation(self, scene: QGraphicsScene, on_finish: Callable[[], None] = None) -> None:
        self.ANIMATION_FLAG = True
        scene.addItem(self.ellipse)
        animator = EllipseElementWrapper(self.ellipse)
        animation = QPropertyAnimation(animator, b'pos')
        path = self.path()
        animation.setDuration(LINE_ANIMATION_DURATION)
        for i in range(101):
            animation.setKeyValueAt(i / 100.0, path.pointAtPercent((100 - i) / 100.0))
        animation.start()
        animation.finished.connect(lambda: self._on_animation_finished(scene, on_finish))
        self.animation = animation

    def _on_animation_finished(self, scene: QGraphicsScene, on_finish: Callable[[], None] = None) -> None:
        scene.removeItem(self.ellipse)
        self.ANIMATION_FLAG = False
        if on_finish:
            on_finish()


# CustomQGraphicsItem Class
class CustomQGraphicsItem(QGraphicsItem):
    def __init__(self, attributes: dict, parent: QGraphicsItem = None):
        super().__init__(parent)
        self.attributes = attributes
        self.text_item: typing.Optional[QGraphicsTextItem] = None
        self.id: str = str(uuid.uuid4())
        self.pen = QPen(QColor(ITEM_PEN_COLOR), ITEM_PEN_WIDTH)
        self.brush = QBrush(QColor(self.attributes.get('fillcolor', ITEM_ORIGINAL_COLOR)))
        self.rect = QRectF(float(attributes['pos'].split(',')[0]),
                           float(attributes['pos'].split(',')[1]),
                           ELEMENT_WIDTH,
                           ELEMENT_HEIGHT)

        self.navigation_buttons: List[QGraphicsRectItem] = []
        self.button_distance = 20  # Default distance

        self.line = None
        self.is_selected: bool = False
        self.original_color = self.attributes.get('fillcolor', ITEM_ORIGINAL_COLOR)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.apply_label_draw_operations()
        self.create_direction_buttons()
        self.update()

    def update_fill_color(self, color: str) -> None:
        self.attributes['fillcolor'] = color
        self.brush.setColor(QColor(color))
        self.update()

    def apply_label_draw_operations(self) -> None:
        for operation in self.attributes.get('_ldraw_', []):
            if operation['op'] == 'T' and not self.text_item:
                self.text_item = QGraphicsTextItem(self.attributes.get("label", "NO LABEL"), self)
                self.text_item.setPos(QPointF(operation['pt'][0], operation['pt'][1]))
                self.text_item.setDefaultTextColor(QColor(operation.get('color', ITEM_PEN_COLOR)))

    def set_selected_color(self) -> None:
        self.update_fill_color(ITEM_SELECTED_COLOR)
        if hasattr(self.pen, 'setWidth'):
            self.pen.setWidth(ITEM_SELECTED_PEN_WIDTH)

    def reset_color(self) -> None:
        self.update_fill_color(self.original_color)
        if hasattr(self.pen, 'setWidth'):
            self.pen.setWidth(ITEM_PEN_WIDTH)

    def boundingRect(self) -> QRectF:
        return self.rect

    def paint(self, painter: QPainter, option, widget) -> None:
        raise NotImplementedError("Subclasses should implement this!")

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange and self.scene():
            if value:
                self.is_selected = True
                self.set_selected_color()
                self.toggle_navigation_buttons(True)
            else:
                self.is_selected = False
                self.reset_color()
                self.toggle_navigation_buttons(False)
        return super().itemChange(change, value)

    def mouseMoveEvent(self, event) -> None:
        super().mouseMoveEvent(event)
        self.scene().on_element_moved.emit(event)

    def create_direction_buttons(self) -> None:
        button_size = 10

        # Top button
        top_button = DirectionButton(
            self, 'top',
            QRectF(self.rect.center().x() - button_size / 2,
                   self.rect.top() - self.button_distance - button_size,
                   button_size, button_size)
        )
        self.create_arrow(top_button, 'top')

        # Bottom button
        bottom_button = DirectionButton(
            self, 'bottom',
            QRectF(self.rect.center().x() - button_size / 2,
                   self.rect.bottom() + self.button_distance,
                   button_size, button_size)
        )
        self.create_arrow(bottom_button, 'bottom')

        # Left button
        left_button = DirectionButton(
            self, 'left',
            QRectF(self.rect.left() - self.button_distance - button_size,
                   self.rect.center().y() - button_size / 2,
                   button_size, button_size)
        )
        self.create_arrow(left_button, 'left')

        # Right button
        right_button = DirectionButton(
            self, 'right',
            QRectF(self.rect.right() + self.button_distance,
                   self.rect.center().y() - button_size / 2,
                   button_size, button_size)
        )
        self.create_arrow(right_button, 'right')

        self.navigation_buttons.extend([right_button, left_button, top_button, bottom_button])
        self.toggle_navigation_buttons(False)

    def toggle_navigation_buttons(self, show: bool):
        for button in self.navigation_buttons:
            if show:
                button.show()
            else:
                button.hide()

    def create_arrow(self, button: QGraphicsRectItem, direction: str) -> None:
        arrow_polygon = QPolygonF()
        if direction == 'top':
            arrow_polygon << QPointF(button.rect().center().x(), button.rect().top()) \
            << QPointF(button.rect().left(), button.rect().bottom()) \
            << QPointF(button.rect().right(), button.rect().bottom())
        elif direction == 'bottom':
            arrow_polygon << QPointF(button.rect().center().x(), button.rect().bottom()) \
            << QPointF(button.rect().left(), button.rect().top()) \
            << QPointF(button.rect().right(), button.rect().top())
        elif direction == 'left':
            arrow_polygon << QPointF(button.rect().left(), button.rect().center().y()) \
            << QPointF(button.rect().right(), button.rect().top()) \
            << QPointF(button.rect().right(), button.rect().bottom())
        elif direction == 'right':
            arrow_polygon << QPointF(button.rect().right(), button.rect().center().y()) \
            << QPointF(button.rect().left(), button.rect().top()) \
            << QPointF(button.rect().left(), button.rect().bottom())

        arrow_item = QGraphicsPolygonItem(arrow_polygon, button)
        arrow_item.setBrush(QBrush(QColor(ITEM_PEN_COLOR)))
        arrow_item.setPen(QPen(Qt.NoPen))

    def on_button_pressed(self, button_direction: typing.Literal["top", "bottom", "right", "left"]) -> None:
        print(f"Button {button_direction} pressed.")
        self.scene().on_new_element_requested.emit([self, button_direction])


class DirectionButton(QGraphicsRectItem):
    def __init__(self, parent: CustomQGraphicsItem, direction: typing.Literal["top", "bottom", "right", "left"],
                 rect: QRectF):
        super().__init__(rect, parent)
        self.parent_item = parent
        self.direction = direction

    def mousePressEvent(self, event) -> None:
        self.parent_item.on_button_pressed(self.direction)


# TransitionGraphicsItem Class
class TransitionGraphicsItem(QGraphicsRectItem, CustomQGraphicsItem):
    def __init__(self, attributes: typing.Dict, parent: QGraphicsItem = None):
        # Initialize both base classes
        QGraphicsRectItem.__init__(self, parent)
        CustomQGraphicsItem.__init__(self, attributes, parent)
        self.setRect(self.rect)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setPen(self.pen)
        self.brush.setStyle(Qt.SolidPattern)
        painter.setBrush(self.brush)
        painter.drawRect(self.rect)

    def can_fire(self, lines: List[CustomLineItem]) -> bool:
        pre_area: List[PlaceGraphicsItem] = get_pre_area(self, lines)
        return all([place.has_marks() for place in pre_area])

    def fire(self, lines: List[CustomLineItem]) -> None:
        def after_animation():
            post_area: List[PlaceGraphicsItem] = get_post_area(self, lines)
            for p in post_area:
                all_edges = [edge for edge in lines if edge.check_parents(p, self)]
                p.add_marking(LINE_ANIMATION_DURATION)
                all_edges[0].run_animation(self.scene())

        pre_area: List[PlaceGraphicsItem] = get_pre_area(self, lines)
        for place in pre_area:
            for item in lines:
                if item.check_parents(self, place):
                    item.run_animation(self.scene())
                    break
            place.remove_marking()
        QTimer.singleShot(LINE_ANIMATION_DURATION, lambda: after_animation())
        self.scene().on_transition_fired.emit(self)


# PlaceGraphicsItem Class
class PlaceGraphicsItem(CustomQGraphicsItem, QGraphicsEllipseItem):
    def __init__(self,
                 attributes: dict,
                 parent: QGraphicsItem = None,
                 on_marking_changed: Callable[[typing.Self], None] = None):
        QGraphicsEllipseItem.__init__(self, parent)
        CustomQGraphicsItem.__init__(self, attributes, parent)
        self.setRect(QRectF(-ELEMENT_WIDTH / 2, -ELEMENT_HEIGHT / 2, ELEMENT_WIDTH, ELEMENT_HEIGHT))
        self.on_marking_changed = on_marking_changed
        self.markings: List[QGraphicsEllipseItem] = []
        self.buttons: List[QPushButton] = []
        self.init_buttons()
        self.hide_children()
        self.update_small_ellipse_positions()

    def init_buttons(self) -> None:
        self.buttons.append(self._add_button("+", BUTTON_OFFSET_X_ADD, self.add_marking))
        self.buttons.append(self._add_button("-", BUTTON_OFFSET_X_REMOVE, self.remove_marking))

    def _add_button(self, label: str, offset_x: int = 0, callback: Callable[[], None] = None) -> QPushButton:
        parent_rect = self.rect
        coords = parent_rect.getCoords()
        center_x = (coords[0] + coords[2]) / 2
        center_y = (coords[1] + coords[3]) / 2
        button = QPushButton(label)
        proxy_button = QGraphicsProxyWidget(self)
        proxy_button.setWidget(button)
        proxy_button.setPos(center_x + offset_x, center_y + BUTTON_OFFSET_Y)
        button.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        button.setStyleSheet(BUTTON_STYLE)
        button.setCursor(Qt.PointingHandCursor)
        button.setAttribute(Qt.WA_TranslucentBackground)
        if callback:
            button.clicked.connect(callback)
        return button

    def add_marking(self, delay: int | None = None) -> None:
        new_small_ellipse = QGraphicsEllipseItem(-ELLIPSE_OFFSET, -ELLIPSE_OFFSET, ELLIPSE_SIZE, ELLIPSE_SIZE, self)
        new_small_ellipse.setBrush(QBrush(Qt.black))
        self.markings.append(new_small_ellipse)
        self.update_small_ellipse_positions()
        new_small_ellipse.hide()
        if delay:
            QTimer.singleShot(delay, lambda: new_small_ellipse.show())
        else:
            new_small_ellipse.show()
        if self.on_marking_changed:
            self.on_marking_changed(self)

    def remove_marking(self) -> None:
        if self.markings:
            self.scene().removeItem(self.markings.pop())
            self.update_small_ellipse_positions()
            if self.on_marking_changed:
                self.on_marking_changed(self)

    def update_small_ellipse_positions(self) -> None:
        parent_rect = self.rect
        coords: tuple[float, float, float, float] = parent_rect.getCoords()
        center_x = (coords[0] + coords[2]) / 2
        center_y = (coords[1] + coords[3]) / 2
        num_ellipses = len(self.markings)
        if num_ellipses == 1:
            self.markings[0].setPos(center_x, center_y)
        elif num_ellipses > 1:
            radius = ELEMENT_WIDTH / 2
            angle_increment = 2 * math.pi / num_ellipses
            for i, ellipse in enumerate(self.markings):
                angle = i * angle_increment
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                ellipse.setPos(x, y)

    def paint(self, painter: QPainter, option, widget):
        painter.setPen(self.pen)
        brush = QBrush(self.brush)
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)
        painter.drawEllipse(self.rect)

    def hide_children(self) -> None:
        for button in self.buttons:
            button.hide()

    def show_children(self) -> None:
        for button in self.buttons:
            button.show()

    def has_marks(self) -> bool:
        return len(self.markings) > 0

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange and self.scene():
            if value:
                self.show_children()
            else:
                self.hide_children()
        return super().itemChange(change, value)


# Helper functions
def get_pre_area(element: CustomQGraphicsItem, edges: List[CustomLineItem]) -> List[CustomQGraphicsItem]:
    post_area: List[CustomQGraphicsItem] = []
    for edge in edges:
        if edge.start_item == element:
            post_area.append(edge.end_item)
    return post_area


def get_post_area(element: CustomQGraphicsItem, edges: List[CustomLineItem]) -> List[CustomQGraphicsItem]:
    pre_area = []
    for edge in edges:
        if edge.end_item.id == element.id:
            pre_area.append(edge.start_item)
    return pre_area


def get_marked_places(elements: List[CustomQGraphicsItem]) -> List[PlaceGraphicsItem]:
    marked_places: List[PlaceGraphicsItem] = []
    for element in elements:
        if isinstance(element, PlaceGraphicsItem):
            place: PlaceGraphicsItem = element
            if len(place.markings):
                marked_places.append(element)
    return marked_places


def extr_e(elements: List[tuple[str, CustomQGraphicsItem]]) -> List[CustomQGraphicsItem]:
    return [element[1] for element in elements]


def get_edge_by_elements(
        start: CustomQGraphicsItem,
        end: CustomQGraphicsItem,
        edges: List[CustomLineItem]
) -> typing.Optional[CustomLineItem]:
    for edge in edges:
        if edge.start_item.id == start.id and edge.end_item.id == end.id:
            return edge
    return None


def create_styled_button(label: str, parent: QWidget, x: int, y: int) -> QPushButton:
    button = QPushButton(label, parent)
    button.move(x, y)
    button.setStyleSheet(BUTTON_STYLE)
    button.setCursor(Qt.PointingHandCursor)
    return button
