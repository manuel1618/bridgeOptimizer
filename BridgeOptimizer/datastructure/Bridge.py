from BridgeOptimizer.scriptBuilder.HyperWorksStarter import HyperWorksStarter
from BridgeOptimizer.scriptBuilder.ScriptBuilderHyperview import ScriptBuilderHyperview
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
        TODO: Combine Rods with the same vector and a shared node where no other rod is attached
        """
        total_costs: float = 0
        for rod in self.rods:
            cost_rod = rod.calculate_cost(self.grid)
            #print(f"Rod: {rod.node_ids} costs {cost_rod}")
            total_costs += cost_rod

        self.costs = total_costs

    def remove_rods_with_low_density(self, calc_dir: str, path_to_des_file: str, path_to_densityFile_out: str, density_threshold: float):
        """
        Removes all rods from the bridge rods collection with density lower than specified 

        """
        calc_dir = calc_dir.replace("\\", "/")
        script_builder = ScriptBuilderHyperview()
        script_builder.write_density_File(
            path_to_des_file, path_to_densityFile_out)
        hyperViewStarter = HyperWorksStarter(calc_dir, "density_file")
        hyperViewStarter.write_script_hyperview(
            calc_dir, script_builder.tcl_commands)
        hyperViewStarter.runHyperview(True, True)

        rods_to_remove = []
        with open(path_to_densityFile_out, "r") as density_file:
            for line in density_file.readlines()[1:]:
                element_id = line.split(",")[0]
                element_density = float(line.split(",")[1])
                if element_density < density_threshold:
                    rods_to_remove.append(Rod.get_rod_by_id(int(element_id)))

        print(f"Number of Rods before removal: {len(self.rods)}")
        for rod_to_remove in rods_to_remove:
            if rod_to_remove in self.rods:
                self.rods.remove(rod_to_remove)
        print(
            f"Number of Rods after removal: {len(self.rods)}, density threshold value used: {density_threshold}")


if __name__ == "__main__":
    bridge = Bridge(Grid(1, 1, 1), [])
    bridge.remove_rods_with_low_density(
        r"C:\Users\Manuel\Desktop\test\model_optimization_des.h3d", r"C:\Users\Manuel\Desktop\test\density_file.txt", 0.1)
