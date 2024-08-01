from typing import Set, Dict

from graphviz import Digraph
from pm4py import PetriNet


def wrap_label(label: str, max_length: int) -> str:
    if not label:
        return ""
    words = label.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + len(current_line) > max_length:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word)

    if current_line:
        lines.append(' '.join(current_line))

    return '\n'.join(lines)


def add_places(dot: Digraph, places: Set[PetriNet.Place], max_label_length: int) -> None:
    for place in places:
        label = place.label if hasattr(place, 'label') else place.name
        wrapped_label = wrap_label(label, max_label_length)
        fillcolor = place.properties.get("color", "white")
        dot.node(place.name,
                 shape='circle',
                 label=wrapped_label,
                 style='filled',
                 fillcolor=fillcolor)


def add_transitions(dot: Digraph, transitions: Set[PetriNet.Transition], max_label_length: int) -> None:
    for transition in transitions:
        label = transition.label if hasattr(transition, 'label') else transition.name
        wrapped_label = wrap_label(label, max_label_length)
        fillcolor = transition.properties.get("color", "white")
        dot.node(transition.name,
                 shape='box',
                 style='filled',
                 fillcolor=fillcolor,
                 label=wrapped_label)


def add_arcs(dot: Digraph, arcs: Set[PetriNet.Arc], ranks: Dict[str, Set[str]]) -> None:
    for arc in arcs:
        dot.edge(arc.source.name, arc.target.name)
        source_rank = ranks.get(arc.source.name, set())
        source_rank.add(arc.target.name)
        ranks[arc.source.name] = source_rank


def apply_ranks(dot: Digraph, ranks: Dict[str, Set[str]]) -> None:
    for rank, elements in ranks.items():
        with dot.subgraph() as s:
            s.attr(rank='same')
            for element in elements:
                s.node(element)


def render_petri_net(net: PetriNet, render: bool = True) -> Digraph:
    dot = Digraph(comment='ONLINE ORDER SIMPLE')

    default_width = "1"
    default_height = "1"
    max_label_length = 10

    dot.attr(rankdir='LR')
    dot.attr(splines='ortho')
    dot.attr(kw="node", fixedsize='true')
    dot.attr(kw="node", labelloc='c')
    dot.attr(kw="node", width=default_width)
    dot.attr(kw="node", height=default_height)
    dot.attr(nodesep='3.0')
    dot.attr(splines="ortho")

    ranks = {}

    add_places(dot, net.places, max_label_length)
    add_transitions(dot, net.transitions, max_label_length)
    add_arcs(dot, net.arcs, ranks)
    apply_ranks(dot, ranks)

    if render:
        dot.view()
    return dot

