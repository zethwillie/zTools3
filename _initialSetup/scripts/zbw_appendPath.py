########################
#file: zbw_appendPath.py
#Author: zeth willie
#Contact: zethwillie@gmail.com, www.williework.blogspot.com
#Date Modified: 04/27/13
#To Use: type in python window  "import zbw_appendPath as zap; zap.appendPath()"
#Notes/Descriptions: use to add paths to the python path attribute, which allows you to import scripts from additional locations on your computer/network
########################

import sys, os
import maya.cmds as cmds
import maya.mel as mel
from functools import partial

widgets = {}

def appendUI():
    """UI for appendPath script"""

    #create window with 3 text fields, buttons call up proc to add path
    if cmds.window("appendPath", exists=True):
        cmds.deleteUI("appendPath")

    widgets["win"] = cmds.window("appendPath", t="zbw_appendPath", w=500, h=5, s=False, rtf=True)

    #create some menus for saving and loading
    cmds.setParent(widgets["win"])
    widgets["menu"] = cmds.menuBarLayout()
    widgets["menuFile"] = cmds.menu(label="file")
    cmds.menuItem(l='Clear Values', c=clearValues)
    cmds.menuItem(l="Save Add Paths", c=saveValues)
    cmds.menuItem(l="Load Add Paths", c=loadValues)

    widgets["tabLO"] = cmds.tabLayout(h=210)
    widgets["columnLO"] = cmds.columnLayout("Add Paths", w=500)
    widgets["path1"] = cmds.textFieldButtonGrp(l="path1", cal=[(1, "left"), (2,"left"),(3,"left")], cw3=(40, 410, 50), bl="<<<", bc=partial(addToField, 1))
    widgets["path2"] = cmds.textFieldButtonGrp(l="path2", cal=[(1, "left"), (2,"left"),(3,"left")], cw3=(40, 410, 50), bl="<<<", bc=partial(addToField, 2))
    widgets["path3"] = cmds.textFieldButtonGrp(l="path3", cal=[(1, "left"), (2,"left"),(3,"left")], cw3=(40, 410, 50), bl="<<<", bc=partial(addToField, 3))
    widgets["melCBG"] = cmds.checkBoxGrp(ncb=1, l1="also add to mel path (MAYA_SCRIPT_PATH)", v1=1, cal=[(1, "left"), (2,
                                                                                                                 "left")], cw = [(1, 100), (2,25)])
    cmds.separator(h=10, st="single")

    widgets["buttonRCL"] = cmds.rowColumnLayout(nc=3, w=500, cw=[(1,123),(2,247 ),(3,123)])
    widgets["addCloseBut"] = cmds.button(l="Add and Close", w=120, h=30, bgc=(.6, .8, .6), c=applyClose)
    widgets["addBut"] = cmds.button(l="Add Paths!", w=245, h=30, bgc=(.8, .8, .6), c=apply)
    widgets["closeBut"] = cmds.button(l="Close", w=120, h=30, bgc=(.8,.6,.6), c=close)

    cmds.setParent(widgets["columnLO"])
    cmds.separator(h=5, style="single")

    cmds.text("Click the '<<<' buttons to browse for paths to add. Click the 'Add' button to add those \npaths to the 'sys.path' list. Use the 'ViewPath' tab to view current list of paths.", al="center")
    cmds.text("Use 'file->save' to save the selected paths. Use 'file->load' to load previously saved paths")

    #back to window
    cmds.setParent(widgets["tabLO"])
    widgets["columnLO2"] = cmds.columnLayout("View Paths", w=500)
    cmds.text("Double-click to display full path in script editor")
    widgets["listTSL"] = cmds.textScrollList(w=500, h=120, fn="smallPlainLabelFont", append=["click button below",
                                                                                           "to refresh this list!"], dcc=printMe)
    refresh()
    cmds.separator(h=5, style="single")

    widgets["columnLO3"] = cmds.columnLayout(w=500)
    widgets["refreshBut"] = cmds.button(l="Refresh Paths", w=500, h=20, bgc=(.5, .5, .6), c=refresh)

    cmds.rowColumnLayout(nc=3, cw=[(1,200),(2,150 ),(3,150)])
    widgets["removeBut"] = cmds.button(l="Remove Selected", w=180,  h=20, bgc=(.7, .5, .5), c=removePath)
    widgets["topBut"] = cmds.button(l="Selected To Top", w=130, h=20, bgc=(.7, .5, .5), c=topPath)
    widgets["bottomBut"] = cmds.button(l="Selected To Bottom", w=130, h=20, bgc=(.7, .5, .5), c=bottomPath)

    #load (and check) previous saves


    cmds.showWindow(widgets["win"])
    cmds.window(widgets["win"], e=True, w=5, h=5, rtf=True)

def apply(*args):
    append()

def applyClose(*args):
    apply()
    close()

def close(*args):
    cmds.deleteUI("appendPath")

def bottomPath(*args):
    """function to move path of selected index to the bottom of the list"""
    #get the selection index from the TSL
    indexRaw = cmds.textScrollList(widgets["listTSL"], q=True, sii=True)
    if indexRaw:
        index = indexRaw[0]-1
        dropped = sys.path.pop(index)
        sys.path.append(dropped)
        refresh()
        print(("Moved '%s' to bottom of list"%sys.path[0]))
    else:
        cmds.warning("You need to select an entry on the path list to move it to the bottom")

def topPath(*args):
    """function to move the selected index item to the top of the path list"""
    #get the selection index from the TSL
    indexRaw = cmds.textScrollList(widgets["listTSL"], q=True, sii=True)
    if indexRaw:
        index = indexRaw[0]-1
        sys.path[0:0] = [sys.path.pop(index)]
        refresh()
        print(("Moved '%s' to top of list"%sys.path[0]))
    else:
        cmds.warning("You need to select an entry on the path list to move it to the top")

def removePath(*args):
    """removes the path from sys.path"""
    #get the selection index from the TSL
    indexRaw = cmds.textScrollList(widgets["listTSL"], q=True, sii=True)
    if indexRaw:
        index = indexRaw[0]-1
        dropped = sys.path.pop(index)
        refresh()
        print(("Removed '%s' from sys.path"%dropped))
    else:
        cmds.warning("You need to select an entry on the path list to remove it")

def addToField(num, *args):
    """calls a file dialog to get a path and adds it to the selected field"""
    #set the field to add to
    textField  = widgets["path%s"%num]

    #call up browser to look for paths
    path = cmds.fileDialog2(fm=3)[0]

    #add text
    if path:
        cmds.textFieldButtonGrp(textField, e=True, tx=path)


def printMe():
    """prints the path from the list"""

    #get text at selected index
    sel = cmds.textScrollList(widgets["listTSL"], q=True, si=True)

    #print that text to script editor
    print((sel[0]))

def append(*args):
    paths = []
    melChk = cmds.checkBoxGrp(widgets["melCBG"], q=True, v1=True)

    #get paths
    path1 = cmds.textFieldButtonGrp(widgets["path1"], q=True, tx=True)
    path2 = cmds.textFieldButtonGrp(widgets["path2"], q=True, tx=True)
    path3 = cmds.textFieldButtonGrp(widgets["path3"], q=True, tx=True)
    paths.append(path1)
    paths.append(path2)
    paths.append(path3)

    #append path with text from fields
    check = 0
    for path in paths:
        if path:
            if os.path.isdir(path):
                if path in sys.path:
                    cmds.warning("'%s' is already in sys.path. Skipping!"%path)
                else:
                    sys.path.append(path)
                    check += 1
            else:
                cmds.warning("%s is not an existing path and wasn't added to sys.path"%path)
    if check > 0:
        cmds.warning("Added paths! Check the 'View Paths' tab to see them")

    if melChk:
        # do the mel script path adding
        scriptPathList = [x for x in os.environ["MAYA_SCRIPT_PATH"].split(";")]
        for path in paths:
            if path not in scriptPathList:
                scriptPathList.append(path)
        newScriptPathList = ";".join(scriptPathList)
        os.putenv('MAYA_SCRIPT_PATH', newScriptPathList)
        mel.eval("rehash;")

    #delete the text
    cmds.textFieldButtonGrp(widgets["path1"], e=True, tx="")
    cmds.textFieldButtonGrp(widgets["path2"], e=True, tx="")
    cmds.textFieldButtonGrp(widgets["path3"], e=True, tx="")

    #refresh the path list on second tab
    refresh()

def refresh(*args):
    """refreshes the list of the paths"""

    #delete anything in the list
    cmds.textScrollList(widgets["listTSL"], edit=True, ra=True)

    #get the sys.path
    pathList = sys.path

    #add each element to list
    for path in pathList:
        cmds.textScrollList(widgets["listTSL"], edit=True, append=[path])

def clearValues(*args):
    """clears the text fields"""

    cmds.textFieldButtonGrp(widgets["path1"], e=True, tx="")
    cmds.textFieldButtonGrp(widgets["path2"], e=True, tx="")
    cmds.textFieldButtonGrp(widgets["path3"], e=True, tx="")

def loadValues(*args):
    """loads the saved path file, if there is one"""
    #check if file exists
    try:
        userDir = cmds.internalVar(upd=True) + "zbw_appendPathSave.txt"
        file = open(userDir, "r")
        paths = []
        #read values from file to list
        for line in file:
            paths.append(line.rstrip("\n"))
        file.close()

        #replace tfbg's with those values
        cmds.textFieldButtonGrp(widgets["path1"], e=True, tx=paths[0])
        cmds.textFieldButtonGrp(widgets["path2"], e=True, tx=paths[1])
        cmds.textFieldButtonGrp(widgets["path3"], e=True, tx=paths[2])
    except IOError:
        cmds.warning("You don't seem to have a 'zbw_appendPathSave.txt' file saved in your user prefs dir")

def saveValues(*args):
    """saves the current path fields to a file in your user pref directory. Files is called 'zbw_appendPath.txt'"""

    path1 = cmds.textFieldButtonGrp(widgets["path1"], q=True, tx=True) + "\n"
    path2 = cmds.textFieldButtonGrp(widgets["path2"], q=True, tx=True) + "\n"
    path3 = cmds.textFieldButtonGrp(widgets["path3"], q=True, tx=True) + "\n"

    #write to file
    userDir = cmds.internalVar(upd=True) + "zbw_appendPathSave.txt"
    file = open(userDir, "w")

    file.write(path1)
    file.write(path2)
    file.write(path3)

    file.close()

def appendPath(*args):
    """Use this to start the script!"""

    appendUI()