from typing import Set, Dict, Union, List

import pm4py
from graphviz import Digraph
from pm4py.objects.petri_net.obj import PetriNet

from src.parsers.pattern_parser import PatternNode
from src.utils.petri_net_renderer import render_petri_net


def online_order_petri_net() -> PetriNet:
    # Define places
    places: Set[PetriNet.Place] = set()
    p1: PetriNet.Place = PetriNet.Place("Ready for Order")
    p2: PetriNet.Place = PetriNet.Place("Open Online-Shop")
    p3: PetriNet.Place = PetriNet.Place("Show Results")
    p4: PetriNet.Place = PetriNet.Place("Alternatives article found")
    p5: PetriNet.Place = PetriNet.Place("Article selected")
    p6: PetriNet.Place = PetriNet.Place("Ready to Pay")
    p7: PetriNet.Place = PetriNet.Place("Enter Order Data")
    p8: PetriNet.Place = PetriNet.Place("Input mask for shipping details opened")
    p9: PetriNet.Place = PetriNet.Place("Input mask for credit card details opened")
    p10: PetriNet.Place = PetriNet.Place("Credit card details entered")
    p11: PetriNet.Place = PetriNet.Place("Credit card details checked")
    p12: PetriNet.Place = PetriNet.Place("Credit card details verified")
    p13: PetriNet.Place = PetriNet.Place("Address and shipping method entered")
    p14: PetriNet.Place = PetriNet.Place("Order completed")

    # Add places to the set
    places.update([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14])

    # Define transitions
    transitions: Set[PetriNet.Transition] = set()
    t1: PetriNet.Transition = PetriNet.Transition("t1", label="Open Online-Shop")
    t2: PetriNet.Transition = PetriNet.Transition("t2", label="Start searching")
    t3: PetriNet.Transition = PetriNet.Transition("t3", label="Search alternative article")
    t4: PetriNet.Transition = PetriNet.Transition("t4", label="Select alternative article")
    t5: PetriNet.Transition = PetriNet.Transition("t5", label="Select Article")
    t6: PetriNet.Transition = PetriNet.Transition("t6", label="Added to shopping cart")
    t7: PetriNet.Transition = PetriNet.Transition("t7", label="Enter login data")
    t8: PetriNet.Transition = PetriNet.Transition("t8", label="Login data is incorrect")
    t9: PetriNet.Transition = PetriNet.Transition("t9", label="Login data is correct")
    t10: PetriNet.Transition = PetriNet.Transition("t10", label="Enter address and shipping method")
    t11: PetriNet.Transition = PetriNet.Transition("t11", label="Enter credit card details")
    t12: PetriNet.Transition = PetriNet.Transition("t12", label="Mark credit card details as verified")
    t13: PetriNet.Transition = PetriNet.Transition("t13", label="Confirm order")
    t14: PetriNet.Transition = PetriNet.Transition("t14", label="Check credit card details")
    t15: PetriNet.Transition = PetriNet.Transition("t15", label="Mark credit card details as incorrect")

    # Add transitions to the set
    transitions.update([t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14, t15])

    # Define arcs
    arcs: Set[PetriNet.Arc] = set()
    arcs.update([
        PetriNet.Arc(p1, t1),
        PetriNet.Arc(t1, p2),
        PetriNet.Arc(p2, t2),
        PetriNet.Arc(t2, p3),
        PetriNet.Arc(p3, t3),
        PetriNet.Arc(p3, t5),
        PetriNet.Arc(t3, p4),
        PetriNet.Arc(p4, t4),
        PetriNet.Arc(t4, p5),
        PetriNet.Arc(t5, p5),
        PetriNet.Arc(p5, t6),
        PetriNet.Arc(t6, p6),
        PetriNet.Arc(p6, t7),
        PetriNet.Arc(t7, p7),
        PetriNet.Arc(p7, t8),
        PetriNet.Arc(t8, p6),
        PetriNet.Arc(p7, t9),
        PetriNet.Arc(t9, p9),
        PetriNet.Arc(p9, t11),
        PetriNet.Arc(t11, p10),
        PetriNet.Arc(p10, t14),
        PetriNet.Arc(t14, p11),
        PetriNet.Arc(p11, t12),
        PetriNet.Arc(p11, t15),
        PetriNet.Arc(t15, p9),
        PetriNet.Arc(t9, p8),
        PetriNet.Arc(p8, t10),
        PetriNet.Arc(t10, p13),
        PetriNet.Arc(p13, t13),
        PetriNet.Arc(t12, p12),
        PetriNet.Arc(p12, t13),
        PetriNet.Arc(t13, p14)
    ])

    # Create the Petri net
    return PetriNet("ONLINE ORDER", places=places, transitions=transitions, arcs=arcs)


def online_order_simple_petri_net() -> PetriNet:
    places: Set[PetriNet.Place] = set()
    p1: PetriNet.Place = PetriNet.Place("Ready for Order")
    places.add(p1)
    p2: PetriNet.Place = PetriNet.Place("Open Online-Shop")
    places.add(p2)
    p3: PetriNet.Place = PetriNet.Place("Show Results")
    places.add(p3)

    transitions: Set[PetriNet.Transition] = set()
    t1: PetriNet.Transition = PetriNet.Transition("Open Online-Shop", label="Open Online-Shop",
                                                  properties={"color": "red"})
    transitions.add(t1)
    t2: PetriNet.Transition = PetriNet.Transition("Start searching", label="Start searching")
    transitions.add(t2)

    arcs: Set[PetriNet.Arc] = set()
    a1: PetriNet.Arc = PetriNet.Arc(p1, t1)
    arcs.add(a1)
    a2: PetriNet.Arc = PetriNet.Arc(t1, p2)
    arcs.add(a2)
    a3: PetriNet.Arc = PetriNet.Arc(p2, t2)
    arcs.add(a3)
    a4: PetriNet.Arc = PetriNet.Arc(t2, p3)
    arcs.add(a4)

    net = pm4py.PetriNet("ONLINE ORDER SIMPLE", places=places, transitions=transitions, arcs=arcs)
    return net


def place_loop_petri_net() -> PetriNet:

    places: Set[PetriNet.Place] = set()
    p1: PetriNet.Place = PetriNet.Place("Ready for Order")
    places.add(p1)
    p2: PetriNet.Place = PetriNet.Place("Shop Opened")
    places.add(p2)
    p3: PetriNet.Place = PetriNet.Place("Searching Started")
    places.add(p3)
    p4: PetriNet.Place = PetriNet.Place("Results Shown")
    places.add(p4)
    p5: PetriNet.Place = PetriNet.Place("Repeat Search")
    places.add(p5)

    transitions: Set[PetriNet.Transition] = set()
    t1: PetriNet.Transition = PetriNet.Transition("Open Online-Shop", label="Open Online-Shop")
    transitions.add(t1)
    t2: PetriNet.Transition = PetriNet.Transition("Start searching", label="Start searching")
    transitions.add(t2)
    t3: PetriNet.Transition = PetriNet.Transition("Show Results", label="Show Results")
    transitions.add(t3)
    t4: PetriNet.Transition = PetriNet.Transition("Search Again", label="Search Again")
    transitions.add(t4)

    arcs: Set[PetriNet.Arc] = set()
    a1: PetriNet.Arc = PetriNet.Arc(p1, t1)
    arcs.add(a1)
    a2: PetriNet.Arc = PetriNet.Arc(t1, p2)
    arcs.add(a2)
    a3: PetriNet.Arc = PetriNet.Arc(p2, t2)
    arcs.add(a3)
    a4: PetriNet.Arc = PetriNet.Arc(t2, p3)
    arcs.add(a4)
    a5: PetriNet.Arc = PetriNet.Arc(p3, t3)
    arcs.add(a5)
    a6: PetriNet.Arc = PetriNet.Arc(t3, p4)
    arcs.add(a6)
    a7: PetriNet.Arc = PetriNet.Arc(p4, t4)
    arcs.add(a7)
    a8: PetriNet.Arc = PetriNet.Arc(t4, p5)
    arcs.add(a8)
    a9: PetriNet.Arc = PetriNet.Arc(p5, t2)  # Schleife
    arcs.add(a9)

    net = PetriNet("PLACE LOOP", places=places, transitions=transitions, arcs=arcs)
    return net

def transistion_loop_petri_net() -> PetriNet:

    places: Set[PetriNet.Place] = set()
    p1: PetriNet.Place = PetriNet.Place("Place 1")
    places.add(p1)
    p2: PetriNet.Place = PetriNet.Place("Place 2")
    places.add(p2)
    p3: PetriNet.Place = PetriNet.Place("Place 3")
    places.add(p3)

    transitions: Set[PetriNet.Transition] = set()
    t1: PetriNet.Transition = PetriNet.Transition("t1", label="Transition 1")
    transitions.add(t1)
    t2: PetriNet.Transition = PetriNet.Transition("t2", label="Transition 2")
    transitions.add(t2)
    t3: PetriNet.Transition = PetriNet.Transition("t3", label="Transition 3")
    transitions.add(t3)

    arcs: Set[PetriNet.Arc] = set()
    a1: PetriNet.Arc = PetriNet.Arc(p1, t1)
    arcs.add(a1)
    a2: PetriNet.Arc = PetriNet.Arc(t1, p2)
    arcs.add(a2)
    a3: PetriNet.Arc = PetriNet.Arc(p2, t2)
    arcs.add(a3)
    a4: PetriNet.Arc = PetriNet.Arc(t2, p3)
    arcs.add(a4)
    a5: PetriNet.Arc = PetriNet.Arc(p3, t3)
    arcs.add(a5)
    a6: PetriNet.Arc = PetriNet.Arc(t3, p2)
    arcs.add(a6)

    net = PetriNet("TRANSISTION LOOP", places=places, transitions=transitions, arcs=arcs)
    return net

def petri_net_from_image() -> PetriNet:

    # Erstellen der Stellen (Places)
    places: Set[PetriNet.Place] = set()
    p1: PetriNet.Place = PetriNet.Place("P1")
    places.add(p1)
    p2: PetriNet.Place = PetriNet.Place("P2")
    places.add(p2)
    p3: PetriNet.Place = PetriNet.Place("P3")
    places.add(p3)
    p4: PetriNet.Place = PetriNet.Place("P4")
    places.add(p4)

    # Erstellen der Transitionen (Transitions)
    transitions: Set[PetriNet.Transition] = set()
    t1: PetriNet.Transition = PetriNet.Transition("T1", label="T1")
    transitions.add(t1)
    t2: PetriNet.Transition = PetriNet.Transition("T2", label="T2")
    transitions.add(t2)
    t3: PetriNet.Transition = PetriNet.Transition("T3", label="T3")
    transitions.add(t3)

    # Erstellen der Kanten (Arcs)
    arcs: Set[PetriNet.Arc] = set()
    a1: PetriNet.Arc = PetriNet.Arc(p1, t1)
    arcs.add(a1)
    a2: PetriNet.Arc = PetriNet.Arc(t1, p2)
    arcs.add(a2)
    a3: PetriNet.Arc = PetriNet.Arc(p2, t2)
    arcs.add(a3)
    a4: PetriNet.Arc = PetriNet.Arc(t2, p4)
    arcs.add(a4)
    a5: PetriNet.Arc = PetriNet.Arc(t3, p2)
    arcs.add(a5)
    a6: PetriNet.Arc = PetriNet.Arc(p3, t3)
    arcs.add(a6)
    a7: PetriNet.Arc = PetriNet.Arc(t2, p3)
    arcs.add(a7)

    # Erstellen des Petri-Netzes
    net = PetriNet("Custom Petri Net from Image", places=places, transitions=transitions, arcs=arcs)
    return net


def petri_net_from_image2() -> PetriNet:

    # Erstellen der Stellen (Places)
    places: Set[PetriNet.Place] = set()
    p1: PetriNet.Place = PetriNet.Place("P1")
    places.add(p1)
    p2: PetriNet.Place = PetriNet.Place("P2")
    places.add(p2)
    p3: PetriNet.Place = PetriNet.Place("P3")
    places.add(p3)
    p4: PetriNet.Place = PetriNet.Place("P4")
    places.add(p4)

    # Erstellen der Transitionen (Transitions)
    transitions: Set[PetriNet.Transition] = set()
    t1: PetriNet.Transition = PetriNet.Transition("T1", label="T1")
    transitions.add(t1)
    t2: PetriNet.Transition = PetriNet.Transition("T2", label="T2")
    transitions.add(t2)
    t3: PetriNet.Transition = PetriNet.Transition("T3", label="T3")
    transitions.add(t3)
    t4: PetriNet.Transition = PetriNet.Transition("T4", label="t4")
    transitions.add(t4)

    # Erstellen der Kanten (Arcs)
    arcs: Set[PetriNet.Arc] = set()
    a1: PetriNet.Arc = PetriNet.Arc(p1, t1)
    arcs.add(a1)
    a2: PetriNet.Arc = PetriNet.Arc(t1, p2)
    arcs.add(a2)
    a3: PetriNet.Arc = PetriNet.Arc(p2, t2)
    arcs.add(a3)
    a4: PetriNet.Arc = PetriNet.Arc(t2, p4)
    arcs.add(a4)
    a5: PetriNet.Arc = PetriNet.Arc(t3, p2)
    arcs.add(a5)
    a6: PetriNet.Arc = PetriNet.Arc(p3, t3)
    arcs.add(a6)
    a7: PetriNet.Arc = PetriNet.Arc(t2, p3)
    arcs.add(a7)
    a8: PetriNet.Arc = PetriNet.Arc(p4, t4)
    arcs.add(a8)


    # Erstellen des Petri-Netzes
    net = PetriNet("Custom Petri Net from Image", places=places, transitions=transitions, arcs=arcs)
    return net


def or_loop_petri_net() -> PetriNet:
    places: Set[PetriNet.Place] = set()
    p1: PetriNet.Place = PetriNet.Place("P1")
    places.add(p1)
    p2: PetriNet.Place = PetriNet.Place("P2")
    places.add(p2)
    p3: PetriNet.Place = PetriNet.Place("P3")
    places.add(p3)
    p4: PetriNet.Place = PetriNet.Place("P4")
    places.add(p4)

    transitions: Set[PetriNet.Transition] = set()
    t1: PetriNet.Transition = PetriNet.Transition("T1", label="T1")
    transitions.add(t1)
    t2: PetriNet.Transition = PetriNet.Transition("T2", label="T2")
    transitions.add(t2)
    t3: PetriNet.Transition = PetriNet.Transition("T3", label="T3")
    transitions.add(t3)

    arcs: Set[PetriNet.Arc] = set()
    a1: PetriNet.Arc = PetriNet.Arc(p1, t1)
    arcs.add(a1)
    a2: PetriNet.Arc = PetriNet.Arc(t1, p2)
    arcs.add(a2)
    a3: PetriNet.Arc = PetriNet.Arc(p2, t2)
    arcs.add(a3)
    a4: PetriNet.Arc = PetriNet.Arc(p2, t3)
    arcs.add(a4)
    a5: PetriNet.Arc = PetriNet.Arc(t2, p3)
    arcs.add(a5)
    a6: PetriNet.Arc = PetriNet.Arc(t3, p4)
    arcs.add(a6)
    a7: PetriNet.Arc = PetriNet.Arc(p3, t1)  # Rückschleife (Loop)
    arcs.add(a7)
    a8: PetriNet.Arc = PetriNet.Arc(p4, t1)  # Rückschleife (Loop)
    arcs.add(a8)

    net = PetriNet("OR Loop Petri Net", places=places, transitions=transitions, arcs=arcs)
    return net

def and_loop_petri_net() -> PetriNet:
    places: Set[PetriNet.Place] = set()
    p1: PetriNet.Place = PetriNet.Place("P1")
    places.add(p1)
    p2: PetriNet.Place = PetriNet.Place("P2")
    places.add(p2)
    p3: PetriNet.Place = PetriNet.Place("P3")
    places.add(p3)
    p4: PetriNet.Place = PetriNet.Place("P4")
    places.add(p4)
    p5: PetriNet.Place = PetriNet.Place("P5")
    places.add(p5)

    transitions: Set[PetriNet.Transition] = set()
    t1: PetriNet.Transition = PetriNet.Transition("T1", label="T1")
    transitions.add(t1)
    t2: PetriNet.Transition = PetriNet.Transition("T2", label="T2")
    transitions.add(t2)
    t3: PetriNet.Transition = PetriNet.Transition("T3", label="T3")
    transitions.add(t3)
    t4: PetriNet.Transition = PetriNet.Transition("T4", label="T4")
    transitions.add(t4)

    arcs: Set[PetriNet.Arc] = set()
    a1: PetriNet.Arc = PetriNet.Arc(p1, t1)
    arcs.add(a1)
    a2: PetriNet.Arc = PetriNet.Arc(t1, p2)
    arcs.add(a2)
    a3: PetriNet.Arc = PetriNet.Arc(t1, p3)
    arcs.add(a3)
    a4: PetriNet.Arc = PetriNet.Arc(p2, t2)
    arcs.add(a4)
    a5: PetriNet.Arc = PetriNet.Arc(p3, t3)
    arcs.add(a5)
    a6: PetriNet.Arc = PetriNet.Arc(t2, p4)
    arcs.add(a6)
    a7: PetriNet.Arc = PetriNet.Arc(t3, p4)
    arcs.add(a7)
    a8: PetriNet.Arc = PetriNet.Arc(p4, t4)
    arcs.add(a8)
    a9: PetriNet.Arc = PetriNet.Arc(t4, p5)
    arcs.add(a9)
    a10: PetriNet.Arc = PetriNet.Arc(p5, t1)  # Rückschleife (Loop)
    arcs.add(a10)

    net = PetriNet("AND Loop Petri Net", places=places, transitions=transitions, arcs=arcs)
    return net


def or_and_combined_loop_petri_net() -> PetriNet:
    places: Set[PetriNet.Place] = set()
    p1: PetriNet.Place = PetriNet.Place("P1")
    places.add(p1)
    p2: PetriNet.Place = PetriNet.Place("P2")
    places.add(p2)
    p3: PetriNet.Place = PetriNet.Place("P3")
    places.add(p3)
    p4: PetriNet.Place = PetriNet.Place("P4")
    places.add(p4)
    p5: PetriNet.Place = PetriNet.Place("P5")
    places.add(p5)
    p6: PetriNet.Place = PetriNet.Place("P6")
    places.add(p6)

    transitions: Set[PetriNet.Transition] = set()
    t1: PetriNet.Transition = PetriNet.Transition("T1", label="T1")
    transitions.add(t1)
    t2: PetriNet.Transition = PetriNet.Transition("T2", label="T2")
    transitions.add(t2)
    t3: PetriNet.Transition = PetriNet.Transition("T3", label="T3")
    transitions.add(t3)
    t4: PetriNet.Transition = PetriNet.Transition("T4", label="T4")
    transitions.add(t4)
    t5: PetriNet.Transition = PetriNet.Transition("T5", label="T5")
    transitions.add(t5)

    arcs: Set[PetriNet.Arc] = set()
    a1: PetriNet.Arc = PetriNet.Arc(p1, t1)
    arcs.add(a1)
    a2: PetriNet.Arc = PetriNet.Arc(t1, p2)
    arcs.add(a2)
    a3: PetriNet.Arc = PetriNet.Arc(t1, p3)
    arcs.add(a3)
    a4: PetriNet.Arc = PetriNet.Arc(p2, t2)
    arcs.add(a4)
    a5: PetriNet.Arc = PetriNet.Arc(p3, t3)
    arcs.add(a5)
    a6: PetriNet.Arc = PetriNet.Arc(t2, p4)
    arcs.add(a6)
    a7: PetriNet.Arc = PetriNet.Arc(t3, p4)
    arcs.add(a7)
    a8: PetriNet.Arc = PetriNet.Arc(p4, t4)
    arcs.add(a8)
    a9: PetriNet.Arc = PetriNet.Arc(t4, p5)
    arcs.add(a9)
    a10: PetriNet.Arc = PetriNet.Arc(t4, p6)
    arcs.add(a10)
    a11: PetriNet.Arc = PetriNet.Arc(p5, t5)
    arcs.add(a11)
    a12: PetriNet.Arc = PetriNet.Arc(p6, t5)
    arcs.add(a12)
    a13: PetriNet.Arc = PetriNet.Arc(t5, p1)  # Rückschleife (Loop)
    arcs.add(a13)

    net = PetriNet("OR AND Combined Loop Petri Net", places=places, transitions=transitions, arcs=arcs)
    return net




if __name__ == "__main__":
    # pm4py.view_petri_net(online_order_petri_net(), None, None)
    # net: PetriNet = place_loop_petri_net()
    # pm4py.view_petri_net(net, None, None)
    net = and_loop_petri_net()
    render_petri_net(net)
    # pattern = convert_petri_net_to_pattern(net)
    # print(pattern)

