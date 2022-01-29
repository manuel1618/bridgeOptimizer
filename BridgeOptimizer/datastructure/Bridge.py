from typing import List
from BridgeOptimizer.scriptBuilder.HyperWorksStarter import HyperWorksStarter
from BridgeOptimizer.scriptBuilder.ScriptBuilderHyperview import ScriptBuilderHyperview
from BridgeOptimizer.datastructure.Grid import Grid
from BridgeOptimizer.datastructure.hypermesh.Rod import Rod


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

    def combine_rods_where_possible(self, grid: Grid):
        """
        Rods pointing in the same direction with no additional rods in between are combined
        """

        length_before = len(self.rods)
        print(f"Rods before Combining: {length_before}")

        node_ids = set()
        for rod in self.rods:
            node_ids.add(rod.node_ids[0])
            node_ids.add(rod.node_ids[1])

        nodeId_to_rods = dict()
        for node in node_ids:
            rods = []
            for rod in self.rods:
                if node in rod.node_ids:
                    rods.append(rod)
            nodeId_to_rods[node] = rods

        rods_to_combine = []
        for node in nodeId_to_rods.keys():
            if len(nodeId_to_rods[node]) == 2:
                if Rod.have_same_direction(nodeId_to_rods[node][0], nodeId_to_rods[node][1], grid):
                    rods_to_add = nodeId_to_rods[node]
                    added = False
                    for rod_pair in rods_to_combine:
                        add = False
                        # if they share a common rod
                        if not set(rod_pair).isdisjoint(rods_to_add):
                            # find a rod that is not common and test the direction
                            rod_to_add = rods_to_add[0]
                            for rod in rod_pair:
                                if rod != rod_to_add:
                                    if Rod.have_same_direction(rod, rod_to_add, grid):
                                        add = True
                            if add:  # extend the rodpair by the new rods
                                rod_pair_new = [x for x in rod_pair]
                                rod_pair_new.append(rods_to_add[0])
                                rod_pair_new.append(rods_to_add[1])
                                rods_to_combine.remove(rod_pair)
                                rods_to_combine.append(set(rod_pair_new))
                                added = True
                    if not added:
                        rods_to_combine.append(set(rods_to_add))

        # Finally combining the rods
        for rods in rods_to_combine:
            all_node_ids = []
            rods = [rod for rod in rods]
            for rod in rods:
                for node_id in rod.node_ids:
                    if node_id in all_node_ids:
                        all_node_ids.remove(node_id)
                    else:
                        all_node_ids.append(node_id)
            rod_adapt: Rod = rods[0]
            rods.remove(rod_adapt)
            if len(all_node_ids) == 2:
                rod_adapt.node_ids = all_node_ids
                for rod_to_remove in set(rods):
                    if rod_to_remove in self.rods:
                        self.rods.remove(rod_to_remove)
            else:
                print("Error: Not two independent nodes found")

        length_after = len(self.rods)
        print(f"Rods after Combining: {length_before}")
        # Recursive Iteration until nothing changes
        if length_after != length_before:
            self.combine_rods_where_possible(grid)


if __name__ == "__main__":
    bridge = Bridge(Grid(1, 1, 1), [])
    bridge.remove_rods_with_low_density(
        r"C:\Users\Manuel\Desktop\test\model_optimization_des.h3d", r"C:\Users\Manuel\Desktop\test\density_file.txt", 0.1)
