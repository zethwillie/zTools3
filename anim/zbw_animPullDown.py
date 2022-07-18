########################
# file: zbw_animPullDown.py
# Author: zeth willie
# Contact: zeth@catbuks.com, www.williework.blogspot.com
# Date Modified: 05/01/13
# To Use: type in python window  "import zbw_animPullDown as apd; apd.animPullDown()"
# Notes/Descriptions: Use in blocking. Move the master control and then run script to transfer the animation from the master control to the selected world controls under it
########################

import maya.cmds as cmds
import maya.OpenMaya as om
import math
from functools import partial
import maya.mel as mel

# import zbw_undoable

# TO-DO----------------option to turn filtering on/off
# TO-DO----------------add help menu with popup to describe situation
# TO-DO----------------DUMMY CHECK SELECTIONS (FOR CLEAR, GRAB SELECTED, ADD TO LIST, GET FROM STORED, ETC)

# TO-DO----------------add option for including scale??
# TO_DO----------------save out the selected controls to get them later?
# TO-DO----------------option to select all objects in world ctrl list, double click in list to select?
# TO-DO----------------frame range option? probably not necessary, think of a situation in which you'd need it

widgets = {}


def animPullDownUI():
    """the ui for the module"""

    if cmds.window("apdWin", exists=True):
        cmds.deleteUI("apdWin", window=True)
        cmds.windowPref("apdWin", remove=True)

    widgets["win"] = cmds.window("apdWin", t="zbw_pullDownAnim", w=400, h=550)

    widgets["tabLO"] = cmds.tabLayout()
    widgets["mainCLO"] = cmds.columnLayout("SetupControls")

    # master controls layout
    widgets["zeroFLO"] = cmds.frameLayout("zeroFrameLO", l="Master Controls", w=400, bgc=(0, 0, 0), h=180)
    widgets["zeroCLO"] = cmds.columnLayout("zeroColumnLO", w=400)
    cmds.text("Select Master Control Items To Zero Out")
    widgets["zeroBut"] = cmds.button("zeroButton", l="Add Selected Master CTRLs", bgc=(.8, .8, .6), w=400, h=30,
                                     c=partial(getControl, "masterTSL"))

    widgets["zeroRCLO"] = cmds.rowColumnLayout("zeroRCLO", nc=2, w=400)
    widgets["zeroClearBut"] = cmds.button("clearZeroButton", l="Clear Selected", w=200, h=20, bgc=(.8, .6, .6),
                                          c=partial(clearList, "masterTSL"))
    widgets["zeroClearBut"] = cmds.button("clearAllZeroButton", l="Clear All", w=200, h=20, bgc=(.8, .5, .5),
                                          c=partial(clearAll, "masterTSL"))
    widgets["zeroSelObjBut"] = cmds.button("selObjZeroButton", l="Grab All Items From List", w=200, h=20,
                                           bgc=(.5, .6, .8), c=partial(selectObj, "masterTSL"))
    widgets["zeroKeysCB"] = cmds.checkBox("zeroKeysCB", l="Delete Master Keys?", v=1, en=True)
    cmds.setParent(widgets["zeroCLO"])
    cmds.separator(h=10)
    widgets["masterTSL"] = cmds.textScrollList("masterTSL", nr=4, w=400, h=60, ams=True,
                                               dcc=partial(showName, "masterTSL"), bgc=(.2, .2, .2))

    # ik items layout
    cmds.setParent(widgets["mainCLO"])
    widgets["IKFLO"] = cmds.frameLayout("IKFrameLO", l="World Space Controls (Translation and Rotation)", w=400,
                                        bgc=(0, 0, 0))
    widgets["IKCLO"] = cmds.columnLayout("IKColumnLO", w=400)
    cmds.text("Select World Space Controls (translate and rotate)")
    widgets["IKBut"] = cmds.button("IKButton", l="Add World Space CTRLs", w=400, h=30, bgc=(.8, .8, .6),
                                   c=partial(getControl, "IKTSL"))

    widgets["IKRCLO"] = cmds.rowColumnLayout("IKRCLO", nc=2, w=400)
    widgets["IKClearSelBut"] = cmds.button("clearIKButton", l="Clear Selected", bgc=(.8, .6, .6), w=200, h=20,
                                           c=partial(clearList, "IKTSL"))
    widgets["IKClearAllBut"] = cmds.button("moveIKButton", l="Clear All", w=200, h=20, bgc=(.8, .5, .5),
                                           c=partial(clearAll, "IKTSL"))
    widgets["IKStoredBut"] = cmds.button("storedIKButton", l="Add Stored From Selected Master", bgc=(.6, .6, .8), w=200,
                                         h=20, c=partial(addStoredSolo, "storeTSL", "IKTSL"))
    widgets["IKSelObjBut"] = cmds.button("selObjIKButton", l="Grab All Items From List", bgc=(.5, .6, .8), w=200, h=20,
                                         c=partial(selectObj, "IKTSL"))
    cmds.setParent("IKColumnLO")
    cmds.separator(h=10)
    widgets["IKTSL"] = cmds.textScrollList("IKTSL", nr=10, w=400, h=90, ams=True, dcc=partial(showName, "IKTSL"),
                                           bgc=(.2, .2, .2))
    cmds.separator(h=10)

    # ik items layout
    cmds.setParent(widgets["mainCLO"])
    widgets["rotFLO"] = cmds.frameLayout("rotFrameLO", l="World Rotation Controls (Rotation Only) -optional-", w=400,
                                         bgc=(0, 0, 0), cll=True, cl=True)
    widgets["rotCLO"] = cmds.columnLayout("rotColumnLO", w=400)
    cmds.text("Select World Rotation Controls (rotation only!)")
    widgets["rotBut"] = cmds.button("rotButton", l="Add World Rotation CTRLs", w=400, h=30, bgc=(.8, .8, .6),
                                    c=partial(getControl, "rotTSL"))

    widgets["rotRCLO"] = cmds.rowColumnLayout("rotRCLO", nc=2, w=400)
    widgets["rotClearSelBut"] = cmds.button("clearrotButton", l="Clear Selected", bgc=(.8, .6, .6), w=200, h=20,
                                            c=partial(clearList, "rotTSL"))
    widgets["rotClearAllBut"] = cmds.button("moveRotButton", l="Clear All", w=200, h=20, bgc=(.8, .5, .5),
                                            c=partial(clearAll, "rotTSL"))
    widgets["rotStoredBut"] = cmds.button("storedRotButton", l="Add Stored From Selected Master", bgc=(.6, .6, .8),
                                          w=200, h=20, c=partial(addStoredSolo, "storeRotTSL", "rotTSL"))
    widgets["rotSelObjBut"] = cmds.button("selObjRotButton", l="Grab All Items From List", bgc=(.5, .6, .8), w=200,
                                          h=20, c=partial(selectObj, "rotTSL"))
    cmds.setParent("rotColumnLO")
    cmds.separator(h=10)
    widgets["rotTSL"] = cmds.textScrollList("rotTSL", nr=10, w=400, h=70, ams=True, dcc=partial(showName, "rotTSL"),
                                            bgc=(.2, .2, .2))
    cmds.separator(h=10)

    cmds.setParent(widgets["mainCLO"])
    # create key type rbuttons
    widgets["keyRBG"] = cmds.radioButtonGrp(nrb=3, l="Key Type:", l1="Step", l2="Auto", l3="linear", sl=3,
                                            cw=[(1, 75), (2, 60), (3, 60), (4, 60)],
                                            cal=[(1, "left"), (2, "left"), (3, "left"), (4, "left")])
    # doIt button layout
    cmds.setParent(widgets["mainCLO"])
    # TO-DO----------------clear all button!
    widgets["doItRCLO"] = cmds.rowColumnLayout("doItLayout", nc=3, cw=[(1, 220), (2, 100), (3, 80)])
    widgets["doItBut"] = cmds.button("doItButton", l="Pull Animation Down from Master!", w=220, h=50, bgc=(.4, .8, .4),
                                     c=pullDownAnim)
    widgets["pullBut"] = cmds.button("pullButton", l="Store \nWS Controls", w=100, h=50, bgc=(.4, .4, .8),
                                     c=storeControls)
    widgets["clearBut"] = cmds.button("clearButton", l="Clear All\nFields", w=80, h=50, bgc=(.8, .4, .4),
                                      c=clearAllLists)

    # create second tab
    cmds.setParent(widgets["tabLO"])
    widgets["storeCLO"] = cmds.columnLayout("Stored Control Names", w=400)
    widgets["storeFL"] = cmds.frameLayout(l="Stored World Space Control Names (Translate and Rotate)", w=400,
                                          bgc=(0, 0, 0))
    widgets["storeRCL"] = cmds.rowColumnLayout(nc=2)
    widgets["storeClearSelBut"] = cmds.button(l="Clear Selected", bgc=(.8, .6, .6), w=200, h=20,
                                              c=partial(clearList, "storeTSL"))
    widgets["storeClearAllBut"] = cmds.button(l="Clear All", bgc=(.9, .6, .6), w=200, h=20,
                                              c=partial(clearAll, "storeTSL"))
    cmds.setParent(widgets["storeCLO"])
    widgets["storeTSL"] = cmds.textScrollList("storeTSL", nr=8, h=100, w=400, ams=True, bgc=(.2, .2, .2))
    cmds.separator(h=5, style="none")

    # storing rotation only objects
    widgets["storeRotFL"] = cmds.frameLayout(l="Stored World Rotation Control Names (Rotation Only!)", w=400,
                                             bgc=(0, 0, 0))
    widgets["storeRotRCL"] = cmds.rowColumnLayout(nc=2)
    widgets["storeRotClearSelBut"] = cmds.button(l="Clear Selected", bgc=(.8, .6, .6), w=200, h=20,
                                                 c=partial(clearList, "storeRotTSL"))
    widgets["storeRotClearAllBut"] = cmds.button(l="Clear All", bgc=(.9, .6, .6), w=200, h=20,
                                                 c=partial(clearAll, "storeRotTSL"))
    cmds.setParent(widgets["storeRotFL"])
    widgets["storeRotTSL"] = cmds.textScrollList("storeRotTSL", nr=8, h=100, w=400, ams=True, bgc=(.2, .2, .2))

    cmds.setParent(widgets["storeCLO"])
    cmds.separator(h=10, style="single")
    widgets["storeRotPullBut"] = cmds.button(l="Pull Controls To Store Lists from Previous Tab!", bgc=(.8, .8, .4),
                                             w=400, h=40, c=storeControls)
    widgets["storeRotPushBut"] = cmds.button(l="Push These To Lists from Selected Master Ctrl!", bgc=(.4, .8, .4),
                                             w=400, h=40, c=partial(addStored, "yup"))
    cmds.text(
        "WARNING!\nThis 'push' button clears all fields on prev tab and add the stored controls \n to their respective lists AND put the selected master control into \nthe 'Master List'",
        al="center", w=400)

    # showWindow
    cmds.showWindow(widgets["win"])


def showName(layout, *args):
    """this prints the name from the selected item in the list"""
    sel = cmds.textScrollList(widgets[layout], q=True, si=True)
    print()
    sel


def selectObj(layout, *args):
    """this takes the selection from the list and selects itS"""
    selected = cmds.textScrollList(widgets[layout], q=True, ai=True)
    cmds.select(cl=True)

    cmds.select(selected)


def storeControls(*args):
    """this stores the controls from the first tab into the second tab"""
    # get list
    sourceSL = ["IKTSL", "rotTSL"]
    targetSL = ["storeTSL", "storeRotTSL"]
    for i in range(2):
        sel = cmds.textScrollList(widgets[sourceSL[i]], q=True, ai=True)
        if sel:
            for item in sel:
                nsCtrl = item.rpartition("|")[2]
                ctrl = nsCtrl.rpartition(":")[2]
                cmds.textScrollList(widgets[targetSL[i]], e=True, a=ctrl)
        else:
            cmds.warning("There wasn't anything to store in that list!")


def clearAll(layout, *args):
    """clears the selected text scroll list"""
    cmds.textScrollList(widgets[layout], e=True, ra=True)


def addStored(push="None", *args):
    """search for the stored nurbs curve ctrl names under the selected master control"""
    clearAllLists()

    # get master ctrl
    sourceSL = ["storeTSL", "storeRotTSL"]
    targetSL = ["IKTSL", "rotTSL"]
    for x in range(2):
        # get master ctrl
        source = sourceSL[x]
        target = targetSL[x]
        fullNames = []
        stripNames = []
        storedNames = []
        # get selected master
        master = cmds.ls(sl=True)
        if not master:
            cmds.warning("Select the Master control to pull the stored values from (viewport or outliner)!")
        elif len(master) > 1:
            cmds.warning("Only select one master control (viewport or outliner)!")
        else:
            # get all of the children on that make 2 lists (fullname, stripName)
            fullNames = cmds.listRelatives(master, ad=True, f=True, type="transform")
            if fullNames:
                for fullDag in fullNames:
                    noNS = fullDag.rpartition(":")[2]
                    noHier = noNS.rpartition("|")[2]
                    stripNames.append(noHier)
            # get the list of stored names from source TSL
            storedNames = cmds.textScrollList(widgets[source], q=True, ai=True)

            # if stored name is in strip name, get the stripName index
            if storedNames:
                for obj in storedNames:
                    if obj in stripNames:
                        ind = stripNames.index(obj)
                        fullObj = fullNames[ind]
                        cmds.textScrollList(widgets[target], e=True, a=fullObj)
                # put master in list(on first pass)
                if x == 0:
                    getControl("masterTSL")

            else:
                cmds.warning("Couldn't find any objects in your stored list!")


def addStoredSolo(source, target, *args):
    """search for the stored nurbs curve ctrl names under the selected master control"""
    # get master ctrl
    sourceSL = source
    targetSL = target
    fullNames = []
    stripNames = []
    storedNames = []
    # get selected master
    master = cmds.ls(sl=True)
    if not master:
        cmds.warning("Select the Master control to pull the stored values from (viewport or outliner)!")
    elif len(master) > 1:
        cmds.warning("Only select one master control (viewport or outliner)!")
    else:
        # get all of the children on that make 2 lists (fullname, stripName)
        fullNames = cmds.listRelatives(master, ad=True, f=True, type="transform")
        if fullNames:
            for fullDag in fullNames:
                noNS = fullDag.rpartition(":")[2]
                noHier = noNS.rpartition("|")[2]
                stripNames.append(noHier)
        # get the list of stored names from source TSL
        storedNames = cmds.textScrollList(widgets[source], q=True, ai=True)

        # if stored name is in strip name, get the stripName index
        if storedNames:
            for obj in storedNames:
                if obj in stripNames:
                    ind = stripNames.index(obj)
                    fullObj = fullNames[ind]
                    cmds.textScrollList(widgets[target], e=True, a=fullObj)

        else:
            cmds.warning("Couldn't find any objects in your stored list!")


def clearAllLists(*args):
    """clears all lists on first tab"""
    tslList = ["IKTSL", "rotTSL", "masterTSL"]
    for tsl in tslList:
        clearAll(tsl)


def clearList(layout, *args):
    """clears the list of textFields"""
    # get selected items
    sel = cmds.textScrollList(widgets[layout], q=True, sii=True)
    # remove selected items
    if sel:
        for item in sel:
            cmds.textScrollList(widgets[layout], e=True, rii=True)


def getControl(layout, *args):
    """gets the selected objs and puts them into the assoc. layout"""
    selList = cmds.ls(sl=True, type="transform", l=True)
    if selList:
        cmds.textScrollList(layout, e=True, a=selList)


def getLocalValues(obj, *args):
    """use the matrix(xform) to get world space vals, convert to trans and rots"""
    # get values
    # add as key in dict
    obj_values = []

    obj_wRot = cmds.xform(obj, q=True, ws=True, ro=True)
    obj_wTrans = cmds.xform(obj, q=True, ws=True, t=True)

    for tval in obj_wTrans:
        obj_values.append(tval)
    for rval in obj_wRot:
        obj_values.append(rval)

    return obj_values
    # return (tx, ty, tz, rx, ry, rz)


# @zbw_undoable.undoable
def pullDownAnim(*args):
    """this is the function that does the anim pulldown based on stuff in the lists"""

    # get master controls
    masters = []
    rawKeys = []
    keyList = []
    worldCtrls = []
    rotateCtrls = []
    currentTime = mel.eval("currentTime-q;")
    allControls = []
    deleteMaster = cmds.checkBox(widgets["zeroKeysCB"], q=True, v=True)
    # get tangent type to use
    keyT = cmds.radioButtonGrp(widgets["keyRBG"], q=True, sl=True)
    if keyT == 1:
        outTan = "step"
        inTan = "linear"
    elif keyT == 2:
        outTan = "auto"
        inTan = "auto"
    else:
        outTan = "linear"
        inTan = "linear"

    # get list of master ctrls
    mChildren = cmds.textScrollList(widgets["masterTSL"], q=True, ai=True)
    if mChildren:
        for thisM in mChildren:
            masters.append(thisM)
            allControls.append(thisM)

    # get list of world space objects
    wChildren = cmds.textScrollList(widgets["IKTSL"], q=True, ai=True)
    if wChildren:
        for thisIK in wChildren:
            worldCtrls.append(thisIK)
            allControls.append(thisIK)

    # get list of rotate only objects
    rChildren = cmds.textScrollList(widgets["rotTSL"], q=True, ai=True)
    # print "rChildren = %s"%rChildren
    if rChildren:
        for thisRot in rChildren:
            rotateCtrls.append(thisRot)
            allControls.append(thisRot)

    if mChildren and (wChildren or rChildren):
        # get keys from secondary controls also. .  .
        # get full list of keys (keyList)
        if allControls:
            for each in allControls:
                # get list of keys for each master
                keys = cmds.keyframe(each, q=True)
                # add keys to rawKeys
                if keys:
                    for thisKey in keys:
                        rawKeys.append(thisKey)
        # make list from set of list
        keySet = set(rawKeys)
        for skey in keySet:
            keyList.append(skey)

        # if no keys, then just add the current time value
        if not rawKeys:
            keyList.append(currentTime)

        keyList.sort()
        # print keyList

        # -------------
        localVals = {}

        # for each control, grab the values at that key and store them in a dict, "control":[(vals), (vals)], list of values are at key indices
        if worldCtrls:
            for wCtrl in worldCtrls:
                localList = []
                # store these in a dict (obj:(tx, ty, tz, rx, ry, rz))
                for key in keyList:
                    mel.eval("currentTime %s;" % key)
                    theseVals = getLocalValues(wCtrl)
                    localList.append(theseVals)
                localVals[wCtrl] = localList

        if rotateCtrls:
            for rCtrl in rotateCtrls:
                localList = []
                # store these in a dict (obj:(tx, ty, tz, rx, ry, rz))
                for key in keyList:
                    mel.eval("currentTime %s;" % key)
                    theseVals = getLocalValues(rCtrl)
                    localList.append(theseVals)
                localVals[rCtrl] = localList

        # zero out the master controls
        for key in range(len(keyList)):
            mel.eval("currentTime %s;" % keyList[key])
            for mCtrl in masters:
                cmds.xform(mCtrl, ws=True, t=(0, 0, 0))
                cmds.xform(mCtrl, ws=True, ro=(0, 0, 0))
                cmds.setKeyframe(mCtrl, ott="step", t=keyList[key])

            # THEN setKey each control's values to the values in the dict
            for wCtrl in worldCtrls:
                # --------if attr is locked skip it
                cmds.xform(wCtrl, ws=True, a=True,
                           t=(localVals[wCtrl][key][0], localVals[wCtrl][key][1], localVals[wCtrl][key][2]))
                cmds.xform(wCtrl, ws=True,
                           ro=(localVals[wCtrl][key][3], localVals[wCtrl][key][4], localVals[wCtrl][key][5]))
                try:
                    cmds.setKeyframe(wCtrl, t=keyList[key], at="tx")
                except:
                    cmds.warning("Couldn't set key for %s.tx, skipping") % wCtrl
                try:
                    cmds.setKeyframe(wCtrl, t=keyList[key], at="ty")
                except:
                    cmds.warning("Couldn't set key for %s.ty, skipping") % wCtrl
                try:
                    cmds.setKeyframe(wCtrl, t=keyList[key], at="tz")
                except:
                    cmds.warning("Couldn't set key for %s.tz, skipping") % wCtrl
                try:
                    cmds.setKeyframe(wCtrl, t=keyList[key], at="rx")
                except:
                    cmds.warning("Couldn't set key for %s.rx, skipping") % wCtrl
                try:
                    cmds.setKeyframe(wCtrl, t=keyList[key], at="ry")
                except:
                    cmds.warning("Couldn't set key for %s.ry, skipping") % wCtrl
                try:
                    cmds.setKeyframe(wCtrl, t=keyList[key], at="rz")
                except:
                    cmds.warning("Couldn't set key for %s.rz, skipping") % wCtrl

                cmds.keyTangent(wCtrl, at=["tx", "ty", "tz", "rx", "ry", "rz"], itt=inTan, ott=outTan,
                                t=(keyList[key], keyList[key]))
                # now filter all rot curves. . .
                # get the rot anim curve name
                conns = cmds.listConnections(["%s.rx" % wCtrl, "%s.ry" % wCtrl, "%s.rz" % wCtrl], s=True, t="animCurve")
                cmds.filterCurve(conns)

            # now do the world rotation
            for rCtrl in rotateCtrls:
                # --------if attr is locked skip it
                cmds.xform(rCtrl, ws=True,
                           ro=(localVals[rCtrl][key][3], localVals[rCtrl][key][4], localVals[rCtrl][key][5]))
                try:
                    cmds.setKeyframe(rCtrl, t=keyList[key], at="rx")
                except:
                    cmds.warning("Couldn't set key for %s.rx, skipping") % rCtrl
                try:
                    cmds.setKeyframe(rCtrl, t=keyList[key], at="ry")
                except:
                    cmds.warning("Couldn't set key for %s.ry, skipping") % rCtrl
                try:
                    cmds.setKeyframe(rCtrl, t=keyList[key], at="rz")
                except:
                    cmds.warning("Couldn't set key for %s.rz, skipping") % rCtrl

                cmds.keyTangent(rCtrl, at=["rx", "ry", "rz"], itt=inTan, ott=outTan, t=(keyList[key], keyList[key]))
                # now filter all rot curves. . .
                # get the rot anim curve name
                conns = cmds.listConnections(["%s.rx" % rCtrl, "%s.ry" % rCtrl, "%s.rz" % rCtrl], s=True, t="animCurve")
                cmds.filterCurve(conns)
        else:
            cmds.warning(
                "You need at least one Master ctrl and either a World Space ctrl or World Rotation ctrl in the lists!")

    for mCtrl in masters:
        if deleteMaster:
            try:
                cmds.cutKey(mCtrl, at=["tx", "ty", "tz", "rx", "ry", "rz"])
            except:
                cmds.warning("Tried to cut keys on master, but couldn't")


def animPullDown():
    """Use this to start the script!"""

    animPullDownUI()
