import maya.cmds as cmds
import zTools.rig.zbw_rig as rig
import importlib
importlib.reload(rig)
import maya.OpenMaya as om


def create_joint_chain(ptList=None, baseNames=None, alongAxis="xyz", upAxis="yup"):
    cmds.select(cl=True)
    jntList = []
    for i in range(len(ptList)):
        jnt = cmds.joint(name=baseNames[i], p=ptList[i])
        jntList.append(jnt)
    orient_joint_chain(jntList[0], alongAxis, upAxis)

    return(jntList)


def orient_joint_to_transform(jnt, obj):
    children = cmds.listRelatives(jnt, c=True, fullPath=True, ad=False)[0]
    newChildren = cmds.parent(children, world=True, absolute=True) # to get new names
    dupe = cmds.duplicate(obj)
    if cmds.listRelatives(jnt, p=True):
        newDupe = cmds.parent(dupe, cmds.listRelatives(jnt, p=True)[0])[0]
    else:
        newDupe = cmds.parent(dupe, world=True)[0]
    rot = cmds.xform(newDupe, q=True, objectSpace=True, rotation=True)
    cmds.delete(newDupe)
    cmds.setAttr("{0}.rotate".format(jnt), 0, 0, 0)
    cmds.setAttr("{0}.rotateAxis".format(jnt), 0, 0 , 0)
    cmds.setAttr("{0}.jointOrient".format(jnt), rot[0], rot[1], rot[2])
    cmds.parent(newChildren, jnt)


def orient_joint_chain(joint=None, alongAxis="xyz", upAxis="yup"):
    cmds.joint(joint, e=True, orientJoint=alongAxis, children=True, secondaryAxisOrient=upAxis, zso=True )


# rename joint chain
def name_object(obj, side=None, part=None, chain=None, typeSuf=None):
    """lf_shoulder_IK_JNT"""
# MAYBE JUST DO THIS WITH *ARGS AT END? 
    newName = "{0}_{1}_{2}_{3}".format(side, part, chain, typeSuf)
    name = cmds.rename(obj, newName)
    return(name)


def get_chain_hierarchy(topJoint=None):
    cmds.select(topJoint, r=True, hi=True)
    chain = cmds.ls(sl=True)
    return(chain)


def mirror_joint_chain(topJoint, oldSidePrefix=None, newSidePrefix=None, axis="yz"):
    """axis is mirror plane (xy, xz, yz)"""
    mirrored_chain = []
    if axis=="xy":
        mirrored_chain = cmds.mirrorJoint(topJoint, mirrorXY=True, searchReplace=[oldSidePrefix, newSidePrefix], mirrorBehavior=True)
    if axis=="xz":
        mirrored_chain = cmds.mirrorJoint(topJoint, mirrorXZ=True, searchReplace=[oldSidePrefix, newSidePrefix], mirrorBehavior=True)
    if axis=="yz":
        mirrored_chain = cmds.mirrorJoint(topJoint, mirrorYZ=True, searchReplace=[oldSidePrefix, newSidePrefix], mirrorBehavior=True)
    return(mirrored_chain)


def duplicate_and_rename_chain(topJnt, chain):
    """chain is string name of this chain (i.e. 'IK', 'measure', etc)"""
    dupe = cmds.duplicate(topJnt, renameChildren=True)
    newChainList = []
    for jnt in dupe:
        tokens = jnt.split("_")
        if tokens[3][-1].isdigit():
            tokens[3] = tokens[3][:-1]
        renamed = name_object(jnt, tokens[0], tokens[1], chain, tokens[3])
        newChainList.append(renamed)

    return(newChainList)


# set up blend procedures for blending joints
# THINK ABOUT HOW TO DEAL WITH INDIVIDUAL ATTRS, but not TONS of paras, do we need it?
def create_blend_network(name, oneAttr, twoAttr, blendAttr, targetAttr):
    """ 
        name is string
        targetAttr is triple
    """
    blend = cmds.shadingNode("blendColors", asUtility=True, name=name)
    cmds.connectAttr(oneAttr, "{0}.color1".format(blend))
    cmds.connectAttr(twoAttr, "{0}.color2".format(blend))
    cmds.connectAttr(blendAttr, "{0}.blender".format(blend))
    cmds.connectAttr("{0}.output".format(blend), targetAttr)

    return(blend)


def create_orient_reverse_network(srcList, tgt, switchAttr, index=0):
    """
    create orient constraint to A, B, which is reversed
    """
    oc = cmds.orientConstraint(srcList, tgt, mo=False)[0]
    if index == 0:
        cmds.connectAttr(switchAttr, "{0}.w1".format(oc))
        create_reverse_network(tgt, switchAttr, "x", "{0}.w0".format(oc))
    elif index == 1:
        cmds.connectAttr(switchAttr, "{0}.w0".format(oc))
        create_reverse_network(tgt, switchAttr, "x", "{0}.w1".format(oc))
    return(oc)


def create_parent_reverse_network(srcList, tgt, switchAttr, index=0):
    """
    create parent constraint to A, B, which is reversed
    ARGS:
        index (0, 1): which index gets the reverse
    """
    pc = cmds.parentConstraint(srcList, tgt, mo=False)[0]
    if index == 0:
        cmds.connectAttr(switchAttr, "{0}.w1".format(pc))
        create_reverse_network(tgt, switchAttr, "x", "{0}.w0".format(pc))
    elif index == 1:
        cmds.connectAttr(switchAttr, "{0}.w0".format(pc))
        create_reverse_network(tgt, switchAttr, "x", "{0}.w1".format(pc))
    return(pc)


def create_scale_reverse_network(srcList, tgt, switchAttr, index=0):
    sc = cmds.scaleConstraint(srcList, tgt, mo=False)[0]
    if index == 0:
        cmds.connectAttr(switchAttr, "{0}.w1".format(sc))
        create_reverse_network(tgt, switchAttr, "x", "{0}.w0".format(sc))
    elif index == 1:
        cmds.connectAttr(switchAttr, "{0}.w0".format(sc))
        create_reverse_network(tgt, switchAttr, "x", "{0}.w1".format(sc))
    return(sc)


def create_reverse_network(name,  inputAttr, revAttr, targetAttr,):
    """revAttr should be 'all', 'x', 'y' or 'z'"""
    reverse = cmds.shadingNode("reverse", asUtility=True, name=name+"_reverse")
    if revAttr=="all":
        cmds.connectAttr(inputAttr, "{0}.input".format(reverse))
        cmds.connectAttr("{0}.output".format(reverse), targetAttr)
    if revAttr=="x":
        cmds.connectAttr(inputAttr, "{0}.input.inputX".format(reverse))
        cmds.connectAttr("{0}.output.outputX".format(reverse), targetAttr)
    if revAttr=="y":
        cmds.connectAttr(inputAttr, "{0}.input.inputY".format(reverse))        
        cmds.connectAttr("{0}.output.outputY".format(reverse), targetAttr)
    if revAttr=="z":
        cmds.connectAttr(inputAttr, "{0}.input.inputZ".format(reverse))
        cmds.connectAttr("{0}.output.outputZ".format(reverse), targetAttr)
    return(reverse)


def create_control_at_joint(jnt, ctrlType, axis, name, grpSuffix="GRP", orient=True):
    """
        orient is whether we should rotate/orient ctrl to jnt or leave in world rotation
        NAME  is full name including "ctrl"
    """
    ctrl = rig.create_control(name, ctrlType, axis)
    grp = rig.group_freeze(ctrl, grpSuffix)
    rotOrder = cmds.xform(jnt, q=True, roo=True)
    cmds.xform(ctrl, roo=rotOrder)
    cmds.xform(grp, roo=rotOrder)
    if orient:
        rig.snap_to(jnt, grp)
    else:
        rig.snap_to(jnt, grp, rot=False)
    return(ctrl, grp)


def create_controls_and_orients_at_joints(jntList, ctrlType, axis, suffix, orient=False, upAxis="y"):
    """orient will create a new control UNDER the ctrl that we can use to  orient pose joints"""
    ctrls = []
    groups = []
    octrls = []
    ogrps = []
    for jnt in jntList:
        if "_" in jnt:
            name = "_".join(jnt.split("_")[:-1]) + "_{0}".format(suffix)
            oname = "_".join(jnt.split("_")[:-1]) + "_{0}".format("ORIENT"+suffix)
        else:
            name = "{0}_{1}".format(jnt, suffix)
            oname = "{0}_{1}".format(jnt, "ORIENT"+suffix)
        ctrl = rig.create_control(name, ctrlType, axis)
        grp = rig.group_freeze(ctrl)
        rig.snap_to(jnt, grp)
        ctrls.append(ctrl)
        groups.append(grp)
        if orient:
            octrl = rig.create_control(oname, "arrow", upAxis) # FLIP THIS IN AXIS
            rig.strip_to_rotate(octrl)
            cmds.setAttr("{0}.ry".format(octrl), l=True)
            cmds.setAttr("{0}.rz".format(octrl), l=True)
            ogrp = rig.group_freeze(octrl)
            rig.snap_to(jnt, ogrp)
            cmds.parent(ogrp, ctrl)
            octrls.append(octrl)
            ogrps.append(ogrp)

    if not orient:
        return(ctrls, groups)
    else:
        return(ctrls, groups, octrls, ogrps)


def parent_hierarchy_grouped_controls(ctrls, grps):
    """assumes in order from top to bottom, groups are parents of controls"""
    if not len(ctrls)==len(grps) or len(ctrls)<2:
        cmds.warning("riggerTools.parent_hierarchy_grouped_controls: lists don't match in length or aren't long enough")
        return()

    for x in range(1, len(grps)):
        cmds.parent(grps[x], ctrls[x-1])


# SEPARATE THIS INTO TWO FUNCTIONS (ONE FOR PV SPECIFICALLY, THE OTHER TO JUST FIND THE PLANE)
def find_pole_vector_location(handle):
    # arg is ikHandle
    ikJntList = cmds.ikHandle(handle, q=True, jointList=True)
    ikJntList.append(cmds.listRelatives(ikJntList[-1], children=True, type="joint")[0])

    # get jnt positions
    rootPos = cmds.xform(ikJntList[0], q=True, ws=True, rp=True)
    midPos = cmds.xform(ikJntList[1], q=True, ws=True, rp=True)
    endPos = cmds.xform(ikJntList[2], q=True, ws=True, rp=True)

    poleVecPos = get_planar_position(rootPos, midPos, endPos)

    return(poleVecPos) 
    

def get_planar_position(rootPos, midPos, endPos, percent=None, dist=None):
    # convert to vectors
    rootVec = om.MVector(rootPos[0], rootPos[1], rootPos[2])
    midVec = om.MVector(midPos[0], midPos[1], midPos[2])
    endVec = om.MVector(endPos[0], endPos[1], endPos[2])
    
    # get vectors
    line = (endVec - rootVec)
    point = (midVec - rootVec)

    # get center-ish of rootEnd (relative to midjoint)
    if not percent:
        percent = (line*point)/(line*line)
    
    projVec = line * percent + rootVec
    
    if not dist:
        dist = (midVec-rootVec).length() + (endVec-midVec).length()
    poleVecPos = (midVec - projVec).normal() * dist + midVec
    
    return(poleVecPos)


def create_line_between(startXform, endXform, name):
    pos1 = [0,0,0]
    pos2 = [1,1,1]
    crv = cmds.curve(d=1, p=[pos1, pos2])
    crv = cmds.rename(crv, "{0}_CRV".format(name))

    dm1 = cmds.createNode("decomposeMatrix", name="{0}0_DM".format(name))
    dm2 = cmds.createNode("decomposeMatrix", name="{0}1_DM".format(name))

    cmds.connectAttr("{0}.worldMatrix".format(startXform), "{0}.inputMatrix".format(dm1))
    cmds.connectAttr("{0}.worldMatrix".format(endXform), "{0}.inputMatrix".format(dm2))

    cmds.connectAttr("{0}.outputTranslate".format(dm1), "{0}.controlPoints[0]".format(crv))
    cmds.connectAttr("{0}.outputTranslate".format(dm2), "{0}.controlPoints[1]".format(crv))

    return(crv)

def measure_chain_length(chainList, name):
    """

    Args:
        chainList: list of objects in the chain
        name: the base name network

    Returns:
        the created addNode (string)
        the created distance nodes (list)
    """
    distNodes = []
    dmNodes = []
    for i in range(len(chainList)-1):
        if i==0:
            dm0 = cmds.createNode("decomposeMatrix", name="{0}{1}_0_DM".format(name, i))
            dmNodes.append(dm0)
            dm1 = cmds.createNode("decomposeMatrix", name="{0}{1}_1_DM".format(name, i))
            dmNodes.append(dm1)
        else:
            dm0 = dmNodes[-1]
            dm1 = cmds.createNode("decomposeMatrix", name="{0}{1}_0_DM".format(name, i))
            dmNodes.append(dm1)
            
        db = cmds.createNode("distanceBetween", name="{0}{1}_DB".format(name, i))
        
        if i==0:
            cmds.connectAttr("{0}.worldMatrix".format(chainList[i]), "{0}.inputMatrix".format(dm0))
        cmds.connectAttr("{0}.worldMatrix".format(chainList[i+1]), "{0}.inputMatrix".format(dm1))
        cmds.connectAttr("{0}.outputTranslate".format(dm0), "{0}.point1".format(db))
        cmds.connectAttr("{0}.outputTranslate".format(dm1), "{0}.point2".format(db))        

        distNodes.append(db)
        
    add = cmds.shadingNode("plusMinusAverage", asUtility=True, name="{0}_PMA".format(name))
    for i in range(len(distNodes)):
        cmds.connectAttr("{0}.distance".format(distNodes[i]), "{0}.input1D[{1}]".format(add, i))
    
    # returns the plusMinusAvg node, and the distance nodes
    return(add, distNodes)


def create_stretch_setup(measureJnts, ikCtrl, limbName):
    """
    note: returs only the mult nodes that you need to hook up to your joints
    """
    # get measure distances (x2)
    msrAdd, msrDists = measure_chain_length(measureJnts, "{0}_measure".format(limbName))
    # get ik to measure shoulder distance
    ikAdd, ikDist = measure_chain_length([measureJnts[0], ikCtrl], "{0}_ik".format(limbName))

    # check if ikCtrl has necessary attrs
    divider = cmds.attributeQuery("__stretch__", node=ikCtrl, exists=True)    
    upScale = cmds.attributeQuery("upScale", node=ikCtrl, exists=True)
    loScale = cmds.attributeQuery("loScale", node=ikCtrl, exists=True)
    autostretch = cmds.attributeQuery("autostretch", node=ikCtrl, exists=True)    
    
    if not divider:
        cmds.addAttr(ikCtrl, sn="__stretch__", at="enum", enumName="------", k=True)
        cmds.setAttr("{0}.__stretch__".format(ikCtrl), l=True)
    if not upScale:
        cmds.addAttr(ikCtrl, ln="upScale", at="float", dv=1, min=0.1, max=3, k=True)
    if not loScale:
        cmds.addAttr(ikCtrl, ln="loScale", at="float", dv=1, min=0.1, max=3, k=True)
    if not autostretch:
        cmds.addAttr(ikCtrl, ln="autostretch", at="float", dv=1, min=0, max=1.0, k=True)

    # create mult for up and down limb
    upMult1 = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_up1_mult".format(limbName))
    loMult1 = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_lo1_mult".format(limbName))
    
    # connect distance up/down to mults, connect ik ctrl up/down attrs to mults
    cmds.connectAttr("{0}.distance".format(msrDists[0]), "{0}.input1X".format(upMult1))
    cmds.connectAttr("{0}.distance".format(msrDists[1]), "{0}.input1X".format(loMult1))
    cmds.connectAttr("{0}.upScale".format(ikCtrl), "{0}.input2X".format(upMult1))
    cmds.connectAttr("{0}.loScale".format(ikCtrl), "{0}.input2X".format(loMult1))
    
    # connect mults to addNode (up/down)
    cmds.connectAttr("{0}.outputX".format(upMult1), "{0}.input1D[0]".format(msrAdd), f=True)
    cmds.connectAttr("{0}.outputX".format(loMult1), "{0}.input1D[1]".format(msrAdd), f=True)

    # create blend color, connect ikCtrl.autostretch to blender, add nodes out to blend.x (x2)
    asBlend = cmds.shadingNode("blendColors", asUtility=True, name="{0}_autostretchBlend".format(limbName))
    cmds.connectAttr("{0}.autostretch".format(ikCtrl), "{0}.blender".format(asBlend))
    cmds.connectAttr("{0}.output1D".format(msrAdd), "{0}.color2.color2R".format(asBlend))
    cmds.connectAttr("{0}.output1D".format(ikAdd), "{0}.color1.color1R".format(asBlend))

    # create multdiv ratio,blend.out to ratio1.x,up/down measure add to ratio2.x
    ratio = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_ratio_mult".format(limbName))
    cmds.setAttr("{0}.operation".format(ratio), 2)
    cmds.connectAttr("{0}.output.outputR".format(asBlend), "{0}.input1.input1X".format(ratio))
    cmds.connectAttr("{0}.output1D".format(msrAdd), "{0}.input2.input2X".format(ratio))

    # create condition node
    # ratio out x to cond first term, color if true
    # second term=1, color if Flase = 1
    cond = cmds.shadingNode("condition", asUtility=True, name="{0}_stretchCond".format(limbName))
    cmds.connectAttr("{0}.output.outputX".format(ratio), "{0}.firstTerm".format(cond))
    cmds.connectAttr("{0}.output.outputX".format(ratio), "{0}.colorIfTrue.colorIfTrueR".format(cond))
    cmds.setAttr("{0}.operation".format(cond), 2)
    cmds.setAttr("{0}.secondTerm".format(cond), 1)
    cmds.setAttr("{0}.colorIfFalse.colorIfFalseR".format(cond), 1)

    # create mult for up/down limbs
    upMult2 = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_up2_mult".format(limbName))
    loMult2 = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_lo2_mult".format(limbName))
    # out color of cond to mults 1x,up/down scale from ikCtrl to mult2
    cmds.connectAttr("{0}.outColor.outColorR".format(cond), "{0}.input1.input1X".format(upMult2))
    cmds.connectAttr("{0}.outColor.outColorR".format(cond), "{0}.input1.input1X".format(loMult2))
    cmds.connectAttr("{0}.upScale".format(ikCtrl), "{0}.input2.input2X".format(upMult2))
    cmds.connectAttr("{0}.loScale".format(ikCtrl), "{0}.input2.input2X".format(loMult2))

    # returns 2 mults go to the up/down jnts
    return(upMult2, loMult2)


def create_twist_extractor(rotJnt, tgtCtrl, parObj, tgtAttr=None, axis="x"):
    """ 
    rotJnt is jnt we're getting rotation from 
    parObj is parent of that rotJnt (should be at same mtx of the rot jnt, and oriented to the rot jnt)
    tgtCtrl is the ctrl we'll drop the twist attr onto
    tgtAttr is what to call the attr we're creating on the tgtCtrl
    axis is the attr of the quat we connect out of the decomposeMatrix to the quat to euler, i think this rougly corresponds to the twist axis
    """
# TRY THIS AS CONSTAINTS? 
    baseLoc = cmds.spaceLocator(name="{0}_baseTswt_Loc".format(rotJnt))[0]
    cmds.parent(baseLoc, rotJnt)
    cmds.setAttr("{0}.t".format(baseLoc), 0,0,0)
    cmds.setAttr("{0}.r".format(baseLoc), 0,0,0)
    cmds.parent(baseLoc, parObj)
    cmds.setAttr("{0}.v".format(baseLoc), 0)

    twstLoc = cmds.spaceLocator(name="{0}_rotTswt_Loc".format(rotJnt))[0]
    cmds.parent(twstLoc, rotJnt)
    cmds.setAttr("{0}.t".format(twstLoc), 0,0,0)
    cmds.setAttr("{0}.r".format(twstLoc), 0,0,0)
    cmds.setAttr("{0}.v".format(twstLoc), 0)

    # mult matrix (obj world into 1, parent inverse into 2)
    multMat = cmds.shadingNode("multMatrix", asUtility=True, name="{0}_twist_multMat".format(rotJnt))

    cmds.connectAttr("{0}.worldMatrix[0]".format(twstLoc), "{0}.matrixIn[0]".format(multMat), f=True)
    cmds.connectAttr("{0}.worldInverseMatrix[0]".format(baseLoc), "{0}.matrixIn[1]".format(multMat), f=True)

    # multMatrix out to decomposeMatrix
    dm = cmds.shadingNode("decomposeMatrix", asUtility=True, name="{0}_twist_dm".format(rotJnt))
    cmds.connectAttr("{0}.matrixSum".format(multMat), "{0}.inputMatrix".format(dm), f=True)

    # create quatToEuler
    qte = cmds.shadingNode("quatToEuler", asUtility=True, name="{0}_twist_qte".format(rotJnt))
    if axis == "x":
        cmds.connectAttr("{0}.outputQuat.outputQuatX".format(dm), "{0}.inputQuat.inputQuatX".format(qte))
    if axis == "y":
        cmds.connectAttr("{0}.outputQuat.outputQuatY".format(dm), "{0}.inputQuat.inputQuatX".format(qte))
    if axis == "z":
        cmds.connectAttr("{0}.outputQuat.outputQuatZ".format(dm), "{0}.inputQuat.inputQuatX".format(qte))

    cmds.connectAttr("{0}.outputQuat.outputQuatW".format(dm), "{0}.inputQuat.inputQuatW".format(qte))

    if not tgtAttr:
        tgtAttr = "{0}_twist".format(rotJnt)

    attrTest = cmds.attributeQuery(tgtAttr, node=tgtCtrl, exists=True)
    if not attrTest:
        cmds.addAttr(tgtCtrl, ln=tgtAttr, at="float", dv=0, k=False)

# connect reverse mult
    if axis == "x":
        cmds.connectAttr("{0}.outputRotate.outputRotateX".format(qte), "{0}.{1}".format(tgtCtrl, tgtAttr))
    if axis == "y":
        multRev = cmds.shadingNode('multiplyDivide', asUtility=True, n="{0}_revMult".format(twstLoc))
        cmds.setAttr("{0}.input2X".format(multRev), -1.0)
        cmds.connectAttr("{0}.outputRotate.outputRotateX".format(qte), "{0}.input1X".format(multRev))
        cmds.connectAttr("{0}.outputX".format(multRev), "{0}.{1}".format(tgtCtrl, tgtAttr))
    cmds.setAttr("{0}.{1}".format(tgtCtrl, tgtAttr), l=True)

    return("{0}.{1}".format(tgtCtrl, tgtAttr))


def create_twist_joints(numJnts, rotJnt, parentJnt, childJnt, twistAttr, baseName, primaryAxis="x", grpSuffix="GRP", jntSuffix="JNT", reverse=True):
    """
    numJnts: NOT inclusive for first and last
    rotJnt: joint twist comes from
    parentJnt: jnt that twist joints are dupes of and is parent of twist jnts
    childJnt: jnt that is child of parent joint (used to find location of twist jnt)
    reverse: measn that twstjnt1 gets 100% and shrinks, false means it gets 0% and grows
    twistAttr: full name.attr of twist source
    """
# ADD ATTRS FOR EACH JOINTS TWIST PERCENTAGE ONTO CONTROL? SET THAT TO INIT VALUE
# if no child given, find it
    num = numJnts + 2 # to account for start and end
    factor = 1.0/(num-1.0)
    fullDistance = cmds.getAttr("{0}.t{1}".format(childJnt, primaryAxis))

    twistJnts = []
    # create twist joints from shoulder, place them and parent to deform shoulder
    for i in range(num):
        dupe = cmds.duplicate(parentJnt, parentOnly=True, name="{0}_twist{1}_{2}".format(baseName, i, jntSuffix))[0]
        dupeGrp = cmds.group(em=True, name="{0}_twist{1}_{2}".format(baseName, i, grpSuffix))
        rig.snap_to(dupe, dupeGrp)
        cmds.parent(dupe, dupeGrp)
        twistJnts.append(dupe)
        cmds.parent(dupeGrp, parentJnt)
        shrink = 1-(factor*i)
        grow = factor*i
        cmds.setAttr("{0}.t{1}".format(dupeGrp, primaryAxis), fullDistance*grow)

        pc = cmds.pointConstraint([parentJnt, childJnt], dupeGrp, mo=False)
        if i == 0:
            cmds.pointConstraint(childJnt, dupeGrp, e=True, w=0.0)
            cmds.pointConstraint(parentJnt, dupeGrp, e=True, w=1)
        elif i == num-1:
            cmds.pointConstraint(childJnt, dupeGrp, e=True, w=1)
            cmds.pointConstraint(parentJnt, dupeGrp, e=True, w=0)
        else:
            chldW = i
            parntW = (numJnts+1)-i
            cmds.pointConstraint(childJnt, dupeGrp, e=True, w=chldW)
            cmds.pointConstraint(parentJnt, dupeGrp, e=True, w=parntW)

    # figure out how to do this with the fewest possible mult nodes
        mult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_twst{1}_mult".format(baseName, i))
        if reverse:
            cmds.setAttr("{0}.input2.input2X".format(mult), -shrink)
        else:
            cmds.setAttr("{0}.input2.input2X".format(mult), grow)

        cmds.connectAttr(twistAttr, "{0}.input1.input1X".format(mult))
        cmds.connectAttr("{0}.output.outputX".format(mult), "{0}.r{1}".format(dupeGrp, primaryAxis))

    topHook = cmds.spaceLocator(name="{0}_topHook_LOC".format(baseName))[0]
    cmds.parent(topHook, twistJnts[0])
    cmds.setAttr("{0}.t".format(topHook), 0, 0, 0)
    cmds.setAttr("{0}.r".format(topHook), 0, 0, 0)
    lowHook = cmds.spaceLocator(name="{0}_lowHook_LOC".format(baseName))[0]
    cmds.parent(lowHook, twistJnts[-1])
    cmds.setAttr("{0}.t".format(lowHook), 0, 0, 0)
    cmds.setAttr("{0}.r".format(lowHook), 0, 0, 0)

    return(twistJnts, [topHook, lowHook])


def initial_pose_joints(ptsList, baseNames, orientOrder, upOrientAxis, primaryAxis="x", upAxis="y"):
    """
    ptsList (list of vec3's): locs for jnts
    baseNames (list of strings): names of joints
    orientOrder (string): "xyz", etc for init jnt orient
    upOrientAxis (string): "yup", etc for init jnt orient
    primaryAxis (string): "x", etc for manual jnt orient
    upAxis (string): "y", etc for manual jnt orient

    """
# get and pass values for orient order and uporient axis
# put joint in ref display layer temporarily
    joints = create_joint_chain(ptsList, baseNames, orientOrder, upOrientAxis)

    poseCtrls, poseGrps, octrls, ogrps = create_controls_and_orients_at_joints(joints[:-1], "sphere", primaryAxis, "poseCTRL", orient=True, upAxis=upAxis)
    lockAttrs = ["s","tx", "ty", "tz"]

    ctrlHierList = list(zip(poseCtrls, poseGrps, joints, octrls, ogrps))
    poseConstraints = []
    for i in range(len(ctrlHierList)):
        if i>0:
            oc = cmds.orientConstraint(ctrlHierList[i-1][2], ctrlHierList[i][1], mo=False)[0]
            poseConstraints.append(oc)
        oc1 = cmds.orientConstraint(joints[i], ctrlHierList[i][4], mo=False)
        cmds.delete(oc1)
        const = cmds.parentConstraint(ctrlHierList[i][0], ctrlHierList[i][2], mo=True)[0]
        poseConstraints.append(const)

        if i>0:
            for attr in lockAttrs:
                cmds.setAttr("{0}.{1}".format(ctrlHierList[i][0], attr), l=True)
            cmds.setAttr("{0}.t{1}".format(ctrlHierList[i][0], primaryAxis), l=False)    
        if i==1:
            # unlock the bend attr
            cmds.setAttr("{0}.rx".format(ctrlHierList[i][0]), l=True)
            cmds.setAttr("{0}.ry".format(ctrlHierList[i][0]), l=True)
            cmds.setAttr("{0}.rz".format(ctrlHierList[i][0]), l=True)
            cmds.setAttr("{0}.r{1}".format(ctrlHierList[i][0], upAxis), l=False)
        if i==0:
            cmds.setAttr("{0}.tx".format(ctrlHierList[i][0]), l=False)
            cmds.setAttr("{0}.ty".format(ctrlHierList[i][0]), l=False)
            cmds.setAttr("{0}.tz".format(ctrlHierList[i][0]), l=False)

    parent_hierarchy_grouped_controls(poseCtrls, poseGrps)

    return(joints, poseCtrls, poseGrps, octrls, ogrps, poseConstraints)


def clean_pose_joints(joints, poseConstraints, octrls, poseGrpTop, prefix, jntSuffix, deleteEnd=True):
    """
    joints (list strings): list of jnts
    poseConstraints (list strings):
    octrls (list strings): orient controls
    poseGrpTop (string): top level grp of pose ctrls
    deleteEnd (bool): whether to delete the last joint
    """
    cleanedJnts = []

    cmds.delete(poseConstraints)
    # unlock octrl attrs
    attrs = ["t", "rx", "ry", "rz"]
    for i in range(len(octrls)):
        for attr in attrs:
            cmds.setAttr("{0}.{1}".format(octrls[i], attr), l=False)
        orient_joint_to_transform(joints[i], octrls[i])

# save scale info from ctrls - still need to make a scalable control
    cmds.delete(poseGrpTop)

    for jnt in joints:
        cmds.makeIdentity(jnt, apply=True)

    if deleteEnd:
        cmds.delete(joints[-1])
        joints = joints[:-1]

# maybe store the scale on the joint itself? Then delete it later. . . 
    for jnt in joints:
        name = name_object(jnt, prefix, jnt, "FK", jntSuffix)
        cleanedJnts.append(name)

    return(cleanedJnts)


def create_rotate_order_attr(obj, attrName):
    cmds.addAttr(obj, ln=attrName, at="enum", en="xyz:yzx:zxy:xzy:yxz:zyx", dv=1, k=True)
    return("{0}.{1}".format(obj, attrName))


# **rewrite ribbon stuff. . . 

# *mocap stuff should be put ON TOP of these controls
# *export rig should be put UNDER all of these things

# -- arm 
# hand stuff
