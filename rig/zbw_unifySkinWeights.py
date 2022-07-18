# unify skin weights on obj

#---------------- option to unify to mode or median or first

import maya.cmds as cmds
import maya.mel as mel


vtxs = cmds.ls(sl=True, fl=True)
geo = vtxs[0].partition(".")[0]

# get cluster first?
skCl = mel.eval('findRelatedSkinCluster {0}'.format(geo))

# get joints
jnts = cmds.skinCluster(geo, q=True, inf=True)
jntWgts = {}
for jnt in jnts:
    jntWgts[jnt] = []
    for vtx in vtxs:
        jntWgts[jnt].append(cmds.skinPercent(skCl, vtx, q=True, transform=jnt))

jntAvg = {}
for jnt in list(jntWgts.keys()):
    avg = sum(jntWgts[jnt])/len(jntWgts[jnt])
    jntAvg[jnt] = avg
    
for jnt in list(jntAvg.keys()):
    cmds.skinPercent(skCl, vtxs, transformValue=[(jnt, jntAvg[jnt])])
