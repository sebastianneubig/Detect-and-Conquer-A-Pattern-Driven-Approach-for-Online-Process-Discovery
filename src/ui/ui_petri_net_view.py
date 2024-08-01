import json
import random
import time
import typing
from typing import Tuple, List, Any

from PyQt5.QtCore import pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QPushButton, QVBoxLayout, QWidget
from graphviz import Digraph
from pm4py import PetriNet, Marking
from pm4py.objects.petri_net.utils import petri_utils

from src.ui.ui_functions import create_connection
from src.ui.ui_generic_elements import CustomQGraphicsItem, CustomLineItem, PlaceGraphicsItem, \
    TransitionGraphicsItem, get_post_area, get_marked_places, extr_e, create_styled_button, LINE_ANIMATION_DURATION
from src.utils.petri_net_renderer import render_petri_net


class CustomScene(QGraphicsScene):
    on_element_moved = pyqtSignal(object)
    on_transition_fired = pyqtSignal(TransitionGraphicsItem)
    on_new_element_requested = pyqtSignal(object)
    # on_marking_added = pyqtSignal(object)

    def __init__(self, view: QGraphicsView):
        super().__init__(view)


class PetriNetEditorView(QGraphicsView):

    def __init__(self, graph: Digraph = None):
        super().__init__()
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setStyleSheet("background-color: lightgrey; border-radius: 25px;")
        self.animation_timer: QTimer = None

        self.scene = CustomScene(self)
        self.element_cache: List[Tuple[str, CustomQGraphicsItem]] = []
        self.line_cache: List[CustomLineItem] = []
        self.setScene(self.scene)

        button_next: QPushButton = create_styled_button("Next Step", self, 150, 50)
        button_next.clicked.connect(self._on_next_simulation_step)

        button_all: QPushButton = create_styled_button("FULL", self, 100, 50)
        button_all.clicked.connect(self._on_full_animation)

        self.scene.on_new_element_requested.connect(self.on_new_element_requested_event)

        dot: Digraph
        if graph is not None:
            dot = graph
        else:
            dot = Digraph(comment='')

        json_string = dot.pipe('json').decode()
        json_dict = json.loads(json_string)

        for element in json_dict.get("objects", []):
            if element.get("_draw_", None) is not None:
                self._parse_dot_output(element)

        for edge in json_dict.get("edges", []):
            _gvid = "_gvid"
            start = edge["head"]
            end = edge["tail"]

            head_element: Tuple[str, CustomQGraphicsItem] = \
                list(filter(lambda x: x[0] == json_dict["objects"][start]["name"], self.element_cache))[0]
            tail_element: Tuple[str, CustomQGraphicsItem] = \
                list(filter(lambda x: x[0] == json_dict["objects"][end]["name"], self.element_cache))[0]

            l: CustomLineItem = create_connection(head_element[1], tail_element[1], scene=self.scene)
            self.line_cache.append(l)

    def on_new_element_requested_event(self,
                                       element: tuple[
                                           CustomQGraphicsItem,
                                           typing.Literal["top", "bottom", "right", "left"]]
                                       ):
        q_cf_element: CustomQGraphicsItem = element[0]

        direction: str = element[1]
        attributes: dict = {}

        if isinstance(q_cf_element, PlaceGraphicsItem):
            node_item = PlaceGraphicsItem(attributes)
            self.scene.addItem(node_item)
        elif isinstance(q_cf_element, TransitionGraphicsItem):
            node_item = TransitionGraphicsItem(attributes)
            self.scene.addItem(node_item)
        else:
            raise ValueError("Wrong process item instance")


    def _on_full_animation(self):
        def on_interval():
            res: bool = self._on_next_simulation_step()
            if res is False:
                self.animation_timer.stop()

        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(on_interval)
        self.animation_timer.start((LINE_ANIMATION_DURATION * 2) + 100)

        self._on_next_simulation_step()

    def _on_next_simulation_step(self) -> bool:
        if any([line.ANIMATION_FLAG for line in self.line_cache]):
            return None

        marked_places: List[PlaceGraphicsItem] = get_marked_places(extr_e(self.element_cache))

        can_finish: List[bool] = []

        for curr_p in marked_places:
            post_tr: List[TransitionGraphicsItem] = get_post_area(curr_p, self.line_cache)

            active_tr: List[TransitionGraphicsItem] = [tr for tr in post_tr if tr.can_fire(self.line_cache)]

            if len(active_tr) > 0:
                winning_tr: TransitionGraphicsItem = random.choice(active_tr)
                winning_tr.fire(self.line_cache)
                can_finish.append(False)
            else:
                can_finish.append(True)

        if all(can_finish):
            print("Simulation finished")
            return False
        else:
            return True

    def _on_timer(self):
        for element in self.element_cache:
            if isinstance(element[1], PlaceGraphicsItem):
                place: PlaceGraphicsItem = element[1]

                if len(place.markings) <= 5:
                    place.add_marking()
                else:
                    place.remove_marking()

    def _parse_dot_output(self, attributes: dict):
        # Hacky way to get the type of the element
        if attributes.get("shape", None) == "circle":
            node_item = PlaceGraphicsItem(attributes)
            self.scene.addItem(node_item)
        else:
            node_item = TransitionGraphicsItem(attributes)
            self.scene.addItem(node_item)

        self.element_cache.append((attributes["name"], node_item))

    def to_pm4py_petri_net(self) -> Tuple[PetriNet, Marking[Any], Marking[Any]]:
        net = PetriNet('Petri Net')
        initial_marking = Marking()
        final_marking = Marking()

        place_map = {}
        transition_map = {}

        for name, item in self.element_cache:
            if isinstance(item, PlaceGraphicsItem):
                place = PetriNet.Place(name)
                net.places.add(place)
                place_map[item] = place
                if item.markings:
                    initial_marking[place] = len(item.markings)
            elif isinstance(item, TransitionGraphicsItem):
                transition = PetriNet.Transition(name, item.text_item.toPlainText())
                net.transitions.add(transition)
                transition_map[item] = transition

        for line in self.line_cache:
            target = line.start_item
            source = line.end_item

            if isinstance(source, PlaceGraphicsItem) and isinstance(target, TransitionGraphicsItem):
                petri_utils.add_arc_from_to(place_map[source], transition_map[target], net)
            elif isinstance(source, TransitionGraphicsItem) and isinstance(target, PlaceGraphicsItem):
                petri_utils.add_arc_from_to(transition_map[source], place_map[target], net)

        return net, initial_marking, final_marking

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            zoom_factor = 1.25
            if event.angleDelta().y() > 0:
                self.scale(zoom_factor, zoom_factor)
            else:
                self.scale(1 / zoom_factor, 1 / zoom_factor)
        else:
            super().wheelEvent(event)
