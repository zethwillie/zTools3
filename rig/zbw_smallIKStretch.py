########################
#file: zbw_smallIKStretch.py
#Author: zeth willie
#Contact: zeth@catbuks.com, www.williework.blogspot.com
#Date Modified: 04/27/13
#To Use: type in python window  "import zbw_smallIKStretch as sik; sik.smallIKStretch"
#Notes/Descriptions: makes a two joint ik stretch setup based on selected two joint chain
########################

import maya.cmds as cmds
import zTools3.rig.zbw_rig as rig

def smallIKStretch(*args):
    """
    create the 2 joint chain at the start and end of the shock/spring/whatever. select the base joint and run this.Then you'll hook up the top/bottom locators to whatever they're connected to (parentConstraint, etc) and hook the geo onto the original joints (parentConstraint, etc)
    """

    #select the joint, give as arg the name(?) of the setup
    sel =  cmds.ls(sl=True)
    origJnt = sel[0]
    #get child joint of this joint
    origChild = cmds.listRelatives(origJnt, c=True)[0]

    #create locators at joint start and end positions
    orig1Pos = cmds.xform(origJnt, ws=True, q=True, rp=True)
    orig2Pos = cmds.xform(origChild, ws=True, q=True, rp=True)
    orig1Loc = cmds.spaceLocator(n="%s_LOC"%origJnt)[0]
    orig2Loc = cmds.spaceLocator(n="%s_LOC"%origChild)[0]
    cmds.xform(orig1Loc, ws=True, t=orig1Pos)
    cmds.xform(orig2Loc, ws=True, t=orig2Pos)

    #dupe the joint, rename it, measure it
    dupeJnts = cmds.duplicate(origJnt)
    mJnt1Orig = dupeJnts[0]
    mJnt1 = cmds.rename(mJnt1Orig, "measure_%s"%origJnt)

    mJnt2orig = cmds.listRelatives(mJnt1, c=True, f=True)[0]
    mJnt2 = cmds.rename(mJnt2orig, "measure_%s"%origChild)

    #create IK handles on orig joints, parent handle to second loc
    ik = cmds.ikHandle( n="%s_IK"%origJnt, sj=origJnt, ee=origChild)[0]
    cmds.parent(ik, orig2Loc)

    # print orig2Loc
    #measure from the base measure joint to the ik handle
    origM = rig.measure_distance_nodes((origJnt + "orig_dist"), mJnt1, mJnt2)
    activeM = rig.measure_distance_nodes((origJnt + "active_dist"), mJnt1, orig2Loc)
    #create mult node to compare the two measures
    mult = cmds.shadingNode("multiplyDivide", asUtility=True, n="%s_mult"%origJnt)
    cmds.setAttr("%s.operation"%mult, 2)
    cmds.connectAttr("%s.distance"%activeM, "%s.input1X"%mult)
    cmds.connectAttr("%s.distance"%origM, "%s.input2X"%mult)

    #---use this code if you want to set up a non-scaling piston geo
    # #create a condition node to tell when to use what value
    # cond = cmds.shadingNode("condition", asUtility=True, n="%s_cond"%origJnt)
    # cmds.setAttr("%s.secondTerm"%cond, 1)
    # cmds.setAttr("%s.operation"%cond, 2)
    # cmds.connectAttr("%s.outputX"%mult, "%s.firstTerm"%cond)
    # cmds.connectAttr("%s.outputX"%mult, "%s.colorIfTrueR"%cond)
    # cmds.setAttr("%s.colorIfFalseR"%cond, 1)

    # #hook the condition node into the scale of the ik joint (in x for now)
    # cmds.connectAttr("%s.outColorR"%cond, "%s.sx"%origJnt)

    #hook the mult into the scale of the joint (comment this line out if you use the commented code above)
    cmds.connectAttr("%s.outputX"%mult, "%s.sx"%origJnt)

    #connect the orig joint to the base of the setup (loc)
    cmds.parentConstraint(orig1Loc, origJnt, mo=True)

    #hide measure joints
    cmds.setAttr("%s.visibility"%mJnt1, 0)

    #package up objects in group
    group = cmds.group(empty=True, n="%s_GRP"%origJnt)
    cmds.parent(mJnt1, origJnt, orig1Loc)
    cmds.parent(orig1Loc, orig2Loc, group)
