import os
from typing import List, Tuple

from BridgeOptimizer.datastructure.Grid import Grid
from BridgeOptimizer.datastructure.hypermesh.ModelEntities import Material
from BridgeOptimizer.datastructure.hypermesh.Rod import Rod


from .HypermeshStarter import HypermeshStarter


class ScriptBuilder:
    tcl_commands = []

    def __init__(self, grid: Grid):
        self.tcl_commands = HypermeshStarter.initialize_tcl_commands()
        self.grid = grid

    def write_tcl_create_nodes(self):
        self.grid.ids = [[0 for x in range(len(self.grid.matrix[0]))]
                         for y in range(len(self.grid.matrix))]
        id = 1
        for x in range(len(self.grid.matrix[0])):
            for y in range(len(self.grid.matrix)):
                if self.grid.matrix[y][x] == 1:
                    self.tcl_commands.append(
                        f"*createnode {x*self.grid.spacing} {y*self.grid.spacing} 0 0 0 0")
                    self.grid.ids[y][x] = id
                    id += 1

    def write_tcl_create_rods(self):
        rod_id: int = 1
        rod: Rod = None

        # non optimization - every rod has its comp prop etc
        optimization_id = 0
        for rod in Rod.instances:

            if optimization_id == 0 or not rod.optimization:
                mat = rod.material
                self.tcl_commands.append("*elementtype 61 1")
                material_name = f"material_{rod_id}"
                self.tcl_commands.append(
                    f"*createentity mats cardimage=MAT1 includeid=0 name=\"{material_name}\"")
                self.tcl_commands.append(
                    f"*setvalue mats name=\"{material_name}\" id={{mats {rod_id}}}")
                self.tcl_commands.append("*clearmark materials 1")
                self.tcl_commands.append(
                    f"*setvalue mats id={rod_id} STATUS=1 1={mat.yngs_mdl}")
                self.tcl_commands.append(
                    f"*setvalue mats id={rod_id} STATUS=1 3={mat.poisson_ratio}")
                self.tcl_commands.append(
                    f"*setvalue mats id={rod_id} STATUS=1 4={mat.density}")
                property_name = f"property_{rod_id}"
                self.tcl_commands.append(
                    f"*createentity props cardimage=PROD includeid=0 name=\"{property_name}\"")
                self.tcl_commands.append(
                    f"*setvalue props name=\"{property_name}\" id={{props {rod_id}}}")
                self.tcl_commands.append(
                    f"*createentity beamsectcols includeid=0 name=\"beamsectcol_{rod_id}\"")
                beamsection_name = f"beamsection_{rod_id}"
                self.tcl_commands.append(
                    f"*createentity beamsects includeid=0 name=\"{beamsection_name}\"")

                self.tcl_commands.append(
                    f"*setvalue beamsects name=\"{beamsection_name}\" id={{Beamsections {rod_id}}}")
                self.tcl_commands.append(
                    f"*setvalue beamsects id={rod_id} beamsect_dim1={rod.diameter}")
                self.tcl_commands.append("*clearmark beamsects 1")
                self.tcl_commands.append(
                    f"*setvalue beamsects id={rod_id} config=2")
                self.tcl_commands.append(
                    f"*setvalue props id={rod_id} materialid={{mats {rod_id}}}")
                self.tcl_commands.append(
                    f"*setvalue props id={rod_id} STATUS=2 3179={{beamsects {rod_id}}}")
                self.tcl_commands.append(
                    f"*createmark properties 1 \"property_{rod_id}\"")
                self.tcl_commands.append("*syncpropertybeamsectionvalues 1")
                self.tcl_commands.append("*mergehistorystate \"\" \"\"")

            # optimization - only 1 property
            if rod.optimization and optimization_id == 0:
                optimization_id = rod_id

            rod_id += 1
            if rod.optimization:
                id = optimization_id
            else:
                id = rod_id
            rod.id = id
            self.tcl_commands.append(
                f"*rod {rod.node_ids[0]} {rod.node_ids[1]} \"property_{id}\"")

    def write_tcl_basic_topOpt_minMass(self, node_ids_deflection: List, max_deflection: float):
        """
        Standard Method for min Mass Problems in Optistruct - is dependant on the ROD implementation
        """
        optimization_id = 0
        for rod in Rod.instances:
            if rod.optimization:
                optimization_id = rod.id

        self.tcl_commands.append(
            f"*createmark properties 1 property_{optimization_id}")
        self.tcl_commands.append("*topologydesvarcreate 1 \"topOpt\" f0 0 5")
        self.tcl_commands.append("*createarray 6 0 0 0 0 0 0")
        self.tcl_commands.append("*createdoublearray 6 0 0 0 0 0 0")
        self.tcl_commands.append(
            f"*createarray 7 {optimization_id} 0 0 0 0 0 0")
        self.tcl_commands.append("*createdoublearray 6 0 0 0 0 0 0")
        self.tcl_commands.append(
            f"*optiresponsecreate \"mass\" 29 8 0 0 0 1 6 0 0 0 1 7 1 6")
        self.tcl_commands.append(
            "*optiresponsesetequationdata1 \"mass\" 0 0 0 0 1 0")
        self.tcl_commands.append(
            "*optiresponsesetequationdata2 \"mass\" 0 0 1 0")
        self.tcl_commands.append(
            "*optiresponsesetequationdata3 \"mass\" 0 0 1 0")
        self.tcl_commands.append(
            "*optiresponsesetequationdata4 \"mass\" 0 0 0 0 1 0 1 0")
        line_for_selecting_nodes = f"*createarray {len(node_ids_deflection)+6}"
        for node in node_ids_deflection:
            line_for_selecting_nodes += f" {node}"
        line_for_selecting_nodes += " 0 0 0 0 0 0"
        self.tcl_commands.append(line_for_selecting_nodes)
        # self.tcl_commands.add("*createarray 8 145 162 0 0 0 0 0 0") # reference with two nodes
        self.tcl_commands.append("*createdoublearray 6 0 0 0 0 0 0")
        self.tcl_commands.append(
            f"*optiresponsecreate \"displacement\" 7 0 0 7 0 2 6 0 0 0 1 {len(node_ids_deflection)+6} 1 6")
        self.tcl_commands.append(
            "*optiresponsesetequationdata1 \"displacement\" 0 0 0 0 1 0")
        self.tcl_commands.append(
            "*optiresponsesetequationdata2 \"displacement\" 0 0 1 0")
        self.tcl_commands.append(
            "*optiresponsesetequationdata3 \"displacement\" 0 0 1 0")
        self.tcl_commands.append(
            "*optiresponsesetequationdata4 \"displacement\" 0 0 0 0 1 0 1 0")
        self.tcl_commands.append("*createarray 1 1")
        self.tcl_commands.append(
            f"*opticonstraintcreate \"max_deflection\" 2 1 -1e+20 {max_deflection} 1 1")
        self.tcl_commands.append("*optiobjectivecreate 1 0 0")

    def write_tcl_control_card_displacement_output(self):
        self.tcl_commands.append("*cardcreate \"GLOBAL_OUTPUT_REQUEST\"")
        self.tcl_commands.append("*attributeupdateint cards 1 2938 1 2 0 1")
        self.tcl_commands.append("*attributeupdateint cards 1 1901 1 0 0 1")
        self.tcl_commands.append("*createstringarray 1 \"        \"")
        self.tcl_commands.append(
            "*attributeupdatestringarray cards 1 4871 1 2 0 1 1")
        self.tcl_commands.append("*createstringarray 1 \"OPTI\"")
        self.tcl_commands.append(
            "*attributeupdatestringarray cards 1 4315 1 2 0 1 1")
        self.tcl_commands.append("*createstringarray 1 \"        \"")
        self.tcl_commands.append(
            "*attributeupdatestringarray cards 1 4008 1 2 0 1 1")
        self.tcl_commands.append("*createstringarray 1 \"        \"")
        self.tcl_commands.append(
            "*attributeupdatestringarray cards 1 4876 1 2 0 1 1")
        self.tcl_commands.append("*createstringarray 1 \"        \"")
        self.tcl_commands.append(
            "*attributeupdatestringarray cards 1 2174 1 2 0 1 1")
        self.tcl_commands.append("*createstringarray 1 \"        \"")
        self.tcl_commands.append(
            "*attributeupdatestringarray cards 1 2287 1 2 0 1 1")
        self.tcl_commands.append("*createstringarray 1 \"        \"")
        self.tcl_commands.append(
            "*attributeupdatestringarray cards 1 2175 1 2 0 1 1")
        self.tcl_commands.append("*createstringarray 1 \"        \"")
        self.tcl_commands.append(
            "*attributeupdatestringarray cards 1 12604 1 2 0 1 1")
        self.tcl_commands.append("*createstringarray 1 \"        \"")
        self.tcl_commands.append(
            "*attributeupdatestringarray cards 1 9621 1 2 0 1 1")
        self.tcl_commands.append("*createstringarray 1 \"        \"")
        self.tcl_commands.append(
            "*attributeupdatestringarray cards 1 10026 1 2 0 1 1")
        self.tcl_commands.append("*createstringarray 1 \"        \"")
        self.tcl_commands.append(
            "*attributeupdatestringarray cards 1 10027 1 2 0 1 1")
        self.tcl_commands.append("*createstringarray 1 \"        \"")
        self.tcl_commands.append(
            "*attributeupdatestringarray cards 1 11069 1 2 0 1 1")
        self.tcl_commands.append("*createarray 1 0")
        self.tcl_commands.append(
            "*attributeupdateentityidarray cards 1 11314 1 0 0 analysisparameters 1 1")
        self.tcl_commands.append("*createstringarray 1 \"        \"")
        self.tcl_commands.append(
            "*attributeupdatestringarray cards 1 11387 1 2 0 1 1")
        self.tcl_commands.append("*createstringarray 1 \"ALL\"")
        self.tcl_commands.append(
            "*attributeupdatestringarray cards 1 2939 1 2 0 1 1")

    def write_tcl_basic_topOpt_minCompliance(self, max_volumr_frac: float):
        property_names = ""
        for rod in Rod.instances:
            if rod.optimization:
                property_names += f"\"property_{rod.id}\" "

        self.tcl_commands.append(f"*createmark properties 1 {property_names}")
        self.tcl_commands.append("*topologydesvarcreate 1 \"topOpt\" 0 0 5")
        self.tcl_commands.append("*createarray 6 0 0 0 0 0 0")
        self.tcl_commands.append("*createdoublearray 6 0 0 0 0 0 0")
        self.tcl_commands.append(
            "*optiresponsecreate \"compliance\" 31 0 0 0 0 0 6 0 0 0 1 6 1 6")
        self.tcl_commands.append(
            "*optiresponsesetequationdata1 \"compliance\" 0 0 0 0 1 0")
        self.tcl_commands.append(
            "*optiresponsesetequationdata2 \"compliance\" 0 0 1 0")
        self.tcl_commands.append(
            "*optiresponsesetequationdata3 \"compliance\" 0 0 1 0")
        self.tcl_commands.append(
            "*optiresponsesetequationdata4 \"compliance\" 0 0 0 0 1 0 1 0")
        self.tcl_commands.append("*createarray 6 0 0 0 0 0 0")
        self.tcl_commands.append("*createdoublearray 6 0 0 0 0 0 0")
        self.tcl_commands.append(
            "*optiresponsecreate \"volumefrac\" 3 0 0 0 0 0 6 0 0 0 1 6 1 6")
        self.tcl_commands.append(
            "*optiresponsesetequationdata1 \"volumefrac\" 0 0 0 0 1 0")
        self.tcl_commands.append(
            "*optiresponsesetequationdata2 \"volumefrac\" 0 0 1 0")
        self.tcl_commands.append(
            "*optiresponsesetequationdata3 \"volumefrac\" 0 0 1 0")
        self.tcl_commands.append(
            "*optiresponsesetequationdata4 \"volumefrac\" 0 0 0 0 1 0 1 0")
        self.tcl_commands.append(
            f"*opticonstraintcreate \"vf_dconstraint\" 2 1 -1e+20 {max_volumr_frac} 1 0")
        self.tcl_commands.append(f"*optiobjectivecreate 1 0 1")
