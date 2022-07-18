import maya.cmds as cmds
import random
from functools import partial

widgets = {}

def spaceMatchUI():
    if (cmds.window("spaceMatchWin", exists=True)):
        cmds.deleteUI("spaceMatchWin", window=True)
    #create window
    widgets["window"] = cmds.window("spaceMatchWin", title="Space Matcher", w=250, h=300)

    #create top frame
    widgets["topFrame"] = cmds.frameLayout(l="Object/Attr Selection", w=250, li=70, bgc=(0,0,0))
    widgets["objCLO"] = cmds.columnLayout()

    #create top controls
    widgets["objTFG"] = cmds.textFieldGrp(l="Selected Obj", cw=([1,70],[2,175]), cal=([1,"left"], [2,"left"]), cc=clearList)
    widgets["matchObjButton"] = cmds.button(l="Select Control Object", w=250, bgc=(.8,.8,.8), c = getObj)

#   #or we could assume the obj has a "follow" enum attr. . . .
#     widgets["attrTFG"] = cmds.textFieldGrp(l="Selected Attr", cw=([1,70],[2,175]), cal=([1,"left"], [2,"left"]), cc=clearList)
#     widgets["matchObjButton"] = cmds.button(l="Select Spaces Enum Attr", w=250, bgc=(.8,.8,.8), c = getAttr)

    #back to window
    cmds.setParent(widgets["window"])

    #create bottom frmae
    widgets["bottomFrame"] = cmds.frameLayout(l="Spaces", li=100, w=250, bgc=(0,0,0))
    widgets["bottomRCLO"] = cmds.rowColumnLayout(nc=2, w=250)

    #get obj and put it in
    sel = cmds.ls(sl=True)
    if (len(sel)) == 1:
        getObj()

    #show window
    cmds.showWindow(widgets["window"])
    cmds.window(widgets["window"], e=True, w=250, h=300)

def clearList(*args):
    #get rid of all children of the lower frame layout
    #or
    #delete the rcLayout
    cmds.deleteUI(widgets["bottomRCLO"])
    widgets["bottomRCLO"] = cmds.rowColumnLayout(nc=2, w=250, p=widgets["bottomFrame"])

def switchMatchSpace(index, *args):
    #get the obj and attr
    obj = cmds.textFieldGrp(widgets["objTFG"], q=True, tx=True)
    #print("switchMatch obj val :%s"%obj)
    attr = "%s.follow"%obj


    #get the space value that was selected? why?

    #get the existing ws xform values of obj
    ws1Pos = cmds.xform(obj, q=True, ws=True, t=True)
    ws1Rot = cmds.xform(obj, q=True, ws=True, ro=True)

    #(maybe also key it a frame before at previous value?)
    #set and key the switch
    cmds.setAttr("%s.follow"%obj, index)

    #-------------setKey here?
    #set the old ws xform of obj
    ws2Pos = cmds.xform(obj, ws=True, t=ws1Pos)
    ws2Rot = cmds.xform(obj, ws=True, ro=ws1Rot)
    print(("changed space of %s to index %s"%(obj,index)))

    #set and key the space

    pass

def getObj(*args):
    #get selection and put it in the widgets["objTFG"]
    clearList()
    sel = cmds.ls(sl=True, type="transform")
    if (sel and (len(sel)==1)):
        cmds.textFieldGrp(widgets["objTFG"], e=True, tx=sel[0])
    else:
        cmds.warning("you must select one object with the \"follow\" attribute")

    #------------maybe add attr onto end of obj text, then you don't have to get it later if you needed to ???

    #now create a button for each value in the "follow" attr
    #channels = cmds.channelBox ('mainChannelBox', query=True, selectedMainAttributes=True)
    enumValueStr = cmds.attributeQuery("follow", node=sel[0], listEnum=True)[0]
    values = enumValueStr.split(":")

    for i in range(0,len(values)):
        #pick a random color?
        r = random.uniform(0.5,1)
        g = random.uniform(0.5,1)
        b = random.uniform(0.5,1)
        color = (r, g, b)

        #here create the button
        cmds.button(l=values[i], w=125, p=widgets["bottomRCLO"], bgc=color, h=50, c=partial(switchMatchSpace, i))

def getAttr(*args):
    #get selected attr and put it in the widgets["attrTFG"]
    #or we could assume that the selected obj needs to have a "follow" enum attr
    pass

def spaceMatch():
    """launches the spaceMatchUI"""
    spaceMatchUI()