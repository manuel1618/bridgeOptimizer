from importlib.resources import path
import math
from typing import List, Tuple
from BridgeOptimizer.datastructure.Bridge import Bridge
from BridgeOptimizer.datastructure.DrivingLane import DrivingLane
from BridgeOptimizer.datastructure.hypermesh.ModelEntities import Material
from BridgeOptimizer.datastructure.hypermesh.Rod import Rod
from BridgeOptimizer.scriptBuilder.HypermeshStarter import HypermeshStarter

import BridgeOptimizer.scriptBuilder.ScriptBuilderBoundaryConditions as ScriptBuilderBoundaryConditions
import BridgeOptimizer.scriptBuilder.ScriptBuilder as ScriptBuilder
from BridgeOptimizer.datastructure.hypermesh.SPC import SPC
from BridgeOptimizer.datastructure.hypermesh.Force import Force
from BridgeOptimizer.datastructure.hypermesh.LoadCollector import LoadCollector
from BridgeOptimizer.datastructure.hypermesh.LoadStep import LoadStep
from BridgeOptimizer.datastructure.hypermesh.Rod import Rod
from BridgeOptimizer.datastructure.Grid import Grid
from BridgeOptimizer.datastructure.Bridge import Bridge
from BridgeOptimizer.postprocessing.GlobalOutputReader import DisplacementReader


class BridgeOptimizer:
    """
    Main class of the Bridge Optimizer, used to be called Mesh

    """


def main():
    length = 8
    height = 8
    spacing = 1.25

    driving_lane_height = int(height / 2)
    load_sum = -1500*spacing
    neighbour_distance_threshold_lower = 0.
    # this is grid beam resolution, min 1.5 * spacing
    neighbour_distance_threshold = 5*spacing
    max_beam_length = 4*spacing
    grid = Grid(length, height, spacing)

    # blackout zone
    grid.blackout_zone(0, 0, driving_lane_height-1, length+1)
    grid.print_matrix()

    # Build script
    script_builder = ScriptBuilder.ScriptBuilder(grid)

    script_builder.write_tcl_create_nodes()

    # Rods
    material = Material(200000, 0.3, 7.8e-9)
    diameter = 0.2*spacing
    Rod.create_rods(grid, neighbour_distance_threshold_lower,
                    neighbour_distance_threshold, material, diameter)
    grid.print_matrix_nodeIds()
    # Driving Lane
    driving_lane_nodes = grid.get_path_a_star(grid.ids[driving_lane_height]
                                              [0], grid.ids[driving_lane_height][length])
    # delete all Rods belonging to the driving lane
    Rod.driving_lane_ereaser(driving_lane_nodes)
    driving_lane = DrivingLane(max_beam_length, driving_lane_nodes, grid)
    driving_lane.create_Rods_along_nodes_path(material, 0.1*diameter)
    Rod.create_model_Entities(material)

    # Bridge
    bridge = Bridge(grid, Rod.instances)
    bridge.calculate_costs()

    # write rods to script
    script_builder.write_tcl_create_rods()

    # Boundary Conditions
    spc_node_ids = [grid.ids[y][x]
                    for y, x in zip([driving_lane_height, driving_lane_height], [0, length])]
    spc_loadCollector = LoadCollector()
    SPC(spc_loadCollector, spc_node_ids, [0, 0, 0, 0, 0, -999999])

    # Loads
    load_node_ids = driving_lane.get_load_nodes()
    print(load_node_ids)
    load_loadCollector = LoadCollector()
    Force(load_loadCollector, load_node_ids, 0, load_sum, 0)
    # Loadstep
    LoadStep(spc_loadCollector, load_loadCollector)
    script_builder_bc = ScriptBuilderBoundaryConditions.ScriptBuilderBoundaryConditions()
    script_builder_bc.write_tcl_commands_loadsteps(script_builder.tcl_commands)

    # Get Constraint by Analyzing
    script_builder.write_tcl_control_card_displacement_output()
    hypermesh_starter = HypermeshStarter("C:\\temp", "model")
    calc_dir = "C:\\temp"
    hypermesh_starter.write_script(tcl_commands=script_builder.tcl_commands,
                                   calc_dir=calc_dir, run=True,
                                   user_param="-optskip -len 10000 -nproc 8")
    hypermesh_starter.runHyperMesh(batch=True, wait=True)
    path_to_disp_file = calc_dir+"/"+hypermesh_starter.model_name+".disp"
    path_to_disp_file.replace("\\", "/")
    diplacement_reader = DisplacementReader(path_to_disp_file)
    max_disp = diplacement_reader.get_max_displacement()[1]
    print(f"Max diplacements: {max_disp}")

    # TopOpt
    max_disp_constraint = 5*max_disp
    script_builder.write_tcl_basic_topOpt_minMass(
        load_node_ids, max_disp_constraint)
    calc_dir = "C:\\temp"
    hypermesh_starter_topOpt = HypermeshStarter(
        "C:\\temp", "model_optimization")
    hypermesh_starter_topOpt.write_script(tcl_commands=script_builder.tcl_commands,
                                          calc_dir=calc_dir, run=True,
                                          user_param="-len 10000 -nproc 8")
    hypermesh_starter_topOpt.runHyperMesh(batch=True, wait=False)


if __name__ == "__main__":
    main()
