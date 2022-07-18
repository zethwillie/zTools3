import maya.OpenMaya as om
import maya.cmds as cmds
import math

def ikToFkSnap(*args):
    """
    select FK wrist joint(or control), fk elbow joint (or ctrl), FK shoulder joint (or ctrl), IK wrist ctl and IK pole vector in that order
    """

    sel = cmds.ls(sl=True)
    fkEnd = cmds.listConnections((sel[0]+".fkEnd"))
    fkMid = cmds.listConnections((sel[0]+".fkMid"))
    fkTop = cmds.listConnections((sel[0]+".fkTop"))
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
    pvLong = pvOrigin * 4

    #add that to midpoint (to get the PV back UP in space) (pvPos)
    pvPos = pvLong + midPoint

    #move pv to pv pos
    cmds.move(pvPos.x, pvPos.y, pvPos.z, ikPv, ws=True)

    #this handle rots if it is  arms
    if (sel[0]== "lf_arm_FKIK_CTRL") or (sel[0]=="rt_arm_FKIK_CTRL"):
        #get and set rotations
        fkRot = cmds.xform(fkEnd, q=True, ro=True, ws=True)
        cmds.xform(ikCtrl, ro=((fkRot[0]), fkRot[1], (fkRot[2])), ws=True)

    if (sel[0]== "rt_leg_FKIK_CTRL") or (sel[0]== "lf_leg_FKIK_CTRL"):
        offX = cmds.getAttr("%s.ikOffsetX"%sel[0])
        offY = cmds.getAttr("%s.ikOffsetY"%sel[0])
        offZ = cmds.getAttr("%s.ikOffsetZ"%sel[0])
        #DUDElf____rotOffset = om.MVector( -90, 90, 0 ) * math.pi / 180.0
        #DUDErt____rotOffset = om.MVector( 90, 90, 0 ) * math.pi / 180.0
        rotOffset = om.MVector(offX, offY, offZ) * math.pi/180

        #here I have to select the two objects (first the fkJNT, then the IKCtrl)
        cmds.select(cl=True)
        cmds.select(fkEnd, r=True)
        cmds.select(ikCtrl, add=True)

        # Retrieve the current selection.
        selList = om.MSelectionList()
        om.MGlobal.getActiveSelectionList( selList )

        # Convert it as MFnTransform nodes. First item is the target, second is the source.
        dag_nodes = []
        it_selList = om.MItSelectionList( selList, om.MFn.kTransform )
        while not it_selList.isDone():
            dagPath = om.MDagPath()
            it_selList.getDagPath( dagPath )
            dag_nodes.append( om.MFnTransform( dagPath ) )
            next(it_selList)

        # Create the offset rotation matrix.
        m_rotOffset = om.MEulerRotation( rotOffset,
        om.MEulerRotation.kXYZ ).asMatrix()

        # Retrieve the world matrix of the target node.
        m_worldTarget = dag_nodes[0].dagPath().inclusiveMatrix()

        # Compute the final world matrix.
        m_worldFinal = m_rotOffset * m_worldTarget

        # Convert it in the local space of the source object.
        m_localFinal = m_worldFinal * dag_nodes[1].dagPath().exclusiveMatrixInverse()


        # Apply the rotation component to the source object.
        dag_nodes[1].setRotation( om.MTransformationMatrix( m_localFinal
        ).rotation() )

        #reselect the ikFK ctrl
        cmds.select(sel[0], r=True)

        #