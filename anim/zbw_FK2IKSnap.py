import maya.OpenMaya as om
import maya.cmds as cmds


def zbw_FK2IKSnap(*args):
    """
    select FK wrist joint(or control), fk elbow joint (or ctrl), FK shoulder joint (or ctrl), IK wrist ctl and IK pole vector in that order
    """

    sel = cmds.ls(sl=True)
    fkEndC = cmds.listConnections((sel[0]+".fkEndCtrl"))
    fkMidC = cmds.listConnections((sel[0]+".fkMidCtrl"))
    fkTopC = cmds.listConnections((sel[0]+".fkTopCtrl"))
    ikTopJ = cmds.listConnections((sel[0]+".ikTopJnt"))
    ikMidJ = cmds.listConnections((sel[0]+".ikMidJnt"))
    ikEndJ = cmds.listConnections((sel[0]+".ikEndJnt"))

    #get FK wrist joint position & rot
    ikEndPos = cmds.xform(ikEndJ, q=True, ws=True, t=True)
    iep = om.MVector(ikEndPos[0], ikEndPos[1], ikEndPos[2])
    ikEndRot = cmds.xform(ikEndJ, q=True, ro=True)
    ier = om.MVector(ikEndRot[0], ikEndRot[1], ikEndRot[2])

    #get FK shoulder position & rot
    ikTopPos = cmds.xform(ikTopJ, q=True, ws=True, t=True)
    itp = om.MVector(ikTopPos[0], ikTopPos[1], ikTopPos[2])
    ikTopRot = cmds.xform(ikTopJ, q=True, ro=True)
    itr = om.MVector(ikTopRot[0], ikTopRot[1], ikTopRot[2])

    #get midJnt pos & rot
    ikMidPos = cmds.xform(ikMidJ, q=True, ws=True, t=True)
    imp = om.MVector(ikMidPos[0], ikMidPos[1], ikMidPos[2])
    ikMidRot = cmds.xform(ikMidJ, q=True, ro=True)
    imr = om.MVector(ikMidRot[0], ikMidRot[1], ikMidRot[2])

    #rotate joints to rotations
    cmds.xform(fkEndC, ro=(ier.x, ier.y, ier.z))
    cmds.xform(fkMidC, ro=(imr.x, imr.y, imr.z))
    cmds.xform(fkTopC, ro=(itr.x, itr.y, itr.z))

    #snap FK ctrl to positions
#-------try:except this part . . . Will only work if the channels aren't locked . . .
    cmds.move(iep.x, iep.y, iep.z, fkEndC, ws=True)
    cmds.move(imp.x, imp.y, imp.z, fkMidC, ws=True)
    cmds.move(iep.x, iep.y, iep.z, fkEndC, ws=True)