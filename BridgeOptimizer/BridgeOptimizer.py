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
    length = 4
    height = 4
    spacing = 1.25
    neighbour_distance_threshold = 1.5*spacing  # this is the max length of the beam
    grid = Grid(length, height, spacing)

    # bridge_optimizer.blackout_zone(0,10,0,10)
    # bridge_optimizer.blackout_zone(-10,0,0,10)

    # Build script
    script_builder = ScriptBuilder.ScriptBuilder(grid)

    script_builder.write_tcl_create_nodes()

    # Rods
    material = Material(200000, 0.3, 7.8e-9)
    Rod.create_rods(grid, neighbour_distance_threshold, material, 0.2*spacing)
    # TODO turn of optimization in certain Rods
    Rod.create_model_Entities(material)
    script_builder.write_tcl_create_rods()

    # Boundary Conditions
    spc_node_ids = [grid.ids[y][x]
                    for y, x in zip([2, 2], [0, length])]
    spc_loadCollector = LoadCollector()
    SPC(spc_loadCollector, spc_node_ids, [0, 0, 0, 0, 0, -999999])

    # Loads
    load_node_id = [grid.ids[y][x] for y, x in zip([2], [2])]
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
