from typing import List
import os


class HypermeshStarter:

    ALTAIR_HOME = os.environ["ProgramFiles"]+"\\Altair\\2021.2"
    PATH_HYPERMESH = ALTAIR_HOME+"\\hwdesktop\\hm\\bin\\win64\\hmopengl.exe"

    def initialize_tcl_commands() -> List:
        tcl_commands = []
        return tcl_commands

    def runHyperMesh(self, scriptPath, batch=False, wait=False, hidden=False):
        import subprocess

        # Hide Output of the shell - relax!
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        if (hidden):
            startupinfo.wShowWindow = subprocess.SW_HIDE

        scriptPath = scriptPath.replace("\\", "/")
        # print(scriptPath)
        if(batch):
            process = subprocess.Popen(
                [self.PATH_HYPERMESH, "-clientconfig", "hwfepre.dat", "-uOptiStruct", "-b", "-tcl", scriptPath], startupinfo=startupinfo)

        else:
            process = subprocess.Popen(
                [self.PATH_HYPERMESH,  "-tcl", scriptPath],  startupinfo=startupinfo)

        if (wait):
            process.wait()
