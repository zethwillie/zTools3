import maya.cmds as cmds
import zTools3.rig.zbw_rig as rig
import maya.api.OpenMaya as om
import maya.cmds as cmds
import zTools3.rig.zbw_rig as rig
import importlib

# returns the closest vertex given a mesh and a position [x,y,z] in world space.
# Uses om.MfnMesh.getClosestPoint() returned face ID and iterates through face's vertices.


def getClosestVertex(mayaMesh, pos=[0, 0, 0]):
    mVector = om.MVector(pos)  # using MVector type to represent position
    selectionList = om.MSelectionList()
    selectionList.add(mayaMesh)
    dPath = selectionList.getDagPath(0)
    mMesh = om.MFnMesh(dPath)
    ID = mMesh.getClosestPoint(om.MPoint(mVector), space=om.MSpace.kWorld)[1]  # getting closest face ID
    list = cmds.ls(cmds.polyListComponentConversion(mayaMesh + '.f[' + str(ID) + ']', ff=True, tv=True), flatten=True)  # face's vertices list
    # setting vertex [0] as the closest one
    d = mVector - om.MVector(cmds.xform(list[0], t=True, ws=True, q=True))
    smallestDist2 = d.x * d.x + d.y * d.y + d.z * d.z  # using distance squared to compare distance
    closest = list[0]
    # iterating from vertex [1]
    for i in range(1, len(list)):
        d = mVector - om.MVector(cmds.xform(list[i], t=True, ws=True, q=True))
        d2 = d.x * d.x + d.y * d.y + d.z * d.z
        if d2 < smallestDist2:
            smallestDist2 = d2
            closest = list[i]
    return closest


def create_joints(centerObj, startVtx, endVtx):
    posA = om.MVector(cmds.pointPosition(startVtx))
    posB = om.MVector(cmds.pointPosition(endVtx))
    diff = (posB - posA)
    length = diff.length()
    cmds.select(cl=True)
    topJnt = cmds.joint(name="{0}_top_JNT".format(startVtx.split(".")[0]))
    endJnt = cmds.joint(name="{0}_end_JNT".format(startVtx.split(".")[0]), a=True, position=(0, -length, 0))
    #cmds.parent(endJnt, topJnt)

    return(topJnt, endJnt)


def create_feather_rig(startVtx=23, endVtx=0, centerObj="neck03_JNT", locVtx=7, proxyMesh="neckProxy3", driverCtrl="neck03_Ctrl.featherLift", color="Green", *args):
    # get each piece of geo
    sel = cmds.ls(sl=True)
    pts = []

    for obj in sel:
        srcPos = cmds.pointPosition("{0}.vtx[{1}]".format(obj, locVtx))
        cageVert = getClosestVertex(proxyMesh, srcPos)
        uv = rig.get_vert_uv([cageVert])
        fol, folShape = rig.follicle(proxyMesh, "{0}_foll".format(obj), u=uv[0][0], v=uv[0][1])
        cmds.setAttr("{0}.parameterV".format(folShape), 0.5)

        #cmds.parentConstraint(fol, obj, mo=True)
        topJnt, endJnt = create_joints(centerObj, "{0}.vtx[{1}]".format(obj, startVtx), "{0}.vtx[{1}]".format(obj, endVtx))

        cmds.select(cl=True)
        # for x in ["buffer", "auto", "orient", "attach"]:
        attachGrp = cmds.group(name="{0}_attach".format(obj), em=True)
        cmds.parent(topJnt, attachGrp)

        # move attach to foll location
        attachPos = cmds.pointPosition("{0}.vtx[{1}]".format(obj, startVtx))
        cmds.xform(attachGrp, ws=True, t=attachPos)

        cmds.parent(attachGrp, fol)
        # aim orient to centerObj joint - delete aim if created - neg Z
        ac = cmds.aimConstraint(centerObj, attachGrp, aim=[0, 0, -1.0], mo=False, worldUpType="scene")
        cmds.delete(ac)

        # create controls for joint start and end
        topCtrl = rig.create_control(name="{0}_top_CTRL".format(obj), type="lollipop", axis="-z", color="dark{0}".format(color))
        topGrp = rig.group_freeze(topCtrl)
        autoGrp = rig.group_freeze(topGrp, "auto_GRP")
        rig.scale_nurbs_control(topCtrl, .2, .2, .2)
        endCtrl = rig.create_control(name="{0}_end_CTRL".format(obj), type="lollipop", axis="-z", color="light{0}".format(color))
        endGrp = rig.group_freeze(endCtrl)
        rig.scale_nurbs_control(endCtrl, .2, .2, .2)

        rig.snap_to(topJnt, autoGrp)
        rig.snap_to(endJnt, endGrp)
        cmds.parent(autoGrp, attachGrp)
        cmds.parent(topJnt, topCtrl)
        cmds.parent(endGrp, topJnt)
        cmds.parent(endJnt, endCtrl)

        # attach controls from main neck things to the auto group
        cmds.connectAttr(driverCtrl, "{0}.rx".format(autoGrp))

        skinCluster = cmds.skinCluster([topJnt, endJnt], obj, normalizeWeights=True)[0]


# def featherUI(*args):
#     widgets = {}
#     if cmds.window("jointFeatherWin", exists=True):
#         cmds.deleteUI("jointFeatherWin")

#     cmds.window
