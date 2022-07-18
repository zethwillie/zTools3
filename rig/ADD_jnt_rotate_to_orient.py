import maya.cmds as cmds

sel =  cmds.ls(sl=True)

for obj in sel:
    rot = cmds.getAttr(obj+".r")[0]
    cmds.setAttr(obj+".jointOrientX", rot[0])
    cmds.setAttr(obj+".jointOrientY", rot[1])
    cmds.setAttr(obj+".jointOrientZ", rot[2])
    cmds.setAttr(obj+".r", 0, 0, 0)