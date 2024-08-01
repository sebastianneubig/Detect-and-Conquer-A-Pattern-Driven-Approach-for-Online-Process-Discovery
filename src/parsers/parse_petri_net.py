from typing import Set, Tuple, Dict, List, Union

from pm4py import PetriNet

from tests.parse_petri_net_test_file import online_order_petri_net, online_order_simple_petri_net, render_petri_net


def identify_patterns(
        places: Set[PetriNet.Place],
        transitions: Set[PetriNet.Transition],
        arcs: Set[PetriNet.Arc]
) -> Tuple[
    List[List[Union[PetriNet.Place, PetriNet.Transition]]],  # SEQ patterns: List of sequences of objects
    Set[Tuple[PetriNet.Transition, Tuple[PetriNet.Place]]],  # AND patterns: (transition, tuple of connected places)
    Set[Tuple[PetriNet.Place, Tuple[PetriNet.Transition]]]  # OR patterns: (place, tuple of connected transitions)
]:
    seq_patterns: List[List[Union[PetriNet.Place, PetriNet.Transition]]] = []
    and_patterns: Set[Tuple[PetriNet.Transition, Tuple[PetriNet.Place]]] = set()
    or_patterns: Set[Tuple[PetriNet.Place, Tuple[PetriNet.Transition]]] = set()

    # Mapping von Quellen und Zielen für Transitionen und Stellen
    place_to_transitions: Dict[PetriNet.Place, Set[PetriNet.Transition]] = {place: set() for place in places}
    transition_to_places: Dict[PetriNet.Transition, Set[PetriNet.Place]] = {transition: set() for transition in
                                                                            transitions}

    for arc in arcs:
        if isinstance(arc.source, PetriNet.Place) and isinstance(arc.target, PetriNet.Transition):
            place_to_transitions[arc.source].add(arc.target)
        elif isinstance(arc.source, PetriNet.Transition) and isinstance(arc.target, PetriNet.Place):
            transition_to_places[arc.source].add(arc.target)

    # Funktion zum Finden von SEQ-Ketten
    def find_seq_chain(start_place: PetriNet.Place, visited: Set[PetriNet.Place]) -> List[
        Union[PetriNet.Place, PetriNet.Transition]]:
        chain = [start_place]
        current_place = start_place
        while current_place in place_to_transitions and len(place_to_transitions[current_place]) == 1:
            transition = next(iter(place_to_transitions[current_place]))
            if len(transition_to_places[transition]) == 1:
                next_place = next(iter(transition_to_places[transition]))
                if next_place in visited:
                    break  # Beende die Schleife, wenn wir eine bereits besuchte Stelle erreichen
                visited.add(next_place)
                chain.append(transition)
                chain.append(next_place)
                current_place = next_place
            else:
                break
        return chain

    visited_places = set()
    for place in places:
        if place not in visited_places:
            chain = find_seq_chain(place, visited_places)
            if len(chain) > 1:
                seq_patterns.append(chain)
                visited_places.update([elem for elem in chain if isinstance(elem, PetriNet.Place)])  # nur die Stellen

    for transition, connected_places in transition_to_places.items():
        if len(connected_places) > 1:
            and_patterns.add((transition, tuple(connected_places)))

    for place, connected_transitions in place_to_transitions.items():
        if len(connected_transitions) > 1:
            or_patterns.add((place, tuple(connected_transitions)))

    return seq_patterns, and_patterns, or_patterns


if __name__ == "__main__":

    net = online_order_petri_net()
    seq, and_p, or_p = identify_patterns(net.places, net.transitions, net.arcs)

    # print("SEQ Patterns:", seq)
    # print("AND Patterns:", and_p)
    # print("OR Patterns:", or_p)

    colors: List[str] = ["red", "blue", "green", "yellow", "purple", "orange", "pink", "brown", "gray", "cyan", "magenta"]

    for i, pattern in enumerate(seq):
        for elem in pattern:
            elem.properties["color"] = colors[i]

    render_petri_net(net)
