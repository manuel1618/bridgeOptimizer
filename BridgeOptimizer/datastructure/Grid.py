import math
from tkinter import N
from tracemalloc import start
from typing import List, Tuple

import sys


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

    def blackout_zone(self, lowerY: int, lowerX: int, upperY: int, upperX: int):
        for x in range(lowerX, upperX):
            for y in range(lowerY, upperY):
                self.matrix[y][x] = 0

    def print_matrix(self):
        for i in range(len(self.matrix)-1, -1, -1):
            print(self.matrix[i])

    def print_matrix_nodeIds(self):
        for i in range(len(self.ids)-1, -1, -1):
            print(self.ids[i])

    def get_coordinates(self, index_x: int, index_y: int) -> Tuple:
        return (index_x*self.spacing, index_y*self.spacing)

    def get_index_of_id(self, id: int) -> Tuple:
        """
        Find the index in the matrix for a node id
        Parameters:
        ---------
        id:int
          id of the node for which the index is requested

        Returns:
        ---------
        index : Tuple
          Index in the form: (index_y,index_x)
        """
        index = (-1, -1)
        for i in range(len(self.ids)):
            if id in self.ids[i]:
                if index != (-1, -1):
                    print("Error: Duplicate Id in ids matrix.")
                index = (i, self.ids[i].index(id))
        if index == (-1, -1):
            print(f"Error: Id {id} not found")
        return index

    def get_distance_by_ids(self, id_1: int, id_2: int):
        indices1 = self.get_index_of_id(id_1)
        indices2 = self.get_index_of_id(id_2)
        distance = self.get_distance_by_indices(
            indices1[0], indices1[1], indices2[0], indices2[1])
        return distance

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
                        if distance_lower_threshold < distance < distance_threshold:
                            if self.ids[y1][x1] not in neighbours:
                                neighbours.append(self.ids[y1][x1])
        return neighbours

    def get_path_a_star(self, start_node: int, end_node: int):
        """
        Simple implementation of the A* algorithm, based on:
        https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2 (22.01.2022)

        Parameters:
        start_node:int
          Id of the start node
        end_node:int
          Id of the end node

        Known issues_
          Right now, only N-S-E-W neighbours considered. 

        Returns:
          List of the nodes for the shortest path found

        """
        open_list = [start_node]
        closed_list = []

        costs_g = {}
        costs_g[start_node] = 0

        costs_h = {}
        costs_h[start_node] = 0

        costs_f = {}
        costs_f[start_node] = 0

        parents = {}
        parents[start_node] = None

        while len(open_list) > 0:
            current_node = open_list[0]
            current_index = 0
            # calculate the total costs and find the minimum (sum of distances)
            for index, item in enumerate(open_list):
                if costs_f[item] < costs_f[current_node]:
                    current_node = item
                    current_index = index

            # move current to closed list
            open_list.pop(current_index)
            closed_list.append(current_node)

            # found the path -->end
            if current_node == end_node:
                path = []
                current = current_node
                while current != None:
                    path.append(current)
                    current = parents[current]
                return path[::-1]  # Return reversed path

            # get neighbours
            indices = self.get_index_of_id(current_node)
            index_y = indices[0]
            index_x = indices[1]
            for neighbour in self.get_neighbour_ids(index_x, index_y):
                if self.matrix[index_y][index_x] == 1:
                    if neighbour in closed_list:
                        continue
                    parents[neighbour] = current_node

                    costs_g[neighbour] = costs_g[current_node] + \
                        self.get_distance_by_ids(neighbour, current_node)
                    costs_h[neighbour] = self.get_distance_by_ids(
                        neighbour, end_node)
                    costs_f[neighbour] = costs_g[neighbour] + \
                        costs_h[neighbour]

                    if neighbour in open_list:
                        min_g = min([costs_g[node] for node in open_list])
                        if costs_g[neighbour] > min_g:
                            continue
                    else:
                        open_list.append(neighbour)

    def is_active(self, id: int) -> bool:
        """
        Returns True if the node is active

        Parameters:
        id:int
          id of the node for which the state is requested
        """
        indices = self.get_index_of_id(id)
        index_y = indices[0]
        index_x = indices[1]
        if self.matrix[index_y][index_x] == 1:
            return True
        else:
            return False

    def get_neighbour_ids(self, index_x: int, index_y: int) -> List:
        neighbours = []
        active_neighbours = []

        # east west
        if index_x == 0:
            if index_y == 0:  # bottom left
                neighbours.append(self.ids[index_y][index_x+1])
                neighbours.append(self.ids[index_y+1][index_x])
                neighbours.append(self.ids[index_y+1][index_x+1])
            elif index_y == len(self.matrix)-1:  # top left
                neighbours.append(self.ids[index_y][index_x+1])
                neighbours.append(self.ids[index_y-1][index_x])
                neighbours.append(self.ids[index_y-1][index_x+1])
            else:  # border left
                neighbours.append(self.ids[index_y-1][index_x])
                neighbours.append(self.ids[index_y+1][index_x])
                neighbours.append(self.ids[index_y-1][index_x+1])
                neighbours.append(self.ids[index_y][index_x+1])
                neighbours.append(self.ids[index_y+1][index_x+1])

        elif index_x == len(self.matrix[0])-1:
            if index_y == 0:  # bottom right
                neighbours.append(self.ids[index_y][index_x-1])
                neighbours.append(self.ids[index_y+1][index_x])
                neighbours.append(self.ids[index_y+1][index_x-1])
            elif index_y == len(self.matrix)-1:  # top right
                neighbours.append(self.ids[index_y][index_x-1])
                neighbours.append(self.ids[index_y-1][index_x])
                neighbours.append(self.ids[index_y-1][index_x-1])
            else:  # border right
                neighbours.append(self.ids[index_y+1][index_x])
                neighbours.append(self.ids[index_y-1][index_x])
                neighbours.append(self.ids[index_y][index_x-1])
                neighbours.append(self.ids[index_y+1][index_x-1])
                neighbours.append(self.ids[index_y-1][index_x-1])
        else:
            if index_y == 0:  # border bottom
                neighbours.append(self.ids[index_y][index_x-1])
                neighbours.append(self.ids[index_y][index_x+1])
                neighbours.append(self.ids[index_y+1][index_x-1])
                neighbours.append(self.ids[index_y+1][index_x])
                neighbours.append(self.ids[index_y+1][index_x+1])
            elif index_y == len(self.matrix)-1:  # border top
                neighbours.append(self.ids[index_y][index_x-1])
                neighbours.append(self.ids[index_y][index_x+1])
                neighbours.append(self.ids[index_y-1][index_x-1])
                neighbours.append(self.ids[index_y-1][index_x])
                neighbours.append(self.ids[index_y-1][index_x+1])
            else:  # the rest (somewhere in the middle)
                neighbours.append(self.ids[index_y][index_x+1])
                neighbours.append(self.ids[index_y][index_x-1])
                neighbours.append(self.ids[index_y+1][index_x])
                neighbours.append(self.ids[index_y-1][index_x])
                neighbours.append(self.ids[index_y+1][index_x+1])
                neighbours.append(self.ids[index_y-1][index_x-1])
                neighbours.append(self.ids[index_y+1][index_x-1])
                neighbours.append(self.ids[index_y-1][index_x+1])

        for neighbour in neighbours:
            if self.is_active(neighbour):
                active_neighbours.append(neighbour)
        return active_neighbours


if __name__ == "__main__":
    grid = Grid(10, 10, 1)
    grid.ids = [[x+y*11 for x in range(len(grid.matrix[0]))]
                for y in range(len(grid.matrix))]
    grid.matrix[3][3] = 0
    grid.print_matrix()
    grid.print_matrix_nodeIds()

    path = grid.get_path_a_star(0, 98)
    print(path)
