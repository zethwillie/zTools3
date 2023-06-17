import maya.cmds as cmds
import zTools3.rig.zbw_rig as rig
import importlib
import maya.OpenMaya as om

sel = cmds.ls(sl=True)

box = cmds.exactWorldBoundingBox(sel)  # [xmin, ymin, zmin, xmax, ymax, zmax]
X = om.MVector(box[0], box[3])
Y = om.MVector(box[1], box[4])
Z = om.MVector(box[2], box[5])

# get bbox lengths along axes
lenX = (X.y - X.x)
lenY = (Y.y - Y.x)
lenZ = (Z.y - Z.x)

ctrl = rig.create_control(name="ctrl", type="cube", color="pink")

cvs = {"xyz": [5, 15], "-xyz": [0, 4], "xy-z": [10, 14], "x-yz": [6, 8], "-x-yz": [3, 7], "-x-y-z": [2, 12], "x-y-z": [9, 13], "-xy-z": [1, 11]}

for a in cvs["xyz"]:
    cmds.xform("{0}.cv[{1}]".format(ctrl, a), ws=True, t=(X.y, Y.y, Z.y))
for a in cvs["-xyz"]:
    cmds.xform("{0}.cv[{1}]".format(ctrl, a), ws=True, t=(X.x, Y.y, Z.y))
for a in cvs["x-yz"]:
    cmds.xform("{0}.cv[{1}]".format(ctrl, a), ws=True, t=(X.y, Y.x, Z.y))
for a in cvs["-x-yz"]:
    cmds.xform("{0}.cv[{1}]".format(ctrl, a), ws=True, t=(X.x, Y.x, Z.y))
for a in cvs["xy-z"]:
    cmds.xform("{0}.cv[{1}]".format(ctrl, a), ws=True, t=(X.y, Y.y, Z.x))
for a in cvs["-xy-z"]:
    cmds.xform("{0}.cv[{1}]".format(ctrl, a), ws=True, t=(X.x, Y.y, Z.x))
for a in cvs["-x-y-z"]:
    cmds.xform("{0}.cv[{1}]".format(ctrl, a), ws=True, t=(X.x, Y.x, Z.x))
for a in cvs["x-y-z"]:
    cmds.xform("{0}.cv[{1}]".format(ctrl, a), ws=True, t=(X.y, Y.x, Z.x))

# center pivot on ctrl
cmds.xform(ctrl, cp=True)

cmds.select(sel)
