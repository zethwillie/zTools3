########################
# File: accumulateAttrs.py
# Date Modified: 17 Mar 2017
# creator: Zeth Willie
# Contact: zethwillie@gmail.com, catbuks.com, williework.blogspot.com
# Description: for selection in order, adds successively larger values to selection list
# To Run: type "import zTools3.anim.accumulateAttrs as accattr;accattr.accumulateAttrs()"
########################

# todo check ordered selections

import maya.cmds as cmds
import maya.mel as mel

widgets = {}


def accumulateAttrsUI(*args):
    if cmds.window("accumulateAttrWin", exists=True):
        cmds.deleteUI("accumulateAttrWin")
    widgets["win"] = cmds.window("accumulateAttrWin", t="jk's magic script", w=200, h=100, rtf=True)
    widgets["clo"] = cmds.columnLayout()
    cmds.text("select the objs in order, then select\nthe channel(s) to add to. . .", align="left")
    cmds.separator(h=10)
    widgets["ffg"] = cmds.floatFieldGrp(l="value accumulated per obj:", cw=[(1, 140), (2, 50)],
                                        cal=[(1, "left"), (2, "left")], v1=0)
    cmds.separator(h=10)
    cmds.button(l="add values to channels!", w=200, bgc=(.5, .7, .5), h=30, c=accumDo)

    cmds.window(widgets["win"], e=True, rtf=True)
    cmds.showWindow(widgets["win"])


def accumDo(*args):
    val = cmds.floatFieldGrp(widgets["ffg"], q=True, v1=True)
    accumulateAttrsChange(val)


def accumulateAttrsChange(val, *args):
    if not cmds.selectPref(q=True, trackSelectionOrder=True):
        cmds.selectPref(trackSelectionOrder=True)

    sel = cmds.ls(orderedSelection=True)

    chnls = getChannels()

    for i in range(0, len(sel)):
        j = val * (i + 1)
        for chnl in chnls:
            currentVal = cmds.getAttr("{0}.{1}".format(sel[i], chnl))
            newVal = j + currentVal
            cmds.setAttr("{0}.{1}".format(sel[i], chnl), newVal)


def getChannels(*args):
    cBox = mel.eval('$temp=$gChannelBoxName')
    cAttrs = cmds.channelBox(cBox, q=True, selectedMainAttributes=True, ssa=True, sha=True, soa=True)
    return cAttrs


def accumulateAttrs(*args):
    accumulateAttrsUI()
