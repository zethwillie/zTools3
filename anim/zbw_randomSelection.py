#randSelection.py

"""keep random percent of things from selection"""
import maya.cmds as cmds
import random

#create UI for rand selection (% to keep int field)
widgets = {}

def randomSelectionUI(*args):
    if cmds.window("win", exists = True):
        cmds.deleteUI("win")

    widgets["win"] = cmds.window("win", w=280, h=75, t="zbw_randomSelection")

    widgets["mainCLO"] = cmds.columnLayout()
    widgets["text"] = cmds.text("What percent of selection do you want to keep?")
    widgets["keepIFG"] = cmds.intFieldGrp(l=" % to keep:", v1=50, h=40, cw = ([1, 65], [2, 50]), cal = ([1,"left"], [2, "left"]))
    widgets["text2"] = cmds.text("Random: each obj has % chance to be removed")
    widgets["text3"] = cmds.text("Precise: exact num removed, but randomly chosen")
    cmds.separator(h=10)
    widgets["typeRBG"] = cmds.radioButtonGrp(l="Type:", l1 = "Random Remove", l2 = "Precise Remove", nrb = 2, sl = 1, cw = ([1, 30], [2,120], [3, 120], [4, 50]), cal = ([1, "left"], [2,"left"], [3, "left"], [4, "left"]))
    widgets["but"] = cmds.button(l="Reselect", w=280, h=40, bgc = (.6, .8, .6), c = doSel)

    cmds.window(widgets["win"], e=True, w=280, h=75)
    cmds.showWindow(widgets["win"])

    
def doSel(*args):
    """pass values from window"""
    #get value from win
    keepNum = cmds.intFieldGrp(widgets["keepIFG"], q=True, v1=True)
    #get type of sel to
    typeNum = cmds.radioButtonGrp(widgets["typeRBG"], q=True, sl=True)
    #pass info to corresponding func
    if typeNum == 1:
        randRemovePercent(keepNum)
    if typeNum == 2:
        preciseRemovePercent(keepNum)

def randRemovePercent(keepNum, *args):
    """gives each object the percentage chance to be removed. So will remove a variable number of objs"""

    sel =  cmds.ls(sl=True, fl=True)

    remNum = (100.0 - keepNum)/100.00
    #print remNum, "remove percent"
    count = 0
    ch = []
    if sel:
        for obj in sel:
            x = random.uniform(0,1)
            if x < (remNum):
                # print x, "--->", remNum
                ch.append(obj)
                count = count + 1

    newSel = [g for g in sel if g not in ch]
    cmds.select(newSel, r=True)
    print(count, "objects removed")

    #print len(sel), "objects remaining"

def preciseRemovePercent(keepNum, *args):
    """selects the exact amount of things to remove and randomly selects which from the selection list"""

    sel = cmds.ls(sl=True, fl=True)

    remNum = (100.0-keepNum)/100.0
    remCount = int(remNum*len(sel))

    count = 0
    ch = []

    if sel:
        while len(ch)<remCount:
            x = random.choice(sel)
            if x not in ch:
                ch.append(x)

    newSel = [g for g in sel if g not in ch]
    cmds.select(newSel, r=True)
    print(len(newSel), "objects remaining")

def randomSelection():
    randomSelectionUI()