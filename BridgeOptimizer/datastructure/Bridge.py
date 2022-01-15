from .Grid import Grid
from typing import List
from .hypermesh.Rod import Rod


class Bridge:
    """
    Bridge class, which is used (also) for calculating the costs
    """
    grid: Grid = None
    rods: List[Rod] = []
    costs: float = 0

    def __init__(self, grid: Grid, rods: List) -> None:
        self.grid = grid
        self.rods = rods

    def calculate_costs(self):
        """
        Calculates the costs of a bridge for now just with one single cost/length value

        """
        total_costs: float = 0
        for rod in self.rods:
            cost_rod = rod.calculate_cost(self.grid)
            print(f"Rod: {rod.node_ids} costs {cost_rod}")
            total_costs += cost_rod

        self.costs = total_costs
