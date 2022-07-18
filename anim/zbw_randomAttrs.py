import maya.cmds as cmds
import maya.mel as mel
from functools import partial
import random as rand

"""
assign random values to attributes
"""

widgets = {}


def randomAttrsUI():
    if cmds.window("rndAttrWin", exists=True):
        cmds.deleteUI("rndAttrWin")

    w = 250

    widgets["win"] = cmds.window("rndAttrWin", t="zbw_randomAttrs", w=w, rtf=True)
    widgets["mainCLO"] = cmds.columnLayout()

    widgets["transformFrLO"] = cmds.frameLayout("Transforms", w=w, bgc=(0, 0, 0))
    widgets["settingsCLO"] = cmds.columnLayout()
    widgets["optionsCBG"] = cmds.checkBoxGrp(w=w, ncb=2, cw2=(100, 100), la2=("Relative?", "Obj Space Trans/Rot?"),
                                             va2=(1, 1))

    cmds.setParent(widgets["transformFrLO"])
    # switch to Row column layout to break up the channels
    widgets["transRCLO"] = cmds.rowColumnLayout(nc=2, cw=([1, 100], [2, 150]))
    widgets["transCB"] = cmds.checkBox(l="Translates", v=1, cc=partial(enableChannel, "transCB", "translateCBG"))
    widgets["translateCBG"] = cmds.checkBoxGrp(w=w, cw3=(50, 50, 50), ncb=3, l1="TX", l2="TY", l3="TZ", l4="Vis",
                                               va3=(1, 1, 1), bgc=(.5, .5, .5), en=True,
                                               cc=partial(toggleOnOff, "translateCBG"))
    widgets["rotCB"] = cmds.checkBox(l="Rotates", v=1, cc=partial(enableChannel, "rotCB", "rotateCBG"))
    widgets["rotateCBG"] = cmds.checkBoxGrp(w=w, cw3=(50, 50, 50), ncb=3, l1="RX", l2="RY", l3="RZ", l4="Vis",
                                            va3=(1, 1, 1), bgc=(.5, .5, .5), en=True,
                                            cc=partial(toggleOnOff, "rotateCBG"))
    widgets["scaleCB"] = cmds.checkBox(l="Scales", v=1, cc=partial(enableChannel, "scaleCB", "scaleCBG"))
    widgets["scaleCBG"] = cmds.checkBoxGrp(w=w, cw3=(50, 50, 50), ncb=3, l1="SX", l2="SY", l3="SZ", l4="Vis",
                                           va3=(1, 1, 1), bgc=(.5, .5, .5), en=True,
                                           cc=partial(toggleOnOff, "scaleCBG"))
    cmds.setParent(widgets["transRCLO"])
    widgets["transCLO"] = cmds.columnLayout(w=w)
    cmds.separator(h=10)
    widgets["txFFG"] = cmds.floatFieldGrp(w=w, l="tX Range", nf=2, cl3=["left", "left", "left"], cw3=[95, 70, 70])
    widgets["tyFFG"] = cmds.floatFieldGrp(w=w, l="tY Range", nf=2, cl3=["left", "left", "left"], cw3=[95, 70, 70])
    widgets["tzFFG"] = cmds.floatFieldGrp(w=w, l="tZ Range", nf=2, cl3=["left", "left", "left"], cw3=[95, 70, 70])
    cmds.separator(h=10)
    widgets["rxFFG"] = cmds.floatFieldGrp(w=w, l="rX Range", nf=2, cl3=["left", "left", "left"], cw3=[95, 70, 70])
    widgets["ryFFG"] = cmds.floatFieldGrp(w=w, l="rY Range", nf=2, cl3=["left", "left", "left"], cw3=[95, 70, 70])
    widgets["rzFFG"] = cmds.floatFieldGrp(w=w, l="rZ Range", nf=2, cl3=["left", "left", "left"], cw3=[95, 70, 70])
    cmds.separator(h=10)
    widgets["sxFFG"] = cmds.floatFieldGrp(w=w, l="sX Range", nf=2, cl3=["left", "left", "left"], cw3=[95, 70, 70], v1=1,
                                          v2=1)
    widgets["syFFG"] = cmds.floatFieldGrp(w=w, l="sY Range", nf=2, cl3=["left", "left", "left"], cw3=[95, 70, 70], v1=1,
                                          v2=1)
    widgets["szFFG"] = cmds.floatFieldGrp(w=w, l="sZ Range", nf=2, cl3=["left", "left", "left"], cw3=[95, 70, 70], v1=1,
                                          v2=1)
    cmds.separator(h=10)
    widgets["randTransBut"] = cmds.button(w=w, l="Randomize Transforms", h=35, bgc=(.5, .4, .4), c=randomizeTransforms)
    cmds.separator(h=5)

    cmds.setParent(widgets["mainCLO"])
    widgets["floatFrLO"] = cmds.frameLayout("Other Float Attributes", w=w, cll=True, cl=True, bgc=(0, 0, 0),
                                            cc=resizeWindow)
    widgets["floatCLO"] = cmds.columnLayout()
    cmds.text("This will randomize float/int attributes\nselected in the channel box", al="left")
    cmds.separator(h=10)
    widgets["floatFFG"] = cmds.floatFieldGrp(w=w, l="Value Range", nf=2, cl3=["left", "left", "left"], cw3=[95, 70, 70])
    widgets["floatCB"] = cmds.checkBox(w=w, l="Relative to current?", v=1)
    cmds.separator(h=10)
    widgets["floatTransBut"] = cmds.button(w=w, l="Randomize Float Attributes", h=35, bgc=(.4, .5, .4),
                                           c=randomizeFloats)
    cmds.separator(h=5)

    cmds.setParent(widgets["mainCLO"])
    widgets["multFrLO"] = cmds.frameLayout("Multiply Float Attributes", w=w, cll=True, cl=True, bgc=(0, 0, 0),
                                           cc=resizeWindow)
    widgets["multCLO"] = cmds.columnLayout()
    cmds.text("This will multiply float/int attributes\nselected in the channel box", al="left")
    cmds.separator(h=10)
    widgets["multFFG"] = cmds.floatFieldGrp(w=w, l="Multiplier", nf=1, cl2=["left", "left"], v1=1.0, cw2=[95, 70])
    cmds.separator(h=10)
    widgets["multBut"] = cmds.button(w=w, l="Multiply Attributes", h=35, bgc=(.4, .4, .5), c=multiplyFloats)
    cmds.separator(h=5)

    resizeWindow()
    cmds.showWindow(widgets["win"])


def enableChannel(source, target, *args):
    """This function enables or disables the indiv channel checkboxes when attr is toggled"""
    CBG = widgets[target]
    on = cmds.checkBox(widgets[source], q=True, v=True)
    if on:
        cmds.checkBoxGrp(CBG, e=True, en=True, va3=(1, 1, 1))
    else:
        cmds.checkBoxGrp(CBG, e=True, en=False, va3=(0, 0, 0))


def resizeWindow(*args):
    cmds.window(widgets["win"], e=True, rtf=True, w=100, h=100)


def toggleOnOff(cbg, *args):
    """zeros and disables the relevant fields when disabling a channel"""
    status = cmds.checkBoxGrp(widgets[cbg], q=True, va3=True)
    cbDict = {
        "translateCBG": ["txFFG", "tyFFG", "tzFFG"], "rotateCBG": ["rxFFG", "ryFFG", "rzFFG"],
        "scaleCBG": ["sxFFG", "syFFG", "szFFG"]
        }

    for x in range(3):
        if status[x]:
            cmds.floatFieldGrp(widgets[cbDict[cbg][x]], e=True, en=True)
        else:
            cmds.floatFieldGrp(widgets[cbDict[cbg][x]], e=True, v1=0, v2=0, en=False)


def randomizeTransforms(*args):
    sel = cmds.ls(sl=True, type="transform")

    rel, objSpace = cmds.checkBoxGrp(widgets["optionsCBG"], q=True, va2=True)

    tcb = cmds.checkBox(widgets["transCB"], q=True, v=True)
    rcb = cmds.checkBox(widgets["rotCB"], q=True, v=True)
    scb = cmds.checkBox(widgets["scaleCB"], q=True, v=True)

    # get values from checkboxes
    td = {}
    td["tx"], td["ty"], td["tz"], td["rx"], td["ry"], td["rz"], td["sx"], td["sy"], td["sz"] = [0, [0, 0], 0.0], [0, [0,
                                                                                                                      0],
                                                                                                                  0.0], [
                                                                                                   0, [0, 0], 0.0], [0,
                                                                                                                     [0,
                                                                                                                      0],
                                                                                                                     0.0], [
                                                                                                   0, [0, 0], 0.0], [0,
                                                                                                                     [0,
                                                                                                                      0],
                                                                                                                     0.0], [
                                                                                                   0, [1, 1], 1.0], [0,
                                                                                                                     [1,
                                                                                                                      1],
                                                                                                                     1.0], [
                                                                                                   0, [1, 1], 1.0]
    if tcb:
        td["tx"][0], td["ty"][0], td["tz"][0] = cmds.checkBoxGrp(widgets["translateCBG"], q=True, va3=True)
    if rcb:
        td["rx"][0], td["ry"][0], td["rz"][0] = cmds.checkBoxGrp(widgets["rotateCBG"], q=True, va3=True)
    if scb:
        td["sx"][0], td["sy"][0], td["sz"][0] = cmds.checkBoxGrp(widgets["scaleCBG"], q=True, va3=True)

    # get rand values
    for attr in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]:
        if td[attr][0]:
            td[attr][1] = cmds.floatFieldGrp(widgets["{0}FFG".format(attr)], q=True, v=True)

    for obj in sel:
        # td
        if tcb:
            for attr in ["tx", "ty", "tz"]:
                if td[attr][0]:
                    rand = getRandomFloat(td[attr][1][0], td[attr][1][1])
                    td[attr][2] = rand

            if rel:
                if td["tx"][0]:
                    cmds.xform(obj, ws=not objSpace, os=objSpace, relative=True, t=(td["tx"][2], 0, 0))
                if td["ty"][0]:
                    cmds.xform(obj, ws=not objSpace, os=objSpace, relative=True, t=(0, td["ty"][2], 0))
                if td["tz"][0]:
                    cmds.xform(obj, ws=not objSpace, os=objSpace, relative=True, t=(0, 0, td["tz"][2]))
            else:
                cmds.xform(obj, ws=True, os=objSpace, relative=False, t=(td["tx"][2], td["ty"][2], td["tz"][2]))
        # r
        if rcb:
            for attr in ["rx", "ry", "rz"]:
                if td[attr][0]:
                    rand = getRandomFloat(td[attr][1][0], td[attr][1][1])
                    td[attr][2] = rand
            if rel:
                if td["rx"][0]:
                    cmds.xform(obj, ws=not objSpace, os=objSpace, relative=True, ro=(td["rx"][2], 0, 0))
                if td["ry"][0]:
                    cmds.xform(obj, ws=not objSpace, os=objSpace, relative=True, ro=(0, td["ry"][2], 0))
                if td["rz"][0]:
                    cmds.xform(obj, ws=not objSpace, os=objSpace, relative=True, ro=(0, 0, td["rz"][2]))
            else:
                cmds.xform(obj, ws=True, os=objSpace, relative=False, t=(td["tx"][2], td["ty"][2], td["tz"][2]))
        # s
        if scb:
            for attr in ["sx", "sy", "sz"]:
                if td[attr][0]:
                    rand = getRandomFloat(td[attr][1][0], td[attr][1][1])
                    td[attr][2] = rand

            if rel:
                if td["sx"][0]:
                    cmds.xform(obj, relative=True, s=(td["sx"][2], 1, 1))
                if td["sy"][0]:
                    cmds.xform(obj, relative=True, s=(1, td["sy"][2], 1))
                if td["sz"][0]:
                    cmds.xform(obj, relative=True, s=(1, 1, td["sz"][2]))
            else:
                cmds.xform(obj, relative=False, s=(td["sx"][2], td["sy"][2], td["sz"][2]))


def randomizeFloats(*args):
    sel = cmds.ls(sl=True)
    attrs = getChannels()

    minn = cmds.floatFieldGrp(widgets["floatFFG"], q=True, v1=True)
    maxx = cmds.floatFieldGrp(widgets["floatFFG"], q=True, v2=True)
    rel = cmds.checkBox(widgets["floatCB"], q=True, v=True)

    for obj in sel:
        for attr in attrs:
            if (cmds.attributeQuery(attr, node=obj, exists=True)):
                rand = getRandomFloat(minn, maxx)
                current = 0.0
                if rel:
                    current = cmds.getAttr("{0}.{1}".format(obj, attr))
                newVal = rand + current
                cmds.setAttr("{0}.{1}".format(obj, attr), newVal)


def multiplyFloats(*args):
    sel = cmds.ls(sl=True)
    attrs = getChannels()

    mult = cmds.floatFieldGrp(widgets["multFFG"], q=True, v1=True)

    for obj in sel:
        for attr in attrs:
            if (cmds.attributeQuery(attr, node=obj, exists=True)):
                current = cmds.getAttr("{0}.{1}".format(obj, attr))
                newVal = current * mult
                cmds.setAttr("{0}.{1}".format(obj, attr), newVal)


def getChannels(*args):
    cBox = mel.eval('$temp=$gChannelBoxName')
    cAttrs = cmds.channelBox(cBox, q=True, selectedMainAttributes=True, ssa=True, sha=True, soa=True)
    return cAttrs


def getRandomFloat(low, high):
    x = rand.uniform(low, high)
    return x


def randomAttrs(*args):
    randomAttrsUI()
