########################
#file: zbw_huddle.py
#Author: zeth willie
#Contact: zeth@catbuks.com, www.williework.blogspot.com
#Date Modified: 07/27/17
#To Use: type in python window  "import zbw_huddle as hud; hud.huddle()"
#Notes/Descriptions:  Allows you to pick a pivot and the scale things closer to that, BUT not acutally scaling, but scaling the distance from that point
########################

import maya.cmds as cmds
import maya.OpenMaya as om

widgets = {}

def huddleUI(*args):
    if cmds.window("hudWin", exists=True):
        cmds.deleteUI("hudWin")

    widgets["win"] = cmds.window("hudWin", t="zbw_huddle", w=350, h=100, rtf=True)
    widgets["CLO"] = cmds.columnLayout()
    widgets["slider"] = cmds.floatSliderGrp(min=0, max=2, f=True, label="Factor:", cal=([1, "left"], [2,"left"], [3,
                                                                                                                  "left"]), cw=([1,50],[2,50],[3,225]), pre=3, v=1.0)
    cmds.separator(h=20)
    widgets["button"] = cmds.button(l="Move objects aroudnd first selected", w=350, h=30, bgc=(.6,.8, .6), c=huddleExec)

    cmds.window(widgets["win"], e=True, w=5, h=5, rtf=True)
    cmds.showWindow(widgets["win"])


def huddleExec(*args):
    """
    from first selection, moves the next selected objects closer or farther from first selection based on slider values (as a percentage)
    """
    factor = cmds.floatSliderGrp(widgets["slider"], q=True, v=True)
    sel = cmds.ls(sl=True, type="transform")
    center = sel[0]
    objs = sel[1:]

    centerPos = cmds.xform(center, q=True, ws=True, rp=True)
    centerVec = om.MVector(centerPos[0], centerPos[1], centerPos[2])
    for obj in objs:
        objPos = cmds.xform(obj, ws=True, q=True, rp=True)
        objVec = om.MVector(objPos[0], objPos[1], objPos[2])
        diffVec = objVec-centerVec
        scaledVec = diffVec * factor
        newVec = scaledVec + centerVec
        cmds.xform(obj, ws=True, t=(newVec[0], newVec[1], newVec[2]))

def huddle(*args):
    """Use this to start the script!"""
    huddleUI()