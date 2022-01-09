import os
from typing import List, Tuple
from BridgeOptimizer.datastructure.hypermesh.LoadCollector import LoadCollector
from BridgeOptimizer.datastructure.hypermesh.LoadStep import LoadStep
from BridgeOptimizer.datastructure.hypermesh.Force import Force
from BridgeOptimizer.datastructure.hypermesh.SPC import SPC


class ScriptBuilderBoundaryConditions:
    """
    Extra class for generating Loadstep, Loadcollectors, Forces and Constraints

    Parameters: 
    ---------
    None


    """

    def __init__(self) -> None:
        pass

    def write_tcl_commands_loadCollectors(self, tcl_commands: List) -> None:
        """
        Creates all the load collectors (has to be done before creating loadsteps, as the loadcollectors are referenced)
        """
        load_collector: LoadCollector = None
        # create all load collectors and loads first
        for load_collector in LoadCollector.instances:
            load_collector_type = load_collector.get_load_collector_type()
            load_collector.name = f"{str(load_collector_type.__name__)}_{str(load_collector.get_id())}"
            tcl_commands.append(
                f"*createentity loadcols includeid=0 name=\"{load_collector.name}\"")
            # create loads
            for load in load_collector.loads:
                if load_collector_type == Force:
                    force: Force = load
                    tcl_commands.append(
                        f"*createmark nodes 1 {' '.join([str(x) for x in force.nodeIds])}")
                    tcl_commands.append(
                        f"*loadcreateonentity_curve nodes 1 1 1 {force.x} {force.y} {force.z} 0 {force.x} {force.y} {force.z} 0 0 0 0")
                elif load_collector_type == SPC:
                    spc: SPC = load
                    tcl_commands.append(
                        f"*createmark nodes 1 {' '.join([str(x) for x in spc.nodeIds])}")
                    tcl_commands.append(
                        f"*loadcreateonentity_curve nodes 1 3 1 {spc.dofs[0]} {spc.dofs[1]} {spc.dofs[2]} {spc.dofs[3]} {spc.dofs[4]} {spc.dofs[5]} 0 0 0 0 0")
                    tcl_commands.append("*createmark loads 0 1")
                    tcl_commands.append("*loadsupdatefixedvalue 0 0")

    def write_tcl_commands_loadsteps(self, tcl_commands: List) -> None:
        """
        Single method to write all tcl commands to the file
        """

        self.write_tcl_commands_loadCollectors(tcl_commands)

        # create the load step
        load_step: LoadStep = None
        for load_step in LoadStep.instances:
            load_step_id = str(load_step.get_id())

            # TODO: should be possible to just use a spc collector - not possible rn.
            spc_loadCollector = load_step.spc_loadCollector
            load_loadCollector = load_step.load_loadCollector
            spc_loadCollector_id = str(spc_loadCollector.get_id())
            load_loadCollector_id = str(load_loadCollector.get_id())

            tcl_commands.append(
                f"*createmark loadcols 1 \"{spc_loadCollector.name}\" \"{load_loadCollector.name}\"")
            tcl_commands.append("*createmark outputblocks 1")
            tcl_commands.append("*createmark groups 1")

            tcl_commands.append(
                f"*loadstepscreate \"loadstep_{load_step_id}\" 1")
            tcl_commands.append(
                f"*attributeupdateint loadsteps {load_step_id} 4143 1 1 0 1")
            tcl_commands.append(
                f"*attributeupdateint loadsteps {load_step_id} 4709 1 1 0 1")
            tcl_commands.append(
                f"*setvalue loadsteps id={load_step_id} STATUS=2 4059=1 4060=STATICS")
            tcl_commands.append(
                f"*attributeupdateentity loadsteps {load_step_id} 4145 1 1 0 loadcols {spc_loadCollector_id}")
            tcl_commands.append(
                f"*attributeupdateentity loadsteps {load_step_id} 4147 1 1 0 loadcols {load_loadCollector_id}")
            tcl_commands.append(
                f"*attributeupdateint loadsteps {load_step_id} 3800 1 1 0 0")
            tcl_commands.append(
                f"*attributeupdateint loadsteps {load_step_id} 707 1 1 0 0")
            tcl_commands.append(
                f"*attributeupdateint loadsteps {load_step_id} 2396 1 1 0 0")
            tcl_commands.append(
                f"*attributeupdateint loadsteps {load_step_id} 8134 1 1 0 0")
            tcl_commands.append(
                f"*attributeupdateint loadsteps {load_step_id} 2160 1 1 0 0")
            tcl_commands.append(
                f"*attributeupdateint loadsteps {load_step_id} 10212 1 1 0 0")
