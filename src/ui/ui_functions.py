from typing import List

from PyQt5.QtWidgets import QGraphicsScene

from src.ui.ui_generic_elements import CustomQGraphicsItem, CustomLineItem, PlaceGraphicsItem


def create_connection(start: CustomQGraphicsItem, end: CustomQGraphicsItem, scene: QGraphicsScene) -> CustomLineItem:
    """
    Create a connection between two nodes.
    """
    l = CustomLineItem(start, end, scene)
    start.scene().addItem(l)
    start.scene().on_element_moved.connect(l.update_position)
    end.scene().on_element_moved.connect(l.update_position)
    return l



