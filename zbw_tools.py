########################
# file: zbw_tools.py
# Author: zeth willie
# Contact: zethwillie@gmail.com, www.williework.blogspot.com
# Date Modified: 7/19/2022
# To Use: type in python window  "import zbw_tools as tools; reload(tools); tools.tools()"
# Notes/Descriptions: some rigging, anim, modeling and shading tools. *** requires zTools package in a python path.
########################

from functools import partial
import os
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import importlib

import zTools3.rig.zbw_rig as rig
import zTools3.resources.zbw_pipe as pipe
import zTools3.resources.zbw_removeNamespaces as rmns
import zTools3.resources.zbw_registeredTools as zReg

widgets = {}
# make sure maya can see and call mel scripts from zTools (where this is called from)
zToolsPath = os.path.dirname(os.path.abspath(__file__))
subpaths = [
    "",
    "rig",
    "resources",
    "anim",
    "model",
    "shaderRender",
]

newPaths = [os.path.join(zToolsPath, p) for p in subpaths]

# set up these zTools paths for maya to recognize mel scripts
pipe.add_maya_script_paths(newPaths)

zRigDict = zReg.zRigDict
zAnimDict = zReg.zAnimDict
zModelDict = zReg.zModelDict
zShdDict = zReg.zShdDict
zAnn = zReg.zAnnDict

colors = rig.colors


def tools_UI(*args):
    """UI for tools"""
    if cmds.window("toolsWin", exists=True):
        cmds.deleteUI("toolsWin")

    widgets["win"] = cmds.window("toolsWin", t="zTools", w=280, rtf=True, s=True)
    widgets["tab"] = cmds.tabLayout(w=280)
    widgets["rigCLO"] = cmds.columnLayout("TD", w=280)
    widgets["rigFLO"] = cmds.formLayout(w=280, bgc=(0.1, 0.1, 0.1))

    # controls layout
    widgets["ctrlFLO"] = cmds.formLayout(w=270, h=50, bgc=(0.3, 0.3, 0.3))
    widgets["ctrlFrLO"] = cmds.frameLayout(
        l="CONTROLS", w=270, h=50, bv=True, bgc=(0.0, 0.0, 0.0)
    )
    widgets["ctrlInFLO"] = cmds.formLayout(bgc=(0.3, 0.3, 0.3))
    widgets["ctrlAxisRBG"] = cmds.radioButtonGrp(
        l="Axis",
        nrb=3,
        la3=("x", "y", "z"),
        cw=([1, 33], [2, 33], [3, 33]),
        cal=([1, "left"], [2, "left"], [3, "left"]),
        sl=1,
    )
    widgets["ctrlBut"] = cmds.button(
        l="Create..", w=50, bgc=(0.7, 0.7, 0.5), ann=zAnn["createCtrl"]
    )
    cmds.popupMenu(b=1)
    cmds.menuItem(l="circle", c=partial(control, "circle"))
    cmds.menuItem(l="sphere", c=partial(control, "sphere"))
    cmds.menuItem(l="square", c=partial(control, "square"))
    cmds.menuItem(l="triangle", c=partial(control, "triangle"))
    cmds.menuItem(l="star", c=partial(control, "star"))
    cmds.menuItem(l="cube", c=partial(control, "cube"))
    cmds.menuItem(l="tetrahedron", c=partial(control, "tetrahedron"))
    cmds.menuItem(l="squarePyramid", c=partial(control, "squarePyramid"))
    cmds.menuItem(l="octahedron", c=partial(control, "octahedron"))
    cmds.menuItem(l="lollipop", c=partial(control, "lollipop"))
    cmds.menuItem(l="barbell", c=partial(control, "barbell"))
    cmds.menuItem(l="cross", c=partial(control, "cross"))
    cmds.menuItem(l="bentCross", c=partial(control, "bentCross"))
    cmds.menuItem(l="arrow", c=partial(control, "arrow"))
    cmds.menuItem(l="bentArrow", c=partial(control, "bentArrow"))
    cmds.menuItem(l="arrowCross", c=partial(control, "arrowCross"))
    cmds.menuItem(l="splitCircle", c=partial(control, "splitCircle"))
    cmds.menuItem(l="cylinder", c=partial(control, "cylinder"))
    cmds.menuItem(l="octagon", c=partial(control, "octagon"))
    cmds.menuItem(l="halfCircle", c=partial(control, "halfCircle"))
    cmds.menuItem(l="arrowCircle", c=partial(control, "arrowCircle"))
    cmds.menuItem(l="arrowSquare", c=partial(control, "arrowSquare"))
    cmds.menuItem(l="4ArrowSquare", c=partial(control, "4arrowSquare"))
    cmds.menuItem(l="MASTER PACK", c=create_master_pack)

    widgets["swapBut"] = cmds.button(
        l="Swap..", w=50, bgc=(0.7, 0.5, 0.5), ann=zAnn["swap"]
    )
    cmds.popupMenu(b=1)
    cmds.menuItem(l="circle", c=partial(swap, "circle"))
    cmds.menuItem(l="sphere", c=partial(swap, "sphere"))
    cmds.menuItem(l="square", c=partial(swap, "square"))
    cmds.menuItem(l="triangle", c=partial(swap, "triangle"))
    cmds.menuItem(l="star", c=partial(swap, "star"))
    cmds.menuItem(l="cube", c=partial(swap, "cube"))
    cmds.menuItem(l="tetrahedron", c=partial(swap, "tetrahedron"))
    cmds.menuItem(l="squarePyramid", c=partial(swap, "squarePyramid"))
    cmds.menuItem(l="octahedron", c=partial(swap, "octahedron"))
    cmds.menuItem(l="lollipop", c=partial(swap, "lollipop"))
    cmds.menuItem(l="barbell", c=partial(swap, "barbell"))
    cmds.menuItem(l="cross", c=partial(swap, "cross"))
    cmds.menuItem(l="bentCross", c=partial(swap, "bentCross"))
    cmds.menuItem(l="arrow", c=partial(swap, "arrow"))
    cmds.menuItem(l="bentArrow", c=partial(swap, "bentArrow"))
    cmds.menuItem(l="arrowCross", c=partial(swap, "arrowCross"))
    cmds.menuItem(l="splitCircle", c=partial(swap, "splitCircle"))
    cmds.menuItem(l="cylinder", c=partial(swap, "cylinder"))
    cmds.menuItem(l="octagon", c=partial(swap, "octagon"))
    cmds.menuItem(l="halfCircle", c=partial(swap, "halfCircle"))
    cmds.menuItem(l="arrowCircle", c=partial(swap, "arrowCircle"))
    cmds.menuItem(l="arrowSquare", c=partial(swap, "arrowSquare"))
    cmds.menuItem(l="4ArrowSquare", c=partial(swap, "4arrowSquare"))

    cmds.formLayout(
        widgets["ctrlInFLO"],
        e=True,
        af=[
            (widgets["ctrlAxisRBG"], "left", 0),
            (widgets["ctrlAxisRBG"], "top", 0),
            (widgets["ctrlBut"], "left", 170),
            (widgets["ctrlBut"], "top", 0),
            (widgets["swapBut"], "left", 220),
            (widgets["swapBut"], "top", 0),
        ],
    )
    # TODO - add scale factor field for control creation

    # action layout
    cmds.setParent(widgets["rigFLO"])
    actionHeight = 470
    widgets["actionFLO"] = cmds.formLayout(w=280, h=actionHeight, bgc=(0.3, 0.3, 0.3))
    widgets["actionFrLO"] = cmds.frameLayout(
        l="ACTIONS", w=280, h=actionHeight, bv=True, bgc=(0, 0, 0)
    )
    widgets["actionRCLO"] = cmds.rowColumnLayout(bgc=(0.3, 0.3, 0.3), nc=2)
    widgets["selHier"] = cmds.button(
        l="sel hierarchy..", w=140, bgc=(0.5, 0.7, 0.5), ann=zAnn["selHier"]
    )
    cmds.popupMenu(b=1)
    cmds.menuItem(l="Select Full Hierarchy", c=select_hi)
    cmds.menuItem(l="Select Curve Hierarchy", c=partial(select_hierarchy, "curve"))
    cmds.menuItem(l="Select Joint Hierarchy", c=partial(select_hierarchy, "joint"))
    cmds.menuItem(l="Select Poly Hierarchy", c=partial(select_hierarchy, "poly"))
    widgets["showHide"] = cmds.button(
        l="ShowHide..", w=140, bgc=(0.5, 0.7, 0.5), ann=zAnn["showHide"]
    )
    cmds.popupMenu(b=1)
    cmds.menuItem(l="Show all", c=partial(show_hide_in_panels, "showAll"))
    cmds.menuItem(l="Polys only", c=partial(show_hide_in_panels, "polys"))
    cmds.menuItem(l="Curves only", c=partial(show_hide_in_panels, "curves"))
    cmds.menuItem(
        l="Polys and curves only", c=partial(show_hide_in_panels, "polyCurve")
    )
    cmds.menuItem(l="Joints only", c=partial(show_hide_in_panels, "joints"))
    cmds.menuItem(l="Joints off", c=partial(show_hide_in_panels, "jointsOff"))
    widgets["grpFrzBut"] = cmds.button(
        l="group freeze selected",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=group_freeze,
        ann=zAnn["grpFrz"],
    )
    widgets["grpCnctBut"] = cmds.button(
        l="group freeze + connect",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=freeze_and_connect,
        ann=zAnn["grpFrzCnt"],
    )
    widgets["createBut"] = cmds.button(
        l="Create..", w=140, bgc=(0.5, 0.7, 0.5), ann=zAnn["create"]
    )
    cmds.popupMenu(b=1)
    cmds.menuItem(l="joint", c=create_joint)
    cmds.menuItem(l="locator", c=create_locator)
    cmds.menuItem(l="set from selected", c=rig.create_set)
    cmds.menuItem(l="displayLayer from selected", c=rig.display_layer_from_selection)
    cmds.menuItem(l="zeroed cube", c=partial(zeroed_geo, "cube"))
    cmds.menuItem(l="zeroed cylinder", c=partial(zeroed_geo, "cylinder"))
    cmds.menuItem(l="zeroed cone", c=partial(zeroed_geo, "cone"))
    widgets["zeroSelected"] = cmds.button(
        l="Zero Xforms",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=zero_xforms,
        ann=zAnn["zeroXform"],
    )
    widgets["prntChnBut"] = cmds.button(
        l="parent chain selected",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=parent_chain,
        ann=zAnn["prntChn"],
    )
    widgets["hideShp"] = cmds.button(
        l="shape vis toggle",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=hide_shape,
        ann=zAnn["shpVis"],
    )
    widgets["bBox"] = cmds.button(
        l="bounding box control", w=140, bgc=(0.5, 0.7, 0.5), c=bBox, ann=zAnn["bBox"]
    )
    widgets["remNSBut"] = cmds.button(
        l="remove all namespaces",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=remove_namespace,
        ann=zAnn["namespace"],
    )
    widgets["cntrJnt"] = cmds.button(
        l="joint at sel vtxs",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=center_joint,
        ann=zAnn["selVtxJnt"],
    )
    widgets["snapto"] = cmds.button(
        l="snap B to A", w=140, bgc=(0.5, 0.7, 0.5), c=snap_b_to_a, ann=zAnn["snap"]
    )
    widgets["constrain"] = cmds.button(
        l="Create Constraint..", w=140, bgc=(0.5, 0.7, 0.5), ann=zAnn["constraint"]
    )
    cmds.popupMenu(b=1)
    cmds.menuItem(
        l="parent - maintain offset", c=partial(create_constraint, "prnt", True)
    )
    cmds.menuItem(
        l="parent & scale - maintain offset",
        c=partial(create_constraint, "prntscl", True),
    )
    cmds.menuItem(
        l="point & orient - maintain offset",
        c=partial(create_constraint, "pntornt", True),
    )
    cmds.menuItem(
        l="point - maintain offset", c=partial(create_constraint, "pnt", True)
    )
    cmds.menuItem(
        l="orient - maintain offset", c=partial(create_constraint, "ornt", True)
    )
    cmds.menuItem(
        l="scale - maintain offset", c=partial(create_constraint, "scl", True)
    )
    cmds.menuItem(l="point - no offset", c=partial(create_constraint, "pnt", False))
    cmds.menuItem(l="orient - no offset", c=partial(create_constraint, "ornt", False))
    cmds.menuItem(l="parent - no offset", c=partial(create_constraint, "prnt", False))
    cmds.menuItem(l="scale - no offset", c=partial(create_constraint, "scl", False))
    widgets["centerPiv"] = cmds.button(
        l="Pivot..", w=140, bgc=(0.5, 0.7, 0.5), ann=zAnn["pivot"]
    )
    cmds.popupMenu(b=1)
    cmds.menuItem(l="Center Pivot", c=center_pivot)
    cmds.menuItem(l="Snap pivots to last", c=snap_pivot)
    cmds.menuItem(l="Snap pivots to origin", c=zero_pivot)
    widgets["clnJntBut"] = cmds.button(
        l="Clean Jnt Chain",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=clean_joints,
        ann=zAnn["cleanJnts"],
    )
    widgets["jntRot2Ornt"] = cmds.button(
        l="Jnt Rot->Orient",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=joint_rotate_to_orient,
        ann=zAnn["jntRot2Ornt"],
    )
    widgets["sftJntBut"] = cmds.button(
        l="Joint from softSel",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=partial(zAction, zRigDict, "softJoint"),
        ann=zAnn["softSelJnt"],
    )
    widgets["cpSkinWtsBut"] = cmds.button(
        l="copy skin & weights",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=copy_skinning,
        ann=zAnn["copySkin"],
    )
    widgets["selBindJnts"] = cmds.button(
        l="Select Bind Jnts",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=select_bind_joints_from_geo,
        ann=zAnn["selBind"],
    )
    widgets["shapesToAttr"] = cmds.button(
        l="BSs To Attr",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=shapes_to_channels,
        ann=zAnn["bsToAttr"],
    )
    widgets["faceCtrl"] = cmds.button(
        l="Limit Ctrl Setup",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=partial(zAction, zRigDict, "faceCtrl"),
        ann=zAnn["faceCtrl"],
    )
    widgets["negGrp"] = cmds.button(
        l="negateGrp",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=make_negate_group,
        ann=zAnn["negate"],
    )
    widgets["dupeBlends"] = cmds.button(
        l="dupeBlends",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=partial(zAction, zRigDict, "dupeBlends"),
        ann=zAnn["dupeBlend"],
    )
    widgets["rotateOrder"] = cmds.button(
        l="rotateOrder",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=rotate_order,
        ann=zAnn["rotateOrder"],
    )

    cmds.setParent(widgets["rigFLO"])
    widgets["zSmallFLO"] = cmds.formLayout(w=280, bgc=(0.3, 0.3, 0.3))
    widgets["zSmallFrLO"] = cmds.frameLayout(
        l="QUICK ACTIONS", w=280, bv=True, bgc=(0.0, 0.0, 0.0)
    )
    widgets["zSmallForm"] = cmds.formLayout(w=280, bgc=(0.3, 0.3, 0.3))

    widgets["deleteH"] = cmds.button(
        l="Del History",
        w=82,
        bgc=(0.5, 0.7, 0.5),
        c=partial(deleteH, 0),
        ann=zAnn["delHis"],
    )
    widgets["deleteNDH"] = cmds.button(
        l="Del ND History",
        w=82,
        bgc=(0.5, 0.5, 0.7),
        c=partial(deleteH, 1),
        ann=zAnn["delNDHis"],
    )
    widgets["deleteAnim"] = cmds.button(
        l="Del Animation",
        w=82,
        bgc=(0.7, 0.5, 0.5),
        c=partial(deleteH, 2),
        ann=zAnn["delAnim"],
    )

    widgets["freezeT"] = cmds.button(
        l="Freeze T",
        w=60,
        bgc=(0.7, 0.7, 0.7),
        c=partial(freeze, 1, 0, 0),
        ann=zAnn["freeze"],
    )
    widgets["freezeR"] = cmds.button(
        l="Freeze R",
        w=60,
        bgc=(0.7, 0.7, 0.7),
        c=partial(freeze, 0, 1, 0),
        ann=zAnn["freeze"],
    )
    widgets["freezeS"] = cmds.button(
        l="Freeze S",
        w=60,
        bgc=(0.7, 0.7, 0.7),
        c=partial(freeze, 0, 0, 1),
        ann=zAnn["freeze"],
    )
    widgets["freezeAll"] = cmds.button(
        l="Freeze All",
        w=60,
        bgc=(0.7, 0.7, 0.5),
        c=partial(freeze, 1, 1, 1),
        ann=zAnn["freeze"],
    )

    widgets["crvThkTxt"] = cmds.text(l="Curve Thick:", ann=zAnn["crvThk"])
    widgets["linThkBut"] = cmds.button(
        l="-", w=25, bgc=(0.7, 0.5, 0.5), c=partial(line_width, 0)
    )
    widgets["linThnBut"] = cmds.button(
        l="+", w=25, bgc=(0.5, 0.7, 0.5), c=partial(line_width, 1)
    )

    widgets["jntDrwTxt"] = cmds.text(l="Joint Draw:", ann=zAnn["jntDrw"])
    widgets["jntDrwOn"] = cmds.button(
        l="On", w=25, bgc=(0.5, 0.7, 0.5), c=partial(joint_draw, 0)
    )
    widgets["jntDrwOff"] = cmds.button(
        l="Off", w=25, bgc=(0.7, 0.5, 0.5), c=partial(joint_draw, 2)
    )

    widgets["jntSizeTxt"] = cmds.text(l="Joint Size:", ann=zAnn["jntSz"])
    widgets["jntSizeUp"] = cmds.button(
        l="+", w=25, bgc=(0.5, 0.7, 0.5), c=partial(size_joints, 1)
    )
    widgets["jntSizeDn"] = cmds.button(
        l="-", w=25, bgc=(0.7, 0.5, 0.5), c=partial(size_joints, 0)
    )

    widgets["lraTxt"] = cmds.text(l="Loc Rot Ax:", ann=zAnn["lra"])
    widgets["lraOff"] = cmds.button(
        l="Off", w=25, bgc=(0.7, 0.5, 0.5), c=partial(lra_toggle, 0)
    )
    widgets["lraOn"] = cmds.button(
        l="On", w=25, bgc=(0.5, 0.7, 0.5), c=partial(lra_toggle, 1)
    )

    widgets["tooltipsTxt"] = cmds.text(l="Tooltips:", ann=zAnn["tips"])
    widgets["tooltipsOff"] = cmds.button(
        l="Off", w=25, bgc=(0.7, 0.5, 0.5), c=partial(toggle_tooltips, 0)
    )
    widgets["tooltipsOn"] = cmds.button(
        l="On", w=25, bgc=(0.5, 0.7, 0.5), c=partial(toggle_tooltips, 1)
    )

    widgets["lockTxt"] = cmds.text(l="Lock Objs:", ann=zAnn["lock"])
    widgets["lockOff"] = cmds.button(
        l="Off", w=25, bgc=(0.7, 0.5, 0.5), c=partial(toggle_lock, 0)
    )
    widgets["lockOn"] = cmds.button(
        l="On", w=25, bgc=(0.5, 0.7, 0.5), c=partial(toggle_lock, 1)
    )

    cmds.formLayout(
        widgets["zSmallForm"],
        e=True,
        af=[
            (widgets["deleteH"], "left", 5),
            (widgets["deleteH"], "top", 0),
            (widgets["deleteNDH"], "left", 98),
            (widgets["deleteNDH"], "top", 0),
            (widgets["deleteAnim"], "left", 193),
            (widgets["deleteAnim"], "top", 0),
            (widgets["freezeT"], "left", 5),
            (widgets["freezeT"], "top", 30),
            (widgets["freezeR"], "left", 70),
            (widgets["freezeR"], "top", 30),
            (widgets["freezeS"], "left", 135),
            (widgets["freezeS"], "top", 30),
            (widgets["freezeAll"], "left", 215),
            (widgets["freezeAll"], "top", 30),
            (widgets["crvThkTxt"], "left", 5),
            (widgets["crvThkTxt"], "top", 65),
            (widgets["linThkBut"], "left", 70),
            (widgets["linThkBut"], "top", 60),
            (widgets["linThnBut"], "left", 100),
            (widgets["linThnBut"], "top", 60),
            (widgets["jntDrwTxt"], "left", 150),
            (widgets["jntDrwTxt"], "top", 65),
            (widgets["jntDrwOff"], "left", 220),
            (widgets["jntDrwOff"], "top", 60),
            (widgets["jntDrwOn"], "left", 250),
            (widgets["jntDrwOn"], "top", 60),
            (widgets["jntSizeTxt"], "left", 5),
            (widgets["jntSizeTxt"], "top", 95),
            (widgets["jntSizeDn"], "left", 70),
            (widgets["jntSizeDn"], "top", 90),
            (widgets["jntSizeUp"], "left", 100),
            (widgets["jntSizeUp"], "top", 90),
            (widgets["lraTxt"], "left", 150),
            (widgets["lraTxt"], "top", 95),
            (widgets["lraOff"], "left", 220),
            (widgets["lraOff"], "top", 90),
            (widgets["lraOn"], "left", 250),
            (widgets["lraOn"], "top", 90),
            (widgets["lockTxt"], "left", 5),
            (widgets["lockTxt"], "top", 125),
            (widgets["lockOff"], "left", 70),
            (widgets["lockOff"], "top", 120),
            (widgets["lockOn"], "left", 100),
            (widgets["lockOn"], "top", 120),
            (widgets["tooltipsTxt"], "left", 150),
            (widgets["tooltipsTxt"], "top", 125),
            (widgets["tooltipsOff"], "left", 220),
            (widgets["tooltipsOff"], "top", 120),
            (widgets["tooltipsOn"], "left", 250),
            (widgets["tooltipsOn"], "top", 120),
        ],
    )

    # TODO -- add hide ai attributes
    # script Layout
    cmds.setParent(widgets["rigFLO"])
    widgets["zScrptFLO"] = cmds.formLayout(w=280, bgc=(0.3, 0.3, 0.3))
    widgets["zScrptFrLO"] = cmds.frameLayout(
        l="SCRIPTS - UI", w=280, bv=True, bgc=(0.0, 0.0, 0.0)
    )
    widgets["rigScriptsRCLO"] = cmds.rowColumnLayout(w=280, nc=2)
    widgets["attrBut"] = cmds.button(
        l="zbw_attrs",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "attr"),
        ann=zAnn["attrs"],
    )
    widgets["shpSclBut"] = cmds.button(
        l="zbw_shapeScale",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "shpScl"),
        ann=zAnn["shpScl"],
    )
    widgets["selBufBut"] = cmds.button(
        l="zbw_selectionBuffer",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "selBuf"),
        ann=zAnn["selBuf"],
    )
    widgets["snapBut"] = cmds.button(
        l="zbw_snap",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "snap"),
        ann=zAnn["zSnap"],
    )
    widgets["follBut"] = cmds.button(
        l="zbw_makeFollicle",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "foll"),
        ann=zAnn["fol"],
    )
    widgets["jntRadBut"] = cmds.button(
        l="zbw_jointRadius",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "jntRadius"),
        ann=zAnn["jntRad"],
    )
    widgets["proxyGeoBut"] = cmds.button(
        l="zbw_createProxyGeo",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zClassAction, zRigDict, "proxyGeo"),
        ann=zAnn["proxy"],
    )
    widgets["proxyGeoBut"] = cmds.button(
        l="zbw_poseReader",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "poseReader"),
        ann=zAnn["pose"],
    )
    widgets["sinCreateBut"] = cmds.button(
        l="zbw_sineCreator",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "sineCreator"),
        ann=zAnn["sineCreator"],
    )
    widgets["swapRigGeo"] = cmds.button(
        l="zbw_swap_rig_geo",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "swapRigGeo"),
        ann=zAnn["swapRigGeo"],
    )
    widgets["message"] = cmds.button(
        l="zbw_message_manager",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "messageManager"),
        ann=zAnn["messageManager"],
    )
    widgets["cmtRename"] = cmds.button(
        l="cometRename",
        w=140,
        bgc=(0.5, 0.5, 0.5),
        c=partial(zMelAction, zRigDict, "cmtRename"),
        ann=zAnn["rename"],
    )
    widgets["cmtJntOrnt"] = cmds.button(
        l="cometJntOrient",
        w=140,
        bgc=(0.5, 0.5, 0.5),
        c=partial(zMelAction, zRigDict, "cmtJntOrnt"),
        ann=zAnn["jntOrient"],
    )
    widgets["animPolish"] = cmds.button(
        l="animPolish",
        w=140,
        bgc=(0.5, 0.5, 0.5),
        c=partial(zAction, zRigDict, "animPolish"),
        ann=zAnn["animPolish"],
    )

    # color layout
    cmds.setParent(widgets["rigFLO"])
    widgets["colorFLO"] = cmds.formLayout(w=280, h=66, bgc=(0.3, 0.3, 0.3))
    widgets["colorFrLO"] = cmds.frameLayout(
        l="COLORS", w=280, h=66, bv=True, bgc=(0.0, 0.0, 0.0), ann=zAnn["color"]
    )
    widgets["colorRCLO"] = cmds.rowColumnLayout(nc=6)
    colorw = 280 / 6
    widgets["redCNV"] = cmds.canvas(
        w=colorw, h=20, rgb=(1, 0, 0), pc=partial(changeColor, colors["red"])
    )
    widgets["pinkCNV"] = cmds.canvas(
        w=colorw, h=20, rgb=(1, 0.8, 0.965), pc=partial(changeColor, colors["pink"])
    )
    widgets["blueCNV"] = cmds.canvas(
        w=colorw, h=20, rgb=(0, 0, 1), pc=partial(changeColor, colors["blue"])
    )
    widgets["ltBlueCNV"] = cmds.canvas(
        w=colorw, h=20, rgb=(0.65, 0.8, 1), pc=partial(changeColor, colors["lightBlue"])
    )
    widgets["greenCNV"] = cmds.canvas(
        w=colorw, h=20, rgb=(0, 1, 0), pc=partial(changeColor, colors["green"])
    )
    widgets["dkGreenCNV"] = cmds.canvas(
        w=colorw, h=20, rgb=(0, 0.35, 0), pc=partial(changeColor, colors["darkGreen"])
    )
    widgets["yellowCNV"] = cmds.canvas(
        w=colorw, h=20, rgb=(1, 1, 0), pc=partial(changeColor, colors["yellow"])
    )
    widgets["brownCNV"] = cmds.canvas(
        w=colorw, h=20, rgb=(0.5, 0.275, 0), pc=partial(changeColor, colors["brown"])
    )
    widgets["purpleCNV"] = cmds.canvas(
        w=colorw, h=20, rgb=(0.33, 0, 0.33), pc=partial(changeColor, colors["purple"])
    )
    widgets["dkPurpleCNV"] = cmds.canvas(
        w=colorw,
        h=20,
        rgb=(0.15, 0, 0.25),
        pc=partial(changeColor, colors["darkPurple"]),
    )
    widgets["dkRedCNV"] = cmds.canvas(
        w=colorw, h=20, rgb=(0.5, 0.0, 0), pc=partial(changeColor, colors["darkRed"])
    )
    widgets["ltBrownCNV"] = cmds.canvas(
        w=colorw,
        h=20,
        rgb=(0.7, 0.5, 0.0),
        pc=partial(changeColor, colors["lightBrown"]),
    )
    # formlayout stuff
    cmds.formLayout(
        widgets["rigFLO"],
        e=True,
        af=[
            (widgets["ctrlFLO"], "left", 0),
            (widgets["ctrlFLO"], "top", 0),
            (widgets["actionFLO"], "left", 0),
            (widgets["actionFLO"], "top", 50),
            (widgets["zSmallFLO"], "left", 0),
            (widgets["zSmallFLO"], "top", 350),
            (widgets["zScrptFLO"], "left", 0),
            (widgets["zScrptFLO"], "top", 585),
            (widgets["colorFLO"], "left", 0),
            (widgets["colorFLO"], "top", 515),
        ],
    )

    cmds.setParent(widgets["tab"])
    widgets["rigsCLO"] = cmds.columnLayout("RIGS", w=280)
    widgets["rigsPropFrameLO"] = cmds.frameLayout(
        l="PROP RIGGING", w=280, bv=True, bgc=(0, 0, 0)
    )
    widgets["rigsPropRCLO"] = cmds.rowColumnLayout(nc=2, bgc=(0.3, 0.3, 0.3))
    widgets["sftDefBut"] = cmds.button(
        l="Soft Deformers",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "softMod"),
        ann=zAnn["softDef"],
    )
    widgets["RcrvTools"] = cmds.button(
        l="Curve Tools",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "crvTools"),
        ann=zAnn["crvTools"],
    )
    widgets["smIKBut"] = cmds.button(
        l="Single Jnt IK",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "smIK"),
        ann=zAnn["singleIK"],
    )
    widgets["autoSqBut"] = cmds.button(
        l="AutoSquash Rig",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "autoSquash"),
        ann=zAnn["squash"],
    )
    widgets["wireBut"] = cmds.button(
        l="Wire Def Rig",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "wire"),
        ann=zAnn["wireDef"],
    )

    cmds.setParent(widgets["rigsCLO"])
    widgets["rigsCharFrameLO"] = cmds.frameLayout(
        l="CHARACTER RIGGING", w=280, bv=True, bgc=(0, 0, 0)
    )
    widgets["rigsCharRCLO"] = cmds.rowColumnLayout(nc=2, bgc=(0.3, 0.3, 0.3))
    widgets["legBut"] = cmds.button(
        l="Leg Rig",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zClassAction, zRigDict, "leg"),
        ann=zAnn["legRig"],
    )
    widgets["armBut"] = cmds.button(
        l="Arm Rig",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zClassAction, zRigDict, "arm"),
        ann=zAnn["armRig"],
    )
    widgets["ikSpine"] = cmds.button(
        l="ikfkSpine",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zClassAction, zRigDict, "ikfkSpine"),
        ann=zAnn["spine"],
    )
    widgets["handBut"] = cmds.button(
        l="handRig",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zClassAction, zRigDict, "handRig"),
        ann=zAnn["hand"],
    )
    widgets["mgRig"] = cmds.button(
        l="eyelidRig",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zClassAction, zRigDict, "eyelidRig"),
        ann=zAnn["eye"],
    )

    cmds.setParent(widgets["rigsCLO"])
    widgets["rigsCharTFrameLO"] = cmds.frameLayout(
        l="CHARACTER TOOLS", w=280, bv=True, bgc=(0, 0, 0)
    )
    widgets["rigsCharTRCLO"] = cmds.rowColumnLayout(nc=2, bgc=(0.3, 0.3, 0.3))
    widgets["ribBut"] = cmds.button(
        l="Ribbon Rig",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "ribbon"),
        ann=zAnn["ribbon"],
    )
    widgets["splineBut"] = cmds.button(
        l="Spline IK Rig",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "splineIK"),
        ann=zAnn["spline"],
    )
    widgets["followBut"] = cmds.button(
        l="Follow Constraints",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "follow"),
        ann=zAnn["followCnstr"],
    )

    cmds.setParent(widgets["tab"])
    widgets["modelLgtCLO"] = cmds.columnLayout("MDL_LGT", w=280)
    # curve tools, model scripts, add to lattice, select hierarchy, snap selection buffer, transform buffer
    widgets["mdlMdlFrameLO"] = cmds.frameLayout(
        l="MODELING", w=280, bv=True, bgc=(0, 0, 0)
    )
    widgets["mdlPropRCLO"] = cmds.rowColumnLayout(nc=2, bgc=(0.3, 0.3, 0.3))
    widgets["wrinkle"] = cmds.button(
        l="zbw_wrinklePoly",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zModelDict, "wrinkle"),
        ann=zAnn["wrinkle"],
    )
    widgets["McrvTools"] = cmds.button(
        l="zbw_curveTools",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "crvTools"),
        ann=zAnn["crvTools"],
    )
    widgets["MtrnBuffer"] = cmds.button(
        l="zbw_transformBuffer",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "trfmBuffer"),
        ann=zAnn["xformBuffer"],
    )
    widgets["MrandomSel"] = cmds.button(
        l="zhw_randomSel",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zAnimDict, "randomSel"),
        ann=zAnn["rndSel"],
    )
    widgets["MselBufBut"] = cmds.button(
        l="zbw_selectionBuffer",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "selBuf"),
        ann=zAnn["selBuf"],
    )
    widgets["MsnapBut"] = cmds.button(
        l="zbw_snap",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zRigDict, "snap"),
        ann=zAnn["zSnap"],
    )
    widgets["McmtRename"] = cmds.button(
        l="cometRename",
        w=140,
        bgc=(0.5, 0.5, 0.5),
        c=partial(zMelAction, zRigDict, "cmtRename"),
        ann=zAnn["rename"],
    )
    widgets["cube"] = cmds.button(
        l="zeroed cube",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=partial(zeroed_geo, "cube"),
        ann="create zeroed cube",
    )
    widgets["cylinder"] = cmds.button(
        l="zeroed cylinder",
        w=140,
        bgc=(0.5, 0.7, 0.5),
        c=partial(zeroed_geo, "cylinder"),
        ann="create zeroed cylinder",
    )

    cmds.setParent(widgets["modelLgtCLO"])
    widgets["lgtFrameLO"] = cmds.frameLayout(
        l="LIGHTING RENDER", w=280, bv=True, bgc=(0, 0, 0)
    )
    widgets["lgtPropRCLO"] = cmds.rowColumnLayout(nc=2, bgc=(0.3, 0.3, 0.3))
    widgets["transfer"] = cmds.button(
        l="zbw_shadingTransfer",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zShdDict, "shdTransfer"),
        ann=zAnn["shdTransfer"],
    )
    widgets["previsShd"] = cmds.button(
        l="zbw_previsShaders",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zShdDict, "prvsShd"),
        ann=zAnn["previsShd"],
    )
    widgets["typFindBut"] = cmds.button(
        l="zbw_typeFinder",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zModelDict, "typFind"),
        ann=zAnn["typeFinder"],
    )

    cmds.setParent(widgets["tab"])
    widgets["animCLO"] = cmds.columnLayout("ANIM", w=280)
    widgets["animFrameLO"] = cmds.frameLayout(
        l="ANIMATION", w=280, bv=True, bgc=(0, 0, 0)
    )
    widgets["animRCLO"] = cmds.rowColumnLayout(nc=2, bgc=(0.3, 0.3, 0.3))
    widgets["tween"] = cmds.button(
        l="tween machine",
        w=140,
        bgc=(0.5, 0.5, 0.5),
        c=partial(zAction, zAnimDict, "tween"),
        ann=zAnn["tween"],
    )
    widgets["noise"] = cmds.button(
        l="zbw_animNoise",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zAnimDict, "noise"),
        ann=zAnn["animNoise"],
    )
    widgets["audio"] = cmds.button(
        l="zbw_audioManager",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zAnimDict, "audio"),
        ann=zAnn["audio"],
    )
    widgets["clean"] = cmds.button(
        l="zbw_cleanKeys",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zAnimDict, "clean"),
        ann=zAnn["clean"],
    )
    widgets["dupe"] = cmds.button(
        l="zbw_dupeSwap",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zAnimDict, "dupe"),
        ann=zAnn["dupeSwap"],
    )
    widgets["huddle"] = cmds.button(
        l="zbw_huddle",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zAnimDict, "huddle"),
        ann=zAnn["huddle"],
    )
    widgets["pulldown"] = cmds.button(
        l="zbw_animPulldown",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zAnimDict, "pulldown"),
        ann=zAnn["pulldown"],
    )
    widgets["randomSel"] = cmds.button(
        l="zhw_randomSel",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zAnimDict, "randomSel"),
        ann=zAnn["rndSel"],
    )
    widgets["randomAttr"] = cmds.button(
        l="zbw_randomAttr",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zAnimDict, "randomAttr"),
        ann=zAnn["rndAttr"],
    )
    widgets["clip"] = cmds.button(
        l="zbw_setClipPlanes",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zAnimDict, "clip"),
        ann=zAnn["clip"],
    )
    widgets["tangents"] = cmds.button(
        l="zbw_tangents",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=partial(zAction, zAnimDict, "tangents"),
        ann=zAnn["tangents"],
    )
    widgets["studLib"] = cmds.button(
        l="Studio Library",
        w=140,
        bgc=(0.5, 0.5, 0.5),
        c=partial(zAction, zAnimDict, "studioLib"),
        ann=zAnn["studioLib"],
    )
    widgets["atools"] = cmds.button(
        l="animBot",
        w=140,
        bgc=(0.5, 0.5, 0.5),
        c=partial(zAction, zAnimDict, "animBot"),
        ann=zAnn["animBot"],
    )

    # ---------------- reset cameras? change (reset) overcan to 0.8 in userPrefs?
    cmds.setParent(widgets["tab"])
    widgets["miscCLO"] = cmds.columnLayout("MISC", w=280)
    widgets["miscFrameLO"] = cmds.frameLayout(
        l="MISCELLANEOUS", w=280, bv=True, bgc=(0, 0, 0)
    )
    widgets["miscRCLO"] = cmds.rowColumnLayout(nc=2, bgc=(0.3, 0.3, 0.3))
    widgets["saveScrpt"] = cmds.button(
        l="save script win",
        w=140,
        bgc=(0.7, 0.5, 0.5),
        c=save_script_win,
        ann=zAnn["saveScript"],
    )
    widgets["monWin"] = cmds.button(
        l="window cleanup", w=140, bgc=(0.7, 0.5, 0.5), ann=zAnn["windows"]
    )

    cmds.window(widgets["win"], e=True, rtf=True, w=5, h=5)
    cmds.showWindow(widgets["win"])


##########
# functions
##########


def control(type="none", *args):
    """
    gets the name from the button pushed and the axis from the radio button group
    and creates a control at the origin
    """
    axisRaw = cmds.radioButtonGrp(widgets["ctrlAxisRBG"], q=True, sl=True)
    if axisRaw == 1:
        axis = "x"
    if axisRaw == 2:
        axis = "y"
    if axisRaw == 3:
        axis = "z"

    rig.create_control(name="Ctrl", type=type, axis=axis, color="yellow")


def swap(type="none", *args):
    """swap shape of selected ctrls to 'type'"""
    axisRaw = cmds.radioButtonGrp(widgets["ctrlAxisRBG"], q=True, sl=True)
    if axisRaw == 1:
        axis = "x"
    if axisRaw == 2:
        axis = "y"
    if axisRaw == 3:
        axis = "z"

    rig.swap_shape(type=type, axis=axis, scale=1.0, color=None)


def zAction(dic=None, action=None, *args):
    """
    grabs the action key from the given dictionary
    then imports the first value (module), reloads it
    then gets the function from the second value and runs that
    """
    if action and dic:
        funcName = dic[action][1]
        mod = importlib.import_module(dic[action][0])
        importlib.reload(mod)
        func = getattr(mod, funcName)
        func()

    else:
        cmds.warning(
            "zbw_tools.zAction: There was a problem with either the key or the dictionary given! (key: {0}, "
            "action: {1}".format(action, dic)
        )


def zMelAction(dic=None, action=None, *args):
    """calls mel cmd from dict, and evals it"""
    print((dic[action][0]))
    mel.eval(dic[action][0])


def zClassAction(dic=None, action=None, *args):
    """class import from action[0], then runs code from action[1]"""
    if action and dic:
        funcName = dic[action][1]
        mod = importlib.import_module(dic[action][0])
        importlib.reload(mod)
        func = getattr(mod, funcName)
        func()

    else:
        cmds.warning(
            "zbw_tools.zAction: There was a problem with either the key or the dictionary given! (key: {0}, "
            "action: {1}".format(action, dic)
        )


def snap_b_to_a(*args):
    """
    snaps 2nd selection to 1st, translate and rotate. Transforms only
    """
    sel = cmds.ls(sl=True, type="transform")
    if sel and len(sel) > 1:
        src = sel[0]
        tgt = sel[1:]
        for t in tgt:
            rig.snap_to(src, t)


def joint_rotate_to_orient(*args):
    sel = cmds.ls(sl=True)

    for obj in sel:
        rot = cmds.getAttr(obj + ".r")[0]
        cmds.setAttr(obj + ".jointOrientX", rot[0])
        cmds.setAttr(obj + ".jointOrientY", rot[1])
        cmds.setAttr(obj + ".jointOrientZ", rot[2])
        cmds.setAttr(obj + ".r", 0, 0, 0)


def make_negate_group(*args):
    sel = cmds.ls(sl=True)
    if not sel:
        cmds.warning(
            "zTools.make_negate_group: select one or more transforms to negate"
        )
        return ()

    for obj in sel:
        rig.create_negate_group(obj=obj, suffix="GRP")


def rotate_order(*args):
    sel = cmds.ls(sl=True, type="transform")
    if not sel:
        return ()
    ctrl = sel[0]
    cmds.addAttr(
        ctrl,
        ln="rot_order",
        nn="rotation_order",
        at="enum",
        en="xyz:yzx:zxy:xzy:yxz:zyx",
        k=True,
        dv=0,
    )
    for obj in sel:
        cmds.connectAttr(ctrl + ".rot_order", obj + ".rotateOrder")


def invert_shape(*args):
    """
    just runs the maya cmd to invert the shape. I belive it's based on
    selecting bound shape after modified shape
    """
    # assign a shader to this. . .
    cmds.invertShape()


def zero_pivot(*args):
    """puts pivots zeroed at origin"""
    sel = cmds.ls(sl=True, transforms=True)
    rig.zero_pivot(sel)


def clean_joints(*args):
    """
    unrotates joints and orients them to current settings
    """
    sel = cmds.ls(sl=True, type="joint")
    if sel:
        jnt = sel[0]
        rig.clean_joint_chain(jnt)
        # cmds.joint(jnt, edit=True, orientJoint="xyz", secondaryAxisOrient="yup", ch=True)


def freeze(t=1, r=1, s=1, *args):
    """
    freeze given channels
    """
    sel = cmds.ls(sl=True)
    cmds.makeIdentity(sel, t=t, r=r, s=s, apply=True)


def deleteH(mode, *args):
    """
    deletes history based on mode. 0 is history, 1 is non-deformer, anything else is non-deformer hist
    """
    sel = cmds.ls(sl=True)
    if not sel:
        return ()
    if mode == 0:
        cmds.delete(sel, ch=True)
    if mode == 1:
        cmds.bakePartialHistory(sel, prePostDeformers=True)
    if mode == 2:
        check = cmds.confirmDialog(
            title="Delete Anim?",
            message="Delete time based anim?",
            button=["Yes", "No"],
            defaultButton="Yes",
            cancelButton="No",
            dismissString="No",
        )
        if check == "No":
            return ()
        cmds.delete(
            sel, c=True, timeAnimationCurves=True, unitlessAnimationCurves=False
        )


def zeroed_geo(gtype, *args):
    """creates geo with pivot at origin"""
    geo = None
    if gtype == "cube":
        geo = cmds.polyCube()
        cmds.xform(geo, ws=True, t=(0, 0.5, 0))
        cmds.xform(geo, ws=True, piv=(0, 0, 0))
    if gtype == "cylinder":
        geo = cmds.polyCylinder()
        cmds.xform(geo, ws=True, t=(0, 1, 0))
        cmds.xform(geo, ws=True, piv=(0, 0, 0))
    if gtype == "cone":
        geo = cmds.polyCone()
        cmds.xform(geo, ws=True, t=(0, 1, 0))
        cmds.xform(geo, ws=True, piv=(0, 0, 0))
    cmds.select(geo, r=True)
    freeze()


def save_script_win(*args):
    """saves scripts currently in script editor"""
    mel.eval("syncExecuterBackupFiles")


def line_width(mode, *args):
    """
    thickens or thins selected nurbs curves (for display only)
    """
    sel = cmds.ls(sl=True)
    if sel:
        for obj in sel:
            if rig.type_check(obj, "nurbsCurve"):
                shps = cmds.listRelatives(obj, s=True)
                if shps:
                    for shp in shps:
                        val = cmds.getAttr("{0}.lineWidth".format(shp))
                        if mode == 0:
                            if val <= 1:
                                continue
                            else:
                                val -= 0.5
                        elif mode == 1:
                            if val <= 1:
                                val = 1.5
                            else:
                                val += 0.5
                        cmds.setAttr("{0}.lineWidth".format(shp), val)


def joint_draw(value, *args):
    """turns on/off the joint draw attributes"""
    jnts = cmds.ls(type="joint")
    for jnt in jnts:
        cmds.setAttr("{0}.drawStyle".format(jnt), value)


def size_joints(mode, *args):
    """
    scales up down joint size (by 1.5 or 0.5 respectively)
    """
    jnts = cmds.ls(type="joint")
    for jnt in jnts:
        jntRad = cmds.getAttr("{0}.radius".format(jnt))
        if mode == 0:
            jntRad *= 0.5
        elif mode == 1:
            jntRad *= 1.5

        if jntRad < 0.01:
            jntRad = 0.01
        cmds.setAttr("{0}.radius".format(jnt), jntRad)


def lra_toggle(value, *args):
    """toggles local rotate axes on/off"""
    sel = cmds.ls(sl=True)
    for obj in sel:
        cmds.setAttr("{0}.displayLocalAxis".format(obj), value)


def center_pivot(*args):
    """centers pivot on selected"""
    sel = cmds.ls(sl=True)
    for obj in sel:
        cmds.xform(obj, cp=True, p=True)


def snap_pivot(*args):
    sel = cmds.ls(sl=True)

    if not sel or len(sel) == 1:
        return ()

    src = sel[-1]
    tgts = sel[:-1]

    pos = cmds.xform(src, q=True, ws=True, rp=True)
    for tgt in tgts:
        cmds.xform(tgt, ws=True, piv=pos)


def show_hide_in_panels(objs, *args):
    """polys, curves, joints, jointsOff, polyCurve, showAll"""
    panels = cmds.getPanel(type="modelPanel")
    for p in panels:
        if (
            objs == "polys"
            or objs == "curves"
            or objs == "joints"
            or objs == "polyCurve"
        ):
            cmds.modelEditor(p, e=True, allObjects=False)
        if objs == "polys" or objs == "polyCurve":
            cmds.modelEditor(p, e=True, polymeshes=True)
        if objs == "curves" or objs == "polyCurve":
            cmds.modelEditor(p, e=True, nurbsCurves=True)
        if objs == "joints":
            cmds.modelEditor(p, e=True, joints=True)
        if objs == "jointsOff":
            cmds.modelEditor(p, e=True, joints=False)
        if objs == "showAll":
            cmds.modelEditor(p, e=True, allObjects=True)


def create_joint(*args):
    cmds.select(cl=True)
    cmds.joint()


def create_master_pack(self):
    mst1 = rig.create_control(
        name="master_CTRL", type="arrowCircle", axis="y", color="green"
    )
    mst2 = rig.create_control(
        name="master_sub1_CTRL", type="circle", axis="y", color="darkGreen"
    )
    mst2Grp = rig.group_freeze(mst2)
    mst3 = rig.create_control(
        name="master_sub2_CTRL", type="circle", axis="y", color="yellowGreen"
    )
    mst3Grp = rig.group_freeze(mst3)

    rig.scale_nurbs_control(mst1, 3, 3, 3, origin=True)
    rig.scale_nurbs_control(mst2, 2.5, 2.5, 2.5)
    rig.scale_nurbs_control(mst3, 2, 2, 2)

    cmds.parent(mst3Grp, mst2)
    cmds.parent(mst2Grp, mst1)

    geoGrp = cmds.group(empty=True, name="GEO")
    geoNoXform = cmds.group(empty=True, name="GEO_noTransform")
    cmds.setAttr("{0}.inheritsTransform".format(geoNoXform), 0)
    geoXform = cmds.group(empty=True, name="GEO_transform")

    rigGrp = cmds.group(empty=True, name="RIG")
    rigNoXform = cmds.group(empty=True, name="RIG_noTransform")
    cmds.setAttr("{0}.inheritsTransform".format(rigNoXform), 0)
    rigXform = cmds.group(empty=True, name="RIG_transform")

    cmds.parent([geoXform, geoNoXform], geoGrp)
    cmds.parent([rigNoXform, rigXform], rigGrp)
    cmds.parent([geoGrp, rigGrp], mst3)


def extract_deltas(*args):
    # check plug is loaded
    rig.plugin_load("extractDeltas")
    mel.eval("performExtractDeltas")


def parent_scale_constrain(*args):
    """just creates a parent and scale transform on the tgt object"""
    sel = cmds.ls(sl=True, type="transform")
    if not (sel and len(sel) == 2):
        cmds.warning("You need to select two tranform objects!")
        return ()
    src = sel[0]
    tgt = sel[1]
    cmds.parentConstraint(src, tgt, mo=True)
    cmds.scaleConstraint(src, tgt)


def remove_namespace(*args):
    """removes namespaces . . ."""
    ns = rmns.remove_namespaces()
    if ns:
        print(("Removed namespaces: ", ns))
    else:
        print("Did not delete any namespaces!")


def add_to_deformer(*args):
    """
    select lattice then geo to add to the lattice
    """
    sel = cmds.ls(sl=True)
    if len(sel) < 2:
        cmds.warning("Need to select the deformer, then some geometry")
        return ()
    deformer = sel[0]
    geo = sel[1:]
    rig.add_geo_to_deformer(deformer, geo)


def group_freeze(*args):
    """group freeze an obj"""

    sel = cmds.ls(sl=True, type="transform")
    for obj in sel:
        rig.group_freeze(obj)


def select_hierarchy(sType, *args):
    """
    select top node(s) and this will (inclusively) select all the xforms below it of the given type ('curve', 'poly', 'joint')
    """
    sel = cmds.ls(sl=True, type="transform")
    selectList = []

    for top in sel:
        xforms = []
        cshps = None
        if sType == "curve":
            cshps = cmds.listRelatives(
                top, allDescendents=True, f=True, type="nurbsCurve"
            )
        elif sType == "poly":
            cshps = cmds.listRelatives(top, allDescendents=True, f=True, type="mesh")
        if cshps:
            for cshp in cshps:
                xf = cmds.listRelatives(cshp, p=True, f=True)[0]
                xforms.append(xf)
        elif sType == "joint":
            jnts = cmds.listRelatives(top, allDescendents=True, f=True, type="joint")
            if rig.type_check(top, "joint"):
                jnts.append(top)
            xforms = jnts

        if xforms:
            # sort list by greatest number of path splits first (deepest)
            xforms.sort(key=lambda a: a.count("|"), reverse=True)
            list(set(xforms))
            for x in xforms:
                selectList.append(x)

    cmds.select(selectList, r=True)


def freeze_and_connect(*args):
    sel = cmds.ls(sl=True)
    ctrlOrig = sel[0]
    grpList = []
    ctrlList = []

    for x in range(1, len(sel)):

        pos = cmds.xform(sel[x], ws=True, q=True, rp=True)
        rot = cmds.xform(sel[x], ws=True, q=True, ro=True)

        ctrl = cmds.duplicate(ctrlOrig, n="{}Ctrl".format(sel[x]))[0]
        grp = rig.group_freeze(ctrl)

        rig.snap_to(sel[x], grp)
        cmds.parentConstraint(ctrl, sel[x])
        cmds.scaleConstraint(ctrl, sel[x])
        grpList.append(grp)
        ctrlList.append(ctrl)

    zipList = list(zip(sel[1:], grpList, ctrlList))

    for i in range(len(zipList)):
        parID = None
        par = cmds.listRelatives(zipList[i][0], p=True)
        if par:
            try:
                parID = sel.index(par[0]) - 1
                parCtrl = zipList[parID][2]
                cmds.parent(zipList[i][1], parCtrl)
            except:
                pass

    cmds.delete(sel[0])
    return (ctrlList, grpList)


def parent_chain(*args):
    # parent chain (select objs, child first. WIll parent in order selected)

    sel = cmds.ls(sl=True)
    sizeSel = len(sel)
    for x in range(0, sizeSel - 1):
        cmds.parent(sel[x], sel[x + 1])


def select_hi(*args):
    cmds.select(hi=True)


def select_components(*args):
    sel = cmds.ls(sl=True)
    if sel:
        for obj in sel:
            shape = cmds.listRelatives(obj, s=True)[0]

            if cmds.objectType(shape) == "nurbsCurve":
                cmds.select(cmds.ls("{}.cv[*]".format(obj), fl=True))
            elif cmds.objectType(shape) == "mesh":
                cmds.select(cmds.ls("{}.vtx[*]".format(obj), fl=True))
            else:
                return


def hammer_skin_weights(*args):
    mel.eval("weightHammerVerts")


def create_locator(*args):
    cmds.spaceLocator()


def changeColor(color, *args):
    """change shape color of selected objs"""

    sel = cmds.ls(sl=True)

    if sel:
        for obj in sel:
            shapes = cmds.listRelatives(obj, s=True)
            if shapes:
                for shape in shapes:
                    cmds.setAttr("%s.overrideEnabled" % shape, 1)
                    cmds.setAttr("%s.overrideColor" % shape, color)


def create_constraint(ctype, offset=True, *args):
    sel = cmds.ls(sl=True, type="transform")
    if len(sel) < 2:
        return ()
    if "prnt" in ctype:
        cmds.parentConstraint(mo=offset)
    if "pnt" in ctype:
        cmds.pointConstraint(mo=offset)
    if "ornt" in ctype:
        cmds.orientConstraint(mo=offset)
    if "scl" in ctype:
        cmds.scaleConstraint(mo=offset)


def select_bind_joints_from_geo(*args):
    """selects bind joints from selected geo"""
    jnts = rig.get_bind_joints_from_geo()
    cmds.select(jnts, r=True)


def copy_skinning(*args):
    """select the orig bound mesh, then the new unbound target mesh and run"""

    sel = cmds.ls(sl=True)
    orig = sel[0]
    targets = sel[1:]

    for target in targets:
        try:
            jnts = cmds.skinCluster(orig, q=True, influence=True)
        except:
            cmds.warning("couldn't get skin weights from {0}".format(orig))
        try:
            targetClus = cmds.skinCluster(
                jnts,
                target,
                bindMethod=0,
                skinMethod=0,
                normalizeWeights=1,
                maximumInfluences=3,
                obeyMaxInfluences=False,
                tsb=True,
            )[0]
        except:
            cmds.warning("couln't bind to {}".format(target))
        origClus = mel.eval("findRelatedSkinCluster " + orig)
        # copy skin weights from orig to target
        try:
            cmds.copySkinWeights(
                ss=origClus,
                ds=targetClus,
                noMirror=True,
                sa="closestPoint",
                ia="closestJoint",
            )
        except:
            cmds.warning(
                "couldn't copy skin weights from {0} to {1}".format(orig, target)
            )


def zero_xforms(*args):
    sel = cmds.ls(sl=True, type="transform")
    if not sel:
        return ()
    for obj in sel:
        cmds.setAttr("{0}.translate".format(obj), 0, 0, 0)
        cmds.setAttr("{0}.rotate".format(obj), 0, 0, 0)
        cmds.setAttr("{0}.scale".format(obj), 1, 1, 1)


def toggle_tooltips(state, *args):
    cmds.help(popupMode=state)


def toggle_lock(state, *args):
    sel = cmds.ls(sl=True)
    if not sel:
        cmds.warning("No objs selected!")
        return ()
    for obj in sel:
        if state == 0:
            cmds.lockNode(obj, lock=False, ignoreComponents=True)
        elif state == 1:
            cmds.lockNode(obj, lock=True, ignoreComponents=True)


def shapes_to_channels(*args):
    "select the bs node, then the ctrl"
    sel = cmds.ls(sl=True)
    bsnode = sel[0]
    ctrl = sel[1]
    bs = cmds.listAttr("{0}.w".format(bsnode), m=True)

    for b in bs:
        cmds.addAttr(ctrl, ln=b, min=0, max=1, at="float", k=True)
        cmds.connectAttr("{0}.{1}".format(ctrl, b), "{0}.{1}".format(bsnode, b))


def center_joint(*args):
    """creates a center loc on the avg position"""

    # TODO -------- differentiate if these are objs or points
    sel = cmds.ls(sl=True, fl=True)
    if sel:
        ps = []
        for vtx in sel:
            ps.append(cmds.pointPosition(vtx))

        # this is cool!
        center = rig.average_vectors(ps)
        cmds.select(cl=True)
        jnt = cmds.joint(name="center_JNT")
        cmds.xform(jnt, ws=True, t=center)


def hide_shape(*args):
    """toggels the vis of the shape nodes of the selected objects"""

    sel = cmds.ls(sl=True)
    if sel:
        for obj in sel:
            shp = cmds.listRelatives(obj, shapes=True)
            if shp:
                for s in shp:
                    if cmds.getAttr("{}.visibility".format(s)):
                        cmds.setAttr("{}.visibility".format(s), 0)
                    else:
                        cmds.setAttr("{}.visibility".format(s), 1)


def bBox(*args):
    """creates a control based on the bounding box"""
    sel = cmds.ls(sl=True, type="transform")
    if sel:
        rig.bounding_box_ctrl(sel)


##########
# load function
##########


def tools(*args):
    tools_UI()
