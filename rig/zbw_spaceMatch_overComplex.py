import maya.cmds as cmds
import maya.OpenMaya as om
import math
from functools import partial

widgets = {}

def spaceMatchUI():
    if (cmds.window("spaceMatchWin", exists=True)):
        cmds.deleteUI("spaceMatchWin", window=True)

    widgets["window"] = cmds.window("spaceMatchWin", title="Space Matcher", w=250, h=300)
    widgets["mainLO"] = cmds.columnLayout()
    widgets["tabLO"] = cmds.tabLayout()
    widgets["getObjCLO"] = cmds.columnLayout()
    widgets["instruct"] = cmds.text("get obj, then attr, then space then do it")
    cmds.separator(h=10)

    #----------fill with selection automatically?
    widgets["objTFG"] = cmds.textFieldGrp(l="select obj", cw=([1,50],[2,150],[3,50]), cal=([1,"left"], [2,"left"],[3,"left"]), cc=clearList)
    widgets["matchObjButton"] = cmds.button(l="select object", c=partial(getObj, widgets["objTFG"]))
    cmds.separator(h=10)
    #-----------maybe here have it catch the selected obj by default
    #-----------and/or have a field for the attribute (default to "follow")
    widgets["getAttrButton"] = cmds.button(w=250, al="center", h=20, l="select enum space attr from obj", bgc= (.5, .5, 0), c=getAttr)
    #-----------when the attr is selected list the attrs automagically,
    widgets["spacesTSL"] = cmds.textScrollList(w=250, h=200, nr=8, ams=False, bgc=(.2, .2, .2))
    widgets["matchButton"] = cmds.button(w=250, al="center", h=40, bgc= (0,.5,0), l="space switch/match", c= doSpaceMatch)

    #tab for creation/setup of matching
    cmds.setParent(widgets["tabLO"])
    #----------in this tab, create frames. One (closable) to create constraint and fill items, check boxes for orient, position (with user selecting objects), one frame (maybe already filled out) (always open) for setting up attrs (message, strings)
    widgets["setupCLO"] = cmds.columnLayout()
    #frame layout for creating the constraints
    widgets["createFrameLO"] = cmds.frameLayout(l="create Constrants", collapsable=True, w=250)
    cmds.text("have em select for constraint")
    widgets["posRotCBG"] = cmds.checkBoxGrp(ncb=2, l1="translation", v1=True, l2="rotation", v2=True)
    #----------this button should just create the constraints on the objects in question, but then fill in what parts of the lower half it can
    widgets["createSetupButton"] = cmds.button(l="create constraints")

    cmds.setParent(widgets["setupCLO"])

    #frameLayout for setting up the attrs
    widgets["setupFrameLO"] = cmds.frameLayout(l="setup matching", collapsable=False, w=250, h=250)
    widgets["setupObjTFG"] = cmds.textFieldGrp(l="select ctrl obj", cw=([1,100],[2,150]), cal=([1,"left"], [2,"left"]))
    widgets["setupObjButton"] = cmds.button(l="get ctrl object", h=40, c= partial(getObj, widgets["setupObjTFG"]))

    widgets["setupConstrTFG"] = cmds.textFieldGrp(l="constraint", cw=([1,100],[2,150]), cal=([1,"left"], [2,"left"]))
    widgets["setupConstrButton"] = cmds.button(l="get constraint", h=40, c= partial(getObj, widgets["setupConstrTFG"]))

    #create list of attrs on constraint
    #attr = cmds.listAttr(sel,ud=True )
    #create list of spaces on obj attr

    cmds.tabLayout(widgets["tabLO"], e=True, tabLabel = ((widgets["getObjCLO"], "change spaces"),(widgets["setupCLO"], "setup matching")))

    cmds.showWindow(widgets["window"])
    cmds.window(widgets["window"], e=True, w=250, h=300)

def doSpaceMatch(*args):

    #check for correct attrs
    obj = cmds.textFieldButtonGrp(widgets["objTFG"], q=True, tx=True)


   #look for message attr re: constraint
    if (cmds.attributeQuery("spaceConstraint", node=obj, exists=True)):
        constraint = cmds.listConnections("%s.spaceConstraint"%obj)
    else:
        cmds.warning("this object has no \"spaceConstraint\" message attribute and thus is not set up for this matching")

    #----------look for string attributes for weights of constraints



    #get ws pos of obj before
    ws1Pos = cmds.xform(obj, q=True, ws=True, t=True)
    ws1Rot = cmds.xform(obj, q=True, ws=True, ro=True)

    #pull the constraint info from the message and string attrs
    #attr = cmds.listAttr(sel,ud=True )

    #-----------here just key the space value!!!
    #switch the spaces, set up "cases", i.e. if world, then set all to 0 except world, etc
    cmds.setAttr("group1_parentConstraint1.pCube1W0", 0)
    cmds.setAttr("group1_parentConstraint1.pCube2W1", 1)

    #set ws pos, rot of obj after
    cmds.xform(obj, ws=True, t=ws1Pos)
    cmds.xform(obj, ws=True, ro=ws1Rot)

    #add in scriptjob?

    #-----------try this
    #set up constraints as normal, maybe DO NOT have to moniter them specifically, set them up as SDKs
    #constraint goes in as message mapped "spaceConstraint"
    #create string attrs for constraint, each space attrname = space , attrVal = constraintAttr(ie. nameW1)
    #Create one tab to set it up
    #creat one tab to do it - get spaces

def setUpSpaceMatch(*args):
    """sets up the space matching attrs on the object"""
    #set up message attr on obj called "spaceConstraint"

    #set up string attrs on obj with name:value of (space:constraintWeightAttr)

    #create a textScrollList for each one of the constraint attrs and for each of the space attrs. no multi select. Then when one is selected, check to see if one in the other is selected. put the connections into a new layout with w 2 columns.
    #when you click "doit" button, it'll grab the space, then the attr and create the string attr on obj
    pass

def clearList(*args):
    """clears out the spaces list"""
    print("cleared the list")

    cmds.textScrollList(widgets["spacesTSL"], e=True, ra=True)

def getObj(tfg, *args):
    """gets selected obj and adds it to the text field"""
    sel = cmds.ls(sl=True, type="transform", l=True)
    if (len(sel)) == 1:
        cmds.textFieldGrp(tfg, e=True, tx=sel[0])
        #--------if layout == the space switch text grp
        clearList()
    else:
        cmds.warning("yo. Select one object as your space switch control")

def getAttr(*args):
    """grabs the selected channel from the selected obj and puts the enum values into the list"""
    #--------here could require a channel of a specific name, then you could do it automagically (check for "follow", "spaces", "space", "ss", etc)
    obj = cmds.textFieldGrp(widgets["objTFG"], q=True, tx=True)
    cmds.select(obj, r=True)
    channels = cmds.channelBox ('mainChannelBox', query=True, selectedMainAttributes=True)
    # print channels
    if (channels and (len(channels)==1)):
        if (cmds.attributeQuery(channels[0], node=obj, enum=True)):
            enumValue = cmds.attributeQuery(channels[0], node=obj, listEnum=True)
            values = enumValue[0].split(":")
            for value in values:
                cmds.textScrollList(widgets["spacesTSL"], e=True, append=value)
                #----------create a button for each one???
                #----------or have them be double clicked???
    else:
        cmds.warning("select only the enum space switch channel")

def spaceMatch():
    """launches the spaceMatchUI"""
    spaceMatchUI()