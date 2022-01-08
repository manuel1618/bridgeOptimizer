from typing import List
from .LoadCollector import LoadCollector


class Force:
    """
    Single Point Force

    Parameters
    ----------
    load_collector: LoadCollector 
        LoadCollector where the Force will be put into
    x: float 
        amount of Force in X
    y: float 
        amount of Force in Y
    z: float
        amount of Force in Z

    Notes 
    ----------
    """

    def __init__(self, load_collector: LoadCollector, nodeIds: List,  x: float, y: float, z: float) -> None:
        load_collector.loads.append(self)
        self.nodeIds = nodeIds
        self.x = x
        self.y = y
        self.z = z
