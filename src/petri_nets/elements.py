import pandas as pd
import pm4py
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.bpmn.obj import BPMN

def xor_pattern_pn() -> PetriNet:
    net = PetriNet("XOR JOIN")

    p1 = PetriNet.Place("p1")
    p2 = PetriNet.Place("p2")
    p3 = PetriNet.Place("p3")
    net.places.add(p1)
    net.places.add(p2)
    net.places.add(p3)

    t1 = PetriNet.Transition("t1", "Paper invoice received")
    t2 = PetriNet.Transition("t2", "Electronic invoice received")

    net.transitions.add(t1)
    net.transitions.add(t2)

    net.arcs.add(PetriNet.Arc(p1, t1))
    net.arcs.add(PetriNet.Arc(p2, t2))
    net.arcs.add(PetriNet.Arc(t1, p3))
    net.arcs.add(PetriNet.Arc(t2, p3))
    return net
# pm4py.view_petri_net(net, None, None)

df = pd.read_feather('/Users/christianimenkamp/Documents/Data-Repository/Community/sepsis/Sepsis Cases - Event '
                     'Log.feather')
bpmn = pm4py.discover_bpmn_inductive(df)

pm4py.view_bpmn(bpmn)
