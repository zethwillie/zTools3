import sys
import maya.cmds as cmds
import os
 

widgets = {}

def findScriptUI(*args):
    
    if cmds.window("findScript", exists = True):
        cmds.deleteUI("findScript")
    
    widgets["win"] = cmds.window("findScript", t="zbw_findPath", w=300, h=200)
    widgets["mainCLO"] = cmds.columnLayout()
    
    cmds.separator(h=10)
    widgets["textTx"] = cmds.text(l="Will search your active python paths. \nNo need for suffix (.py or .mel)\nNo wildcards(*). Just string, 3 chars min", al="left")
    cmds.separator(h=20)
    widgets["nameTFG"] = cmds.textFieldGrp(l="search for:", cw = [(1, 75), (2,200)], cal = [(1, "left"),(2, "right")])
    cmds.separator(h=20)
    widgets["searchBut"] = cmds.button(l="Search python paths!", w=300, h=50, bgc=(0,.6, 0), c=searchPaths)
    cmds.separator(h=20)

    widgets["resultTxt"] = cmds.textFieldGrp(l="results:", ed=False, w=300, cw = [(1, 75), (2,200)], bgc = (0,0,0) , cal = [(1, "left"),(2, "right")])
    
    cmds.showWindow(widgets["win"])

def searchPaths(*args):
    
    scriptName = cmds.textFieldGrp(widgets["nameTFG"], q=True, tx=True)
    pathList = []
    nameList = []
    
    trimmed = scriptName.partition(".")[0]
    if len(trimmed)>2:
        try:     
            paths = sys.path
            for myPath in paths:
                contents = os.walk(myPath)
                for dir in contents:
                    path = dir[0]
                    folders = dir[1]
                    files = dir[2]
                    for fl in files:
                        if trimmed in fl: 
                            #print fl + "========>" + path
                            nameList.append(fl)
                            pathList.append(path)
        except: 
            pass
            #cmds.warning("couldn't get into %s"%pth)
    
        if pathList:
            cmds.textFieldGrp(widgets["resultTxt"], e=True, tx = "results found! Check script editor!")
        else:
            cmds.textFieldGrp(widgets["resultTxt"], e=True, tx = "no results found!")
            
        print(("\nfound %s in the following directories:"%trimmed))
        for x in range(0, len(pathList)):
            print(("%s  =======>>>  %s"%(nameList[x],pathList[x])))
         
    else:
        cmds.textFieldGrp(widgets["resultTxt"], e=True, tx = "more than 3 letters, please!")         
         
def findScript(*args):
    findScriptUI()