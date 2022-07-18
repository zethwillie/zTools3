import maya.cmds as cmds

obj = cmds.ls(sl=True)[0]

cvs = cmds.ls("%s.cv[*]"%obj, fl=True)


for cv in cvs:
    pos = cmds.pointPosition(cv)
    posList.append(pos)

print(posList)

