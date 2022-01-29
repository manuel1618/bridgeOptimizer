from typing import List, Tuple, Dict
from BridgeOptimizer.datastructure.hypermesh.ModelEntities import Component, Material, Property
from BridgeOptimizer.datastructure.Grid import Grid
from BridgeOptimizer.utility.VectorUtililty import VectorUtility


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
    id2Rod: Dict = dict()
    linksAlreadyDrawn = []

    def __init__(self, material: Material, diameter: float, node_ids: Tuple, optimization: bool) -> None:
        Rod.instances.append(self)
        Rod.node_ids2Rod[node_ids] = self
        self.material = material
        self.diameter = diameter
        self.node_ids = node_ids
        self.optimization = optimization
        self.id = 0
        self.property_id = 0
        self.cost_first_segment = 300  # hard_coded for now
        self.cost_per_distance = 100  # hard_coded for now

    @classmethod
    def create_rods(self, grid: Grid, neighbour_distance_lower_thresold, neighbour_distance_threshold: float, material: Material, diameter: float):
        """
        Creats a default Grid for every active node tuple within a threshold. Optimization is default set to be true
        """
        for x in range(len(grid.matrix[0])):
            for y in range(len(grid.matrix)):
                if grid.matrix[y][x] == 1:
                    id = grid.ids[y][x]
                    neighbours = grid.get_neighbour_by_distance(
                        x, y, neighbour_distance_lower_thresold, neighbour_distance_threshold)
                    for neighbourId in neighbours:
                        if (id, neighbourId) not in self.linksAlreadyDrawn and (neighbourId, id) not in self.linksAlreadyDrawn:

                            Rod(material, diameter, (id, neighbourId), True)
                            self.linksAlreadyDrawn.append((id, neighbourId))

    @classmethod
    def driving_lane_ereaser(self, node_path: List[int]):
        """
        Makes room for new elements by deleting every element which is on the node path
        """
        rods_to_delete = []

        rod: Rod = None
        for rod in Rod.instances:
            node1 = rod.node_ids[0]
            node2 = rod.node_ids[1]
            if node1 in node_path:
                if node2 in node_path:
                    rods_to_delete.append(rod)

        for rod in rods_to_delete:
            Rod.delete_rod(rod)

    def delete_rod(self):
        """
        Deletes the instance by removing from all instances
        """
        Rod.instances.remove(self)

    @classmethod
    def get_rod_by_id(self, id: int):
        if len(Rod.id2Rod.keys()) == 0:
            for rod in Rod.instances:
                Rod.id2Rod[rod.id] = rod
        if id in Rod.id2Rod:
            return Rod.id2Rod[id]
        else:
            return None

    @classmethod
    def get_rod_based_on_node_ids(self, node_ids: Tuple):
        """
        Simple method to use the dictionary with all the nodes to get the Rod you are looking for.
        Takes order not into account (works both ways)

        Parameters:
        ---------

        node_ids : Tuple
            start and end id of the nodes 

        Returns: instance of the Rod you are looking for
        """
        node_ids_swapped = (node_ids[1], node_ids[0])
        if node_ids in Rod.node_ids2Rod.keys():
            return Rod.node_ids2Rod[node_ids]
        elif node_ids_swapped in Rod.node_ids2Rod.keys():
            return Rod.node_ids2Rod[node_ids_swapped]
        else:
            print(f"No Rod found for node pair: {node_ids}")
            return None

    @classmethod
    def have_same_direction(self, rod1, rod2, grid: Grid) -> bool:
        rod1_node1_coordinates = grid.get_coordinagtes_by_id(rod1.node_ids[0])
        rod1_node2_coordinates = grid.get_coordinagtes_by_id(rod1.node_ids[1])
        vector1 = [b-a for a,
                   b in zip(rod1_node1_coordinates, rod1_node2_coordinates)]
        rod2_node1_coordinates = grid.get_coordinagtes_by_id(rod2.node_ids[0])
        rod2_node2_coordinates = grid.get_coordinagtes_by_id(rod2.node_ids[1])
        vector2 = [b-a for a,
                   b in zip(rod2_node1_coordinates, rod2_node2_coordinates)]

        return (VectorUtility.are_linear_dependent(vector1, vector2))

    @DeprecationWarning
    @classmethod
    def getRodsAlongPath(self, grid: Grid, path: List[Tuple]) -> List:
        """
        In order to toggle the optimization for the driving lane, the path must be selected, this method does that in the 
        simplest way possible. By specifing a path with (y,x) coordinates

        Parameters
        ---------

        path : List(Tuple)
            List of coordinate pairs (y,x) with grid indices

        Returns:
        ---------
        rods : List[Rod]
            Rods which fit the given list
        """
        rods = []
        node_ids = []
        for coordinates in path:
            y_index = int(coordinates[0])
            x_index = int(coordinates[1])
            node_ids.append(grid.ids[y_index][x_index])

        for i in range(len(node_ids)-1):
            rod = Rod.get_rod_based_on_node_ids((node_ids[i], node_ids[i+1]))
            if rod != None:
                rods.append(rod)
        return rods

    @classmethod
    def toggleOptimization(self, rods: List):
        """
        Used to switch the optimization flag
        """
        for rod in rods:
            if rod != None:
                if rod.optimization:
                    print(f"Rod turned optimization off")
                    rod.optimization = False
                else:
                    print(f"Rod turned optimization on")
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

    def calculate_cost(self, grid: Grid):
        distance = grid.get_distance_by_ids(self.node_ids[0], self.node_ids[1])
        return (self.cost_first_segment+distance*self.cost_per_distance)
