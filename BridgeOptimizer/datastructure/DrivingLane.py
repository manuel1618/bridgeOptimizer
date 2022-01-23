from bdb import Breakpoint
from collections import deque
import math
from tracemalloc import start
from typing import List
from BridgeOptimizer.datastructure.Grid import Grid
from BridgeOptimizer.datastructure.hypermesh.Rod import Rod
from BridgeOptimizer.datastructure.hypermesh.ModelEntities import Material


class DrivingLane:

    nodes: List[int] = []
    rods: List[Rod] = []

    def __init__(self, max_beam_length: int, node_path: List[int], grid: Grid) -> None:
        DrivingLane.nodes.clear()
        self.grid = grid
        self.create_driving_lane(max_beam_length, node_path)

    def create_Rods_along_nodes_path(self, material: Material, diameter: float):
        # nodes are listed like : 1 2 2 3 - so 2 is the step size
        for i in range(0, len(self.nodes)-1, 2):
            DrivingLane.rods.append(
                Rod(material, diameter, (self.nodes[i], self.nodes[i+1]), False))

    def create_driving_lane(self, max_beam_length: int, node_path: List[int]):
        """
        Method for creating the driving lane Rods by equally spacing with symmetrical adding

        Parameters:
        ---------
        max_beam_length:int
          Maximum length of one beam
        node_path:deque
          List of nodes which should be followed.
        """

        left_side = deque()
        right_side = deque()

        # copy for safety reasons
        all_nodes = deque([node for node in node_path])

        # check if solvable
        for i in range(len(all_nodes)-1):
            distance = self.calculate_distance(all_nodes[i], all_nodes[i+1])
            if distance > max_beam_length:
                print(
                    "Error driving lane: on segment is less than the max beam length. Impossible")

        distance = self.calculate_distance(all_nodes[0], all_nodes[-1])

        # Driving lane must have at least 2 elements
        if distance > 2*max_beam_length:
            start_left = all_nodes.popleft()
            start_right = all_nodes.pop()

            # Build driving lane until there are max. 2 elements neccessary
            while len(all_nodes) >= 2:
                distance_remaining = self.calculate_distance(
                    start_left, start_right)

                if distance_remaining <= 2*max_beam_length:
                    if distance_remaining < max_beam_length:
                        print(f"Final {start_left} {start_right}")
                        left_side.append(start_left)
                        right_side.appendleft(start_right)
                        all_nodes.clear()
                    break

                # find the next node left
                next_left = all_nodes.popleft()
                while len(all_nodes) > 0:
                    next_left_temp = all_nodes.popleft()  # temporary pop one left
                    # check if length exceeds beemlength
                    if self.calculate_distance(start_left, next_left_temp) > max_beam_length:
                        # put node back in and leave
                        all_nodes.appendleft(next_left_temp)
                        break
                    else:
                        next_left = next_left_temp  # next_left : last node not exceeding max beam length

                # find next node right
                next_right = all_nodes.pop()
                while len(all_nodes) > 0:
                    next_right_temp = all_nodes.pop()  # temporary pop one left
                    # check if length exceeds beemlength
                    if self.calculate_distance(start_right, next_right_temp) > max_beam_length:
                        # put node back in and leave
                        all_nodes.append(next_right_temp)
                        break
                    else:
                        next_right = next_right_temp  # next_left : last node not exceeding max beam length

                print(f"Left: {start_left} {next_left}")
                left_side.append(start_left)
                left_side.append(next_left)
                print(f"Right: {start_right} {next_right}")
                right_side.appendleft(start_right)
                right_side.appendleft(next_right)

                start_left = next_left
                start_right = next_right
        else:
            start_left = all_nodes.popleft()
            start_right = all_nodes.pop()

        # one element case
        if len(all_nodes) == 0:
            print(f"Final {start_left} {start_right}")
            left_side.append(start_left)
            right_side.appendleft(start_right)
        # symmetric case - one node left (the middle hopefully)
        elif len(all_nodes) % 2 != 0:  # non even number left
            if self.calculate_distance(start_left, start_right) < max_beam_length:
                print(f"Final {start_left} {start_right}")
                left_side.append(start_left)
                right_side.appendleft(start_right)
            else:
                # get the center - pop as long as there are more than 1
                while len(all_nodes) != 1:
                    middle = all_nodes.pop()
                    middle = all_nodes.popleft()
                middle = all_nodes.pop()

                print(f"Final {start_left} {middle}")
                print(f"Final {middle} {start_right}")
                left_side.append(start_left)
                left_side.append(middle)
                left_side.append(middle)
                right_side.appendleft(start_right)

        # assymetric final with at least two elements
        elif len(all_nodes) >= 2:
            # on middle node (2 elements, Option A)
            while len(all_nodes) > 0:
                next_left_temp = all_nodes.popleft()  # temporary pop one left
                # check if length exceeds beemlength
                if self.calculate_distance(start_left, next_left_temp) > max_beam_length:
                    # put node back in and leave
                    all_nodes.appendleft(next_left_temp)
                    break
                else:
                    middle_left = next_left_temp  # next_left : last node not exceeding max beam length

            if self.calculate_distance(middle_left, start_right) < max_beam_length:
                # Finish 2 elements
                print(f"Final {start_left} {middle_left} {start_right}")
                left_side.append(start_left)
                left_side.append(middle_left)
                left_side.append(middle_left)
                right_side.appendleft(start_right)
            # two middle nodes (3 elements, Option B)
            else:
                while len(all_nodes) > 0:
                    next_right_temp = all_nodes.pop()  # temporary pop one
                    # check if length exceeds beemlength
                    if self.calculate_distance(start_right, next_right_temp) > max_beam_length:
                        # put node back in and leave
                        all_nodes.appendleft(next_right_temp)
                        break
                    else:
                        middle_right = next_right_temp

                print(
                    f"Final: {start_left} {middle_left} {middle_right} {start_right}")
                left_side.append(start_left)
                left_side.append(middle_left)
                left_side.append(middle_left)
                left_side.append(middle_right)
                right_side.appendleft(start_right)
                right_side.appendleft(middle_right)

        DrivingLane.nodes = [node for node in left_side] + \
            [node for node in right_side]

    def calculate_distance(self, id1: int, id2: int) -> int:
        """
        Returs the distance between two nodes
        """
        return self.grid.get_distance_by_ids(id1, id2)

    def get_load_nodes(self):
        """
        Returns the load nodes without duplicates and without the first and last one, as they are 
        single point constraints most likely
        """
        load_nodes = [node for node in DrivingLane.nodes]
        load_nodes.remove(load_nodes[0])
        load_nodes.remove(load_nodes[len(load_nodes)-1])
        load_nodes = set(load_nodes)  # no duplicates
        load_nodes = [node for node in load_nodes]
        return load_nodes


if __name__ == "__main__":
    print("0-10, length 3")
    DrivingLane(3, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    print(DrivingLane.nodes)
    print("0-9, length 3")
    DrivingLane(3, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    print(DrivingLane.nodes)
    print("0-9, length 20")
    DrivingLane(20, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    print(DrivingLane.nodes)
    print("0-9, length 10")
    DrivingLane(10, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    print(DrivingLane.nodes)
    print("0-10, length 1")
    DrivingLane(1, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    print(DrivingLane.nodes)
    print("0-9, length 1")
    DrivingLane(1, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    print(DrivingLane.nodes)
