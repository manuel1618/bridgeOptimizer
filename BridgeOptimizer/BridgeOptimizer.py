from importlib.resources import path
import os
from msilib.schema import File
from typing import Dict, List, Tuple
from datetime import datetime
from BridgeOptimizer.datastructure.Bridge import Bridge
from BridgeOptimizer.datastructure.DrivingLane import DrivingLane
from BridgeOptimizer.datastructure.hypermesh.ModelEntities import Material
from BridgeOptimizer.datastructure.hypermesh.Rod import Rod
from BridgeOptimizer.postprocessing.BridgeVisualizer import BridgeVisualizer
from BridgeOptimizer.scriptBuilder.HyperWorksStarter import HyperWorksStarter
import BridgeOptimizer.scriptBuilder.ScriptBuilderBoundaryConditions as ScriptBuilderBoundaryConditions
import BridgeOptimizer.scriptBuilder.ScriptBuilder as ScriptBuilder
from BridgeOptimizer.scriptBuilder.ScriptBuilderHyperview import ScriptBuilderHyperview
from BridgeOptimizer.datastructure.hypermesh.SPC import SPC
from BridgeOptimizer.datastructure.hypermesh.Force import Force
from BridgeOptimizer.datastructure.hypermesh.LoadCollector import LoadCollector
from BridgeOptimizer.datastructure.hypermesh.LoadStep import LoadStep
from BridgeOptimizer.datastructure.hypermesh.Rod import Rod
from BridgeOptimizer.datastructure.Grid import Grid
from BridgeOptimizer.datastructure.Bridge import Bridge
from BridgeOptimizer.postprocessing.GlobalOutputReader import DisplacementReader
from BridgeOptimizer.utility.DirectoryHelper import DirectoryHelper


class BridgeOptimizer:
    """
    Main class of the Bridge Optimizer

    """

    def __init__(self, values: Dict = dict()) -> None:
        print("------------------- New Study -----------------------")
        default_values = self.load_default_values()

        for key in default_values.keys():
            if key not in values:
                values[key] = default_values[key]
                print("Fetched Default value for key: "+key)
        values["driving_lane_end_x"] = values["length"]

        # Independent variables
        now = datetime.now()
        model_name_optimization = values["model_name_optimization"]
        simulation_dir = values["simulation_dir"]+"/" + \
            model_name_optimization+"_"+str(now.timestamp())
        if not os.path.exists(simulation_dir):
            os.makedirs(simulation_dir)

        density_threshold = values["density_threshold"]

        length = values["length"]
        height = values["height"]
        spacing = values["spacing"]

        load_sum = -1500*spacing
        neighbour_distance_threshold_lower = values["min_beam_length"]
        # this is grid beam resolution, min 1.5 * spacing
        neighbour_distance_threshold = values["neighbour_distance_threshold"]
        max_beam_length = values["max_beam_length"]
        grid = Grid(length, height, spacing)

        # blackout zone
        if values["blackout_lower_zone"] == True:
            print("Bottom half is ignored")
            grid.blackout_zone(0, 0, values["driving_lane_start_y"], length+1)
        # grid.print_matrix()

        # Build script
        script_builder = ScriptBuilder.ScriptBuilder(grid)

        script_builder.write_tcl_create_nodes()

        # Rods
        material = Material(200000, 0.3, 7.8e-9)
        diameter = 0.2*spacing
        Rod.instances = []
        Rod.create_rods(grid, neighbour_distance_threshold_lower,
                        neighbour_distance_threshold, material, diameter)

        # Driving Lane
        start_x = values["driving_lane_start_x"]
        start_y = values["driving_lane_start_y"]
        end_x = values["driving_lane_end_x"]
        end_y = values["driving_lane_end_y"]
        driving_lane_nodes = grid.get_path_a_star(
            grid.ids[start_y][start_x], grid.ids[end_y][end_x])
        # delete all Rods belonging to the driving lane
        Rod.driving_lane_ereaser(driving_lane_nodes)
        driving_lane = DrivingLane(max_beam_length, driving_lane_nodes, grid)
        driving_lane.create_Rods_along_nodes_path(material, 0.1*diameter)

        # Model Entities Creation
        Rod.create_model_Entities(material)

        # Bridge
        bridge = Bridge(grid, Rod.instances)
        bridge.calculate_costs()

        # write rods to script
        script_builder.write_tcl_create_rods()

        # Empty Lists of Boundary Conditions
        LoadCollector.instances = []
        LoadStep.instances = []
        # Boundary Conditions
        spc_node_ids = [grid.ids[y][x]
                        for y, x in zip([start_y, end_y], [start_x, end_x])]
        spc_loadCollector = LoadCollector()
        SPC(spc_loadCollector, spc_node_ids, [0, 0, 0, 0, 0, -999999])

        # Loads
        load_node_ids = driving_lane.get_load_nodes()
        load_loadCollector = LoadCollector()
        Force(load_loadCollector, load_node_ids, 0, load_sum, 0)
        # Loadstep
        LoadStep(spc_loadCollector, load_loadCollector)
        script_builder_bc = ScriptBuilderBoundaryConditions.ScriptBuilderBoundaryConditions()
        script_builder_bc.write_tcl_commands_loadsteps(
            script_builder.tcl_commands)

        # Get Constraint by Analyzing
        script_builder.write_tcl_control_card_displacement_output()
        hypermesh_starter = HyperWorksStarter(
            simulation_dir, model_name_optimization+"_disp")

        hypermesh_starter.write_script(tcl_commands=script_builder.tcl_commands,
                                       calc_dir=simulation_dir, run=True,
                                       user_param="-optskip -len 10000 -nproc 8")
        hypermesh_starter.runHyperMesh(batch=True, wait=True)
        path_to_disp_file = simulation_dir+"/"+hypermesh_starter.model_name+".disp"
        path_to_disp_file.replace("\\", "/")
        diplacement_reader = DisplacementReader(path_to_disp_file)
        max_disp = diplacement_reader.get_max_displacement()[1]
        print(f"Max diplacements: {max_disp}")

        # TopOpt
        max_disp_constraint = values["max_disp_constraint_factor"]*max_disp
        script_builder.write_tcl_basic_topOpt_minMass(
            load_node_ids, max_disp_constraint)
        script_builder.write_tcl_opticontrolParameter(
            99, values["opticontrol_discrete"])
        hypermesh_starter_topOpt = HyperWorksStarter(
            simulation_dir, model_name_optimization)
        hypermesh_starter_topOpt.write_script(tcl_commands=script_builder.tcl_commands,
                                              calc_dir=simulation_dir, run=True,
                                              user_param="-len 10000 -nproc 8")
        hypermesh_starter_topOpt.runHyperMesh(batch=True, wait=True)

        # Density File
        path_to_des_file = simulation_dir+"/"+model_name_optimization+"_des.h3d"
        path_to_density_file = simulation_dir+"/" + \
            model_name_optimization+"_densityFile.txt"
        # Remove Rods which did not make it
        bridge.remove_rods_with_low_density(
            simulation_dir, path_to_des_file, path_to_density_file, density_threshold)

        # Screenshots
        script_builder_hyperview = ScriptBuilderHyperview()
        script_builder_hyperview.screenshot_element_density(
            path_to_des_file, density_threshold)
        hypermesh_starter.write_script_hyperview(
            simulation_dir, script_builder_hyperview.tcl_commands)
        hypermesh_starter.runHyperview(True, True)

        bridge.combine_rods_where_possible(grid)
        # Visualize
        # BridgeVisualizer.visualize_bridge(simulation_dir, grid, bridge.rods)

        # Cleanup
        hypermesh_starter.clean_up_simulation_dir(simulation_dir)

    def load_default_values(self) -> Dict:
        default_vaules = dict()
        # independent
        default_vaules["simulation_dir"] = "C:\\temp"
        default_vaules["model_name_optimization"] = "model_name_optimization"
        default_vaules["density_threshold"] = 0.2
        default_vaules["length"] = 32
        default_vaules["height"] = 8
        default_vaules["spacing"] = 1.25
        default_vaules["min_beam_length"] = 0
        default_vaules["max_beam_length"] = 8*default_vaules["spacing"]
        default_vaules["neighbour_distance_threshold"] = 1.5 * \
            default_vaules["spacing"]
        default_vaules["max_disp_constraint_factor"] = 5
        default_vaules["opticontrol_discrete"] = 3

        # defaults ( or dependent)
        default_vaules["driving_lane_height"] = int(
            default_vaules["height"]/2.)
        default_vaules["driving_lane_start_x"] = 0
        default_vaules["driving_lane_end_x"] = default_vaules["length"]
        default_vaules["driving_lane_start_y"] = int(
            default_vaules["height"]/2.)
        default_vaules["driving_lane_end_y"] = int(
            default_vaules["height"]/2.)
        default_vaules["blackout_lower_zone"] = False
        return default_vaules


if __name__ == "__main__":
    # spacing test
    values = dict()
    values["simulation_dir"] = "C:\\temp\Study_test"
    if not os.path.exists(values["simulation_dir"]):
        os.makedirs(values["simulation_dir"])
    DirectoryHelper.clean_directory(
        values["simulation_dir"])  # CLEAN DIRECTORY

    values["spacing"] = 1.
    values["neighbour_distance_threshold"] = 1.5 * values["spacing"]
    values["model_name_optimization"] = "level1"
    values["density_threshold"] = 0.3
    values["length"] = 8
    values["height"] = 8
    values["min_beam_length"] = 0.9 * values["spacing"]
    values["max_beam_length"] = 4.5 * values["spacing"]
    values["max_disp_constraint_factor"] = 15
    values["blackout_lower_zone"] = True
    values["opticontrol_discrete"] = 3

    BridgeOptimizer(values)
