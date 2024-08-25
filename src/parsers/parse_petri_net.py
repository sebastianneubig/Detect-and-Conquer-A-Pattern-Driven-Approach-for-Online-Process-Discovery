from typing import Set, Tuple, Dict, List, Union
from pm4py import PetriNet
from tests.parse_petri_net_test_file import online_order_petri_net, online_order_simple_petri_net, render_petri_net, place_loop_petri_net, transistion_loop_petri_net, petri_net_from_image, petri_net_from_image2, or_loop_petri_net, and_loop_petri_net, or_and_combined_loop_petri_net


def identify_patterns(
        places: Set[PetriNet.Place],
        transitions: Set[PetriNet.Transition],
        arcs: Set[PetriNet.Arc]
) -> Tuple[
    List[List[Union[PetriNet.Place, PetriNet.Transition]]],  # SEQ patterns: List of sequences of objects
    List[List[Union[PetriNet.Place, PetriNet.Transition]]],  # LOOP patterns: List of sequences of objects
    Set[Tuple[PetriNet.Transition, Tuple[PetriNet.Place]]],  # AND patterns: (transition, tuple of connected places)
    Set[Tuple[PetriNet.Place, Tuple[PetriNet.Transition]]]  # OR patterns: (place, tuple of connected transitions)
]:
    seq_patterns: List[List[Union[PetriNet.Place, PetriNet.Transition]]] = []
    loop_patterns: List[List[Union[PetriNet.Place, PetriNet.Transition]]] = []
    and_patterns: Set[Tuple[PetriNet.Transition, Tuple[PetriNet.Place]]] = set()
    or_patterns: Set[Tuple[PetriNet.Place, Tuple[PetriNet.Transition]]] = set()

    # Mapping of sources and targets for transitions and places
    place_to_transitions: Dict[PetriNet.Place, Set[PetriNet.Transition]] = {place: set() for place in places}
    transition_to_places: Dict[PetriNet.Transition, Set[PetriNet.Place]] = {transition: set() for transition in transitions}

    for arc in arcs:
        if isinstance(arc.source, PetriNet.Place) and isinstance(arc.target, PetriNet.Transition):
            place_to_transitions[arc.source].add(arc.target)
        elif isinstance(arc.source, PetriNet.Transition) and isinstance(arc.target, PetriNet.Place):
            transition_to_places[arc.source].add(arc.target)

    # Function for finding SEQ chains
    # Hab ich noch bisschen angepasst, da sonst nicht alles erkannt worden wäre, aber jetzt gibt es Duplikate, deshalb funktioniert das mit der Farbcodierung nicht mehr so richtig und es kann jetzt bei verschiedenen Durchführungen ein unterschiedliches Ergebnis rauskommen
    def find_seq_chain(start_place: PetriNet.Place, visited: Set[PetriNet.Place]) -> List[Union[PetriNet.Place, PetriNet.Transition]]:
        chain: List[Union[PetriNet.Place, PetriNet.Transition]] = [start_place]
        current_place: PetriNet.Place = start_place
        while current_place in place_to_transitions and len(place_to_transitions[current_place]) == 1:
            transition = next(iter(place_to_transitions[current_place]))
            if len(transition_to_places[transition]) != 0:
                chain.append(transition)
                if len(transition_to_places[transition]) == 1:
                    next_place = next(iter(transition_to_places[transition]))
                    if next_place in visited:
                        break
                    visited.add(next_place)
                    chain.append(next_place)
                    current_place = next_place
                else:
                    break
            else:
                chain.append(transition)
                break
        return chain

    # Function for finding LOOP chains
    def find_loop_chain(
            current_place: PetriNet.Place,
            visited: Set[PetriNet.Place],
            chain: List[Union[PetriNet.Place, PetriNet.Transition]],
            start_place: PetriNet.Place
    ) -> List[List[Union[PetriNet.Place, PetriNet.Transition]]]:

        loops: List[List[Union[PetriNet.Place, PetriNet.Transition]]] = []
        if current_place in place_to_transitions:
            for transition in place_to_transitions[current_place]:
                if transition not in chain:
                    new_chain: List[Union[PetriNet.Place, PetriNet.Transition]] = chain + [transition]
                    for next_place in transition_to_places[transition]:
                        if next_place == start_place:  # loop
                            loops.append(new_chain + [next_place])
                        else:
                            if next_place not in visited:
                                visited.add(next_place)
                                loops.extend(
                                    find_loop_chain(next_place, visited, new_chain + [next_place], start_place))
                                visited.remove(next_place)
        return loops

    # Function to eliminate pattern duplicates
    def remove_duplicate_loops(loop_patterns: List[List[Union[PetriNet.Place, PetriNet.Transition]]]) -> List[List[Union[PetriNet.Place, PetriNet.Transition]]]:

        loop_set: List[Set[Union[PetriNet.Place, PetriNet.Transition]]] = []
        unique_patterns: List[List[Union[PetriNet.Place, PetriNet.Transition]]] = []

        for pattern in loop_patterns:
            current_set = set(pattern)

            unique = True
            for existing_set in loop_set:
                if current_set == existing_set:
                    unique = False
                    break

            if unique:
                loop_set.append(current_set)
                unique_patterns.append(pattern)

        return unique_patterns

    for place in places:
        loops = find_loop_chain(place, {place}, [place], place)
        if loops:
            loop_patterns.extend(loops)

    visited_places: Set[PetriNet.Place] = set()
    for place in places:
        if place not in visited_places:
            chain: List[Union[PetriNet.Place, PetriNet.Transition]] = find_seq_chain(place, visited_places)
            if len(chain) > 1:
                seq_patterns.append(chain)
                visited_places.update([elem for elem in chain if isinstance(elem, PetriNet.Place)])

    for transition, connected_places in transition_to_places.items():
        if len(connected_places) > 1:
            and_patterns.add((transition, tuple(connected_places)))

    for place, connected_transitions in place_to_transitions.items():
        if len(connected_transitions) > 1:
            or_patterns.add((place, tuple(connected_transitions)))

    #print(remove_duplicate_loops(loop_patterns))
    loop_patterns: List[List[Union[PetriNet.Place, PetriNet.Transition]]] = remove_duplicate_loops(loop_patterns)

    return seq_patterns, loop_patterns, and_patterns, or_patterns


if __name__ == "__main__":
    net: PetriNet = or_and_combined_loop_petri_net()

    seq: List[List[Union[PetriNet.Place, PetriNet.Transition]]] = []
    loop: List[List[Union[PetriNet.Place, PetriNet.Transition]]] = []
    and_p: Set[Tuple[PetriNet.Place, Tuple[PetriNet.Transition]]] = set()
    or_p: Set[Tuple[PetriNet.Place, Tuple[PetriNet.Transition]]] = set()

    seq, loop, and_p, or_p = identify_patterns(net.places, net.transitions, net.arcs)

    print("SEQ Patterns:", seq)
    print("LOOP Patterns:", loop)
    print("AND Patterns:", and_p)
    print("OR Patterns:", or_p)

    colors: List[str] = ["red", "blue", "green", "yellow", "purple", "orange", "pink", "brown", "gray", "cyan", "magenta"]

    for i, pattern in enumerate(seq):
        for elem in pattern:
            elem.properties["color"] = colors[i]

    render_petri_net(net)
