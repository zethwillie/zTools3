import maya.cmds as cmds
import zTools.rig.zbw_rig as rig
from functools import partial
import maya.OpenMaya as OpenMaya
#---------------- window with list of deformers from a particular transform (selected component)
#---------------- float field with with value (to use as a multiplier)
#---------------- soft select will give values 
#---------------- button to change values (use cmds.percent)
widgets = {}

def deformerWeightUI(*args):
    if cmds.window("defWgtsWin", exists=True):
        cmds.deleteUI("defWgtsWin")
    w, h = 300, 200
    widgets["win"] = cmds.window("defWgtsWin", w=w, h=h, t="zbw_deformerWeights")
    widgets["mainFLO"] = cmds.formLayout(w=w, h=h)

    widgets["defTSL"] = cmds.textScrollList(w=w, h=100, allowMultiSelection=True)
    widgets["weightFFG"] = cmds.floatFieldGrp(w=w, l="Weight Mult (soft)selection value x this", v1=1.0, cw=[(1, 215), (2, 50)], cal=[(1, "left"), (2, "left")], cc=limitMinMax)
    widgets["objTFG"] = cmds.textFieldGrp(w=w, l="Deforming Object", cw=[(1, 100), (2, 200)], cal=[(1, "left"), (2, "left")], en=False)
    widgets["doBut"] = cmds.button(l="set selected weights (based on softSel)", w=w, h=40, bgc = (.5, .7, .5), c=partial(setWeights, "selection"))
    widgets["zeroBut"] = cmds.button(l="zero all weights on selected deformer", w=w, h=20, bgc = (.7, .7, .5), c=partial(setWeights,"zero"))
    widgets["resetBut"] = cmds.button(l="reset deformer list based on selection obj", w=w, h=20, bgc = (.7, .5, .5), c=populateList)

    cmds.formLayout(widgets["mainFLO"], e=True, af=[
        (widgets["defTSL"], "left", 0),
        (widgets["defTSL"], "top", 0),
        (widgets["objTFG"], "left", 0),
        (widgets["objTFG"], "top", 105),                
        (widgets["zeroBut"], "left", 0),
        (widgets["zeroBut"], "top", 135),     
        (widgets["weightFFG"], "left", 0),
        (widgets["weightFFG"], "top", 165),  
        (widgets["doBut"], "left", 0),
        (widgets["doBut"], "top", 195),
        (widgets["resetBut"], "left", 0),
        (widgets["resetBut"], "top", 245),
        ])

    cmds.window(widgets["win"], e=True, w=5, h=5, rtf=True)
    cmds.showWindow(widgets["win"])
    populateList()


def populateList(*args):
    xform = None
    tsl = widgets["defTSL"]
    cmds.textScrollList(tsl, e=True, removeAll=True)
    cmpnts = cmds.filterExpand(ex=False, sm=[28, 31])
    if cmpnts:
        xform = cmpnts[0].partition(".")[0]
    if not cmpnts:
        sel = cmds.ls(sl=True, type="transform")
        if sel:
            xform = sel[0]
    if not xform:
        cmds.warning("You must select a piece of geo or some components on a piece of geo!")
        return()
    cmds.textFieldGrp(widgets["objTFG"], e=True, tx=xform)
    defs = getDeformers(xform)
    for d in defs:
        cmds.textScrollList(tsl, e=True, a=d)

def limitMinMax(*args):
    val = cmds.floatFieldGrp(widgets["weightFFG"], q=True, v1=True)
    new = val
    if val <= 0.0:
        new = 0.0

    elif val >= 1.0:
        new =1.0

    cmds.floatFieldGrp(widgets["weightFFG"], e=True, v1=new)

def getDeformers(obj):
    """take in an xform"""
    defs = []
    history = cmds.listHistory(obj) or []
    defHist = cmds.ls(history, type="geometryFilter", int=True)
    for d in defHist:
        if d not in ["tweak1"]:
            defs.append(d)
    return(defs)

def setWeights(mode, *args):
    """mode: "zero" to zero all weights or "selection" to apply weights to selection"""

#---------------- if current selection is a transform then do the whole thing by this mult value. . . . 

    deformers = cmds.textScrollList(widgets["defTSL"], q=True, selectItem=True)
    if mode == "selection":
        c, w = getWeights()
        if not c or not w:
            cmds.warning("zbw_deformerWeights(line 85): Couldn't get the components.")
            return()

        mult = cmds.floatFieldGrp(widgets["weightFFG"], q=True, v1=True)
        for d in deformers:
            for each in zip(c, w):
                cmds.percent(d, each[0], v=(each[1]*mult))

    if mode == "zero":
        t = cmds.textFieldGrp(widgets["objTFG"], q=True, tx=True)
        sel = []
        if rig.type_check(t, "mesh"):
            sel = cmds.ls("{0}.vtx[*]".format(t), fl=True)
        elif rig.type_check(t, "nurbsCurve") or rig.type_check(t, "nurbsSurface"):
            sel = cmds.ls("{0}.cv[*]".format(t), fl=True)

        for d in deformers:
            if sel:
                for each in sel:
                    cmds.percent(d, each, v=0)

def getWeights(*args):
    tType = ""
    t = cmds.textFieldGrp(widgets["objTFG"], q=True, tx=True)
    if rig.type_check(t, "mesh"):
        tType = "poly"
    if rig.type_check(t, "nurbsCurve") or rig.type_check(t, "nurbsSurface"):
        tType = "nurbs"

    # get type of object (nurbs or poly)
    selection = OpenMaya.MSelectionList()
    softSelection = OpenMaya.MRichSelection()
    OpenMaya.MGlobal.getRichSelection(softSelection)
    softSelection.getSelection(selection)

    dagPath = OpenMaya.MDagPath()
    component = OpenMaya.MObject()

    # Filter Defeats the purpose of the else statement
    # print "********** selection: " + str(OpenMaya.MDagPath(selection))
    if tType == "nurbs":
        iter = OpenMaya.MItSelectionList( selection,OpenMaya.MFn.kCurveCVComponent)
    elif tType == "poly":
        iter = OpenMaya.MItSelectionList( selection,OpenMaya.MFn.kMeshVertComponent)
    else:
        return(None, None)

    elements, weights = [], []
    while not iter.isDone():
        iter.getDagPath( dagPath, component )
        dagPath.pop() #Grab the parent of the shape node
        node = dagPath.fullPathName()
        fnComp = OpenMaya.MFnSingleIndexedComponent(component)
        getWeight = lambda i: fnComp.weight(i).influence() if fnComp.hasWeights() else 1.0

        for i in range(fnComp.elementCount()):
            if tType == "nurbs":
                elements.append('%s.cv[%i]' % (node, fnComp.element(i)))
            elif tType == "poly":
                elements.append('%s.vtx[%i]' % (node, fnComp.element(i)))
            weights.append(getWeight(i))
        next(iter)

    return elements, weights

def deformerWeights(*args):
    deformerWeightUI()