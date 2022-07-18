########################
#file: zbw_curveTools.py
#Author: zeth willie
#Contact: zethwillie@gmail.com, www.williework.blogspot.com
#Date Modified: 8/3/2017
#To Use: type in python window  "zbw_curveTools.curveTools()"
#Notes/Descriptions: # some tools to work with crvs
########################

import maya.cmds as cmds
import maya.OpenMaya as om
import math
from functools import partial
import zTools.rig.zbw_rig as rig
import zTools.rig.zbw_curveExtrude as cExtrude
import importlib
importlib.reload(cExtrude)
import zTools.rig.zbw_curveCVControls as zcc
importlib.reload(zcc)
#TODO---------------- on rebuild curves options: have checkbox for keep history, keep original
#TODO ------------  extrude curve w options

widgets = {}

def crvToolsUI():
    if cmds.window("crvToolWin", exists = True):
        cmds.deleteUI("crvToolWin")

    width, height = 300, 220
    widgets["win"] = cmds.window("crvToolWin", t="zbw_curveTools", w=width, h=height)
    widgets["mainTLO"] = cmds.tabLayout()

    widgets["CLO"] = cmds.columnLayout("Tools")
    # common functions
    widgets["funcsFrLO"] = cmds.frameLayout("Common Curve Functions", w=width, cll=False, bgc = (0, 0, 0),
                                            cc=resize_window)
    widgets["funcsFLO"] = cmds.formLayout(w=width, h= 235, bgc = (.3, .3, .3))
    
    widgets["cvDisplBut"] = cmds.button(l="Toggle CV display on selected crvs!", width = 280, h=30, bgc = (.5, .5,
                                                                                                              .4),
                                        c = toggle_display_cvs)
    widgets["reverseBut"] = cmds.button(l="Reverse Selected Curves!", width = 280, h=30, bgc = (.4, .5, .4),
                                        c = reverse_curve)
    widgets["align_attachBut"] = cmds.button(l="Quick align/attach! (2 selected, move 2nd->1st)", w=280, h=30,
                                            bgc = (.5, .5, .4), c= align_attach)
    widgets["reparaBut"] = cmds.button(l="Reparameterize Selected Crvs to 0-1!", width = 280, h=30, bgc = (.5, .5,.4), c = reparameter)
    widgets["pivStartBut"] = cmds.button(l="Move Pivot to Start!", width = 135, h=30, bgc = (.5, .4, .4),
                                         c = partial(move_pivot, 0))
    widgets["pivEndBut"] = cmds.button(l="Move Pivot to End!", width = 135, h=30, bgc = (.5, .4, .4), c = partial(
        move_pivot, 1))
    widgets["cvToolBut"] = cmds.button(l="CV Curve Tool!", width = 135, h=30, bgc = (.5, .5, .4),
                                         c = cmds.CVCurveTool)
    widgets["epToolBut"] = cmds.button(l="EP Curve Tool!", width = 135, h=30, bgc = (.4, .5, .4), c = cmds.EPCurveTool)

    cmds.formLayout(widgets["funcsFLO"], e=True, af = [
        (widgets["cvDisplBut"], "left", 10),
        (widgets["cvDisplBut"], "top", 0),
        (widgets["reverseBut"], "left", 10),
        (widgets["reverseBut"], "top", 40),
        (widgets["align_attachBut"], "left", 10),
        (widgets["align_attachBut"], "top", 80),
        (widgets["reparaBut"], "left", 10),
        (widgets["reparaBut"], "top", 120),
        (widgets["pivStartBut"], "left", 10),
        (widgets["pivStartBut"], "top", 160),
        (widgets["pivEndBut"], "left", 155),
        (widgets["pivEndBut"], "top", 160),
        (widgets["cvToolBut"], "left", 10),
        (widgets["cvToolBut"], "top", 200),
        (widgets["epToolBut"], "left", 155),
        (widgets["epToolBut"], "top", 200),
        ])

    # create curves
    cmds.setParent(widgets["CLO"])
    widgets["lineFrLO"] = cmds.frameLayout("Create Curves", w=width, cll=True, cl=True, bgc = (0, 0, 0),
                                           cc=resize_window)
    widgets["lineFLO"] = cmds.formLayout(w=width,h=140 , bgc = (.3, .3, .3))
    widgets["lineText"] = cmds.text(l="Create a nurbs line along an axis", al="left")
    widgets["lineLenFFG"] = cmds.floatFieldGrp(nf = 1, l = "Length", cal=[(1, "left"), (2,"left")], cw = [(1, 40), (2, 35)], v1=10.0)
    widgets["lineDenFFG"] = cmds.floatFieldGrp(nf = 1, l = "Pts/Unit", cal=[(1, "left"), (2,"left")], cw = [(1, 40), (2, 35)], v1=.5, pre=3)
    widgets["lineAxisRBG"] = cmds.radioButtonGrp(nrb=3, l1="x", l2="y", l3="z", cw = [(1, 35), (2, 35),(3, 35)], sl=1)
    widgets["lineBut"] = cmds.button(l="Create Line!", w = 280, h=30, bgc = (.5, .5, .4), c = create_line)
    widgets["crvSelBut"] = cmds.button(l="Create Curve Through Selection!", w = 280, h=30, bgc = (.5, .4, .4),
                                     c = curve_through_selection)
    widgets["crvSelRBG"] = cmds.radioButtonGrp(l="Type of curve creation:", nrb=2, l1="CV", l2="EP", cal=[(1, "left"), (2,"left"), (3, "left")], cw=[(1, 150), (2, 50), (3, 50)], sl=1)

    cmds.formLayout(widgets["lineFLO"], e=True, af=[
        (widgets["lineText"], "left", 10),
        (widgets["lineText"], "top", 5),
        (widgets["lineLenFFG"], "left", 10),
        (widgets["lineLenFFG"], "top", 25),
        (widgets["lineDenFFG"], "left", 90),
        (widgets["lineDenFFG"], "top", 25),
        (widgets["lineAxisRBG"], "left", 170),
        (widgets["lineAxisRBG"], "top", 25),
        (widgets["lineBut"], "left", 10),
        (widgets["lineBut"], "top", 50),
        (widgets["crvSelBut"], "left", 10),
        (widgets["crvSelBut"], "top", 85),
        (widgets["crvSelRBG"], "left", 10),
        (widgets["crvSelRBG"], "top", 120),
        ])

    # rebuild curve
    cmds.setParent(widgets["CLO"])
    widgets["rebuildFrLO"] = cmds.frameLayout("Rebuild Curves", w=width, cll=True, cl=True, bgc = (0, 0, 0),
                                              cc=resize_window)
    widgets["rebuildFLO"] = cmds.formLayout(w=width, h=120, bgc = (.3, .3, .3))
    widgets["ptText"] = cmds.text(l = "How to calculate rebuild pt count?")
    widgets["methodRBG"] = cmds.radioButtonGrp(nrb=2, l1="pts/unit", l2="total count", sl = 1, cc = toggle_method)
    widgets["recoFFG"] = cmds.floatFieldGrp(l="Points/Unit:", nf = 1, cal = [(1, "left"), (2, "left")], v1= 1, en = True, cw=[(1, 70), (2, 50)])
    widgets["totalIFBG"] = cmds.intFieldGrp(l="Total Count:", nf = 1, cal = [(1, "left"), (2, "left")], v1= 1000, en = False, cw=[(1, 70), (2, 50)])	
    widgets["rebuildBut"] = cmds.button(l="Rebuild Curves!", w = 280, h=30, bgc = (.5, .4, .4), c = rebuild_curves)

    cmds.formLayout(widgets["rebuildFLO"], e=True, af = [
        (widgets["ptText"], "left", 10),
        (widgets["ptText"], "top", 5),		
        (widgets["methodRBG"], "left", 10),
        (widgets["methodRBG"], "top", 25),
        (widgets["recoFFG"], "left", 10),
        (widgets["recoFFG"], "top", 55),
        (widgets["totalIFBG"], "left", 145),
        (widgets["totalIFBG"], "top", 55),
        (widgets["rebuildBut"], "left", 10),
        (widgets["rebuildBut"], "top", 80),
        ])

    # hammer points
    cmds.setParent(widgets["CLO"])
    widgets["hammerFrLO"] = cmds.frameLayout("Hammer/Smooth Points", w=width, cll=True, cl=True, bgc = (0, 0, 0),
                                             cc=resize_window)
    widgets["hammerFLO"] = cmds.formLayout(w=width,h=90 , bgc = (.3, .3, .3))
    widgets["hammerText"] = cmds.text(l="Move selected points towards surrounding pts", al="left")
    widgets["hammerNumIFG"] = cmds.intFieldGrp(nf = 1, l = "# of sample pts on either side", cal=[(1, "left"), (2, "left")], cw = [(1, 170), (2, 50)], v1=1)
    widgets["hammerBut"] = cmds.button(l="Hammer/Smooth Points!", w = 280, h=30, bgc = (.3, .4, .5), c = do_hammer)

    cmds.formLayout(widgets["hammerFLO"], e=True, af=[
        (widgets["hammerText"], "left", 10),
        (widgets["hammerText"], "top", 5),
        (widgets["hammerNumIFG"], "left", 10),
        (widgets["hammerNumIFG"], "top", 25),
        (widgets["hammerBut"], "left", 10),
        (widgets["hammerBut"], "top", 50),
        ])

    # align and extrude
    cmds.setParent(widgets["CLO"])
    widgets["alExFrLO"] = cmds.frameLayout("Align/Extrude", w=width, cll=True, cl=True, bgc = (0, 0, 0), cc=resize_window)
    widgets["alExFLO"] = cmds.formLayout(w=width,h=135 , bgc = (.3, .3, .3))
    widgets["alExText"] = cmds.text("Select curve then object to align to curve.\nSet param along curve.", al="left")
    widgets["alExFFG"] = cmds.floatFieldGrp(nf=1, l= "0.0 - 1.0 param along curve", cal=[(1, "left"), (2,"left")],
                                            cw = [(1, 150), (2, 50)], v1=0.0, pre=3)
    widgets["alExBut"] = cmds.button(l="Align object to curve (curve then object selection)",  w=280, h=30, bgc = (.5,
                                     .5,.4),  c = align_along_curve)
    widgets["extrudeBut"] = cmds.button(l="create poly extrusion (profile then crv)",  w=280, h=30,
                                        bgc = (.5,.4,.4),
                                     c = extrude_curve)
    cmds.formLayout(widgets["alExFLO"], e=True, af=[
        (widgets["alExText"], "left", 10),
        (widgets["alExText"], "top", 5),
        (widgets["alExFFG"], "left", 10),
        (widgets["alExFFG"], "top", 25),
        (widgets["alExBut"], "left", 10),
        (widgets["alExBut"], "top", 50),
        (widgets["extrudeBut"], "left", 10),
        (widgets["extrudeBut"], "top", 90),
        ])

    cmds.setParent(widgets["mainTLO"])
    widgets["rigCLO"] = cmds.columnLayout("Rigs")
    widgets["ctrlCrvFrLO"] = cmds.frameLayout("Ctrls on Curves Setup", w=width, cll=False, bgc = (0, 0, 0),
                                            cc=resize_window)
    widgets["ctrlCrvFLO"] = cmds.formLayout(w=width,h=65 , bgc = (.3, .3, .3))
    widgets["ctrCrvTxt"] = cmds.text("Select crvs and this will create controls on each pt", al="left")
    widgets["ctrlCrvBut"] = cmds.button(l="ctrl on crv button", w=280, h=30, bgc=(.5, .5, .4), c=zcc.curveCVControls)
    cmds.formLayout(widgets["ctrlCrvFLO"], e=True, af=[
        (widgets["ctrCrvTxt"], "left", 10),
        (widgets["ctrCrvTxt"], "top", 5),
        (widgets["ctrlCrvBut"], "left", 10),
        (widgets["ctrlCrvBut"], "top", 25)])

    cmds.setParent(widgets["rigCLO"])
    widgets["spacedRigFrLO"] = cmds.frameLayout("Spaced Ctrls on Curves Setup", w=width, cll=False, bgc = (0, 0, 0),
                                            cc=resize_window)
    widgets["spacedRigFLO"] = cmds.formLayout(w=width,h=65 , bgc = (.3, .3, .3))
    widgets["spacedRigTxt"] = cmds.text("Select Curve stuff", al="left")
    widgets["spacedRigBut"] = cmds.button(l="spaced ctrl on crv button", w=280,h=30, bgc=(.4, .5, .4))
    cmds.formLayout(widgets["spacedRigFLO"], e=True, af=[
        (widgets["spacedRigTxt"], "left", 10),
        (widgets["spacedRigTxt"], "top", 5),
        (widgets["spacedRigBut"], "left", 10),
        (widgets["spacedRigBut"], "top", 25)])

    cmds.setParent(widgets["rigCLO"])
    widgets["crvExtrudeFrLO"] = cmds.frameLayout("curve extrusion Setup", w=width, cll=False, bgc = (0, 0, 0),
                                            cc=resize_window)
    widgets["crvExtrudeFLO"] = cmds.formLayout(w=width, h=65, bgc = (.3, .3, .3))
    widgets["crvExtrudeTxt"] = cmds.text("Open curve_extrusion rig window", al="left")
    widgets["crvExtrudeBut"] = cmds.button(l="open curve extrusion button", w=280,h=30, bgc=(.4, .4, .5), c=curve_extrude)
    cmds.formLayout(widgets["crvExtrudeFLO"], e=True, af=[
        (widgets["crvExtrudeTxt"], "left", 10),
        (widgets["crvExtrudeTxt"], "top", 5),
        (widgets["crvExtrudeBut"], "left", 10),
        (widgets["crvExtrudeBut"], "top", 25)])

    cmds.setParent(widgets["rigCLO"])
    widgets["moPathFrLO"] = cmds.frameLayout("moPath builder", w=width, cll=False, bgc = (0, 0, 0),
                                            cc=resize_window)
    widgets["moPathFLO"] = cmds.formLayout(w=width, h=65, bgc = (.3, .3, .3))
    widgets["moPathTxt"] = cmds.text("Select obj, then crv, create mopath", al="left")
    widgets["moPathBut"] = cmds.button(l="maybe create mopath rig?", w=280, h=30, bgc=(.5, .4, .4))
    cmds.formLayout(widgets["moPathFLO"], e=True, af=[
        (widgets["moPathTxt"], "left", 10),
        (widgets["moPathTxt"], "top", 5),
        (widgets["moPathBut"], "left", 10),
        (widgets["moPathBut"], "top", 25)])

    cmds.window(widgets["win"], e=True, w=5, h=5, resizeToFitChildren = True, sizeable=True)
    cmds.showWindow(widgets["win"])


def resize_window(*args):
    cmds.window(widgets["win"], e=True, rtf=True, w=100, h=100)


def create_line(uniform = True, *args):
    """ 
    gets info from win to create nurbs curve along an axis
    Args:
         uniform (bool): whether the parameterization should be uniform (even), which makes the points not even
    """
    axis = cmds.radioButtonGrp(widgets["lineAxisRBG"], q=True, sl=True)
    length = cmds.floatFieldGrp(widgets["lineLenFFG"], q=True, v1=True)
    density = cmds.floatFieldGrp(widgets["lineDenFFG"], q=True, v1=True)

    numCvs = length * density
    if numCvs < 3.0: # curve needs 3 cvs (for 3 dg curve)
        numCvs = 3.0

    cvDist = length/numCvs

    # make a list of pt dist along some axis
    axisList = []
    for x in range(0,int(numCvs)+1):
        axisList.append(x)

    pts = []

    if axis == 1:
        for y in range(0, int(numCvs)+1):
            pt = [axisList[y]*cvDist, 0, 0]
            pts.append(pt)

    if axis == 2:
        for y in range(0, int(numCvs)+1):
            pt = [0, axisList[y]*cvDist, 0]
            pts.append(pt)

    if axis == 3:
        for y in range(0, int(numCvs)+1):
            pt = [0, 0, axisList[y]*cvDist]
            pts.append(pt)			
        
    line = cmds.curve(name = "line_01", d=3, p=pts)
    shp = cmds.listRelatives(line, s=True)[0]
    cmds.rename(shp, "{0}Shape".format(line))
    if uniform:
        line = cmds.rebuildCurve(line, rebuildType = 0, spans = 0, keepRange = 0, replaceOriginal=True, end=1, keepControlPoints=0)[0]

    cmds.select(line, r=True)


def curve_extrude(*args):
    cExtrude.curveExtrude()


def move_pivot(end, *args):
    """

    Args:
        end (int): parameter value (0 or 1 from buttons) the point on curve will return, start or end
        *args:
    """

    check = False	
    sel = cmds.ls(sl=True, exactType = "transform")

    if sel:
        for x in sel:
            check = rig.type_check(x, "nurbsCurve")
            if check:
                # get curve info
                pos = cmds.pointOnCurve(x, parameter = end, position = True)
                cmds.xform(x, ws=True, piv=pos)
            else:
                cmds.warning("{0} is not a nurbsCurve object. Skipping!".format(x))


def reparameter(*args):
    """
    reparameterizes curves to be from 0-1
    Args:
    Returns:
    """
    sel = cmds.ls(sl=True, exactType = "transform")

    check = False
    newCrvs = []

    if sel:
        for x in sel:
            check = rig.type_check(x, "nurbsCurve")
            if check:
                crv = x
                newCrv = cmds.rebuildCurve(crv, constructionHistory=False, rebuildType = 0, keepControlPoints=True,  keepRange = 0, replaceOriginal=True, name = "{0}_RB".format(crv))[0]

            # reconnect parents and children of orig curve

            else:
                cmds.warning("{0} is not a nurbsCurve object. Skipping!".format(x))

    cmds.select(sel, r=True)


def align_attach(*args):
    """
    alings then attaches two selected curves
    Args:
        *args:

    Returns:

    """
    # check selection, curves, etc
    sel = cmds.ls(sl=True)
    crv1 = ""
    crv2 = ""

    if sel and len(sel)== 2:
        check1 = rig.type_check(sel[0], "nurbsCurve")
        check2 = rig.type_check(sel[1], "nurbsCurve")
        if not check1 and check2:
            cmds.warning("you must select two curves!")
            return
    else:
        cmds.warning("you must select two curves!")
        return		

    crv1, crv2 = sel[0], sel[1]
    newCrv = cmds.alignCurve(crv1, crv2, ch=False, replaceOriginal=False, attach=True, keepMultipleKnots=True, positionalContinuityType=2, tangentContinuity=False, curvatureContinuity=False, name = "{0}_ATT".format(crv1))
    cmds.setAttr("{0}.v".format(crv1), 0)
    cmds.setAttr("{0}.v".format(crv2), 0)


def get_curve(*args):
    sel = cmds.ls(sl=True)
    crv = ""

    if sel and len(sel) == 1:
        check = rig.type_check(sel[0], "nurbsCurve")
        if not check:
            cmds.warning("Must select one curve object!")
            return
    else:
        cmds.warning("Must select one curve object!")
        return

    crv = sel[0]
    cmds.textFieldButtonGrp(widgets["curveTFBG"], e=True, tx = crv)

def calculate_pts(crv, *args):
    """
    uses the window to get the number of pts that should be in the curve
    """	
    mode = cmds.radioButtonGrp(widgets["methodRBG"], q=True, sl=True)

    if mode == 1:
        cLen = cmds.arclen(crv, ch=False)
        perUnit = cmds.floatFieldGrp(widgets["recoFFG"], q=True, v1=True)
        total = int(cLen * perUnit)
    if mode == 2:
        total = cmds.intFieldGrp(widgets["totalIFBG"], q=True, v1=True)

    # print "curve =  {0}, total = {1}".format(crv, total)
    return total


def rebuild_curves(*args):
    """ 
        rebuilds selected curves to specs in window
    """
    sel = cmds.ls(sl=True, exactType = "transform")

    check = False
    newCrvs = []

    if sel:
        for x in sel:
            check = rig.type_check(x, "nurbsCurve")

            if check:
                crv = x
                parent = ""
                parList = cmds.listRelatives(crv, parent = True) 
                if parList:
                    parent = parList[0]

                num = calculate_pts(crv)

                newCrv = cmds.rebuildCurve(crv, rebuildType = 0, spans = num, keepRange = 0, replaceOriginal=False, name = "{0}_RB".format(crv))[0]
                newCrvs.append(newCrv)

                if cmds.objExists("crvRebuildOriginals_GRP"):
                    if (parent and parent != "crvRebuildOriginals_GRP"):
                        cmds.parent(newCrv, parent)
                    if parent != "crvRebuildOriginals_GRP":
                        cmds.parent(crv, "crvRebuildOriginals_GRP")
                    cmds.setAttr("{0}.v".format(crv), 0)

                else:
                    cmds.group(empty = True, name = "crvRebuildOriginals_GRP")
                    if (parent and parent != "crvRebuildOriginals_GRP"):
                        cmds.parent(newCrv, parent)
                    if parent != "crvRebuildOriginals_GRP":
                        cmds.parent(crv, "crvRebuildOriginals_GRP")
                    cmds.setAttr("{0}.v".format(crv), 0)

            else:
                cmds.warning("{0} is not a nurbsCurve object. Skipping!".format(x))

    cmds.select(newCrvs, r=True)


def toggle_method(*args):
    """
    ui helper func to toggle enable/disable ui elements

    """
    sel = cmds.radioButtonGrp(widgets["methodRBG"], q=True, sl=True)
    
    if sel == 1:
        cmds.floatFieldGrp(widgets["recoFFG"], e=True, en=True)
        cmds.intFieldGrp(widgets["totalIFBG"], e=True, en=False)

    elif sel == 2:
        cmds.floatFieldGrp(widgets["recoFFG"], e=True, en=False)
        cmds.intFieldGrp(widgets["totalIFBG"], e=True, en=True)


def toggle_display_cvs(*args):
    cmds.toggle(cv=True)


def reverse_curve(*args):
    sel = cmds.ls(sl=True, exactType = "transform")

    check = False

    if sel:
        for x in sel:
            check = rig.type_check(x, "nurbsCurve")
            if check:
                cmds.reverseCurve(x, ch=False, replaceOriginal=True)
    else:
        cmds.warning("Must select some curves")
        return

    cmds.select(sel, r=True)


def getNormalizedTangent(pt = ""):
    """
    gets normalized tan of selected (or given) list of cvs
    """

    if cmds.objectType(pt) != "nurbsCurve":
        return

    crv = pt.partition(".")[0]
    print((pt, crv))
    cvs = cmds.ls("{0}.cv[*]".format(crv), fl=True)
    denom = len(cvs)
    num = float(pt.partition("[")[2].rpartition("]")[0])
    pr = num/denom
    tan = cmds.pointOnCurve(crv, pr=pr, nt=True)

    return(tan)


def lerp(a, b, perc):
    """
    pass in a, b as lists[3], perc as 0-1 float
    """
    vx = (perc*float(b[0]))+((1-perc)*float(a[0]))
    vy = (perc*float(b[1]))+((1-perc)*float(a[1]))
    vz = (perc*float(b[2]))+((1-perc)*float(a[2]))
    return [vx, vy, vz]


def do_smooth(*args):
    num = cmds.intFieldGrp(widgets["smthNumIFG"], q=True, v1=True)
    smoothPoints(num, push)


def curve_through_selection(*args):
    """
    creates a curve through the selection, hopefully in order
    Args:
        None
    Returns:
        string, name of curve created
    """
    sel = cmds.ls(sl=True, fl=True)
    if not sel or len(sel)==1:
        cmds.warning("You need to select multiple things to create curve through!")
        return()

    pList = []
    crvType = cmds.radioButtonGrp(widgets["crvSelRBG"], q=True, sl=True)

    for obj in sel:
        if cmds.objectType(obj) in ["transform"]:
            pos = cmds.xform(obj, q=True, ws=True, rp=True)
            pList.append(pos)
        elif obj in cmds.filterExpand(sm=[28, 30, 31, 32, 34, 46]):
            pos = cmds.pointPosition(obj)
            pList.append(pos)

    #add points if only 2 (cv, ep) or 3 (cv) are given, and create the curve
    if crvType == 1:
        if len(pList) == 2:
            f = [float(sum(x)/2) for x in zip(*pList)]
            pList.insert(1, f)
            vec1 = [pList[1][0]-pList[0][0], pList[1][1]-pList[0][1], pList[1][2]-pList[0][2]]
            newPt1 =[pList[0][0] + (vec1[0]*0.05), pList[0][1] + (vec1[1]*0.05), pList[0][2] + (vec1[2]*0.05)]
            vec2 = [pList[1][0] - pList[2][0], pList[1][1] - pList[2][1], pList[1][2] - pList[2][2]]
            newPt2= [pList[2][0] + (vec2[0]*0.05), pList[2][1] + (vec2[1]*0.05), pList[2][2] + (vec2[2]*0.05)]
            pList.insert(1, newPt1)
            pList.insert(3, newPt2)
        if len(pList) == 3:
            vec1 = [pList[1][0]-pList[0][0], pList[1][1]-pList[0][1], pList[1][2]-pList[0][2]]
            newPt1 =[pList[0][0] + (vec1[0]*0.05), pList[0][1] + (vec1[1]*0.05), pList[0][2] + (vec1[2]*0.05)]
            vec2 = [pList[1][0] - pList[2][0], pList[1][1] - pList[2][1], pList[1][2] - pList[2][2]]
            newPt2= [pList[2][0] + (vec2[0]*0.05), pList[2][1] + (vec2[1]*0.05), pList[2][2] + (vec2[2]*0.05)]
            pList.insert(1, newPt1)
            pList.insert(3, newPt2)
        crv = cmds.curve(d=3, p=pList, name="newCurve")

    if crvType == 2:
        if len(pList) == 2:
            f = [float(sum(x)/2) for x in zip(*pList)]
            pList.insert(1, f)
        crv = cmds.curve(d=3, ep=pList, name="newCurve")

    return(crv)


def smoothPoints(num = 5, push = 0.05):
    """
    tries to smooth the surrounding pts around an outlier cv
    num = number of points on either side to affect
    push = amount to push out along tangent
    """
    tgtPts = cmds.ls(sl=True, fl=True)

    for tgtPt in tgtPts:

        tgtPtPos = cmds.pointPosition(tgtPt)
        
        tgtNum = int(tgtPt.partition("[")[2].rpartition("]")[0])
        tgtBase = tgtPt.partition("[")[0]
        #crv = tgtBase.partition(".")[0]

        tgtTan = getNormalizedTangent(tgtPt)
        
        for x in range(-num, num+1):
            
            if x != 0:
                origPt = "{0}[{1}]".format(tgtBase, tgtNum + x)
                origPtPos = cmds.pointPosition(origPt)
                
                perc = (float(abs(x))/(num + 1.0))
                #print origPt, perc
                
                newPosRaw = om.MVector(*lerp(tgtPtPos, origPtPos, math.sin(perc*3.14*0.5)))
                tan = om.MVector(tgtTan[0]*math.pow(1-perc/num, num)*push, tgtTan[1]*math.pow(1-perc/num, num)*push, tgtTan[2]*math.pow(1-perc/num, num)*push)
                #tan = om.MVector(tgtTan[0]*push, tgtTan[1]*push, tgtTan[2]*push)

                if x<0:
                    newPos = newPosRaw + tan
                if x>0:
                    newPos = newPosRaw - tan
                
                #print origPt, newPosRaw.x, newPosRaw.y, newPosRaw.z
                
                cmds.xform(origPt, ws=True, t=newPos)


def do_hammer(*args):
    num = cmds.intFieldGrp(widgets["hammerNumIFG"], q=True, v1=True)
    hammer_points(num)


def hammer_points(neighbors = 3):
    """
    moves selected cvs to the weighted average of the pts around it [neighbors]
    """
    tgtPts = cmds.ls(sl=True, fl=True)
#---------------- add in soft selection? 
    if not tgtPts:
        cmds.warning("Select one or more cvs")
        return

    for tgtPt in tgtPts:

        #tgtPtPos = cmds.pointPosition(tgtPt)
        
        tgtNum = int(tgtPt.partition("[")[2].rpartition("]")[0])
        #tgtBase = tgtPt.partition("[")[0]
        crv = tgtPts[0].partition(".")[0]
        
        ptPosListX = []
        ptPosListY = []
        ptPosListZ = []
        
        count = 0
        
        for x in range(-neighbors, neighbors+1):
            
            count += abs(x)
            
            if x != 0:
                origPt = "{0}.cv[{1}]".format(crv, tgtNum + x)
                origPtPos = cmds.pointPosition(origPt)
                
                for a in range(abs(x)):
                    ptPosListX.append(origPtPos[0])
                    ptPosListY.append(origPtPos[1])
                    ptPosListZ.append(origPtPos[2])
                
        avgX = sum(ptPosListX)/(len(ptPosListX))
        avgY = sum(ptPosListY)/(len(ptPosListY))
        avgZ = sum(ptPosListZ)/(len(ptPosListZ))
        
        newPos = [avgX, avgY, avgZ]
        
        cmds.xform(tgtPt, ws=True, t=newPos)


def align_along_curve(*args):
    """
    aligns and objet along a curve at given param
    Args:
        *args:
    Returns:
        void
    """
    sel = cmds.ls(sl=True, type="transform")
    if len(sel) != 2:
        cmds.warning("You need to select curve then object to align!")
        return()
    crv = sel[0]
    obj = sel[1]
    if not rig.type_check(crv, "nurbsCurve"):
        cmds.warning("select curve first, THEN object")
        return()

    param = cmds.floatFieldGrp(widgets["alExFFG"], q=True, v1=True)

    rig.align_to_curve(crv, obj, param)


def extrude_curve(*args):
    pass
# extrude -ch true -rn false -po 1 -et 2 -ucp 1 -fpt 1 -upn 1 -rotation 0 -scale 1 -rsp 1 "nurbsCircle1" "newCurve" ;



def curveTools():
    crvToolsUI()