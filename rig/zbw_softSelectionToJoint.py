import maya.cmds as cmds
import maya.mel as mel

import zTools.rig.zbw_rig as rig


def soft_selection_to_joint(jointName=None, auto=True, surfacePosition=True, surfaceRotation=True, *args):
    """
    takes a soft selection of verts and creates a joint to bind & wieght them in that proportion
    """
    verts = cmds.filterExpand(sm=31)
    if verts:
        # make sure vtx's just from one object
        objList = [v.split(".")[0] for v in verts]
        if len(set(objList))>1:
            cmds.warning("need to select verts from only one object")
            return()
        initPos = rig.average_point_positions(verts)
        tform = objList[0]
    else:
        cmds.warning("didn't select any verts")
        return()

    vtxs, wts = rig.get_soft_selection()

    tform = verts[0].split(".")[0]
    mesh = cmds.listRelatives(tform, s=True)[0]

    skinCluster = mel.eval("findRelatedSkinCluster " + tform)
    if not skinCluster:
        if auto:
            baseJnt, skinCluster = rig.new_joint_bind_at_center(tform)
        else:
            cmds.warning("There isn't an initial bind on this geometry. Either create one or run command with auto flag")
            return()

    center = rig.average_point_positions(verts)
    rot = (0,0,0)
    if surfacePosition:
        center = rig.closest_point_on_mesh_position(center, mesh)
    if surfaceRotation:
        rot = rig.closest_point_on_mesh_rotation(center, mesh)

    cmds.select(cl=True)
    name = "{0}_JNT".format(tform)
    if jointName:
        name = "{0}_JNT".format(jointName)
    jnt = cmds.joint(name = name)
    cmds.xform(jnt, ws=True, t=center)
    cmds.xform(jnt, ws=True, ro=rot)

    # add influence to skin Cluster
    cmds.select(tform, r=True)
    cmds.skinCluster(e=True, ai=jnt, wt=0)

    # apply weights to that joint
    for v in range(len(vtxs)):
        cmds.skinPercent(skinCluster, vtxs[v], transformValue=[jnt, wts[v]])

    return(jnt)

def softSelectionToJoint(**kwargs):
    soft_selection_to_joint(kwargs)
