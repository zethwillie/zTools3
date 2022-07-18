########################
# File: zbw_curveCVControls.py
# Date Modified: 08 Aug 2017
# creator: Zeth Willie
# Contact: zethwillie@gmail.com, catbuks.com, williework.blogspot.com
# Description: puts controls on curve to drive it's shape node
# To Run: type "import zTools.zbw_curveCVControls as zbw_curveCVControls; reload(zbw_curveCVControls);zbw_curveCVControls.zbw_curveCVControls()"
########################

import maya.cmds as cmds
import zTools.rig.zbw_rig as rig

def curve_CV_controls_execute(crv, *args):
    """
    takes given curve and makes a ctrl for each cv. Then connects the matrix of the control directly to the point
    position of the cv. Basically hijacking the shape node, more or less. If there's a parent to the curve,
    will put whole rig under that and turn off inherit transforms for the crv itself.
    puts an attr called 'controlScale' on the group controls are under to scale size of controls
    Args:
        crv: string - name of given curve
        *args:

    Returns:
        Void
    """

    par = cmds.listRelatives(crv, p=True)

    ctrlGrps = []
    cvs = cmds.ls("{0}.cv[*]".format(crv), fl=True)
    xformGrp = cmds.group(empty=True, name="{0}_ctrl_GRP".format(crv))
    cmds.addAttr(xformGrp, ln="controlScale", at="float", min=0.01, max=100, dv=1.0, k=True)
    for x in range(0, len(cvs)):
        pos = cmds.pointPosition(cvs[x])
        shp = cmds.listRelatives(crv, s=True)[0]
        ctrl = rig.create_control(type="sphere", name="{0}_{1}_CTRL".format(crv, x), color="red")
        grp = rig.group_freeze(ctrl)
        cmds.connectAttr("{0}.controlScale".format(xformGrp), "{0}.sx".format(ctrl))
        cmds.connectAttr("{0}.controlScale".format(xformGrp), "{0}.sy".format(ctrl))
        cmds.connectAttr("{0}.controlScale".format(xformGrp), "{0}.sz".format(ctrl))
        cmds.setAttr("{0}.scale".format(ctrl), l=True, k=False)
        cmds.xform(grp, ws=True, t=pos)

        dm = cmds.shadingNode("decomposeMatrix", asUtility=True,name="{0}_{1}_DM".format(crv, x))
        cmds.connectAttr("{0}.worldMatrix[0]".format(ctrl), "{0}.inputMatrix".format(dm))
        cmds.connectAttr("{0}.outputTranslate".format(dm), "{0}.controlPoints[{1}]".format(shp, x))
        ctrlGrps.append(grp)

    cmds.xform(xformGrp, ws=True, t=(cmds.xform(crv, ws=True, q=True, rp=True)))
    cmds.xform(xformGrp, ws=True, ro=(cmds.xform(crv, ws=True, q=True, ro=True)))
    cmds.xform(xformGrp, s=(cmds.xform(crv, q=True, r=True, s=True)))

    if par:
        inhGrp = cmds.group(empty=True, name="noInherit_{0}_GRP".format(crv))
        cmds.parent(xformGrp, par[0])
        cmds.parent(inhGrp, par[0])
        cmds.parent(crv, inhGrp)
        cmds.setAttr("{0}.inheritsTransform".format(inhGrp), 0)

    cmds.parent(ctrlGrps, xformGrp)
    cmds.xform(crv, ws=True, t=(0,0,0))
    cmds.xform(crv, ws=True, ro=(0,0,0))
    cmds.xform(crv, a=True, s=(1,1,1))


def curveCVControls(*args):
    """
    puts a controls on each cv of selected curves

    """
    sel = cmds.ls(sl=True, type="transform")
    for crv in sel:
        if rig.type_check(crv, "nurbsCurve"):
            curve_CV_controls_execute(crv)

