from functools import partial

import maya.cmds as cmds

import zTools3.rig.zbw_rig as rig
# get how many ctrls we want, then make curve have that many cvs
# refactor this out to functions - outputs for api style

# todo ---------- make this into a class, easier for the variable passing

widgets = {}

def splineRig_UI( *args):
    # name, base obj, top obj, num jnt
    if cmds.window("splineRigWin", exists=True):
        cmds.deleteUI("splineRigWin")

    widgets["win"] = cmds.window("splineRigWin")
    widgets["clo"] = cmds.columnLayout(w=300, h=150)

    widgets["nameTFG"] = cmds.textFieldGrp(l="Name:", cw=[(1, 50), (2, 200)], cal=[(1, "left"),(2, "left")])
    widgets["baseTFBG"] = cmds.textFieldButtonGrp(l="Base Obj:", cal=[(1, "left"),(2, "left"), (3, "left")], cw=[(1, 50), (2, 200), (3, 50)], bl="<<<", bc=partial(get_object, "baseTFBG"))
    widgets["endTFBG"] = cmds.textFieldButtonGrp(l="End Obj:", cal=[(1, "left"),(2, "left"), (3, "left")], cw=[(1, 50), (2, 200), (3, 50)], bl="<<<", bc=partial(get_object, "endTFBG"))
    widgets["numJntsIFG"] = cmds.intFieldGrp(l="Number of Joints:", cw=[(1, 100), (2, 50)], cal=[(1, "left"),(2, "left")], v1=10, cc=check_number_valid)
    widgets["executeBut"] = cmds.button(l="Create Spline IK Rig", bgc=(.5, .7, .5), h=40, w=300, c=collect_info)

    cmds.window(widgets["win"], e=True, w=5, h=5, rtf=True)
    cmds.showWindow(widgets["win"])


def check_number_valid(*args):
    num = cmds.intFieldGrp(widgets["numJntsIFG"], q=True, v1=True)
    if num < 3:
        cmds.intFieldGrp(widgets["numJntsIFG"], e=True, v1=3)


def collect_info(*args):
    baseObj = cmds.textFieldButtonGrp(widgets["baseTFBG"], q=True, tx=True)
    endObj = cmds.textFieldButtonGrp(widgets["endTFBG"], q=True, tx=True)
    name = cmds.textFieldGrp(widgets["nameTFG"], q=True, tx=True)
    numJnts = cmds.intFieldGrp(widgets["numJntsIFG"], q=True, v1=True)

    if not baseObj or not endObj or not name:
        cmds.warning("Need to give me some info to work with!")
        return()

    if baseObj == endObj:
        cmds.warning("Can't have the same object as base and end!")
        return()

    create_ikspline_rig(baseObj, endObj, numJnts, name)


def get_object(uiVal, *args):
    sel = cmds.ls(sl=True, l=True)
    if sel:
        obj = sel[0]
        cmds.textFieldButtonGrp(widgets[uiVal], e=True, tx=obj)


#todo ------ refactor this to break out funct
def create_ikspline_rig(baseObj, endObj, numJnts, name=None):
    if not name:
        name=baseObj

    name = name + "_spline"

    basePos = cmds.xform(baseObj, ws=True, q=True, rp=True)
    endPos = cmds.xform(endObj, ws=True, q=True, rp=True)

    dist = rig.measure_distance(baseObj, endObj)

    factor = dist/float(numJnts-1)

    jntList = create_joint_chain(name, baseObj, endObj, factor, numJnts)

    # do some joint orienting
    rig.clean_joint_chain(jntList[0])
    cmds.joint(jntList[0], edit=True, orientJoint="xyz",
               secondaryAxisOrient="yup", ch=True)

#---------------- below have option for how many cv's on curve. have few. Could use option later to rebuild curve and add in blend shapes, etc
    splHandle, splEffector, splCrv = cmds.ikHandle(startJoint=jntList[0], ee=jntList[-1], sol="ikSplineSolver", numSpans=1, rootTwistMode=False, parentCurve=False, name="{0}_IK".format(name))
    splCrv = cmds.rename(splCrv, "{0}_splCrv".format(name))

    pc, oc, bindJnts, bindGrps, bindCtrls, offsetGrps = create_controls(name, baseObj, basePos, endPos)

    measureCrv = setup_scaling(name, splCrv, jntList)

    bind_skin(bindJnts, splCrv)

#---------------- deal with end jnt flipping (add a joint/s at the postion of the "B" jnt)
#---------------- weight the cvs of the crv to those jnts

    setup_spline_advanced_twist(splHandle, bindCtrls[0], bindCtrls[2], 0, 0)

#---------------- option to turn off stretching
#---------------- squash and stretch on a ramp which tells where the effect takes place along the curve (ie. move joints up and down curve?)
#---------------- attrs to lengthen and shorten the curve

    cmds.addAttr(bindCtrls[1], ln="baseTwist", k=True, dv=0, at="float")
    cmds.addAttr(bindCtrls[1], ln="endTwist", k=True, dv=0, at="float")
    cmds.connectAttr("{0}.baseTwist".format(bindCtrls[1]), "{0}.dTwistStart".format(splHandle))
    cmds.connectAttr("{0}.endTwist".format(bindCtrls[1]), "{0}.dTwistEnd".format(splHandle))
    cmds.addAttr(bindCtrls[1], ln="followEnds", k=True, dv=0, at="float", min=0, max=1)
    cmds.connectAttr("{0}.followEnds".format(bindCtrls[1]), "{0}.{1}W0".format(pc, bindCtrls[0]))
    cmds.connectAttr("{0}.followEnds".format(bindCtrls[1]), "{0}.{1}W1".format(pc, bindCtrls[2]))

    finalCtrlGrp = cmds.group(em=True, name="{0}_driverCtrl_GRP".format(name))
    cmds.parent(bindGrps, finalCtrlGrp)
    xformGrp = cmds.group(em=True, name="{0}_transform_GRP".format(name))
    cmds.parent([finalCtrlGrp, measureCrv, jntList[0]], xformGrp)
    noXformGrp = cmds.group(em=True, name="{0}_noTransform_GRP".format(name))
    cmds.parent([splCrv, splHandle], noXformGrp)

    hide = [measureCrv, splCrv, splHandle]
    for obj in hide:
        cmds.setAttr("{0}.v".format(obj), 0)

    # return the things (grps, ctrls, offset grps, etc)


def create_joint_chain(name, baseObj, endObj, factor, numJnts):
    jntList = []
    for i in range(numJnts):
        cmds.select(cl=True)
        if rig.type_check(baseObj, "joint") and rig.type_check(endObj, "joint"):
            jnt = cmds.duplicate(baseObj, po=True, name="{0}_ik_{1}".format(
                name, i))[
                0]
        else:
            jnt = cmds.joint(name="{0}_ik_{1}".format(name, i))
            rig.snap_to(baseObj, jnt, rot=False)
            oc = cmds.aimConstraint(endObj, jnt, aimVector=(1, 0, 0),
                                    upVector=(0, 1, 0), mo=False,
                                    worldUpType="scene")
            cmds.delete(oc)

        if i !=  0:
            cmds.parent(jnt, jntList[0])
            cmds.setAttr("{0}.tx".format(jnt), i*factor)
        jntList.append(jnt)

    for x in range(2, len(jntList)):
        cmds.parent(jntList[x], jntList[x-1])

    return(jntList)


def create_controls(name, baseObj, basePos, endPos):
    bindJnts = []
    bindGrps = []
    bindCtrls = []
    offsetGrps = []

    # this into a loop for however many ctrls we need?
    ctrlNames = ["base", "mid", "end"]
    for cName in ctrlNames:
        ctrl = rig.create_control("{0}_{1}_CTRL".format(cName, name), "circle", color="red")
        grp  = rig.group_freeze(ctrl)
        cmds.select(cl=True)
        jnt = cmds.joint(name="{0}_{1}_JNT".format(cName, name))
        cmds.parent(jnt, ctrl)
        offsetGrp = rig.group_freeze(grp, suffix="offset")
        topGrp = rig.group_freeze(offsetGrp)
        topGrp = cmds.rename(topGrp, "{0}_{1}_ctrl_GRP".format(cName, name))
        bindJnts.append(jnt)
        bindGrps.append(topGrp)
        bindCtrls.append(ctrl)
        offsetGrps.append(offsetGrp)

    percent = 1.0/(len(ctrlNames)-1)
    for i in range(len(ctrlNames)):
        # snap to cvs?
        rig.snap_to(baseObj, bindGrps[i])
        # TODO - -- do this along the curve instead. . . 
        pos = rig.linear_interpolate_vector(basePos, endPos, i*percent)
        cmds.xform(bindGrps[i], ws=True, t=pos)

    pc = cmds.pointConstraint([bindCtrls[0], bindCtrls[2]], offsetGrps[1], mo=True)[0]
    oc = cmds.orientConstraint([bindCtrls[0], bindCtrls[2]], offsetGrps[1], mo=True)[0]

    return(pc, oc, bindJnts, bindGrps, bindCtrls, offsetGrps)


def setup_scaling(name, splCrv, jntList):
    measureCrv = cmds.duplicate(splCrv,name="{0}_measure_CRV".format(name))[0]
    splPoc = cmds.arclen(splCrv, ch=True)
    msrPoc = cmds.arclen(measureCrv, ch=True)
    ratioMult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_ratio_mult".format(name))
    cmds.setAttr("{0}.operation".format(ratioMult), 2)
    cmds.connectAttr("{0}.arcLength".format(splPoc), "{0}.input1.input1X".format(ratioMult))
    cmds.connectAttr("{0}.arcLength".format(msrPoc), "{0}.input2.input2X".format(ratioMult))

    for jnt in jntList[:-1]:
        cmds.connectAttr("{0}.output.outputX".format(ratioMult), "{0}.sx".format(jnt))
    return(measureCrv)


def setup_spline_advanced_twist(handle, startObj, endObj, fwdAxis=0, upAxis=0):
    """
    ARGS:
        handle(str): the ikspline handle
        startObj(str): the xform of the start obj
        endObj(str): the xform of the end obj
        fwdAxis(int): 0 is x, 1 is -x, etc
        upAxis(int): 0, 1, 2 = +y, -y, closest y, (then z then x)
    """
    cmds.setAttr("{0}.dWorldUpType".format(handle), 4) # sets twist to objRotUp
    cmds.setAttr("{0}.dTwistControlEnable".format(handle), 1)
    cmds.setAttr("{0}.dForwardAxis".format(handle), 0)
    cmds.setAttr("{0}.dWorldUpAxis".format(handle), 0)

    cmds.setAttr("{0}.dWorldUpVector".format(handle), 0, 1, 0)
    cmds.setAttr("{0}.dWorldUpVectorEnd".format(handle), 0, 1, 0)

    cmds.connectAttr("{0}.worldMatrix[0]".format(startObj), "{0}.dWorldUpMatrix".format(handle))
    cmds.connectAttr("{0}.worldMatrix[0]".format(endObj), "{0}.dWorldUpMatrixEnd".format(handle))

    cmds.setAttr("{0}.dTwistValueType".format(handle), 1) # sets to start/end


def bind_skin(jntList, objList):
        skin = cmds.skinCluster(jntList, objList, maximumInfluences=5, smoothWeights=0.5, obeyMaxInfluences=False, toSelectedBones=True, normalizeWeights=1)


def splineRig(): 
    # kwargs = {
    #     "baseObj":"a",
    #     "endObj":"b",
    #     "numJnts": 20,
    #     "name": "upArm"
    # }
    splineRig_UI()