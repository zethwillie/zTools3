import maya.OpenMaya as om
import maya.cmds as cmds
import math

def zbw_IK2FKSnap(*args):
    """
    select FK wrist joint(or control), fk elbow joint (or ctrl), FK shoulder joint (or ctrl), IK wrist ctl and IK pole vector in that order
    """

    sel = cmds.ls(sl=True)
    fkEnd = cmds.listConnections((sel[0]+".fkEndJnt"))
    fkMid = cmds.listConnections((sel[0]+".fkMidJnt"))
    fkTop = cmds.listConnections((sel[0]+".fkTopJnt"))
    ikCtrl = cmds.listConnections((sel[0]+".ikCtrl"))
    ikPv = cmds.listConnections((sel[0]+".ikPv"))

    #get FK wrist joint position
    fkEndPos = cmds.xform(fkEnd, q=True, ws=True, t=True)
    fw = om.MVector(fkEndPos[0], fkEndPos[1], fkEndPos[2])

    #get FK shoulder position
    fkTopPos = cmds.xform(fkTop, q=True, ws=True, t=True)
    fs = om.MVector(fkTopPos[0], fkTopPos[1], fkTopPos[2])

    #get midJnt pos
    fkMidPos = cmds.xform(fkMid, q=True, ws=True, t=True)
    midJnt = om.MVector(fkMidPos[0], fkMidPos[1], fkMidPos[2])

    #snap IK ctrl to wrist position
    cmds.move(fw.x, fw.y, fw.z, ikCtrl, ws=True)

    #add that to shoulder (midPoint)
    midPoint = fw/2 + fs/2

    #Subtract that from midJnt (to get midJnt pos relative to outerjoints [at orig]) (pvOrigin)
    pvOrigin = midJnt - midPoint

    #make this longer
    pvLong = pvOrigin * 3

    #add that to midpoint (to get the PV back UP in space) (pvPos)
    pvPos = pvLong + midPoint

    #move pv to pv pos
    cmds.move(pvPos.x, pvPos.y, pvPos.z, ikPv, ws=True)


    #get and set rotations
    fkRot = cmds.xform(fkEnd, q=True, ro=True, ws=True)
    cmds.xform(ikCtrl, ro=((fkRot[0]), fkRot[1], (fkRot[2])), ws=True)
    #pass