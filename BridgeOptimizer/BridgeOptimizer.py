import math
from typing import List, Tuple
from BridgeOptimizer.datastructure.hypermesh.ModelEntities import Material
from BridgeOptimizer.datastructure.hypermesh.Rod import Rod

import BridgeOptimizer.scriptBuilder.ScriptBuilderBoundaryConditions as ScriptBuilderBoundaryConditions
import BridgeOptimizer.scriptBuilder.ScriptBuilder as ScriptBuilder
from BridgeOptimizer.datastructure.hypermesh.SPC import SPC
from BridgeOptimizer.datastructure.hypermesh.Force import Force
from BridgeOptimizer.datastructure.hypermesh.LoadCollector import LoadCollector
from BridgeOptimizer.datastructure.hypermesh.LoadStep import LoadStep
from BridgeOptimizer.datastructure.hypermesh.Rod import Rod
from BridgeOptimizer.datastructure.Grid import Grid


class BridgeOptimizer:
    """
    Main class of the Bridge Optimizer, used to be called Mesh

    """


def main():
    length = 8
    height = 8
    spacing = 1.25

    driving_lane_height = int(height / 2)
    load_x_coord = int(length/2)
    load_sum = -5*spacing
    neighbour_distance_threshold_lower = 0.
    neighbour_distance_threshold = 3*spacing  # this is the max length of the beam
    grid = Grid(length, height, spacing)

    # bridge_optimizer.blackout_zone(0,10,0,10)
    # bridge_optimizer.blackout_zone(-10,0,0,10)

    # Build script
    script_builder = ScriptBuilder.ScriptBuilder(grid)

    script_builder.write_tcl_create_nodes()

    # Rods
    material = Material(200000, 0.3, 7.8e-9)
    Rod.create_rods(grid, neighbour_distance_threshold_lower,
                    neighbour_distance_threshold, material, 0.2*spacing)
    Rod.create_model_Entities(material)

    # driving lane
    driving_lane = []
    for i in range(length+1):
        driving_lane.append((driving_lane_height, i))
    rods_driving_lane = Rod.getRodsAlongPath(grid, driving_lane)

    Rod.toggleOptimization(rods_driving_lane)

    # write rods to script
    script_builder.write_tcl_create_rods()

    # Boundary Conditions
    spc_node_ids = [grid.ids[y][x]
                    for y, x in zip([driving_lane_height, driving_lane_height], [0, length])]
    spc_loadCollector = LoadCollector()
    SPC(spc_loadCollector, spc_node_ids, [0, 0, 0, 0, 0, -999999])

    # Loads
    load_node_id = [grid.ids[y][x]
                    for y, x in zip([driving_lane_height], [load_x_coord])]
    load_loadCollector = LoadCollector()
    Force(load_loadCollector, load_node_id, 0, load_sum, 0)
    # Loadstep
    LoadStep(spc_loadCollector, load_loadCollector)
    script_builder_bc = ScriptBuilderBoundaryConditions.ScriptBuilderBoundaryConditions()
    script_builder_bc.write_tcl_commands_loadsteps(script_builder.tcl_commands)

    # TopOpt
    script_builder.write_tcl_basic_topOpt_minMass(load_node_id, 0.3*spacing)
    script_builder.write_script_and_run()


if __name__ == "__main__":
    main()
