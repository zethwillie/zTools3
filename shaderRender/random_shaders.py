import maya.cmds as cmds
import random


# UI to pull up list of all shaders - select from list

# random shader
sel = cmds.ls(sl=True)
shds = sel[:3]
sgs = []

for shd in shds:
    sg = cmds.listConnections(shd, t="shadingEngine")[0]
    sgs.append(sg)
    
for obj in sel[3:]:
    randShd = random.choice(sgs)
    shp = cmds.listRelatives(obj, s=True)[0]
    cmds.sets(shp, e=True, forceElement=randShd)
    