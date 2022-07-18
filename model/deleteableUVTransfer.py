import maya.mel as mel
import maya.cmds as cmds


# add this to the function in zTools
sel = cmds.ls(sl=True)
for x in range(1, len(sel)):
    cmds.polyTransfer(sel[i], uv=1, ao=sel[0])

# leave only one bind pose in scene
sc = cmds.ls(type="dagPose")
for s in sc:
    cmds.delete(s)
cmds.dagPose(bp=True, save=True)


#stick a joint in center of verts
import maya.cmds as cmds
import maya.mel as mel
import zTools.rig.zbw_rig as rig

# convert this selection to components? 
sel = cmds.ls(sl=True, fl=True)
jnt = cmds.joint(name="CenterJoint")
pos = rig.average_point_positions(sel)
cmds.xform(jnt, ws=True, t=pos)
# cmds.parent(jnt, w=True)