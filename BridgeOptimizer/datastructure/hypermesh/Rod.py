from typing import List, Tuple, Dict
from BridgeOptimizer.datastructure.hypermesh.ModelEntities import Component, Material, Property
from BridgeOptimizer.datastructure.Grid import Grid


class Rod:
    """
    Rod Class for modelling a simple Rod in Hypermesh

    Parameters:
    ---------
    material : Material 
        Definition of the Material assigned to this rod

    diameter : float
        Diameter of the Rod (full, no tube)

    node_ids : Tuple
        start and end node id for the creation of the Rod

    optimization : bool
        Flag if this should be an Rod which can be used in Optimization        

    """
    instances = []
    node_ids2Rod: Dict = dict()

    def __init__(self, material: Material, diameter: float, node_ids: Tuple, optimization: bool) -> None:
        Rod.instances.append(self)
        Rod.node_ids2Rod[node_ids] = self
        self.material = material
        self.diameter = diameter
        self.node_ids = node_ids
        self.optimization = optimization
        self.id = 0

    @classmethod
    def create_rods(self, grid: Grid, neighbour_distance_threshold: float, material: Material, diameter: float):
        """
        Creats a default Grid for every active node tuple within a threshold. Optimization is default set to be true
        """
        linksAlreadyDrawn = []
        for x in range(len(grid.matrix[0])):
            for y in range(len(grid.matrix)):
                if grid.matrix[y][x] == 1:
                    id = grid.ids[y][x]
                    neighbours = grid.get_neighbour_by_distance(
                        x, y, neighbour_distance_threshold)
                    for neighbourId in neighbours:
                        if (id, neighbourId) not in linksAlreadyDrawn and (neighbourId, id) not in linksAlreadyDrawn:
                            Rod(material, diameter, (id, neighbourId), True)
                            linksAlreadyDrawn.append((id, neighbourId))

    def toggleOptimization(self, node_ids: Tuple):
        """
        Used to switch the optimization flag
        """
        rod: Rod = None
        rod = Rod.node_ids2Rod.get(node_ids)
        if rod != None:
            if rod.optimization:
                rod.optimization = False
            else:
                rod.optimization = True

    @classmethod
    def create_model_Entities(self, material: Material):
        """
        Divides the Rods into groups with the same properties
        For right now - only optimization / non optimization , single material
        TODO: depending on material, diameter etc
        """

        for rod in Rod.instances:
            property = Property(material, rod.diameter, rod.optimization)
            Component(property)
