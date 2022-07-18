import maya.cmds as cmds
import maya.mel as mel
import os
import sys
import json

#create a window
widgets = {}

#get dictionary from json file in user prefs(beter location?)
#make this a function that gets called when you get scripts. . . 
prefDir = cmds.internalVar(upd = True)

with open(os.path.join(prefDir, "zbw_scriptListKeys.json"), "r") as f:
    pythonRun = json.load(f)
#######


def getScriptsUI(*args):
    
    if cmds.window("thisWin", exists = True):
        cmds.deleteUI("thisWin")
    
    widgets["win"] = cmds.window("thisWin", w=300, h=200)
    widgets["mainFLO"] = cmds.formLayout()
    
    widgets["list"] = cmds.textScrollList(nr=10, w=300, dcc = executeCommand)
       
    cmds.formLayout(widgets["mainFLO"], e=1, af = [(widgets["list"], "left", 0), (widgets["list"], "top", 0), (widgets["list"], "bottom", 30), (widgets["list"], "right", 0)])

    widgets["button"] = cmds.button(l="Refresh List!", w=300, h= 30, bgc = (.8, .6, .3), c= getScripts)
    cmds.formLayout(widgets["mainFLO"], e=1, af = [(widgets["button"], "left", 0), (widgets["button"], "right", 0), (widgets["button"], "bottom", 0)])
    
    cmds.showWindow(widgets["win"])

#populate the list with the contents of the path
def getScripts(*args):
    
    #### here we should search all possible places, create a separate tab for each location (folder name?)
    
    #get the script path
    usd = cmds.internalVar(usd=True)
    #print usd
    #get list of files there
    fls = os.listdir(usd)
    fls.sort()
    
########### check whether the thing is a folder or not, should really just sort for .mel and .py, not exclude as I'm doing
########### sort files (by name)
    counter = 1
    for fl in fls:
        #print fl
        if (fl.rpartition(".")[2] != "pyc") and (fl[-1] != "~"):
            #if not in our dictionary, color it red
            if (fl.rpartition(".")[0] in pythonRun):
                cmds.textScrollList(widgets["list"], e=True, a=fl, lf = (counter, "boldLabelFont"))

            elif (fl.rpartition(".")[2] == "mel"): 
                cmds.textScrollList(widgets["list"], e=True, a=fl, lf = (counter, "boldLabelFont"))

            else:
                #print "%s doesn't have its' shit together"%fl
                cmds.textScrollList(widgets["list"], e=True, a=fl, lf = (counter, "smallObliqueLabelFont"))

            counter +=1 


def executeCommand(*args):
    item = cmds.textScrollList(widgets["list"], q=True, si=True)[0]
    #### here we should reference a dictionary of scriptName: code to execute script
    #### load our file from userprefs(?)
    
    # with open("/Bluearc/HOME/CHRLX/zwillie/Desktop/jsonTest.json" ,"w") as f:
    # json.dump(animals, f, sort_keys = True, indent=4)
    
    # with open("/Bluearc/HOME/CHRLX/zwillie/Desktop/jsonTest.json", "r") as f:
    #     data  = json.load(f)

    #if there is an item or items that AREN'T in the dictionary as keys, throw a warning and ask for the correct input--
    #separate function to add stuff to our dictionary and save it
    #BETTER - color code the item in the list as red and when clicked, bring up a window to enter the call for the script (and add to dict and save)

    #if the key exists (aka the script name), then execute the code (value) next to it

    #print out in the script editor (warning) which command your trying to run.
    #catch key errors - i.e. this script:command pair isn't registered in the fileName.json

    if (item.rpartition(".")[2] == "mel"):
        mel.eval(item.rpartition(".")[0])
        
    elif (item.rpartition(".")[2] == "py"):
        exec(pythonRun[item.rpartition(".")[0]])
    
def scriptList(*args):
    getScriptsUI()
    

