import maya.cmds as cmds
import zTools3.rig.zbw_rig as rig
import importlib

importlib.reload(rig)

# ---------------- length drives which file texture we use
# TODO - cap should be optional
# TODO - keep history to orig curve optional
# TODO - write own funcs to: a) align objs with cure at %, hook up moPath Node wo command (skip addDoubles)


widgets = {}


def curveExtrudeUI():
    if cmds.window("crvExtrRigWin", exists=True):
        cmds.deleteUI("crvExtrRigWin")

    width = 300
    widgets["win"] = cmds.window("crvExtrRigWin", t="curveExtrudeRig", w=width, sizeable=True, resizeToFitChildren=True)
    widgets["CLO"] = cmds.columnLayout()

    ##### extrude ########
    widgets["extrudeFLO"] = cmds.frameLayout("1. Extrude Curve", w=300, cll=True, cl=False, bgc=(0, 0, 0),
                                             cc=resizeWindow)
    widgets["extrCLO"] = cmds.columnLayout()
    cmds.text(
        l="select the profile curve, cap rig, and curves to\nhook up in that order!\nWARNING: This won't undo cleanly so use 'deleteRig'\nbelow!",
        al="left")
    widgets["recoIFBG"] = cmds.intFieldGrp(l="Points/Unit:", nf=1, cal=[(1, "left"), (2, "left")], v1=.1, en=False,
                                           cw=[(1, 70), (2, 50)])
    widgets["ctrlFFG"] = cmds.floatFieldGrp(l="Control Size (units)", nf=1, cal=[(1, "left"), (2, "left")], v1=2,
                                            cw=[(1, 100), (2, 50)])
    # widgets["keepCBG"] = cmds.checkBoxGrp(l="keep originals?", v1 = True, cal=[(1, "left"), (2, "left")], cw=[(1, 70), (2, 40)])
    widgets["rebuildBut"] = cmds.button(l="Build Rigs!", w=300, h=35, bgc=(.5, .4, .4), c=extrude)
    cmds.separator(h=10)
    cmds.text("To delete a rig(s), select ctrl(s) and click below")
    widgets["deleteBut"] = cmds.button(l="Delete Rigs!", w=300, h=25, bgc=(.3, .2, .2), c=deleteRig)
    cmds.separator(h=10)

    ###### create textures #########
    cmds.setParent(widgets["CLO"])
    widgets["textureFLO"] = cmds.frameLayout("2. Create Textures and Switch", w=300, cll=True, cl=True, bgc=(0, 0, 0),
                                             cc=resizeWindow)
    widgets["textCLO"] = cmds.columnLayout()
    cmds.text(
        l="Select the shader node THEN shift select all curve ctrls,\nThis will assign the shader and create a txt node for each\nand create a 3switch, then connect ctl 'rptHolder' to place2d's",
        al="left")
    cmds.separator(h=10)
    widgets["textBut"] = cmds.button(l="Create shader connections!", w=300, h=35, bgc=(.3, .5, .4), c=texture)

    ####### fill file textures ######
    cmds.setParent(widgets["CLO"])
    widgets["fileFLO"] = cmds.frameLayout("3. Replace File Textures", w=300, cll=True, cl=True, bgc=(0, 0, 0),
                                          cc=resizeWindow)
    widgets["fileCLO"] = cmds.columnLayout()
    # ---------------- option to select from file instead of just from existing, change UI and function
    # widgets["fileRBG"] = cmds.radioButtonGrp(l="Where from?", nrb=2, sl=1, l1="existing txtr", l2="explore", cal=[(1, "left"),(2, "left"),(3, "left")], cw=[(1, 70), (2, 60),(3, 50)], cc=toggleFile)
    # cmds.separator(h=10)
    # widgets["fileFile"] = cmds.text(l="Select file from right side and then ctrl objs")
    # cmds.separator(h=10)
    widgets["selFile"] = cmds.text(
        l="Will populate the file nodes on textures.\nSelect a 'file' node with the correct file\n and then ctrl objs for curves",
        al="left")
    cmds.separator(h=10)
    widgets["fileBut"] = cmds.button(l="Populate connections!", w=300, h=35, bgc=(.5, .5, .4), c=fileLoad)

    ####### replace caps ######
    cmds.setParent(widgets["CLO"])
    widgets["capFLO"] = cmds.frameLayout("4. Replace cap rigs", w=300, cll=True, cl=True, bgc=(0, 0, 0),
                                         cc=resizeWindow)
    widgets["capCLO"] = cmds.columnLayout()
    widgets["capText"] = cmds.text(l="Select the cap replacement obj, then ctrl objs\nfor curves. ", al="left")
    cmds.separator(h=10)
    widgets["capBut"] = cmds.button(l="Replace caps!", w=300, h=35, bgc=(.4, .5, .5), c=capReplace)
    cmds.separator(h=10)
    widgets["baseCapBut"] = cmds.button(l="Add Base Caps!", w=300, h=35, bgc=(.5, .4, .5), c=addBaseCap)

    cmds.showWindow(widgets["win"])
    resizeWindow()


def resizeWindow(*args):
    cmds.window(widgets["win"], e=True, rtf=True, w=100, h=100)


def toggleFile(*args):
    sel = cmds.radioButtonGrp(widgets["fileRBG"], q=True, sl=True)

    if sel == 1:
        cmds.text(widgets["selFile"], e=True, en=False)


def curveCheck(obj):
    """ takes object and returns true if it's a curve"""
    shpList = cmds.listRelatives(obj, shapes=True)
    if (not shpList) or (cmds.objectType(shpList[0]) != "nurbsCurve"):
        return False
    else:
        return True


def extrude(*args):
    sel = cmds.ls(sl=True, exactType="transform")

    # keep = cmds.checkBoxGrp(widgets["keepCBG"], q=True, v1=True)

    if len(sel) < 3:
        cmds.warning("You need to select the profile, then cap, then path curve in order!")
        return

    profileOrig = sel[0]
    cap = sel[1]
    curves = sel[2:]
    selectList = []

    if not cmds.objExists("pastaRigSetupComponents_Grp"):
        cmds.group(empty=True, name="pastaRigSetupComponents_Grp")

    if not curveCheck(profileOrig):
        cmds.warning("Your first selection (profile) is not a curve!")
        return

    if not cmds.objExists("curveRebuild_originals_grp"):
        cmds.group(empty=True, name="curveRebuild_originals_grp")

    # do some checks for parenting
    tempPList = [profileOrig, cap, "curveRebuild_originals_grp"]
    for n in tempPList:
        par = rig.parent_check(n)
        if par != "pastaRigSetupComponents_Grp":
            cmds.parent(n, "pastaRigSetupComponents_Grp")

    for curve in curves:
        if not curveCheck(curve):
            cmds.warning("{0} is not a curve, skipping!".format(curve))

        else:
            profile = cmds.duplicate(profileOrig, name="{0}_profileCrv".format(curve))[0]

            newCap = cmds.duplicate(cap, returnRootsOnly=True, renameChildren=True, name="{0}_capRig".format(curve))[0]
            cmds.setAttr("{0}.v".format(newCap), 1)
            # rigGrp = cmds.group(empty=True, name = "{0}_rig_grp".format(curve))
            curveResults = rebuildCurve(curve)
            newCrv = curveResults[0]
            rebuild = curveResults[1]

            cmds.parent(curve, "curveRebuild_originals_grp")

            capAxis = "y"
            capUp = "z"

            ctrl = rig.create_control(type="sphere", name="{0}_CTRL".format(curve), color="blue")
            ctrlScale(ctrl)
            capGrp = cmds.group(empty=True, name="{0}_cap_grp".format(curve))
            baseCapGrp = cmds.group(empty=True, name="{0}_baseCap_grp".format(curve))
            tempBaseCap = cmds.group(empty=True, name="{0}_tempBaseCap".format(curve))
            cmds.parent(tempBaseCap, baseCapGrp)
            deadGrp = cmds.group(empty=True, name="{0}_noInherit_grp".format(curve))

            cmds.parent(deadGrp, ctrl)
            # cmds.parent(ctrl, rigGrp)
            cmds.parent(newCap, capGrp)

            # add attrs to control
            cmds.addAttr(ctrl, ln="__mainCtrls__", nn="__mainCtrls__", at="bool", k=True)
            cmds.setAttr("{0}.__mainCtrls__".format(ctrl), l=True)
            cmds.addAttr(ctrl, ln="alongPath", at="float", min=0, max=100, k=True, dv=100.0)
            cmds.setAttr("{0}.alongPath".format(ctrl), 100)
            cmds.addAttr(ctrl, ln="geoVis", at="long", min=0, max=1, k=True, dv=1)
            cmds.addAttr(ctrl, ln="pathCurveVis", at="long", min=0, max=1, k=True, dv=1)
            cmds.addAttr(ctrl, ln="capVisibility", at="long", min=0, max=1, k=True, dv=1)
            cmds.addAttr(ctrl, ln="baseCapVisibility", at="long", k=True, dv=1, min=0, max=1)
            cmds.addAttr(ctrl, ln="__curveStuff__", nn="__curveStuff__", at="bool", k=True)
            cmds.setAttr("{0}.__curveStuff__".format(ctrl), l=True)
            cmds.addAttr(ctrl, ln="density", at="float", min=0.02, max=30, k=True, dv=0.1)
            cmds.addAttr(ctrl, ln="radiusDivisions", at="float", k=True, min=1, max=3, dv=1.0)
            cmds.addAttr(ctrl, ln="reverseNormals", at="long", min=0, max=1, k=True)
            cmds.addAttr(ctrl, ln="offsetCap", at="float", k=True, dv=0.0, min=-1.0, max=1.0)

            cmds.addAttr(ctrl, ln="profileWidth", at="float", k=True, min=.001, max=3.0, dv=1.0)
            cmds.addAttr(ctrl, ln="capWidth", at="float", k=True, min=.001, max=3.0, dv=1.0)
            cmds.addAttr(ctrl, ln="baseCapWidth", at="float", k=True, dv=1, min=.001, max=3.0)
            cmds.addAttr(ctrl, ln="capHeight", at="float", k=True, min=.01, max=2.0, dv=1.0)
            cmds.addAttr(ctrl, ln="baseCapHeight", at="float", k=True, dv=1, min=0, max=3.0)
            cmds.addAttr(ctrl, ln="rotateExtrusion", at="float", k=True, min=0, max=360)
            cmds.addAttr(ctrl, ln="rotateCap", at="float", k=True)
            cmds.addAttr(ctrl, ln="rotateBaseCap", at="float", k=True, dv=0.0)

            cmds.addAttr(ctrl, ln="__textureAndRef__", nn="__textureAndRef__", at="bool", k=True)
            cmds.setAttr("{0}.__textureAndRef__".format(ctrl), l=True)
            cmds.addAttr(ctrl, ln="textureRepeatMult", at="float", min=0.01, dv=1.0, k=True)
            # cmds.addAttr(ctrl, ln="textureRepeatU", at="float", min = 0.01, max =10,dv=1, k=True)
            # cmds.addAttr(obj, ln="offsetU", at="float", min=0, max=1, dv=0, k=True)
            # cmds.addAttr(obj, ln="offsetV", at="float", min=0, max=1, dv=0, k=True)

            cmds.addAttr(ctrl, ln="length", at="float", k=True)
            initLen = cmds.arclen(newCrv, ch=False)
            cmds.setAttr("{0}.length".format(ctrl), initLen)
            cmds.setAttr("{0}.length".format(ctrl), l=True)

            cmds.addAttr(ctrl, ln="geo", at="message")
            cmds.addAttr(ctrl, ln="fileTexture", at="message")
            cmds.addAttr(ctrl, ln="capRig", at="message")
            cmds.addAttr(ctrl, ln="tempBaseCap", at="message")

            cmds.addAttr(ctrl, ln="origCrv", at="message")
            cmds.addAttr(ctrl, ln="rptMult", at="message")
            cmds.addAttr(ctrl, ln="paraMult", at="message")
            cmds.addAttr(ctrl, ln="densMult", at="message")

            cmds.connectAttr("{0}.message".format(newCap), "{0}.capRig".format(ctrl))
            cmds.connectAttr("{0}.message".format(curve), "{0}.origCrv".format(ctrl))
            cmds.connectAttr("{0}.message".format(tempBaseCap), "{0}.tempBaseCap".format(ctrl))

            # reference/driver attrs
            cmds.addAttr(ctrl, ln="prmHolder", at="float", k=True)
            cmds.addAttr(ctrl, ln="rptHolder", at="float", k=True)
            # cmds.setAttr("{0}.radiusDivisions".format(ctrl), l=True)

            # connect mult to path
            mult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_paraMult".format(curve))
            cmds.connectAttr("{0}.alongPath".format(ctrl), "{0}.input1X".format(mult))
            cmds.setAttr("{0}.input2X".format(mult), 0.01)
            cmds.connectAttr("{0}.profileWidth".format(ctrl), "{0}.scaleX".format(profile))
            cmds.connectAttr("{0}.profileWidth".format(ctrl), "{0}.scaleZ".format(profile))
            cmds.connectAttr("{0}.message".format(mult), "{0}.paraMult".format(ctrl))

            # reverse for normals
            reverse = cmds.shadingNode("reverse", asUtility=True, name="{0}_reverse".format(curve))
            cmds.connectAttr("{0}.reverseNormals".format(ctrl), "{0}.inputX".format(reverse))

            # cap, path and texture attrs and nodes
            cmds.connectAttr("{0}.capVisibility".format(ctrl), "{0}.v".format(capGrp))
            cmds.connectAttr("{0}.baseCapVisibility".format(ctrl), "{0}.v".format(baseCapGrp))

            repeatMult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_RptMult".format(curve))
            cmds.connectAttr("{0}.outputX".format(mult), "{0}.input1X".format(repeatMult))
            cmds.connectAttr("{0}.textureRepeatMult".format(ctrl), "{0}.input2X".format(repeatMult))
            cmds.connectAttr("{0}.pathCurveVis".format(ctrl), "{0}.visibility".format(newCrv))
            cmds.connectAttr("{0}.message".format(repeatMult), "{0}.rptMult".format(ctrl))

            # connect the rebuild density
            densityMult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_DensityMult".format(curve))
            cmds.connectAttr("{0}.density".format(ctrl), "{0}.input1X".format(densityMult))
            cmds.connectAttr("{0}.length".format(ctrl), "{0}.input2X".format(densityMult))
            cmds.connectAttr("{0}.outputX".format(densityMult), "{0}.spans".format(rebuild))
            cmds.connectAttr("{0}.message".format(densityMult), "{0}.densMult".format(ctrl))

            # cap offest mult and connection
            offsetAdd = cmds.shadingNode("addDoubleLinear", asUtility=True, name="{0}_OffsetAdd".format(curve))
            cmds.connectAttr("{0}.outputX".format(mult), "{0}.input1".format(offsetAdd))
            cmds.connectAttr("{0}.offsetCap".format(ctrl), "{0}.input2".format(offsetAdd))

            cmds.connectAttr("{0}.outputX".format(repeatMult), "{0}.rptHolder".format(ctrl))
            cmds.connectAttr("{0}.outputX".format(mult), "{0}.prmHolder".format(ctrl))
            cmds.setAttr("{0}.prmHolder".format(ctrl), l=True)
            cmds.setAttr("{0}.rptHolder".format(ctrl), l=True)
            cmds.connectAttr("{0}.capWidth".format(ctrl), "{0}.scaleX".format(capGrp))
            cmds.connectAttr("{0}.capWidth".format(ctrl), "{0}.scaleZ".format(capGrp))
            cmds.connectAttr("{0}.capHeight".format(ctrl), "{0}.scaleY".format(capGrp))
            cmds.connectAttr("{0}.rotateCap".format(ctrl), "{0}.rotateY".format(newCap))

            cmds.connectAttr("{0}.baseCapWidth".format(ctrl), "{0}.scaleX".format(baseCapGrp))
            cmds.connectAttr("{0}.baseCapWidth".format(ctrl), "{0}.scaleZ".format(baseCapGrp))
            cmds.connectAttr("{0}.baseCapHeight".format(ctrl), "{0}.scaleY".format(baseCapGrp))

            # position control at start of curve
            startPos = cmds.pointOnCurve(curve, parameter=0, position=True)
            cmds.xform(ctrl, ws=True, t=startPos)

            moPath = cmds.pathAnimation(capGrp, newCrv, fractionMode=True, follow=True, followAxis=capAxis,
                                        upAxis=capUp, worldUpType="scene", startTimeU=0.0, endTimeU=100.0)
            moPathAnimAttr = cmds.listConnections("{0}.uValue".format(moPath), d=False, p=True)[0]

            baseMoPath = cmds.pathAnimation(baseCapGrp, newCrv, fractionMode=True, inverseFront=True, follow=True,
                                            followAxis=capAxis, upAxis=capUp, worldUpType="scene", startTimeU=0.0,
                                            endTimeU=100.0)
            baseMoPathAnimAttr = cmds.listConnections("{0}.uValue".format(baseMoPath), d=False, p=True)[0]

            start, end = getSliderRange()
            current = cmds.currentTime(q=True)
            cmds.currentTime(0)

            pPos = cmds.xform(capGrp, q=True, ws=True, rp=True)
            pRot = cmds.xform(capGrp, q=True, ws=True, ro=True)
            cmds.xform(profile, ws=True, t=pPos)
            cmds.xform(profile, ws=True, ro=pRot)

            cmds.currentTime(current)

            # extrude the curve
            extr = cmds.extrude(profile, newCrv, ch=True, range=True, polygon=True, extrudeType=2,
                                useComponentPivot=True,
                                fixedPath=True, useProfileNormal=True, reverseSurfaceIfPathReversed=True)
            extrGeo, extrNode = extr[0], extr[1]

            # double check that nurbs to poly conversion is set up
            shp = cmds.listRelatives(extrGeo, s=True)[0]
            tess = cmds.connectionInfo("{0}.inMesh".format(shp), sfd=True).partition(".")[0]
            cmds.setAttr("{0}.format".format(tess), 2)
            cmds.setAttr("{0}.polygonType".format(tess), 1)
            cmds.setAttr("{0}.uType".format(tess), 3)
            cmds.setAttr("{0}.vType".format(tess), 3)
            cmds.setAttr("{0}.uNumber".format(tess), 1)
            cmds.setAttr("{0}.vNumber".format(tess), 1)
            cmds.setAttr("{0}.useChordHeight".format(tess), 0)

            normal = cmds.polyNormal(extrGeo, normalMode=4, userNormalMode=0, ch=1)[0]
            cmds.connectAttr("{0}.outputX".format(reverse), "{0}.normalMode".format(normal))
            cmds.connectAttr("{0}.message".format(extrGeo), "{0}.geo".format(ctrl))
            cmds.connectAttr("{0}.geoVis".format(ctrl), "{0}.visibility".format(extrGeo))
            cmds.connectAttr("{0}.rotateExtrusion".format(ctrl), "{0}.rotation".format(extrNode))

            # get extrude connections
            connects = cmds.listConnections(extrNode)
            profNode, pathNode, tessNode = connects[0], connects[1], connects[2]

            # connect up stuff to extrusion
            cmds.connectAttr("{0}.outputX".format(mult), "{0}.maxValue".format(pathNode))
            cmds.connectAttr("{0}.radiusDivisions".format(ctrl), "{0}.uNumber".format(tessNode))
            cmds.parent(newCrv, ctrl)
            cmds.setAttr("{0}.inheritsTransform".format(deadGrp), 0)
            cmds.parent(extrGeo, deadGrp)
            cmds.parent(profile, deadGrp)
            cmds.setAttr("{0}.v".format(profile), 0)
            cmds.parent(capGrp, deadGrp)
            cmds.parent(baseCapGrp, deadGrp)

            # motion path stuff
            cmds.delete(moPathAnimAttr.partition(".")[0])
            cmds.delete(baseMoPathAnimAttr.partition(".")[0])
            cmds.setAttr("{0}.uValue".format(baseMoPath), 0)

            cmds.connectAttr("{0}.output".format(offsetAdd), "{0}.uValue".format(moPath))

            selectList.append(ctrl)

    cmds.setAttr("{0}.visibility".format(cap), 0)
    cmds.setAttr("{0}.visibility".format(profileOrig), 0)
    cmds.select(selectList, r=True)


def deleteRig(*args):
    # check for ctrl
    sel = cmds.ls(sl=True, type="transform")
    if sel:
        for ctrl in sel:
            # try
            rpt = cmds.connectionInfo("{0}.rptMult".format(ctrl), sfd=True).partition(".")[0]
            dens = cmds.connectionInfo("{0}.densMult".format(ctrl), sfd=True).partition(".")[0]
            curve = cmds.connectionInfo("{0}.origCrv".format(ctrl), sfd=True).partition(".")[0]
            para = cmds.connectionInfo("{0}.paraMult".format(ctrl), sfd=True).partition(".")[0]

            if rig.parent_check(curve):
                cmds.parent(curve, world=True)
            cmds.setAttr("{0}.v".format(curve), 1)

            # check for file node, grab it, then find p2d from that and delete it
            fTextFull = cmds.connectionInfo("{0}.fileTexture".format(ctrl), sfd=True)
            print()
            "fTextFull:", fTextFull
            if fTextFull:
                fText = fTextFull.partition(".")[0]
                print()
                fText
                p2dFull = cmds.connectionInfo("{0}.uvCoord".format(fText), sfd=True)
                print()
                p2dFull
                if p2dFull:
                    p2d = p2dFull.partition(".")[0]
                    cmds.delete(p2d)
                print()
                "ready to delete"
                cmds.delete(fText)

            cmds.delete([ctrl, rpt, dens, para])


def getSliderRange(*args):
    """gets framerange in current scene and returns start and end frames"""

    # get timeslider range start
    startF = cmds.playbackOptions(query=True, min=True)
    endF = cmds.playbackOptions(query=True, max=True)

    return (startF, endF)


def ctrlScale(ctrl):
    scl = cmds.floatFieldGrp(widgets["ctrlFFG"], q=True, v1=True) / 2
    cvs = cmds.ls("{0}.cv[*]".format(ctrl), fl=True)
    cmds.select(cvs)
    cmds.scale(scl, scl, scl)
    cmds.select(clear=True)


def calculatePts(crv, *args):
    """
    uses the window to get the number of pts that should be in the curve
    """
    cLen = cmds.arclen(crv, ch=False)
    perUnit = cmds.intFieldGrp(widgets["recoIFBG"], q=True, v1=True)
    total = cLen * perUnit

    return total


def rebuildCurve(curve, *args):
    """
        rebuilds selected curves to specs in window
    """
    num = calculatePts(curve)
    newCrv = cmds.rebuildCurve(curve, rebuildType=0, ch=1, spans=num, keepRange=0, replaceOriginal=0,
                               name="{0}_RB".format(curve))
    cmds.setAttr("{0}.v".format(curve), 0)

    return newCrv


def texture(*args):
    sel = cmds.ls(sl=True)
    shd = sel[0]
    ctrls = sel[1:]

    sg = cmds.listConnections(shd, type="shadingEngine")[0]

    tNode = cmds.shadingNode("file", asTexture=True, name="fileTemplate", isColorManaged=True)
    pNode = cmds.shadingNode("place2dTexture", asUtility=True, name="placeTemplate")
    pAttrs = ["coverage", "translateFrame", "rotateFrame", "mirrorU", "mirrorV", "stagger", "wrapU", "wrapV",
              "repeatUV", "offset", "rotateUV", "noiseUV", "vertexUvOne", "vertexUvTwo", "vertexUvThree",
              "vertexCameraOne", "outUV", "outUvFilterSize"]
    tAttrs = ["coverage", "translateFrame", "rotateFrame", "mirrorU", "mirrorV", "stagger", "wrapU", "wrapV",
              "repeatUV", "offset", "rotateUV", "noiseUV", "vertexUvOne", "vertexUvTwo", "vertexUvThree",
              "vertexCameraOne", "uv", "uvFilterSize"]

    ts = "{0}_TripleSwitch".format(shd)
    if not cmds.objExists(ts):
        ts = cmds.shadingNode("tripleShadingSwitch", asUtility=True, name="{0}_TripleSwitch".format(shd))
        cmds.connectAttr("{0}.output".format(ts), "{0}.color".format(shd))

    for x in range(len(pAttrs)):
        cmds.connectAttr("{0}.{1}".format(pNode, pAttrs[x]), "{0}.{1}".format(tNode, tAttrs[x]))

    for i in range(len(ctrls)):
        geo = cmds.connectionInfo("{0}.geo".format(ctrls[i]), sfd=True).partition(".")[0]

        # clear old connections from this to the triple switch
        clearShaderConnections(ts, geo)

        # don't do if the attr doesn't exist:
        if not cmds.attributeQuery("textureRepeatU", n=ctrls[i], exists=True):
            cmds.addAttr(ctrls[i], ln="textureRepeatU", at="float", min=0.01, max=10, dv=1, k=True)
        if not cmds.attributeQuery("offsetU", n=ctrls[i], exists=True):
            cmds.addAttr(ctrls[i], ln="offsetU", at="float", min=0, max=1, dv=0, k=True)
        if not cmds.attributeQuery("offsetV", n=ctrls[i], exists=True):
            cmds.addAttr(ctrls[i], ln="offsetV", at="float", min=0, max=1, dv=0, k=True)

        cmds.sets(geo, e=True, forceElement=sg)

        # delete file textures and p2d's with the name (and number at end)
        # delete entries in the triple switch

        dupeNodes = cmds.duplicate(tNode, un=True, rc=True)
        fileNode = cmds.rename(dupeNodes[0], "{0}_fileText".format(ctrls[i]))
        placeNode = cmds.rename(dupeNodes[1], "{0}_place2d".format(ctrls[i]))
        cmds.connectAttr("{0}.rptHolder".format(ctrls[i]), "{0}.repeatUV.repeatV".format(placeNode))
        cmds.connectAttr("{0}.textureRepeatU".format(ctrls[i]), "{0}.repeatUV.repeatU".format(placeNode))
        cmds.connectAttr("{0}.offsetU".format(ctrls[i]), "{0}.offsetU".format(placeNode))
        cmds.connectAttr("{0}.offsetV".format(ctrls[i]), "{0}.offsetV".format(placeNode))

        # what if there's already some stuff in the triple switch?
        tsList = cmds.listAttr(ts, m=True, st="*inShape*")
        lastIndex = 0
        if tsList:
            last = tsList[-1]
            lastIndex = int(last.partition("[")[2].partition("]")[0]) + 1

        geoShp = cmds.listRelatives(geo, s=True)[0]
        tsShp = "{0}.instObjGroups[0]".format(geoShp)
        cmds.connectAttr(tsShp, "{0}.input[{1}].inShape".format(ts, lastIndex))
        cmds.connectAttr("{0}.outColor".format(fileNode), "{0}.input[{1}].inTriple".format(ts, lastIndex))
        print()
        "connected {0}!".format(geo)

        cmds.connectAttr("{0}.message".format(fileNode), "{0}.fileTexture".format(ctrls[i]), f=True)

    # delete pNode and tNode
    cmds.delete(pNode, tNode)

    # worry about length switch later when we populate the file node itself


def clearShaderConnections(ts="", geo="", *args):
    myShape = cmds.listRelatives(geo, s=True)[0]
    tsList = cmds.listAttr(ts, m=True, st=["*input*"])
    if tsList:
        # delete empty entries? ?
        # for tsInput in tsList:
        #   shpList = cmds.connectionInfo("{0}.{1}.inShape".format(ts, tsInput), sfd=True)
        #   if not shpList:
        #       cmds.removeMultiInstance("blinn1_TripleSwitch.{0}".format(tsInput))

        for tsInput in tsList:
            shpList = cmds.connectionInfo("{0}.{1}.inShape".format(ts, tsInput), sfd=True).partition(".")
            shp = ""
            if shpList:
                shp = shpList[0]
            if shp == myShape:
                # clear out the shape node
                cmds.disconnectAttr("{0}.instObjGroups[0]".format(shp), "{0}.{1}.inShape".format(ts, tsInput))
                # clear out the texture (delete if we can)
                txt = cmds.connectionInfo("{0}.{1}.inTriple".format(ts, tsInput), sfd=True).partition(".")[0]
                cmds.disconnectAttr("{0}.outColor".format(txt), "{0}.{1}.inTriple".format(ts, tsInput))
                p2d = cmds.connectionInfo("{0}.uvCoord".format(txt), sfd=True).partition(".")[0]
                cmds.delete(txt, p2d)


def fileLoad(*args):
    sel = cmds.ls(sl=True)
    origTexture = sel[0]
    ctrls = sel[1:]

    # get path
    path = cmds.getAttr("{0}.fileTextureName".format(origTexture))
    if not path:
        cmds.warning("No file present in {0}. Cancelling!".format(origTexture))
        return

    for ctrl in ctrls:
        ctrlFile = cmds.connectionInfo("{0}.fileTexture".format(ctrl), sfd=True).partition(".")[0]

        # add path to ctrl file
        cmds.setAttr("{0}.fileTextureName".format(ctrlFile), path, type="string")


def capReplace(*args):
    sel = cmds.ls(sl=True, type="transform")

    if sel < 2:
        cmds.warning("You don't have two things selected (cap and one ctrl minimum)!")
        return

    newCap = sel[0]
    ctrls = sel[1:]
    for ctrl in ctrls:
        oldCap = cmds.connectionInfo("{0}.capRig".format(ctrl), sfd=True).partition(".")[0]
        dupe = rig.swap_dupe(newCap, oldCap, delete=True, name=oldCap)
        cmds.connectAttr("{0}.rotateCap".format(ctrl), "{0}.rotateY".format(dupe))
        cmds.connectAttr("{0}.message".format(dupe), "{0}.capRig".format(ctrl))
        cmds.setAttr("{0}.v".format(dupe), 1)

    # if not already, parent cap replace obj in folder and hide
    par = cmds.listRelatives(newCap, p=True)
    if not par or par[0] != "pastaRigSetupComponents_Grp":
        cmds.parent(newCap, "pastaRigSetupComponents_Grp")

    cmds.setAttr("{0}.v".format(newCap), 0)
    cmds.select(ctrls, r=True)


def addBaseCap(*args):
    sel = cmds.ls(sl=True, type="transform")

    if sel < 2:
        cmds.warning("You don't have two things selected (cap and one ctrl minimum)!")
        return

    newCap = sel[0]
    ctrls = sel[1:]

    for ctrl in ctrls:
        tempCap = cmds.connectionInfo("{0}.tempBaseCap".format(ctrl), sfd=True).partition(".")[0]

        dupe = rig.swap_dupe(newCap, tempCap, delete=True, name="{0}_baseCap".format(ctrl))
        cmds.setAttr("{0}.v".format(dupe), 1)
        cmds.connectAttr("{0}.rotateBaseCap".format(ctrl), "{0}.rotateY".format(dupe))
        cmds.connectAttr("{0}.message".format(dupe), "{0}.tempBaseCap".format(ctrl))

    # if not already, parent cap replace obj in folder and hide
    par = cmds.listRelatives(newCap, p=True)
    if not par or par[0] != "pastaRigSetupComponents_Grp":
        cmds.parent(newCap, "pastaRigSetupComponents_Grp")

    cmds.setAttr("{0}.v".format(newCap), 0)
    cmds.select(ctrls, r=True)


def curveExtrude():
    curveExtrudeUI()
