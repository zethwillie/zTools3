import maya.cmds as cmds
import zTools3.rig.zbw_rig as rig


widgets = {}


def extrudeUI():
    if cmds.window("curveExtrudeWin", exists=True):
        cmds.deleteUI("curveExtrudeWin")

    w, h = 300, 220
    widgets["win"] = cmds.window("curveExtrudeWin", w=w, h=h)
    widgets["CLO"] = cmds.columnLayout(w=w, h=h)

    widgets["text1"] = cmds.text(l="Name the rig to be created:")
    cmds.separator(h=5)
    widgets["nameTFG"] = cmds.textFieldGrp(l="Rig Name: ", cal=[(1, "left"), (2, "left")], cw=[(1, 50), (2, 245)])
    cmds.separator(h=5)

    widgets["text2"] = cmds.text(l="Select the path curve.\nOptionally, "
                                   "then select profile crv and the cap rig in that order\n"
                                   "Note that cap rig and profile curve should be y up!", al="left")
    cmds.separator(h=5)
    widgets["extrBut"] = cmds.button(l="Create Extrusion Rig!", w=300, h=35, bgc=(.4, .5, .4), c=prepExtrude)

    cmds.separator(h=10)

    widgets["text3"] = cmds.text(l="Once you've attached a material :\nselect the control, then any place2DTexture nodes", al="left")
    cmds.separator(h=5)
    widgets["textureBut"] = cmds.button(l="Connect Ctrl to place2DTexture nodes!", w=300, h=35, bgc=(.25, .35, .5), c=connectTexture)

    cmds.window(widgets["win"], e=True, w=w, h=h)
    cmds.showWindow(widgets["win"])


def prepExtrude(*args):

    name = cmds.textFieldGrp(widgets["nameTFG"], q=True, tx=True)
    if not name:
        cmds.warning("You must give the extrusion a name!")
        return

    if cmds.objExists("{}_extRig_GRP".format(name)):
        cmds.warning("A rig of this name already exists")
        return

    sel = cmds.ls(sl=True, exactType="transform")
    if len(sel) < 1 or len(sel) > 3:
        cmds.warning("You must select the profile crv, then path crv, then optionally a cap rig top node")
        return

    if len(sel) == 2:
        for x in range(2):
            shp = cmds.listRelatives(sel[x], shapes=True)
            if shp:
                if cmds.objectType(shp[0]) != "nurbsCurve":
                    cmds.warning("{} is not a curve!".format(sel[x]))
                    return
    elif len(sel) == 1:
        shp = cmds.listRelatives(sel[0], shapes=True)
        if shp:
            if cmds.objectType(shp[0]) != "nurbsCurve":
                cmds.warning("{} is not a curve!".format(sel[0]))
                return

    extrude(name)


def extrude(name="defaultName", *args):
    print("starting extrude")
    sel = cmds.ls(sl=True)
    guideCrv = sel[0]

    if len(sel) > 1:
        profileCrv = cmds.duplicate(sel[1], name="{}_profile_CRV".format(name))[0]
    else:
        profileCrv = cmds.circle(r=1, normal=(0, 1, 0), name="{}_profile_CRV".format(name), ch=False)[0]

    if len(sel) == 3:
        capRig = sel[2]
    else:
        capRig = ""

    if len(sel) > 3:
        return

    capAxis = "y"
    capUp = "z"
    # upLoc = cmds.spaceLocator(name = "{}_upLoc".format(name))[0]

    ctrl = rig.create_control(type="sphere", name="{}_CTRL".format(name), color="blue")
    ctrlGrp = cmds.group(empty=True, name="{}_path_GRP".format(name))
    capGrp = cmds.group(empty=True, name="{}_cap_GRP".format(name))
    deadGrp = cmds.group(empty=True, name="{}_noInherit_GRP".format(name))
    if capRig:
        cmds.parent(capRig, capGrp)

    cmds.parent(deadGrp, ctrlGrp)
    cmds.parent(ctrl, ctrlGrp)

    # add attrs to control
    cmds.addAttr(ctrl, ln="__xtraAttrs__", nn="__xtraAttrs__", at="bool", k=True)
    cmds.setAttr("{}.__xtraAttrs__".format(ctrl), l=True)
    cmds.addAttr(ctrl, ln="alongPath", at="float", min=0, max=100, k=True, dv=100.0)
    cmds.setAttr("{}.alongPath".format(ctrl), 100)
    cmds.addAttr(ctrl, ln="reverseNormals", at="long", min=0, max=1, k=True)
    cmds.addAttr(ctrl, ln="capVisibility", at="long", min=0, max=1, k=True)
    cmds.setAttr("{}.capVisibility".format(ctrl), 1)
    cmds.addAttr(ctrl, ln="capWidth", at="float", k=True, min=.01, max=2.0, dv=1.0)
    cmds.addAttr(ctrl, ln="capHeight", at="float", k=True, min=.01, max=2.0, dv=1.0)
    cmds.addAttr(ctrl, ln="profileWidth", at="float", k=True, min=.001, max=3, dv=1.0)

    # driver attrs
    cmds.addAttr(ctrl, ln="textureRepeatMult", at="float", min=0.01, dv=1.0, k=True)
    cmds.addAttr(ctrl, ln="prmHolder", at="float", k=True)
    cmds.addAttr(ctrl, ln="rptHolder", at="float", k=True)

    # cmds.addAttr(ctrl, ln="repeatMult", at="message", k=True)
    # cmds.addAttr(ctrl, ln="parameterMult", at ="message", k=True)

    # connect mult to path
    mult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{}_paraMult".format(name))
    cmds.connectAttr("{}.alongPath".format(ctrl), "{}.input1X".format(mult))
    cmds.setAttr("{}.input2X".format(mult), 0.01)
    cmds.connectAttr("{}.profileWidth".format(ctrl), "{}.scaleX".format(profileCrv))
    cmds.connectAttr("{}.profileWidth".format(ctrl), "{}.scaleZ".format(profileCrv))

    # reverse for normals
    reverse = cmds.shadingNode("reverse", asUtility=True, name="{}_reverse".format(name))
    cmds.connectAttr("{}.reverseNormals".format(ctrl), "{}.inputX".format(reverse))

    # cap and texture attrs and nodes
    cmds.connectAttr("{}.capVisibility".format(ctrl), "{}.v".format(capGrp))
    repeatMult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{}_RptMult".format(name))
    cmds.connectAttr("{}.outputX".format(mult), "{}.input1X".format(repeatMult))
    cmds.connectAttr("{}.textureRepeatMult".format(ctrl), "{}.input2X".format(repeatMult))
    # cmds.connectAttr("{}.message".format(repeatMult), "{}.repeatMult".format(ctrl))
    # cmds.connectAttr("{}.message".format(mult), "{}.parameterMult".format(ctrl))
    cmds.connectAttr("{}.outputX".format(repeatMult), "{}.rptHolder".format(ctrl))
    cmds.connectAttr("{}.outputX".format(mult), "{}.prmHolder".format(ctrl))
    cmds.setAttr("{}.prmHolder".format(ctrl), l=True)
    cmds.setAttr("{}.rptHolder".format(ctrl), l=True)
    cmds.connectAttr("{}.capWidth".format(ctrl), "{}.scaleX".format(capGrp))
    cmds.connectAttr("{}.capWidth".format(ctrl), "{}.scaleZ".format(capGrp))
    cmds.connectAttr("{}.capHeight".format(ctrl), "{}.scaleY".format(capGrp))

    # position control at start of curve
    startPos = cmds.pointOnCurve(guideCrv, parameter=0, position=True)
    cmds.xform(ctrlGrp, ws=True, t=startPos)
    # cmds.xform(upLoc, ws=True, t=(startPos[0], startPos[1]+3.0, startPos[2]))

    moPath = cmds.pathAnimation(capGrp, guideCrv, fractionMode=True, follow=True, followAxis=capAxis, upAxis=capUp,
                                worldUpType="scene", startTimeU=0.0, endTimeU=100.0)
    moPathAnimAttr = cmds.listConnections("{}.uValue".format(moPath), d=False, p=True)[0]

    start, end = getSliderRange()
    current = cmds.currentTime(q=True)
    cmds.currentTime(start)

    pPos = cmds.xform(capGrp, q=True, ws=True, rp=True)
    pRot = cmds.xform(capGrp, q=True, ws=True, ro=True)
    cmds.xform(profileCrv, ws=True, t=pPos)
    cmds.xform(profileCrv, ws=True, ro=pRot)

    cmds.currentTime(current)

    # extrude the curve
    extr = cmds.extrude(profileCrv, guideCrv, ch=True, range=True, polygon=True, extrudeType=2, useComponentPivot=True,
                        fixedPath=True, useProfileNormal=True, reverseSurfaceIfPathReversed=True)
    extrGeo, extrNode = extr[0], extr[1]

    normal = cmds.polyNormal(extrGeo, normalMode=4, userNormalMode=0, ch=1)[0]
    cmds.connectAttr("{}.outputX".format(reverse), "{}.normalMode".format(normal))

    # get extrude connections
    connects = cmds.listConnections(extrNode)
    profNode, pathNode, tessNode = connects[0], connects[1], connects[2]

    # connect up stuff to extrusion
    cmds.connectAttr("{}.outputX".format(mult), "{}.maxValue".format(pathNode))
    cmds.parent(guideCrv, ctrl)
    cmds.setAttr("{}.inheritsTransform".format(deadGrp), 0)
    cmds.parent(extrGeo, deadGrp)
    cmds.parent(profileCrv, deadGrp)
    cmds.setAttr("{}.v".format(profileCrv), 0)
    cmds.parent(capGrp, deadGrp)

    # motion path stuff
    cmds.delete(moPathAnimAttr.partition(".")[0])
    cmds.connectAttr("{}.outputX".format(mult), "{}.uValue".format(moPath))

    # reference
    # extrude -ch true -rn true -po 1 -et 2 -ucp 1 -fpt 1 -upn 1 -rotation 0 -scale 1 -rsp 1 "nurbsCircle1" "curve4" ;

    print("ending extrude")


def getSliderRange(*args):
    """gets framerange in current scene and returns start and end frames"""

    # get timeslider range start
    startF = cmds.playbackOptions(query=True, min=True)
    endF = cmds.playbackOptions(query=True, max=True)

    return(startF, endF)


def connectTexture(*args):
    sel = cmds.ls(sl=True)
    ctrl = sel[0]
    # repeatMult = cmds.connectionInfo("{}.repeatMult".format(ctrl), sourceFromDestination=True).partition(".")[0]
    # parameterMult = cmds.connectionInfo("{}.parameterMult".format(ctrl), sourceFromDestination=True).partition(".")[0]
    # print repeatMult, parameterMult

    if len(sel) > 1:
        p2ds = sel[1:]

        for node in p2ds:
            cmds.connectAttr("{}.rptHolder".format(ctrl), "{}.repeatV".format(node))


def curveExtrude():
    extrudeUI()
