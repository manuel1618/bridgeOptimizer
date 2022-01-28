import os.path

from BridgeOptimizer.scriptBuilder.HyperWorksStarter import HyperWorksStarter


class ScriptBuilderHyperview:

    tcl_commands = []

    def __init__(self) -> None:
        self.tcl_commands = []

    def write_density_File(self, path_to_des_file: str, path_to_densityFile_out: str):
        """
        Writes a density file with element id, node ids and the contour value.
        More output is possible but not needed for now.
        TODO: Adapt the model creation in this way, that we can differentiate by component id if its an optimization 
        or not an optimization rod - but unsure for now if its even needed at all as the rod id is linked to a rod 
        instance with proper definition if optimization or not
        """
        self.tcl_commands = []
        print("START Density Import")
        self.tcl_commands.append(
            "set outPath \"" + path_to_densityFile_out.replace("\\", "/") + "\"")
        self.tcl_commands.append(
            "set import_file_path \"" + path_to_des_file.replace("\\", "/") + "\"")
        # Setting Animation View
        self.tcl_commands.append("hwi OpenStack")
        self.tcl_commands.append("hwi GetSessionHandle session")
        self.tcl_commands.append("session GetProjectHandle project")
        self.tcl_commands.append("project GetPageHandle page 1")
        self.tcl_commands.append("page GetWindowHandle win 1")
        self.tcl_commands.append("win SetClientType animation")
        # Loading Model
        self.tcl_commands.append("win GetClientHandle anim")
        self.tcl_commands.append("anim AddModel $import_file_path")
        self.tcl_commands.append("anim Draw")
        # #Attatching the Results
        self.tcl_commands.append("anim Clear")
        self.tcl_commands.append("set id [anim AddModel $import_file_path]")
        self.tcl_commands.append("anim GetModelHandle myModel $id")
        self.tcl_commands.append("myModel SetResult $import_file_path")
        self.tcl_commands.append("anim Draw")
        # #Results
        self.tcl_commands.append("myModel GetResultCtrlHandle myResult")
        # LastIteration
        self.tcl_commands.append(
            "set current [myResult GetCurrentSubcase]")
        self.tcl_commands.append(
            "myResult SetCurrentSimulation [expr [myResult GetNumberOfSimulations $current]-1]")
        self.tcl_commands.append(
            "set data_types [myResult GetDataTypeList $current]")
        self.tcl_commands.append("myResult GetContourCtrlHandle myContour")
        self.tcl_commands.append(
            "myContour SetDataType [lindex $data_types 0]")  # Density
        self.tcl_commands.append("myContour SetEnableState true")
        # Query Elements
        self.tcl_commands.append("myModel GetQueryCtrlHandle myQuery")
        self.tcl_commands.append(
            "set set_id [myModel AddSelectionSet element]")
        self.tcl_commands.append(
            "myModel GetSelectionSetHandle elem_set $set_id")
        self.tcl_commands.append("elem_set Add \"all\"")
        self.tcl_commands.append("myQuery SetSelectionSet $set_id")
        self.tcl_commands.append(
            "myQuery SetQuery \"element.id contour.value element.connectivity\"")
        self.tcl_commands.append(
            "myQuery WriteData $outPath")
        self.tcl_commands.append("session ReleaseHandle")
        self.tcl_commands.append("project ReleaseHandle")
        self.tcl_commands.append("page ReleaseHandle")
        self.tcl_commands.append("win ReleaseHandle")
        self.tcl_commands.append("anim ReleaseHandle")
        self.tcl_commands.append("myModel ReleaseHandle")
        self.tcl_commands.append("myQuery ReleaseHandle")
        self.tcl_commands.append("myResult ReleaseHandle")
        self.tcl_commands.append("elem_set ReleaseHandle")
        self.tcl_commands.append("hwi CloseStack")

    def screenshot_element_density(self, path_to_des_file: str, density_threshold: float):
        """
        Hides all elements with lower density than specified and takes a screenshot + screenshot of all elements with density contour
        TODO: Specify output DIR

        """
        self.tcl_commands = []
        print("START Density Import")
        self.tcl_commands.append(
            "set import_file_path \"" + path_to_des_file.replace("\\", "/") + "\"")
        self.tcl_commands.append("set isoValue " + str(density_threshold))
        # Setting Animation View
        self.tcl_commands.append("hwi OpenStack")
        self.tcl_commands.append("hwi GetSessionHandle session")
        self.tcl_commands.append("session GetProjectHandle project")
        self.tcl_commands.append("project GetPageHandle page 1")
        self.tcl_commands.append("page GetWindowHandle win 1")
        self.tcl_commands.append("win SetClientType animation")
        # Loading Model
        self.tcl_commands.append("win GetClientHandle anim")
        self.tcl_commands.append("anim AddModel $import_file_path")
        self.tcl_commands.append("anim Draw")
        # #Attatching the Results
        self.tcl_commands.append("anim Clear")
        self.tcl_commands.append("set id [anim AddModel $import_file_path]")
        self.tcl_commands.append("anim GetModelHandle myModel $id")
        self.tcl_commands.append("myModel SetResult $import_file_path")
        self.tcl_commands.append("anim Draw")
        # #Results
        self.tcl_commands.append("myModel GetResultCtrlHandle myResult")
        # LastIteration
        self.tcl_commands.append(
            "set current [myResult GetCurrentSubcase]")
        self.tcl_commands.append(
            "myResult SetCurrentSimulation [expr [myResult GetNumberOfSimulations $current]-1]")
        self.tcl_commands.append(
            "set data_types [myResult GetDataTypeList $current]")
        self.tcl_commands.append("myResult GetContourCtrlHandle myContour")
        self.tcl_commands.append(
            "myContour SetDataType [lindex $data_types 0]")  # Density
        self.tcl_commands.append("myContour SetEnableState true")
        self.tcl_commands.append("anim Draw")
        # ISO
        self.tcl_commands.append("myResult GetIsoValueCtrlHandle myIso")
        # 1st  screenshot with full elements
        self.tcl_commands.append("win GetViewControlHandle viewctrl_handle")
        self.tcl_commands.append(
            "viewctrl_handle SetViewMatrix \"1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1\"")
        self.tcl_commands.append("viewctrl_handle Fit")
        self.tcl_commands.append("anim Draw")
        self.tcl_commands.append(
            f"session CaptureActiveWindow JPG {os.path.basename(path_to_des_file)}_full.jpg pixels 1024 768")
        self.tcl_commands.append("myIso SetIsoValue $isoValue")
        self.tcl_commands.append("myIso SetEnableState true ")
        self.tcl_commands.append("myIso SetAverageMode None")
        # screenshot
        # self.tcl_commands.append("win GetViewControlHandle viewctrl_handle") # already done above
        self.tcl_commands.append(
            "viewctrl_handle SetViewMatrix \"1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1\"")
        self.tcl_commands.append("viewctrl_handle Fit")
        self.tcl_commands.append("anim Draw")
        self.tcl_commands.append(
            f"session CaptureActiveWindow JPG {os.path.basename(path_to_des_file)}.jpg pixels 1024 768")

        # Manual Release?!
        self.tcl_commands.append("session ReleaseHandle")
        self.tcl_commands.append("project ReleaseHandle")
        self.tcl_commands.append("page ReleaseHandle")
        self.tcl_commands.append("win ReleaseHandle")
        self.tcl_commands.append("anim ReleaseHandle")
        self.tcl_commands.append("myModel ReleaseHandle")
        self.tcl_commands.append("myResult ReleaseHandle")
        self.tcl_commands.append("myContour ReleaseHandle")
        self.tcl_commands.append("myIso ReleaseHandle")
        self.tcl_commands.append("hwi CloseStack")


if __name__ == "__main__":
    """
    Just for testing
    """
    scriptBuilderHyperview = ScriptBuilderHyperview()
    scriptBuilderHyperview.screenshot_element_density(
        r"C:\Users\Manuel\Desktop\test\model_optimization_des.h3d", r"C:\Users\Manuel\Desktop\test", 0.5)
    hyperMeshStarter = HyperWorksStarter(
        r"C:\Users\Manuel\Desktop\test", "model")
    hyperMeshStarter.write_script_hyperview(r"C:\Users\Manuel\Desktop\test",
                                            scriptBuilderHyperview.tcl_commands)
    hyperMeshStarter.runHyperview(batch=True)
