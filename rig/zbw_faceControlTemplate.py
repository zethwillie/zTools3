import maya.cmds as cmds


def face_ctrl_setup(*args):
    """
    This function creates remap nodes driven by translates on selected ctrls. Those remap nodes output 0-1 for the stated input attr and feed into new non-keyable attributes (xPosOut, xNegOut, yPosOut, etc) on the ctrl. These should be connected to blend shapes, etc. So xPosOut might connect to "mouthWide" and xNegOut to "mouthNarrow".
    Also create mult attrs (xPosOutMult, etc) that overcranked the 0-1 out attrs (so setting mult to 3 would output 0-3 instead of 0-1)
    This will set translate limits as default -1 to 1.
    """
    ctrls = cmds.ls(sl=True, type="transform")
    if not ctrls:
        cmds.warning("You need to select at least one control")

    for ctrl in ctrls:
        attrs = ["xPosOut", "yPosOut", "zPosOut","xNegOut", "yNegOut", "zNegOut"]

        for attr in attrs:
            cmds.addAttr(ctrl, ln=attr, at="float", k=False)
            cmds.addAttr(ctrl, ln="{0}OutputMult".format(attr[0:4]), at="float", dv=1, k=False)
            remap = cmds.shadingNode("remapValue", asUtility=True, name="{0}_{1}_REMAP".format(ctrl, attr))
            cmds.connectAttr("{0}.outValue".format(remap), "{0}.{1}".format(ctrl, attr))
            cmds.connectAttr("{0}.t{1}".format(ctrl, attr[0]), "{0}.inputValue".format(remap))
            cmds.connectAttr("{0}.{1}OutputMult".format(ctrl, attr[0:4]), "{0}.outputMax".format(remap))
            if attrs.index(attr)<3:
                cmds.connectAttr("{0}.maxTransLimit.maxTrans{1}Limit".format(ctrl, attr[0].capitalize()), "{0}.inputMax".format(remap))
            if attrs.index(attr)>2:
                cmds.connectAttr("{0}.minTransLimit.minTrans{1}Limit".format(ctrl, attr[0].capitalize()), "{0}.inputMax".format(remap))
    cmds.transformLimits(ctrl, etx=[1, 1], ety=[1, 1], etz=[1, 1])
    cmds.transformLimits(ctrl, tx=[-1, 1], ty=[-1, 1], tz=[-1, 1])

    cmds.select(ctrl, r=True)