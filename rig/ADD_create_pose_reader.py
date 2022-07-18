import maya.cmds as cmds

poseName = "defaultPose"
locs = []
dms = []

# NORMALIZE THE VALUES? OR LOCK TO 1 unit

# check for matrix plug-in
# create cone
# make a control adn put all the input/output on that

tgtLoc = cmds.spaceLocator(name="{0}_tgt_Loc".format(poseName))[0]
cmds.xform(tgtLoc, ws=True, t=(0, 10, 0))
baseLoc = cmds.spaceLocator(name="{0}_base_Loc".format(poseName))[0]
poseLoc = cmds.spaceLocator(name="{0}_pose_Loc".format(poseName))[0]
cmds.xform(poseLoc, ws=True, t=(5, 10, 0))

locs.append(tgtLoc)
locs.append(baseLoc)
locs.append(poseLoc)

for loc in locs:
    dm = cmds.shadingNode("decomposeMatrix", asUtility=True, name="{0}_{1}_DM".format(poseName, loc.split("_")[1]))
    cmds.connectAttr("{0}.worldMatrix[0]".format(loc), "{0}.inputMatrix".format(dm))
    dms.append(dm)

cmds.addAttr(baseLoc, ln="angle", at="float", min=0, dv=45, k=True)
cmds.addAttr(baseLoc, ln="outputValue", at="float", k=True)

tgtPMA = cmds.shadingNode("plusMinusAverage", asUtility=True, name="{0}_tgtMinusBase_PMA".format(poseName))
posePMA = cmds.shadingNode("plusMinusAverage", asUtility=True, name="{0}_poseMinusBase_PMA".format(poseName))

cmds.connectAttr("{0}.outputTranslate".format(dms[0]), "{0}.input3D[0]".format(tgtPMA))
cmds.connectAttr("{0}.outputTranslate".format(dms[1]), "{0}.input3D[1]".format(tgtPMA))
cmds.connectAttr("{0}.outputTranslate".format(dms[1]), "{0}.input3D[1]".format(posePMA))
cmds.connectAttr("{0}.outputTranslate".format(dms[2]), "{0}.input3D[0]".format(posePMA))  

angle = cmds.shadingNode("angleBetween", asUtility=True, name = "{0}_angle".format(poseName))
cmds.connectAttr("{0}.output3D".format(tgtPMA), "{0}.vector1".format(angle))
cmds.connectAttr("{0}.output3D".format(posePMA), "{0}.vector2".format(angle))

angleRatioMult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_angleRatio".format(poseName))
cmds.setAttr("{0}.operation".format(angleRatioMult), 2)
cmds.connectAttr("{0}.angle".format(angle), "{0}.input1X".format(angleRatioMult))
cmds.connectAttr("{0}.angle".format(baseLoc), "{0}.input2X".format(angleRatioMult))

reversePMA = cmds.shadingNode("plusMinusAverage", asUtility=True, name="{0}_reverseRatio".format(poseName))
cmds.connectAttr("{0}.outputX".format(angleRatioMult), "{0}.input1D[1]".format(reversePMA))
cmds.setAttr("{0}.input1D[0]".format(reversePMA), 1.0)
cmds.setAttr("{0}.operation".format(reversePMA), 2)

clamp = cmds.shadingNode("clamp", asUtility=True, name="{0}_clamp".format(poseName))
cmds.connectAttr("{0}.output1D".format(reversePMA), "{0}.inputR".format(clamp))
cmds.setAttr("{0}.minR".format(clamp), 0)
cmds.setAttr("{0}.maxR".format(clamp), 1)

cmds.connectAttr("{0}.outputR".format(clamp), "{0}.outputValue".format(baseLoc))

grp = cmds.group([tgtLoc, poseLoc, baseLoc], name="{0}_poseReader_GRP".format(poseName))
