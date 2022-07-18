import maya.cmds as cmds
import zTools.rig.zbw_rig as rig


#ikhandle, pvctrl, measure jnts, ik mid/end
#---------------- make it so you can change the axis of the joints
#---------------- MAKE SURE TO ADD THE LOCATOR SO STRETCH DOESN'T KICK IN FROM BALL ROTATE, ETC

def build_translate_stretch(partname, ikctrl, pvctrl, measureTop, measureMid, measureEnd, ikmid, ikend):
    #get distances
    origUpDist = connect_distance(partname, "up_orig_dist", measureTop, measureMid)
    origLowDist = connect_distance(partname, "lo_orig_dist", measureMid, measureEnd)
    currDist = connect_distance(partname, "curr_IK_dist", measureTop, ikctrl)

    origFullAdd = add_attributes(partname, "ikFull_adl", origUpDist+".distance", origLowDist+".distance")

    UpPvDist = connect_distance(partname, "up_pv_dist", pvctrl, measureTop)
    LowPvDist = connect_distance(partname, "low_pv_dist", pvctrl, ikctrl)

    # setup basic stretch ratio
    ikScaleRatioMult = get_ratio(partname, "ikScale_ratio", currDist+".distance", origFullAdd+".output")
    ikScaleCond = cmds.createNode("condition", name="{0}_scale_cond".format(partname))
    cmds.connectAttr(currDist+".distance", ikScaleCond+".firstTerm")
    cmds.connectAttr(origFullAdd + ".output", ikScaleCond+".secondTerm")
    cmds.connectAttr(ikScaleRatioMult+".output", ikScaleCond+".colorIfTrue")
    cmds.setAttr(ikScaleRatioMult + ".operation", 2)
    cmds.setAttr(ikScaleCond+".operation", 2)

    constants = cmds.createNode("multiplyDivide", name=partname+"_constants")
    cmds.setAttr(constants+".input1X", 1)
    cmds.setAttr(constants+".input1Y", 0.001)

    lowStretchSwitch = create_switch(partname, "low_stretch_switch", constants+".outputX", ikScaleCond+".outColorR", ikctrl+".autostretch")
    upStretchSwitch = create_switch(partname, "up_stretch_switch", constants+".outputX", ikScaleCond+".outColorR", ikctrl+".autostretch")

    # setup nudge
    nudgeMult = cmds.createNode("multiplyDivide", name=partname+"_nudgeFactor")
    cmds.connectAttr(ikctrl+".nudge", nudgeMult+".input1X")
    cmds.connectAttr(constants+".outputY", nudgeMult+".input2X")
    
    nudgeAdd = cmds.createNode("plusMinusAverage", name=partname+"_nudge_add")
    cmds.connectAttr(nudgeMult+".outputX", nudgeAdd+".input2D[0].input2Dx")
    cmds.connectAttr(nudgeMult+".outputX", nudgeAdd+".input2D[0].input2Dy")
    cmds.connectAttr(lowStretchSwitch+".output", nudgeAdd+".input2D[1].input2Dy")
    cmds.connectAttr(upStretchSwitch+".output", nudgeAdd+".input2D[1].input2Dx")

    # setup lock
    lockUpRatioMult = get_ratio(partname, "up_pvscale_ratio", UpPvDist+".distance", origUpDist+".distance")
    lockLowRatioMult = get_ratio(partname, "low_pvscale_ratio", LowPvDist+".distance", origLowDist+".distance")

    lowLockSwitch = create_switch(partname, "low_lockSwitch", nudgeAdd+".output2Dy",lockLowRatioMult+".outputX",  ikctrl+".lock")
    upLockSwitch = create_switch(partname, "up_lockSwitch", nudgeAdd+".output2Dy",lockUpRatioMult+".outputX",  ikctrl+".lock")

    # final ratio to translate
    upTranslateMult = create_mult(partname, "up_translate_mult", upLockSwitch+".output", measureMid + ".tx")
    lowTranslateMult = create_mult(partname, "low_translate_mult", lowLockSwitch+".output", measureEnd + ".tx")

    # connect translates
    cmds.connectAttr(upTranslateMult+".outputX", ikmid+".tx")
    cmds.connectAttr(lowTranslateMult+".outputX", ikend+".tx")


def connect_distance(partname, distName, a, b):
    dist = cmds.createNode("distanceBetween", name=partname+"_"+distName)
    cmds.connectAttr(a+".worldMatrix[0]", dist+".inMatrix1")
    cmds.connectAttr(b+".worldMatrix[0]", dist+".inMatrix2")
    return(dist)


def add_attributes(partname, addName, attrA, attrB):
    add = cmds.createNode("addDoubleLinear", name=partname+"_"+addName)
    cmds.connectAttr(attrA, add+".input1")
    cmds.connectAttr(attrB, add+".input2")
    return(add)

def get_ratio(partname, ratioName, attrA, attrB):
    mult = cmds.createNode("multiplyDivide", name=partname+"_"+ratioName)
    cmds.connectAttr(attrA, mult+".input1X")
    cmds.connectAttr(attrB, mult+".input2X")
    cmds.setAttr(mult+".operation", 2)
    return(mult)


def create_switch(partname, switchName, attrA, attrB, blender):
    switch = cmds.createNode("blendTwoAttr", name=partname+"_"+switchName)
    cmds.connectAttr(attrA, switch+".input[0]")
    cmds.connectAttr(attrB, switch+".input[1]")
    cmds.connectAttr(blender, switch+".attributesBlender")
    return(switch)

def create_mult(partname, multName, attrA, attrB):
    mult = cmds.createNode("multiplyDivide", name=partname+"_"+multName)
    cmds.connectAttr(attrA, mult+".input1X")
    cmds.connectAttr(attrB, mult+".input2X")
    return(mult)
