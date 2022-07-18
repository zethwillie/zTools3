import os, sys
import maya.mel as mel
import maya.cmds as cmds

# MAKE THIS TAKE A LIST!! OR OVERRIDE STRING IF WE WANT THAT OPTION
def add_maya_script_paths(pathList=None, *args):
    """
    adds given path to MAYA_SCRIPT_PATH temp variable in maya session
    """
    scriptPathList = get_maya_script_path_list()
    for path in pathList:
        if path not in scriptPathList:
            scriptPathList.append(path)

    newScripts = ";".join(scriptPathList)
    os.putenv('MAYA_SCRIPT_PATH', newScripts)
    mel.eval("rehash;")

#BELOW WONT' WORK!
def get_current_script_dir(*args):
    currDir = os.path.dirname(os.path.abspath(__file__))
    # won't this just give us the current script (zbw_pipe)?
    return(currDir)

#BELOW WON'T WORK!
def get_current_script_full_path(*args):
    currScript = os.path.abspath(__file__)
    # won't this just give us the current script (zbw_pipe)?
    return(currScript)


def get_maya_script_path_list(*args):
    """
    returns the list of maya's script paths
    """
    scriptPathList = [x for x in os.environ["MAYA_SCRIPT_PATH"].split(";")]
    return(scriptPathList)