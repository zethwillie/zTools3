
########################
# File: zbw_shapeScale.py
# Date Modified: 18 Mar 2017
# creator: Zeth Willie
# Contact: zethwillie@gmail.com, catbuks.com, williework.blogspot.com
# Description: scales an obj at the component level
# To Run: type "import zTools.zbw_shapeScale as zbw_shapeScale; reload(zbw_shapeScale);zbw_shapeScale.zbw_shapeScale()"
########################

import maya.cmds as cmds
import zTools3.rig.zbw_rig as rig

widgets = {}


def shapeScaleUI():
    """
    UI for the script
    """

    if (cmds.window("ssWin", exists=True)):
        cmds.deleteUI("ssWin", window=True)
        # cmds.winPref("shapeScaleWin", remove=True)

    widgets["win"] = cmds.window("ssWin", t="zbw_shapeScale", w=400, h=75, s=False)

    widgets["colLo"] = cmds.columnLayout("mainCLO", w=400, h=75)
    widgets["formLO"] = cmds.formLayout(nd=100, w=400)
    cmds.separator(h=10)
    widgets["slider"] = cmds.floatSliderGrp("slider", f=False, l="Scale", min=0.01, max=2, pre=3, v=1, adj=3,
                                            cal=([1, "left"], [2, "left"], [3, "left"]), cw=([1, 50], [2, 220]),
                                            cc=shapeScaleExecute)
    cmds.separator(h=10)
    widgets["scaleFFG"] = cmds.floatFieldGrp(v1=100, pre=1, l="Scale %", en1=True, w=110, cw=([1, 50], [2, 50]),
                                             cal=([1, "left"], [2, "left"]))
    widgets["scaleDoBut"] = cmds.button(l="Scale", w=160, h=25, bgc=(.2, .4, .2), c=manualScale)
    widgets["trackerFFG"] = cmds.floatFieldGrp(l="Change", w=100, v1=100, pre=1, en1=False, cw=([1, 45], [2, 50]),
                                               cal=([1, "left"], [2, "right"]), bgc=(.2, .2, .2))
    widgets["clearBut"] = cmds.button(l="RESET", w=45, bgc=(.2, .2, .2), c=resetScale)

    widgets["origBut"] = cmds.button(l="ORIG", w=45, bgc=(.2, .2, .2), c=origScale)

    # attach to form layout
    cmds.formLayout(widgets["formLO"], e=True,
                    attachForm=[(widgets["slider"], 'top', 5), (widgets["slider"], 'left', 5)])
    cmds.formLayout(widgets["formLO"], e=True,
                    attachForm=[(widgets["scaleFFG"], 'top', 34), (widgets["scaleFFG"], 'left', 5)])
    cmds.formLayout(widgets["formLO"], e=True,
                    attachForm=[(widgets["scaleDoBut"], 'top', 34), (widgets["scaleDoBut"], 'left', 120)])
    cmds.formLayout(widgets["formLO"], e=True,
                    attachForm=[(widgets["clearBut"], 'top', 34), (widgets["clearBut"], 'left', 344)])
    cmds.formLayout(widgets["formLO"], e=True,
                    attachForm=[(widgets["trackerFFG"], 'top', 5), (widgets["trackerFFG"], 'left', 290)])
    cmds.formLayout(widgets["formLO"], e=True,
                    attachForm=[(widgets["origBut"], 'top', 34), (widgets["origBut"], 'left', 290)])

    cmds.showWindow(widgets["win"])
    cmds.window(widgets["win"], e=True, w=400, h=75)


def resetScale(*args):
    """
    resets the scale float field
    """
    cmds.floatFieldGrp(widgets["trackerFFG"], e=True, v1=100)


def origScale(*args):
    """
    scales the object by the inverse of the currentScale (as measured by the tracker floatfield). So if everything was reset when you started it will
    undo all subsequent scaling operations
    """
    currScale = cmds.floatFieldGrp(widgets["trackerFFG"], q=True, v1=True)
    scaleVal = 100 / currScale

    cmds.floatFieldGrp(widgets["trackerFFG"], e=True, v1=scaleVal * currScale)
    done = scale_the_objects(scaleVal)

    if done:
        cmds.floatFieldGrp(widgets["scaleFFG"], e=True, v1=scaleVal * 100)


def manualScale(*args):
    """uses the float field group to manually scale the object by that amount"""
    origScale = cmds.floatFieldGrp(widgets["trackerFFG"], q=True, v1=True)

    scalePer = cmds.floatFieldGrp(widgets["scaleFFG"], q=True, v1=True)
    scaleVal = scalePer / 100

    done = scale_the_objects(scaleVal)

    if done:
        newScale = origScale * scaleVal
        cmds.floatFieldGrp(widgets["trackerFFG"], e=True, v1=newScale)


def shapeScaleExecute(*args):
    """
    takes the components of the selected obj and scales them according the slider
    """
    origScale = cmds.floatFieldGrp(widgets["trackerFFG"], q=True, v1=True)
    oldScale = 100
    scaleVal = cmds.floatSliderGrp(widgets["slider"], q=True, v=True)

    done = scale_the_objects(scaleVal)

    # reset slider to 1, so we don't stack scalings
    cmds.floatSliderGrp(widgets["slider"], e=True, v=1)

    if done:
        newScale = oldScale * scaleVal
        cmds.floatFieldGrp(widgets["scaleFFG"], e=True, v1=newScale)
        newScale = origScale * scaleVal
        cmds.floatFieldGrp(widgets["trackerFFG"], e=True, v1=newScale)


def scale_the_objects(scaleVal, *args):
    """
    does the scaling bits
    """
    sel = cmds.ls(sl=True, type="transform")
    if sel:
        for obj in sel:
            if (rig.type_check(obj, "nurbsSurface")) or (rig.type_check(obj, "nurbsCurve")):
                piv = cmds.xform(obj, q=True, ws=True, rp=True)
                cvs = cmds.select((obj + ".cv[*]"))
                cmds.scale(scaleVal, scaleVal, scaleVal, cvs, pivot=piv)
            elif rig.type_check(obj, "mesh"):
                piv = cmds.xform(obj, q=True, ws=True, rp=True)
                vs = cmds.select((obj + ".vtx[*]"))
                cmds.scale(scaleVal, scaleVal, scaleVal, vs, pivot=piv)
            else:
                cmds.warning("{0} isn't a nurbs or poly object, so it was skipped".format(obj))
    # clear and reselect all
    if sel:
        cmds.select(cl=True)
        cmds.select(sel)
        return (True)

    return (False)


def shapeScale():
    """Use this to start the script!"""
    shapeScaleUI()
