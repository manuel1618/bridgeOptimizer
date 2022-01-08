from typing import List
from .LoadCollector import LoadCollector


class SPC:
    """
    Single Point Constraint

    Prameters
    ---------
    dofs: List 
        List of constraint for dof1 - dof6, -999999 means free, 0 means fixed 

    """

    dofs = []

    def __init__(self, load_collector: LoadCollector, nodeIds: List, dofs: List) -> None:
        load_collector.loads.append(self)
        self.nodeIds = nodeIds
        if len(dofs) == 6:
            self.dofs = dofs
        else:
            print("ERROR: SPC has not 6 long List of DOF specification")
