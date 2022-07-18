"""change all joint display radius"""
# put a slider on this, floatField and button

import maya.cmds as cmds

widgets = {}


def jointRadiusUI(*args):
    if cmds.window("jntWin", exists=True):
        cmds.deleteUI("jntWin")

    widgets["win"] = cmds.window("jntWin", t="zbw_jointRadius", w=200, h=90, s=False)
    widgets["clo"] = cmds.columnLayout(rs=10)

    widgets["slider"] = cmds.floatSliderGrp(l="radius", min=0.05, max=2, field=True, fieldMinValue=0.01,
                                            fieldMaxValue=50, precision=2, sliderStep=0.1, value=0.5,
                                            cw=([1, 40], [2, 45], [3, 115]),
                                            cal=([1, "left"], [2, "left"], [3, "left"]))
    # radio button group, all or selected
    widgets["rbg"] = cmds.radioButtonGrp(nrb=2, l1="all", l2="selected", cw=([1, 50], [1, 50]), sl=1)
    widgets["but"] = cmds.button(l="Set Radius", w=205, h=50, bgc=(.5, .8, .5), c=adjustRadius)

    cmds.window(widgets["win"], e=True, w=200, h=90)
    cmds.showWindow(widgets["win"])


def adjustRadius(*args):
    sel = cmds.ls(sl=True)  # for reselecting later
    jnts = getJoints()
    # get radius from slider field
    radius = cmds.floatSliderGrp(widgets["slider"], q=True, value=True)

    for jnt in jnts:
        cmds.setAttr("{}.radius".format(jnt), radius)

    cmds.select(sel)


def getJoints(*args):
    jnt = cmds.radioButtonGrp(widgets["rbg"], q=True, sl=True)

    if jnt == 1:
        jnts = cmds.ls(type="joint")
    else:
        jnts = cmds.ls(sl=True, type="joint")

    cmds.select(jnts)
    return (jnts)


def jointRadius():
    jointRadiusUI()
