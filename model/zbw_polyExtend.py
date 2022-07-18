########################
#file: zbw_polyExtend.py
#Author: zeth willie
#Contact: zeth@catbuks.com, www.williework.blogspot.com
#Date Modified: 04/29/13
#To Use: type in python window  "import zbw_polyExtend as pex; pex.polyExtend"
#Notes/Descriptions: use to take an edge of poly (or curve) and offset it in space and loft from the original, then convert that to a polygon.
########################

import maya.cmds as cmds
import maya.mel as mel

def extendUI(*args):
    """UI for the script"""
    #UI
    if cmds.window("curbWin", exists=True):
        cmds.deleteUI("curbWin")

    cmds.window("curbWin", t="zbw_polyExtender", w=200, h=200)
    cmds.columnLayout("colLO")
    cmds.frameLayout("topFrame", l="Covert Edge", cll=True, bgc=(.2,.2,.2))
    cmds.text("Select poly edge to convert")
    cmds.button("convertBut", l="Convert!", w=200, h=30, bgc=(.8, .8,.6), c=convertEdge)
    cmds.separator(h=5)

    cmds.setParent("colLO")

    cmds.frameLayout("midFrame", l="Create Poly", cll=True, bgc=(.2,.2,.2))
    cmds.text("Select curve")
    cmds.separator(h=5)
    cmds.textFieldGrp("name", l="Name", w=200, cw=[(1,30), (2,170)], tx="newPoly")
    cmds.checkBox("curbCB", l="Positive Direction", v=True)
    # cmds.checkBox("bumpCB", l="Add vertical hump?", v=True)
    cmds.floatFieldGrp("curbFFG", l="Curb Width", cal=((1, "left"),(2,"left")), cw=([1,75],[2,50]), v1=10)
    cmds.intFieldGrp("UDivIFG", l="Width Subdivisions", cal=((1, "left"),(2,"left")), cw=([1,75],[2,50]), v1=1)
    cmds.intFieldGrp("VDivIFG", l="Length Subdivisions", cal=((1, "left"),(2,"left")), cw=([1,75],[2,50]), v1=1)
    cmds.checkBox("polyHistory", l="Keep history on final poly?", v=False)
    cmds.checkBox("history", l="Keep history objects?", v=True, cc=enableHistory)

    cmds.separator(h=5)
    cmds.button("curbBut", l="Create Curb", h=40, w=200, bgc=(.6, .8, .6), c=extendPoly)

    cmds.showWindow("curbWin")
    cmds.window("curbWin", e=True, h=150, w=200)


def convertEdge(*args):
    """converts the selected poly edge to a nurbs curve"""

    sel = cmds.ls(sl=True, type="transform")
    try:
        mel.eval("polyToCurve -form 2 -degree 3;")
    except:
        cmds.warning("Couldn't complete this operation! Sorry buddy. Maybe you haven't selected a poly edge?")

def enableHistory(*args):
    """turns on/off the history checkbox"""

    #if keep objs is off, then history on poly is off and disabled
    keep = cmds.checkBox("history", q=True, v=True)
    if keep:
        cmds.checkBox("polyHistory", e=True, en=True, v=True)
    else:
        cmds.checkBox("polyHistory", e=True, en=False, v=False)

def extendPoly(*args):
    """does the polyextension by grabbing the curve, offsetting it and then lofting. Then converts the nurbs surface to polys"""

    #make sure a curve is selected
    selection = cmds.ls(sl=True)
    if selection:
        sel = selection[0]
        shape = cmds.listRelatives(sel, s=True)[0]
        type = cmds.objectType(shape)
        name = cmds.textFieldGrp("name", q=True, tx=True)
        hisGrp = cmds.checkBox("history", q=True, v=True)
        hisPoly = cmds.checkBox("polyHistory", q=True, v=True)

        if type== "nurbsCurve":
            #offset the curb
            distance = cmds.floatFieldGrp("curbFFG", q=True, v1=True)
            # bump = cmds.checkBox("bumpCB", q=True, v=True)
            pos = cmds.checkBox("curbCB", q=True, v=True)
            if pos == 0:
                dist = distance * -1
            else:
                dist = distance
            U = cmds.intFieldGrp("UDivIFG", q=True, v1=True)
            V = cmds.intFieldGrp("VDivIFG", q=True, v1=True)

            origCrv = cmds.rename(sel, "%s_inner_CRV"%name)
            outCurve = cmds.offsetCurve(origCrv, d=dist, n="%s_outer_CRV"%name)
            midCurve = cmds.offsetCurve(origCrv, d=dist/2, n="%s_mid_CRV"%name)
            # if bump:
            #     cmds.xform(midCurve, ws=True, r=True, t=(0,5,0))

            cmds.select(cl=True)

            lofted = cmds.loft(origCrv, midCurve, outCurve)[0]
            loft = cmds.rename(lofted, "%s_lofted"%name)

            polygon = cmds.nurbsToPoly(loft, pt=1, ch=hisPoly, f=2, un=U, vn=V)[0]
            poly = cmds.rename(polygon, "%s_poly"%name)

            curbGrp = cmds.group(empty=True)
            grp = cmds.rename(curbGrp, "%s_History_GRP"%name)

            # cmds.rename(poly, "polyCurb")

            cmds.parent(loft, outCurve, midCurve, origCrv, grp)

            cmds.setAttr("%s.v"%grp, 0)
            if not hisGrp:
                cmds.delete(grp)

        else:
            cmds.warning("That's not a curve! You need to select a curve!")
    else:
        cmds.warning("You haven't selected anything!")


def polyExtend():
    """Use this to start the script!"""

    extendUI()