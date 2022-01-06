import math
import os
from HypermeshStarter import HypermeshStarter
import ScriptBuilder
from typing import List, Tuple


class Mesh:

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
    neighbour_distance_threshold = 3*spacing  # this is the max length of the beam
    mesh = Mesh(length, height, spacing)

    # mesh.blackout_zone(0,10,0,10)
    # mesh.blackout_zone(-10,0,0,10)

    # Build script
    script_builder = ScriptBuilder.ScriptBuilder(mesh)

    script_builder.write_tcl_create_nodes()
    script_builder.write_tcl_create_rods(neighbour_distance_threshold, spacing)
    spc_node_ids = [mesh.ids[y][x] for y, x in zip([8, 8], [0, length])]
    script_builder.write_tcl_spc(spc_node_ids, [0, 0, 0, 0, 0, -999999])
    load_node_id = [mesh.ids[y][x] for y, x in zip([8], [8])]
    script_builder.write_tcl_load(load_node_id, (0, -spacing, 0))
    script_builder.write_tcl_loadstep()
    script_builder.write_tcl_basic_topOpt_minMass(load_node_id, 0.3*spacing)
    script_builder.write_script_and_run()


if __name__ == "__main__":
    main()
