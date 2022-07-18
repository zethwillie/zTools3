########################
#file: zbw_cleanKeys.py
#Author: zeth willie
#Contact: zeth@catbuks.com, www.williework.blogspot.com
#Date Modified: 04/29/13
#To Use: type in python window  "import zbw_tangents as tan; tan.tangents()"
#Notes/Descriptions: Use to clean up extra keys, etc in animation curves. Can be from master control or on individual controls
########################

#TO-DO----------------check boxes for ins and outs

import maya.cmds as cmds
from functools import partial
widgets = {}

def tanUI(*args):
    """the UI for the clean/tangent functions"""
    if cmds.window("tanWin", exists=True):
        cmds.deleteUI("tanWin")

    widgets["win"] = cmds.window("tanWin", t="zbw_tangents", w=300, h=160)
    widgets["mainCLO"] = cmds.columnLayout()
    # widgets["tabLO"] = cmds.tabLayout()

    #tab for changing all tangent types
    # cmds.setParent(widgets["tabLO"])
    widgets["tangentCLO"] = cmds.columnLayout("Tangents")

    #radioButtons for tangent type (step, linear, auto, spline)
    widgets["tangentType"] = cmds.radioButtonGrp(nrb=4, l1="Step", l2="Linear", l3="Spline", l4="Auto", sl=1, cw=[(1,50),(2,50),(3,50),(4,50)])
    #radio button group for all selected or for hierarchy under selected
    widgets["tanHierRBG"] = cmds.radioButtonGrp(nrb=2, l1="Selected Objs Only", l2="Hierarchy Under Selected", sl=2, cc=enableSelect)
    #radioButtons for time (timeslider, all anim, range)
    widgets["tanTimeRBG"] = cmds.radioButtonGrp(nrb=3,l1="Timeslider", l2="All Anim", l3="Frame Range", sl=2, cw=[(1,100),(2,75),(3,75)],cc=partial(enableFR,"tanTimeRBG","tanFrameRangeIFG"))
    #int field group for frame range
    widgets["tanFrameRangeIFG"] = cmds.intFieldGrp(nf=2, l="Start/End", v1=1, v2=24, en=False, cal=[(1,"left"),(2,"left"),(3,"left")], cw=[(1,75),(2,75),(3,75)])
    #radioButtons for curves only or for all DAG objects
    widgets["tanCurvesRBG"] = cmds.radioButtonGrp(nrb=2, l1="Curves/Volume Primatives Only", l2="All DAG", sl=1, cw=[(1, 190),(2, 110)])
    cmds.separator(h=10)

    #Button for executing the change
    #button to SELECT those objects rather than change the tangents
    widgets["buttonRCLO"] = cmds.rowColumnLayout(w=300, nc=2, cw=[(1,200),(2,100)])
    widgets["tanBut"] = cmds.button(l="Change Tangent Type!", w=200, h=40, bgc=(.6,.6,.8), c=changeTan)
    widgets["selectBut"] = cmds.button(l="Select \nHierarchy", w=100, h=40, bgc=(.8,.6,.6), c=selectHier)

    cmds.showWindow(widgets["win"])
    cmds.window(widgets["win"], e=True, w=300, h=160)

def enableSelect(*args):
    """when hierarchy is selected, this enables the option for curves only """
    val = cmds.radioButtonGrp(widgets["tanHierRBG"], q=True, sl=True)
    if val==2:
        cmds.radioButtonGrp(widgets["tanCurvesRBG"], e=True, en=True)
        cmds.button(widgets["selectBut"], e=True, en=True)
    else:
        cmds.radioButtonGrp(widgets["tanCurvesRBG"], e=True, en=False)
        cmds.button(widgets["selectBut"], e=True, en=False)

def getSliderRange(*args):
    """gets framerange in current scene and returns start and end frames"""
    #get timeslider range start
    startF = cmds.playbackOptions(query=True, min=True)
    endF = cmds.playbackOptions(query=True, max=True)
    return(startF, endF)

def enableCurve(*args):
    """when hierarchy is selected, this enables the option for curves only """
    val = cmds.radioButtonGrp(widgets["hierarchyRBG"], q=True, sl=True)
    if val==2:
        cmds.radioButtonGrp(widgets["curvesRBG"], e=True, en=True)
    else:
        cmds.radioButtonGrp(widgets["curvesRBG"], e=True, en=False)

def enableFR(source, intField, singles=None, *args):
    """when frame range option is selected, this activates the frame range int field group"""
    val = cmds.radioButtonGrp(widgets[source], q=True, sl=True)
    if val==3:
        cmds.intFieldGrp(widgets[intField], e=True, en=True)
        if source == "timeRBG":
            if singles:
                cmds.checkBoxGrp(widgets[singles], e=True, en=False)
    elif val==2:
        cmds.intFieldGrp(widgets[intField], e=True, en=False)
        if source == "timeRBG":
            if singles:
                cmds.checkBoxGrp(widgets[singles], e=True, en=True)
    elif val==1:
        cmds.intFieldGrp(widgets[intField], e=True, en=False)
        if source == "timeRBG":
            if singles:
                cmds.checkBoxGrp(widgets[singles], e=True, en=False)

def changeTan(*args):
    """this changes the tangent types of the objects based on settings in the tangent tab"""
    #get selected objects
    hier = cmds.radioButtonGrp(widgets["tanHierRBG"], q=True, sl=True)
    curves = cmds.radioButtonGrp(widgets["tanCurvesRBG"], q=True, sl=True)

    selection = cmds.ls(sl=True, type="transform")
    #this is the selection list to operate on
    sel = []
    if selection:
        if hier==2:
            #if hierarchy is selected, we then (and only then) have the option to choose the types we'll get
            if curves == 1:
                #filter the selection down to the new selection
                curveList = []
                for obj in selection:
                    relsSh = cmds.listRelatives(obj, ad=True, f=True, type=["nurbsCurve", "renderBox", "renderSphere", "renderCone"])
                    if relsSh:
                        for shape in relsSh:
                            curve = cmds.listRelatives(shape, p=True, f=True, type="transform")[0]
                            curveList.append(curve)
                if curveList:
                    for curve in curveList:
                        sel.append(curve)
                for obj in selection:
                    sel.append(obj)

            elif curves == 2:
                #get transforms without filtering for curves
                dagList = []
                for obj in selection:
                    transform = cmds.listRelatives(obj, ad=True, f=True, type="transform")
                    if transform:
                        for this in transform:
                            dagList.append(this)
                    #add in the object itself
                    dagList.append(obj)

                for this in dagList:
                    sel.append(this)

                for obj in selection:
                    sel.append(obj)

        elif hier==1:
            for obj in selection:
                sel.append(obj)

    else:
        cmds.warning("You haven't selected any transform nodes!")
    #get framerange
    rangeRaw = cmds.radioButtonGrp(widgets["tanTimeRBG"], q=True, sl=True)
    if rangeRaw==1:
        startF = cmds.playbackOptions(query=True, min=True)
        endF = cmds.playbackOptions(query=True, max=True)
    if rangeRaw==3:
        startF = cmds.intFieldGrp(widgets["tanFrameRangeIFG"], q=True, v1=True)
        endF = cmds.intFieldGrp(widgets["tanFrameRangeIFG"], q=True, v2=True)
    #get tangent type
    tanNum = cmds.radioButtonGrp(widgets["tangentType"], q=True, sl=True)
    if tanNum==1:
        tanType = "step"
    elif tanNum==2:
        tanType = "linear"
    elif tanNum==3:
        tanType = "spline"
    elif tanNum==4:
        tanType = "auto"

    #for keys in range, change tangent type (don't use frame range if rangeRaw==2
    for obj in sel:
        if rangeRaw==2:
            if tanNum==1:
                cmds.keyTangent(obj, ott="step")
            else:
                cmds.keyTangent(obj, ott=tanType, itt=tanType)
        else:
            if tanNum==1:
                cmds.keyTangent(obj, ott="step", t=(startF,endF))
            else:
                cmds.keyTangent(obj, ott=tanType, itt=tanType, t=(startF,endF))

def selectHier(*args):
    """this selects the objects based on the filters in the tangents tab"""
    #get selected objects
    hier = cmds.radioButtonGrp(widgets["tanHierRBG"], q=True, sl=True)
    curves = cmds.radioButtonGrp(widgets["tanCurvesRBG"], q=True, sl=True)

    selection = cmds.ls(sl=True, type="transform")
    #this is the selection list to operate on
    sel = []
    if selection:
        if hier==2:
            #if hierarchy is selected, we then (and only then) have the option to choose the types we'll get
            if curves == 1:
                #filter the selection down to the new selection
                curveList = []
                for obj in selection:
                    relsSh = cmds.listRelatives(obj, ad=True, f=True, type=["nurbsCurve", "renderBox", "renderSphere", "renderCone"])
                    if relsSh:
                        for shape in relsSh:
                            curve = cmds.listRelatives(shape, p=True, f=True, type="transform")[0]
                            curveList.append(curve)
                if curveList:
                    for curve in curveList:
                        sel.append(curve)

                for obj in selection:
                    sel.append(obj)

            elif curves == 2:
                #get transforms without filtering for curves
                dagList = []
                for obj in selection:
                    transform = cmds.listRelatives(obj, ad=True, f=True, type="transform")
                    if transform:
                        for this in transform:
                            dagList.append(this)
                    #add in the object itself
                    dagList.append(obj)

                for this in dagList:
                    sel.append(this)

                for obj in selection:
                    sel.append(obj)

        elif hier==1:
            for obj in selection:
                sel.append(obj)

        #now select
        cmds.select(cl=True)
        cmds.select(sel)

    else:
        cmds.warning("You don't have any transforms selected!")

def tangents(*args):
    """Use this to start the script!"""
    tanUI()
