import os
from typing import List, Tuple

from HypermeshStarter import HypermeshStarter
import Mesh


class ScriptBuilder:
    tcl_commands = []
    mesh: Mesh

    def __init__(self, mesh: Mesh):
        self.tcl_commands = HypermeshStarter.initialize_tcl_commands()
        self.mesh = mesh

    def write_tcl_create_nodes(self):
        self.mesh.ids = [[0 for x in range(len(self.mesh.matrix[0]))]
                         for y in range(len(self.mesh.matrix))]
        id = 1
        for x in range(len(self.mesh.matrix[0])):
            for y in range(len(self.mesh.matrix)):
                if self.mesh.matrix[y][x] == 1:
                    self.tcl_commands.append(
                        f"*createnode {x*self.mesh.spacing} {y*self.mesh.spacing} 0 0 0 0")
                    self.mesh.ids[y][x] = id
                    id += 1

    def write_tcl_create_rods_optimization(self, neighbour_distance_threshold: float, shortest_beam_length: float):

        property_name_optimization = "property1"

        self.tcl_commands.append("*elementtype 61 1")
        self.tcl_commands.append(
            "*createentity mats cardimage=MAT1 includeid=0 name=\"material1\"")
        self.tcl_commands.append("*clearmark materials 1")
        self.tcl_commands.append("*setvalue mats id=1 STATUS=1 1=210000")
        self.tcl_commands.append("*setvalue mats id=1 STATUS=1 3=0.3")
        self.tcl_commands.append("*setvalue mats id=1 STATUS=1 4=7.85e-09")
        self.tcl_commands.append(
            f"*createentity props cardimage=PROD includeid=0 name=\"{property_name_optimization}\"")
        self.tcl_commands.append(
            "*createentity beamsectcols includeid=0 name=\"beamsectcol1\"")
        self.tcl_commands.append(
            "*createentity beamsects includeid=0 name=\"beamsection1\"")
        self.tcl_commands.append(
            f"*setvalue beamsects id=1 beamsect_dim1={0.2*shortest_beam_length}")
        self.tcl_commands.append("*clearmark beamsects 1")
        self.tcl_commands.append("*setvalue beamsects id=1 config=2")
        self.tcl_commands.append("*setvalue props id=1 materialid={mats 1}")
        self.tcl_commands.append(
            "*setvalue props id=1 STATUS=2 3179={beamsects 1}")
        self.tcl_commands.append(
            f"*createmark properties 1 \"{property_name_optimization}\"")
        self.tcl_commands.append("*syncpropertybeamsectionvalues 1")
        self.tcl_commands.append("*mergehistorystate \"\" \"\"")
        linksAlreadyDrawn = []
        for x in range(len(self.mesh.matrix[0])):
            for y in range(len(self.mesh.matrix)):
                if self.mesh.matrix[y][x] == 1:
                    id = self.mesh.ids[y][x]
                    neighbours = self.mesh.get_neighbour_by_distance(
                        x, y, neighbour_distance_threshold)
                    for neighbourId in neighbours:
                        if (id, neighbourId) not in linksAlreadyDrawn and (neighbourId, id) not in linksAlreadyDrawn:
                            self.tcl_commands.append(
                                f"*rod {id} {neighbourId} \"{property_name_optimization}\"")
                            linksAlreadyDrawn.append((id, neighbourId))

    """

    Parameters:
    - dofs: List of values for the DOFs of the spcs to create. -999999 is a free contraint

    """

    def write_tcl_spc(self, nodeIDs: List, dofs: List):
        # TODO: Add some chekc if the load collecor has been created
        self.tcl_commands.append(
            "*createentity loadcols includeid=0 name=\"spc\"")
        for nodeID in nodeIDs:
            self.tcl_commands.append(f"*createmark nodes 1 {nodeID}")
            self.tcl_commands.append(
                f"*loadcreateonentity_curve nodes 1 3 1 {dofs[0]} {dofs[1]} {dofs[2]} {dofs[3]} {dofs[4]} {dofs[5]} 0 0 0 0 0")
            self.tcl_commands.append("*createmark loads 0 1")
            self.tcl_commands.append("*loadsupdatefixedvalue 0 0")
        pass

    def write_tcl_load(self, nodeIDs: List, force: Tuple):
        # TODO: Add some chekc if the load collecor has been created
        self.tcl_commands.append(
            "*createentity loadcols includeid=0 name=\"loads\"")
        for nodeID in nodeIDs:
            self.tcl_commands.append(f"*createmark nodes 1 {nodeID}")
            self.tcl_commands.append(
                f"*loadcreateonentity_curve nodes 1 1 1 {force[0]} {force[1]} {force[2]} 0 {force[0]} {force[1]} {force[2]} 0 0 0 0")
        pass

    def write_tcl_loadstep(self):
        self.tcl_commands.append("*createmark loadcols 1 \"spc\" \"loads\"")
        self.tcl_commands.append("*createmark outputblocks 1")
        self.tcl_commands.append("*createmark groups 1")
        self.tcl_commands.append("*loadstepscreate \"ls1\" 1")
        self.tcl_commands.append(
            "*attributeupdateint loadsteps 1 4143 1 1 0 1")
        self.tcl_commands.append(
            "*attributeupdateint loadsteps 1 4709 1 1 0 1")
        self.tcl_commands.append(
            "*setvalue loadsteps id=1 STATUS=2 4059=1 4060=STATICS")
        self.tcl_commands.append(
            "*attributeupdateentity loadsteps 1 4145 1 1 0 loadcols 1")
        self.tcl_commands.append(
            "*attributeupdateentity loadsteps 1 4147 1 1 0 loadcols 2")
        self.tcl_commands.append(
            "*attributeupdateint loadsteps 1 3800 1 1 0 0")
        self.tcl_commands.append("*attributeupdateint loadsteps 1 707 1 1 0 0")
        self.tcl_commands.append(
            "*attributeupdateint loadsteps 1 2396 1 1 0 0")
        self.tcl_commands.append(
            "*attributeupdateint loadsteps 1 8134 1 1 0 0")
        self.tcl_commands.append(
            "*attributeupdateint loadsteps 1 2160 1 1 0 0")
        self.tcl_commands.append(
            "*attributeupdateint loadsteps 1 10212 1 1 0 0")

    def write_tcl_basic_topOpt_minMass(self, node_ids_deflection: List, max_deflection: float):
        self.tcl_commands.append("*createmark properties 1 \"property1\"")
        self.tcl_commands.append("*topologydesvarcreate 1 \"topOpt\" 0 0 5")
        self.tcl_commands.append("*createarray 6 0 0 0 0 0 0")
        self.tcl_commands.append("*createdoublearray 6 0 0 0 0 0 0")
        self.tcl_commands.append("*createarray 7 1 0 0 0 0 0 0")
        self.tcl_commands.append("*createdoublearray 6 0 0 0 0 0 0")
        self.tcl_commands.append(
            "*optiresponsecreate \"mass\" 29 8 0 0 0 1 6 0 0 0 1 7 1 6")
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

    def write_tcl_basic_topOpt_minCompliance(self, max_volumr_frac: float):
        self.tcl_commands.append("*createmark properties 1 \"property1\"")
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

    def write_script_and_run(self):
        with open('tcl_commands.tcl', 'w') as tcl_file:
            pathScript = os.path.abspath("tcl_commands.tcl")
            for line in self.tcl_commands:
                tcl_file.write("%s\n" % line)
        hypermeshStarter = HypermeshStarter()
        hypermeshStarter.runHyperMesh(pathScript)


# def main():
#     script_builder = ScriptBuilder()
#     script_builder.write_tcl_load([1, 2], (1, 2, 3))

#     for line in script_builder.tcl_commands:
#         print(line)


# if __name__ == "__main__":
#     main()
