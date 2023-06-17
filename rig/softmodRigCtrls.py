import maya.cmds as cmds
import zTools3.rig.zbw_rig as rig


def softmodRigCtrls():
    # softmod grps
    sms = cmds.ls(sl=True)

    for sm in sms:
        chld = cmds.listRelatives(sm, ad=True, c=True, type="nurbsCurve")
        base = cmds.listRelatives(chld[0], p=True)[0]
        mover = cmds.listRelatives(chld[1], p=True)[0]
        baseGrp = cmds.listRelatives(base, p=True)[0]
        moverGrp = cmds.listRelatives(mover, p=True)[0]

        origFalloff = cmds.getAttr(mover + ".falloffRadius")
        origScale = cmds.getAttr(mover + ".s")[0]

        # create new ctrls
        newBase = rig.create_control(name=base + "_CTRL", type="cross", axis="z", color="yellow")
        newBaseGrp = rig.group_freeze(newBase)
        newMover = rig.create_control(name=mover + "_CTRL", type="sphere", axis="z", color="red")
        newMoverGrp = rig.group_freeze(newMover)
        cmds.parent(newMoverGrp, newBase)

        rig.snap_to(baseGrp, newBaseGrp)
        rig.snap_to(base, newBase)
        rig.snap_to(mover, newMover)
        cmds.setAttr(newMover + ".s", origScale[0], origScale[1], origScale[2])

        rig.scale_nurbs_control(newBase, .1, .1, .1)
        rig.scale_nurbs_control(newMover, .05, .05, .05)

        cmds.addAttr(newMover, ln="__xtra__", nn="__xtra__", at="enum", en="-----", k=True)
        cmds.setAttr(newMover + ".__xtra__", l=True)
        cmds.addAttr(newMover, ln="falloff", at="float", min=0, dv=origFalloff, k=True)
        cmds.addAttr(newMover, ln="showBaseCtrl", at="short", min=0, max=1, dv=0, k=True)

        cmds.connectAttr(newMover + ".showBaseCtrl", cmds.listRelatives(newBase, s=True)[0] + ".v")
        cmds.connectAttr(newMover + ".falloff", mover + ".falloffRadius")

        attrs = [".t", ".r", ".s"]
        for attr in attrs:
            cmds.connectAttr(newMover + attr, mover + attr)
            cmds.connectAttr(newBase + attr, base + attr)
