import math
from typing import List, Tuple


class Grid:
    """
    The new Mesh Class seperating the geometry from the Main class
    Used for a lot of operations on the geometry as well as the modelling (like neighbour relations of the nodes)

    Parameters
    ---------

    n_dots_x : int
        number of grid points in the x direction

    n_dots_y : int
        number of grid points in the y direction
    """

    def __init__(self, n_dots_x: int, n_dots_y: int, spacing: float) -> None:
        self.n_dots_x = n_dots_x
        self.n_dots_y = n_dots_y
        self.spacing = spacing
        self.matrix = [[1 for x in range(n_dots_x+1)]
                       for y in range(n_dots_y+1)]
        self.ids = [[0 for x in range(len(self.matrix[0]))]
                    for y in range(len(self.matrix))]

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

    def get_coordinates(self, index_x: int, index_y: int) -> Tuple:
        return (index_x*self.spacing, index_y*self.spacing)

    def get_distance_by_indices(self, index_x1: int, index_y1: int, index_x2: int, index_y2: int) -> float:
        coord1 = self.get_coordinates(index_x1, index_y1)
        coord2 = self.get_coordinates(index_x2, index_y2)
        distance = math.sqrt(
            ((coord1[0]-coord2[0])**2)+((coord1[1]-coord2[1])**2))
        return distance

    def get_neighbour_by_distance(self, index_x: int, index_y: int, distance_lower_threshold: float, distance_threshold: float) -> List:
        """
        Returns a list of Node IDs 
        """
        neighbours = []
        for x1 in range(len(self.matrix[0])):
            for y1 in range(len(self.matrix)):
                if self.matrix[y1][x1] == 1:
                    if index_x != x1 or index_y != y1:
                        distance = self.get_distance_by_indices(
                            index_x, index_y, x1, y1)
                        print(distance)
                        if distance_lower_threshold < distance < distance_threshold:
                            print("yes")
                            if self.ids[y1][x1] not in neighbours:
                                neighbours.append(self.ids[y1][x1])
                        else:
                            print("no")
        return neighbours

    @DeprecationWarning
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
