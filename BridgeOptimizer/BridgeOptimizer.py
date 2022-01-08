import math
from typing import List, Tuple

import BridgeOptimizer.scriptBuilder.ScriptBuilderBoundaryConditions as ScriptBuilderBoundaryConditions
import BridgeOptimizer.scriptBuilder.ScriptBuilder as ScriptBuilder
from BridgeOptimizer.datastructure.hypermesh.SPC import SPC
from BridgeOptimizer.datastructure.hypermesh.Force import Force
from BridgeOptimizer.datastructure.hypermesh.LoadCollector import LoadCollector
from BridgeOptimizer.datastructure.hypermesh.LoadStep import LoadStep


class BridgeOptimizer:
    """
    Main class of the Bridge Optimizer, used to be called Mesh    

    """

    ids = [[]]
    matrix = [[]]

    def __init__(self, n_dots_x: int, n_dots_y: int, spacing: float):
        self.n_dots_x = n_dots_x
        self.n_dots_y = n_dots_y
        self.spacing = spacing
        self.matrix = [[1 for x in range(n_dots_x+1)]
                       for y in range(n_dots_y+1)]

    def blackout_zone(self, lowerX: int, upperX: int, lowerY: int, upperY: int):
        for x in range(lowerX, upperX+1):
            for y in range(lowerY, upperY+1):
                self.matrix[y][x] = 0

    def print_matrix(self):
        for i in range(len(self.matrix)-1, -1, -1):
            print(self.matrix[i])

    def print_matrix_nodeIds(self):
        for i in range(len(self.ids)-1, -1, -1):
            print(self.ids[i])

    def get_neighbour_by_distance(self, index_x: int, index_y: int, distance_threshold: float) -> List:
        neighbours = []
        for x1 in range(len(self.matrix[0])):
            for y1 in range(len(self.matrix)):
                if self.matrix[y1][x1] == 1:
                    if index_x != x1 or index_y != y1:
                        distance = self.get_distance_by_indices(
                            index_x, index_y, x1, y1)
                        if distance < distance_threshold:
                            if self.ids[y1][x1] not in neighbours:
                                neighbours.append(self.ids[y1][x1])
        return neighbours

    def get_coordinates(self, index_x: int, index_y: int) -> Tuple:
        return (index_x*self.spacing, index_y*self.spacing)

    def get_distance_by_indices(self, index_x1: int, index_y1: int, index_x2: int, index_y2: int) -> float:
        coord1 = self.get_coordinates(index_x1, index_y1)
        coord2 = self.get_coordinates(index_x2, index_y2)
        distance = math.sqrt(
            ((coord1[0]-coord2[0])**2)+((coord1[1]-coord2[1])**2))
        return distance

    def get_neighbour_ids(self, index_x: int, index_y: int) -> List:
        neighbours = []
        # east west
        if index_x == 0:
            if self.matrix[index_y][index_x+1] == 1:
                neighbours.append(self.ids[index_y][index_x+1])
        elif index_x == len(self.matrix[0])-1:
            if self.matrix[index_y][index_x-1] == 1:
                neighbours.append(self.ids[index_y][index_x-1])
        else:
            if self.matrix[index_y][index_x+1] == 1:
                neighbours.append(self.ids[index_y][index_x+1])
            if self.matrix[index_y][index_x-1] == 1:
                neighbours.append(self.ids[index_y][index_x-1])

        # north south
        if index_y == 0:
            if self.matrix[index_y+1][index_x] == 1:
                neighbours.append(self.ids[index_y+1][index_x])
        elif index_y == len(self.matrix)-1:
            if self.matrix[index_y-1][index_x] == 1:
                neighbours.append(self.ids[index_y-1][index_x])
        else:
            if self.matrix[index_y+1][index_x] == 1:
                neighbours.append(self.ids[index_y+1][index_x])
            if self.matrix[index_y-1][index_x] == 1:
                neighbours.append(self.ids[index_y-1][index_x])
        return neighbours


def main():
    length = 16
    height = 16
    spacing = 1.25
    neighbour_distance_threshold = 1.5*spacing  # this is the max length of the beam
    bridge_optimizer = BridgeOptimizer(length, height, spacing)

    # bridge_optimizer.blackout_zone(0,10,0,10)
    # bridge_optimizer.blackout_zone(-10,0,0,10)

    # Build script
    script_builder = ScriptBuilder.ScriptBuilder(bridge_optimizer)

    script_builder.write_tcl_create_nodes()
    script_builder.write_tcl_create_rods_optimization(
        neighbour_distance_threshold, spacing)

    # Boundary Conditions
    spc_node_ids = [bridge_optimizer.ids[y][x]
                    for y, x in zip([8, 8], [0, length])]
    spc_loadCollector = LoadCollector()
    SPC(spc_loadCollector, spc_node_ids, [0, 0, 0, 0, 0, -999999])

    # Loads
    load_node_id = [bridge_optimizer.ids[y][x] for y, x in zip([8], [8])]
    load_loadCollector = LoadCollector()
    Force(load_loadCollector, load_node_id, 0, -spacing, 0)
    # Loadstep
    LoadStep(spc_loadCollector, load_loadCollector)
    script_builder_bc = ScriptBuilderBoundaryConditions.ScriptBuilderBoundaryConditions()
    script_builder_bc.write_tcl_commands_loadsteps(script_builder.tcl_commands)

    # TopOpt
    script_builder.write_tcl_basic_topOpt_minMass(load_node_id, 0.3*spacing)
    script_builder.write_script_and_run()


if __name__ == "__main__":
    main()
