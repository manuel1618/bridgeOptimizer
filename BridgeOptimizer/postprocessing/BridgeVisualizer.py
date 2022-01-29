from typing import List
from BridgeOptimizer.datastructure.Grid import Grid
from BridgeOptimizer.datastructure.hypermesh.Rod import Rod
from BridgeOptimizer.scriptBuilder.HyperWorksStarter import HyperWorksStarter
from BridgeOptimizer.scriptBuilder.ScriptBuilder import ScriptBuilder


class BridgeVisualizer:
    """
    Visualizes Bridge by building lines instead of rods
    TODO: Maybe in the future create 3D representations instead for visualizing the diameters
    """

    @classmethod
    def visualize_bridge(self, calc_dir: str, grid: Grid, rods: List[Rod]):
        script_builder = ScriptBuilder(grid)
        script_builder.write_tcl_create_nodes()
        script_builder.write_tcl_visualize_rods_as_lines(rods)
        hyperworksStarter = HyperWorksStarter(calc_dir, "visualize")
        hyperworksStarter.write_script(
            script_builder.tcl_commands, calc_dir, False, "")
        hyperworksStarter.runHyperMesh(False, False)
