########################
#file: zbw_transformBuffer.py
#Author: zeth willie
#Contact: zethwillie@gmail.com, www.williework.blogspot.com
#Date Modified: 1/20/17
#To Use: type in python window  "zbw_transformBuffer.transformBuffer()"
#Notes/Descriptions: script to just buffer(catch) the transform vals of an object. Then push them back to some selected geo
########################

import maya.cmds as cmds

widgets = {}

def transformBufferUI(*args):
    if cmds.window("tbWin", exists=True):
        cmds.deleteUI("tbWin")
    
    widgets["win"] = cmds.window("tbWin", t="zbw_tranformBuffer", s=False, w=200)
    widgets["mainCLO"] = cmds.columnLayout(w=200)

######## ------ checkbox to enable/disable these. . . .

    widgets["trnFFG"] = cmds.floatFieldGrp(l="Trns: ", nf=3, cw=[(1, 40), (2, 50), (3, 50), (4,50)], cal = [(1, "left"), (2, "left"), (3, "left"), (4,"left")])
    widgets["rotFFG"] = cmds.floatFieldGrp(l="Rot: ", nf=3, cw=[(1, 40), (2, 50), (3, 50), (4,50)], cal = [(1, "left"), (2, "left"), (3, "left"), (4,"left")])
    widgets["sclFFG"] = cmds.floatFieldGrp(l="Scl: ", nf=3, cw=[(1,40), (2, 50), (3, 50), (4,50)],cal = [(1, "left"), (2, "left"), (3, "left"), (4,"left")])
    cmds.separator(h=10)
    widgets["transCBG"] = cmds.checkBoxGrp(ncb=3, la3 = ("Trns", "Rot", "Scl"), va3=(1, 1, 1), cal=[(1, "left"), (2, "left"), (3, "left")], cw = [(1, 50), (2, 50), (3, 50)])
    cmds.separator(h=10)
    widgets["butFLO"] = cmds.formLayout(w=200, h=50)
    widgets["getBut"] = cmds.button(l="Catch\nValues", bgc = (.8, .5, .5), h=50, w=100, c=getValues)
    widgets["setBut"] = cmds.button(l="Set\nValues", bgc = (.5, .8,.5), h=50, w=100, c=setValues)

    cmds.formLayout(widgets["butFLO"], e=True, af = [
        (widgets["getBut"], "top", 0),
        (widgets["getBut"], "left", 0),
        (widgets["setBut"], "top", 0),
        (widgets["setBut"], "left", 100)
        ])
    cmds.window(widgets["win"], e=True, w=200, h=100)
    cmds.showWindow(widgets["win"])
    
def getValues(*args):
    """gets the values for the appropriate channels from first selected obj"""
    
    cmds.floatFieldGrp(widgets["trnFFG"], e=True, v = (0.0,0.0,0.0,0.0))
    cmds.floatFieldGrp(widgets["rotFFG"], e=True, v = (0.0,0.0,0.0,0.0))
    cmds.floatFieldGrp(widgets["sclFFG"], e=True, v = (1.0,1.0,1.0,1.0))

    obj = ""

    attrs = cmds.checkBoxGrp(widgets["transCBG"], q=True, va3=True)
    trans = attrs[0]
    rots = attrs[1]
    scls = attrs[2]

    sel = cmds.ls(sl=True)
    if sel:
        obj = sel[0]
        if cmds.objectType(obj)=="transform":
            t = cmds.getAttr("{}.translate".format(obj))[0]
            cmds.floatFieldGrp(widgets["trnFFG"], e=True, v1 = t[0])
            cmds.floatFieldGrp(widgets["trnFFG"], e=True, v2 = t[1])
            cmds.floatFieldGrp(widgets["trnFFG"], e=True, v3 = t[2])
            r = cmds.getAttr("{}.rotate".format(obj))[0]
            cmds.floatFieldGrp(widgets["rotFFG"], e=True, v1 = r[0])
            cmds.floatFieldGrp(widgets["rotFFG"], e=True, v2 = r[1])
            cmds.floatFieldGrp(widgets["rotFFG"], e=True, v3 = r[2])
            s = cmds.getAttr("{}.scale".format(obj))[0]
            cmds.floatFieldGrp(widgets["sclFFG"], e=True, v1 = s[0])
            cmds.floatFieldGrp(widgets["sclFFG"], e=True, v2 = s[1])
            cmds.floatFieldGrp(widgets["sclFFG"], e=True, v3 = s[2])

        else: 
            cmds.warning("Select an object to catch transforms from")

def setValues(*args):
    """sets the values from window on all selected objs for appropriate channels"""

    sel = cmds.ls(sl=True)

    attrs = cmds.checkBoxGrp(widgets["transCBG"], q=True, va3=True)
    trans = attrs[0]
    rots = attrs[1]
    scls = attrs[2]

    for obj in sel:
        if cmds.objectType(obj)=="transform":
            if trans:
                t = cmds.floatFieldGrp(widgets["trnFFG"], q=True, v=True)
                cmds.setAttr("{}.translate".format(obj), t[0], t[1], t[2])
            if rots:
                r = cmds.floatFieldGrp(widgets["rotFFG"], q=True, v=True)
                cmds.setAttr("{}.rotate".format(obj), r[0],r[1], r[2])
            if scls:
                s = cmds.floatFieldGrp(widgets["sclFFG"], q=True, v=True)
                cmds.setAttr("{}.scale".format(obj), s[0], s[1], s[2])
    
def transformBuffer(*args):
    transformBufferUI(*args)