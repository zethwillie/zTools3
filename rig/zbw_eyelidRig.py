import maya.cmds as cmds
import maya.OpenMaya as om

from functools import partial

import zTools3.rig.zbw_rig as rig
import importlib


class EyelidRigUI(object):
    def __init__(self):
        self.create_UI()

    # get center of eyeball obj? derive up object from that?
    # pause to orient objects?

    # color radio buttons (red, blue, green?)

    # clean up rig at end

    def create_UI(self):
        if cmds.window("eyelidWin", exists=True):
            cmds.deleteUI("eyelidWin")

        self.win = cmds.window("eyelidWin", wh=[300, 400], s=False, t="zbw_eyelidRig")
        self.CLO = cmds.columnLayout()
        self.tab = cmds.tabLayout()
        cmds.columnLayout("Eyelid_Rig")

        self.name = cmds.textFieldGrp(l="Rig Name: ", cw=[(1, 100), (2, 180)], cal=[(1, "left"), (2, "left")], tx="lf_eyelid")
        self.colorRBG = cmds.radioButtonGrp(l="Color :", l1="Red", l2="Blue", l3="Green", nrb=3, cw4=[100, 50, 50, 50], cl4=["left", "left", "left", "left"], sl=2)
        self.centerObj = cmds.textFieldButtonGrp(l="Center Object: ", cw=[(1, 100), (2, 160), (3, 30)], cal=[(1, "left"), (2, "left"), (3, "left")], bl=">>>", bc=partial(self.get_object, "center"))
        self.upObj = cmds.textFieldButtonGrp(l="Up Object: ", cw=[(1, 100), (2, 160), (3, 30)], cal=[(1, "left"), (2, "left"), (3, "left")], bl=">>>", bc=partial(self.get_object, "up"))
        cmds.separator(h=10)

        self.topCrv = cmds.textFieldButtonGrp(l="Top Curve: ", cw=[(1, 100), (2, 160), (3, 30)], cal=[(1, "left"), (2, "left"), (3, "left")], bl=">>>", bc=partial(self.get_curves, "top"))
        self.botCrv = cmds.textFieldButtonGrp(l="Bot Curve: ", cw=[(1, 100), (2, 160), (3, 30)], cal=[(1, "left"), (2, "left"), (3, "left")], bl=">>>", bc=partial(self.get_curves, "bot"))
        cmds.separator(h=10)

        self.numCtrlIFG = cmds.intFieldGrp(l="Number of Ctrls: ", v1=5, cw=[(1, 100), (2, 180)], cal=[(1, "left"), (2, "left")], en=False)
        cmds.separator(h=10)

        self.blendCBG = cmds.checkBoxGrp(l="Group for Blend Shape: ", ncb=1, v1=1, cw=[(1, 140), (2, 180)], cal=[(1, "left"), (2, "left")])
        cmds.separator(h=10)

        self.createBut = cmds.button(l="Create eye lid rig!", w=290, h=50, bgc=(.5, .7, .5), c=self.gather_info_and_run)

        cmds.setParent(self.tab)
        cmds.columnLayout("Curve_tools")
        cmds.button(l="Create Curve From Selected Edge", w=290, h=50, bgc=(.7, .5, .5), c=self.create_curve_from_edge)
        cmds.separator(h=10)
        cmds.button(l="Selected Curve Match Test", w=290, h=50, bgc=(.5, .7, .5), c=self.test_selection_match)
        cmds.separator(h=10)
        cmds.button(l="Reverse Selected Curves", w=290, h=50, bgc=(.7, .5, .5), c=self.reverse_curve)
        cmds.separator(h=10)
        cmds.button(l="Duplicate and Mirror Curves to -X", w=290, h=50, bgc=(.5, .7, .5), c=self.duplicate_and_mirror_curves)

        cmds.showWindow(self.win)
        cmds.showWindow(self.win, e=True, w=5, h=5, rtf=True)

    def gather_info_and_run(self, *args):
        name = cmds.textFieldGrp(self.name, q=True, tx=True)
        cnt = cmds.textFieldButtonGrp(self.centerObj, q=True, tx=True)
        up = cmds.textFieldButtonGrp(self.upObj, q=True, tx=True)
        num = cmds.intFieldGrp(self.numCtrlIFG, q=True, v1=True)
        topCrv = cmds.textFieldButtonGrp(self.topCrv, q=True, tx=True)
        botCrv = cmds.textFieldButtonGrp(self.botCrv, q=True, tx=True)
        blend = cmds.checkBoxGrp(self.blendCBG, q=True, v1=True)
        colorID = cmds.radioButtonGrp(self.colorRBG, q=True, sl=True)
        color = "red"

        if colorID == 1:
            color = "red"
        if colorID == 2:
            color = "blue"
        if colorID == 3:
            color = "green"

        # test all ui stuff is there
        for x in [name, cnt, up, num, topCrv, botCrv]:
            if not x:
                cmds.warning("All fields have to have info!")
                return()

        confirm = self.test_curves(topCrv, botCrv)
        if confirm == "No":
            return()

        eyerig = EyelidRigBuild(name=name, cnt=cnt, up=up, num=num, topCrv=topCrv, botCrv=botCrv, blend=blend, color=color)

    def test_curves(self, topCrv, botCrv, dialog=True):
        # give two curves
        a = cmds.pointPosition("{0}.cv[0]".format(topCrv))
        b = cmds.pointPosition("{0}.cv[0]".format(botCrv))
        match0 = rig.is_close(a[0], b[0])
        match1 = rig.is_close(a[1], b[1])
        match2 = rig.is_close(a[2], b[2])
        if dialog:
            if not (match0 and match1 and match2):
                confirm = cmds.confirmDialog(title='Confirm', message="Your two curves don't have identical start points.\nContinue?", button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
                return(confirm)
            return("Yes")
        else:
            return((match0 and match1 and match2))

    def reverse_curve(self, *args):
        sel = cmds.ls(sl=True, exactType="transform")

        check = False
        if sel:
            for x in sel:
                check = rig.type_check(x, "nurbsCurve")
                if check:
                    cmds.reverseCurve(x, ch=False, replaceOriginal=True)
                    cmds.warning("Reversed direction of: {0}".format(x))
                else:
                    cmds.warning("{0} is not a nurbs curve".format(x))
        else:
            cmds.warning("Must select some curves")
            return

        cmds.select(sel, r=True)

    def create_curve_from_edge(self, *args):
        cmds.polyToCurve(ch=False, degree=1, form=2, conformToSmoothMeshPreview=True)

    def duplicate_and_mirror_curves(self, *args):
        sel = cmds.ls(sl=True, type="transform")
        if not sel:
            return()

        for x in sel:
            par = None
            origGrp = cmds.group(em=True, name="orig_tmp_grp")
            # get par
            parRaw = cmds.listRelatives(x, p=True)
            if parRaw:
                par = parRaw[0]
            # group objects, pivot at origin
            cmds.parent(x, origGrp)
            # duplicate group, rename children
            grp = cmds.duplicate(origGrp, renameChildren=True)
            newGrp = grp[0]
            newObj = grp[1]
            cmds.setAttr(newGrp + ".sx", -1.0)
            # reparent orig to par
            if par:
                cmds.parent(x, par)
            if not par:
                cmds.parent(x, w=True)
            cmds.delete(origGrp)
            # freeze transforms on group
            cmds.makeIdentity(newGrp, apply=True)
            cmds.parent(newObj, w=True)
            cmds.delete(newGrp)
            cmds.select(sel, r=True)

    def test_selection_match(self, *args):
        sel = cmds.ls(sl=True, exactType="transform")
        if len(sel) != 2:
            cmds.warning("you must select two curves to compare.")
            return()
        for x in sel:
            check = rig.type_check(x, "nurbsCurve")
            if not check:
                cmds.warning("Both objects must be nurbsCurves.")
                return()
        match = self.test_curves(sel[0], sel[1], False)

        if match:
            msg = "Your two curves match within a reasonable tolerance!"
            bgc = [.5, .7, .5]
        if not match:
            msg = "Your two curve DO NOT match within a reasonable tolerance.\nTry reversing one of the curves."
            bgc = [.7, .5, .5]

        cmds.confirmDialog(title="Curve Check", message=msg, button="OK", bgc=bgc)

    def get_curves(self, field):
        if field == "top":
            ui = self.topCrv
        if field == "bot":
            ui = self.botCrv

        sel = cmds.ls(sl=True, type="transform")
        if (not sel) or (len(sel) > 1):
            cmds.warning("You need to select one obj")
            return()
        obj = sel[0]
        shp = cmds.listRelatives(obj, s=True)[0]
        if cmds.objectType(shp) != "nurbsCurve":
            cmds.warning("This object isn't a nurbsCurve.")
            return()

        cmds.textFieldButtonGrp(ui, e=True, tx=obj)

    def get_object(self, field):
        if field == "center":
            ui = self.centerObj
        if field == "up":
            ui = self.upObj

        sel = cmds.ls(sl=True, type="transform")
        if (not sel) or (len(sel) > 1):
            cmds.warning("You need to select one obj")
            return()

        obj = sel[0]
        cmds.textFieldButtonGrp(ui, e=True, tx=obj)


class EyelidRigBuild(object):

    def __init__(self, name="eye", cnt=None, up=None, num=5, topCrv=None, botCrv=None, blend=1, color="blue"):
        """
        blend(int): 1 = grp things for blend shaping into rig, 0 = grp things for attaching into rig
        """
        if not (cnt and up):
            cmds.warning("You haven't provided a center and up object!")
            return()
        if not (topCrv and botCrv):
            cmds.warning("You haven't provided up and down curves!")
            return()

        self.name = name
        self.center = cnt
        self.up = up
        self.numCtrl = num
        self.topHiresCrv = cmds.rename(topCrv, "{0}_top_hi_CRV".format(name))
        self.botHiresCrv = cmds.rename(botCrv, "{0}_bot_hi_CRV".format(name))
        self.blend = blend
        self.centerPos = cmds.xform(self.center, q=True, ws=True, rp=True)
        self.color = color

        self.sides = ["top", "bot"]
        self.blinkCrvs = []
        self.blinkCrvGrp = cmds.group(empty=True, n="{0}_blink_crv_GRP".format(self.name))
        self.center_pivot([self.blinkCrvGrp])

        self.eyeRig = {"top": {}, "bot": {}}
        for side in self.sides:
            self.eyeRig[side]["crvList"] = []
            self.eyeRig[side]["crvGrp"] = cmds.group(empty=True, n="{0}_{1}_CRV_GRP".format(self.name, side))
            self.eyeRig[side]["locList"] = []
            self.eyeRig[side]["locGrp"] = cmds.group(empty=True, n="{0}_{1}_AIMLOC_GRP".format(self.name, side))
            self.eyeRig[side]["bindJntList"] = []
            self.eyeRig[side]["bindJntGrp"] = cmds.group(empty=True, n="{0}_{1}_BNDJNT_GRP".format(self.name, side))
            self.eyeRig[side]["bindCtrlList"] = []
            self.eyeRig[side]["fineCtrlGrp"] = cmds.group(empty=True, n="{0}_{1}_FINECTRL_GRP".format(self.name, side))
            self.eyeRig[side]["wires"] = []
            self.eyeRig[side]["wireBases"] = []
            self.eyeRig[side]["ctrlJntList"] = []
            self.eyeRig[side]["ctrlJntGrps"] = cmds.group(empty=True, n="{0}_{1}_ctrlJnt_GRP".format(self.name, side))
            self.eyeRig[side]["ctrlList"] = []
            self.eyeRig[side]["ctrlGrpList"] = []
            self.eyeRig[side]["ctrlsGrp"] = cmds.group(empty=True, n="{0}_{1}_ctrls_GRP".format(self.name, side))
            self.eyeRig[side]["proxyList"] = []
            self.eyeRig[side]["proxyGrpList"] = []
            self.eyeRig[side]["proxyGrp"] = cmds.group(empty=True, n="{0}_{1}_proxies_GRP".format(self.name, side))

            grps = [self.eyeRig[side]["crvGrp"], self.eyeRig[side]["bindJntGrp"], self.eyeRig[side]["locGrp"], self.eyeRig[side]["fineCtrlGrp"], self.eyeRig[side]["ctrlJntGrps"], self.eyeRig[side]["ctrlsGrp"], self.eyeRig[side]["proxyGrp"]]
            self.center_pivot(grps)

            if side == "top":
                cmds.parent(self.topHiresCrv, self.eyeRig[side]["crvGrp"])
            if side == "bot":
                cmds.parent(self.botHiresCrv, self.eyeRig[side]["crvGrp"])

        self.eyeRig["top"]["crvList"].append(self.topHiresCrv)
        self.eyeRig["bot"]["crvList"].append(self.botHiresCrv)

        self.create_rig()

    def create_rig(self):
        for side in list(self.eyeRig.keys()):
            # hiresCrv = self.eyeRig[side]["crvList"][0]
            self.create_locs_joints_at_curve(side)
            self.create_control_joints(side)
            self.create_control_wire_deformer(side)
            self.bind_control_curve(side)
            self.create_and_connect_ctrls(side)
            # can we orient off of eyeball? Does that make sense?
        self.smart_blink_setup()
        self.clean_up_rig()

    def center_pivot(self, clist):
        for obj in clist:
            cmds.xform(obj, ws=True, rp=self.centerPos)
            cmds.xform(obj, ws=True, sp=self.centerPos)

    def create_locs_joints_at_curve(self, side=None):

        crv = self.eyeRig[side]["crvList"][0]
        eps = cmds.ls("{0}.ep[*]".format(crv), fl=True)

        for x in range(len(eps)):
            loc = cmds.spaceLocator(n="{0}_{1}_{2}_LOC".format(self.name, side, x))[0]
            self.eyeRig[side]["locList"].append(loc)
            cmds.connectAttr(eps[x], "{0}.t".format(loc))
            cmds.setAttr("{0}.localScale".format(loc), 0.1, 0.1, 0.1)
            locPos = cmds.xform(loc, q=True, ws=True, rp=True)
            cmds.select(cl=True)
            baseJnt = cmds.joint(n="baseJnt_{0}{1}".format(crv[:-4], x), position=self.centerPos)
            endJnt = cmds.joint(n="endJnt_{0}{1}".format(crv[:-4], x), position=locPos)
            tmpEndJnt = self.extend_joint_chain(endJnt)
            cmds.select(cl=True)
            cmds.joint(baseJnt, e=True, oj="xyz", sao="yup", ch=True)
            cmds.delete(tmpEndJnt)
            self.eyeRig[side]["bindJntList"].append(baseJnt)

            cmds.parent(baseJnt, self.eyeRig[side]["bindJntGrp"])
            cmds.parent(loc, self.eyeRig[side]["locGrp"])

            ac = cmds.aimConstraint(loc, baseJnt, mo=False, wuo=self.up, wut="object", aim=(1, 0, 0), u=(0, 1, 0))

        # put controls on indiv joints for fine ctrl, create proxy for these? we have groups for these.

    def extend_joint_chain(self, endObj, baseObj=None):
        # get vector from par to endJnt
        if not baseObj:
            par = cmds.listRelatives(endObj, p=True)[0]
            pPos = cmds.xform(par, q=True, ws=True, rp=True)
        else:
            pPos = cmds.xform(baseObj, q=True, ws=True, rp=True)
        jPos = cmds.xform(endObj, q=True, ws=True, rp=True)
        parPos = om.MVector(pPos[0], pPos[1], pPos[2])
        jntPos = om.MVector(jPos[0], jPos[1], jPos[2])

        vec = jntPos - parPos
        newPos = jntPos + (vec * .25)
        cmds.select(cl=True)
        tmpEndJoint = cmds.joint(name="{0}_temp".format(endObj), p=newPos)
        cmds.parent(tmpEndJoint, endObj)
        return(tmpEndJoint)

    def create_control_joints(self, side=None):
        crv = self.eyeRig[side]["crvList"][0]
        ctrlCrvName = crv.replace("_hi_", "_ctrl_")
        ctrlCrv = rig.rebuild_curve(curve=crv, num=self.numCtrl - 1, name=ctrlCrvName, keep=True, ch=False)
        self.eyeRig[side]["crvList"].append(ctrlCrv)

        ctrlEps = cmds.ls("{0}.ep[*]".format(ctrlCrv), fl=True)

        # create joints
        for x in range(0, len(ctrlEps)):
            pos = cmds.getAttr(ctrlEps[x])[0]
            cmds.select(cl=True)
            jnt = cmds.joint(n="{0}_Jnt{1}".format(ctrlCrv, x), position=pos)
#---------------- orient this to eyelid?
            tmpEndJnt = self.extend_joint_chain(jnt, self.center)
            cmds.joint(jnt, e=True, oj="xyz", sao="yup", ch=True)
            cmds.delete(tmpEndJnt)
            jntGrp = rig.group_freeze(jnt)
            cmds.parent(jntGrp, self.eyeRig[side]["ctrlJntGrps"])
            self.eyeRig[side]["ctrlJntList"].append(jnt)

    def create_control_wire_deformer(self, side):
        wireNode = cmds.wire(self.eyeRig[side]["crvList"][0], envelope=1, groupWithBase=False, crossingEffect=0, localInfluence=0, wire=self.eyeRig[side]["crvList"][1], name="{0}_{1}_ctrl_WIRE".format(self.name, side))[0]
        wireBase = self.get_base_wire(wireNode)
        self.eyeRig[side]["wireBases"].append(wireBase)
        self.eyeRig[side]["wires"].append(wireNode)

        cmds.parent(self.eyeRig[side]["crvList"][1], self.eyeRig[side]["crvGrp"])
        cmds.parent(wireBase, self.eyeRig[side]["crvGrp"])

    def bind_control_curve(self, side):
        skinCluster = self.bind_crv_to_joints(self.eyeRig[side]["crvList"][1], self.eyeRig[side]["ctrlJntList"])

    def create_and_connect_ctrls(self, side):
        # create ctrls
        sideGrps = self.create_ctrls_for_joints(side)
        sideProxies = self.connect_ctrl_via_proxies(side)

    def bind_crv_to_joints(self, crv, jntList):
        skinCluster = cmds.skinCluster(jntList, crv, maximumInfluences=3, dropoffRate=4, skinMethod=0, normalizeWeights=2)
        return(skinCluster)

    def get_base_wire(self, wireDef):
        shp = cmds.listConnections(wireDef + ".baseWire[0]", p=True, s=True)[0].split(".")[0]
        basewire = cmds.listRelatives(shp, p=True)[0]
        return(basewire)

    def create_ctrls_for_joints(self, side):
        #----------------scale attr from ui to scale the ctrls
        for jnt in self.eyeRig[side]["ctrlJntList"]:
            ctrlName = "{0}_{1}_{2}_CTRL".format(self.name, side, self.eyeRig[side]["ctrlJntList"].index(jnt))
            ctrl = rig.create_control(name=ctrlName, type="circle", axis="x", color=self.color)
            grp = rig.group_freeze(ctrl)
            self.eyeRig[side]["ctrlList"].append(ctrl)
            self.eyeRig[side]["ctrlGrpList"].append(grp)
            rig.snap_to(jnt, grp)
            cmds.parent(grp, self.eyeRig[side]["ctrlsGrp"])

    def connect_ctrl_via_proxies(self, side):
        for grp in self.eyeRig[side]["ctrlGrpList"]:
            index = self.eyeRig[side]["ctrlGrpList"].index(grp)
            ctrl = self.eyeRig[side]["ctrlList"][index]
            ctrlProxy, grpProxy = rig.create_space_buffer_grps(ctrl)
            cmds.parent(grpProxy, self.eyeRig[side]["proxyGrp"])
            self.eyeRig[side]["proxyList"].append(ctrlProxy)
            self.eyeRig[side]["proxyGrpList"].append(grpProxy)
            # connect with joint
            rig.connect_transforms(ctrlProxy, self.eyeRig[side]["ctrlJntList"][index])

            # Do we need to add another layer of this? Don't think so. . .

    def smart_blink_setup(self):
        closeCrv = cmds.duplicate(self.eyeRig["top"]["crvList"][1], name="{0}_blinkLowres".format(self.name))[0]
        cmds.parent(closeCrv, self.blinkCrvGrp)
        self.blinkCrvs.append(closeCrv)

        midBS = cmds.blendShape(self.eyeRig["top"]["crvList"][1], self.eyeRig["bot"]["crvList"][1], closeCrv)[0]
        midTopAttr = "{0}.{1}".format(midBS, self.eyeRig["top"]["crvList"][1])
        midBotAttr = "{0}.{1}".format(midBS, self.eyeRig["bot"]["crvList"][1])
        # dupe bot hirez crvs and create wires
        cmds.setAttr(midTopAttr, 0)
        cmds.setAttr(midBotAttr, 1)
        # rename base wire crv
        botBlinkTgt = cmds.duplicate(self.eyeRig["bot"]["crvList"][0], name="{0}_bot_blinkTarget".format(self.name))[0]
        cmds.parent(botBlinkTgt, self.blinkCrvGrp)

        topBlinkTgt = cmds.duplicate(self.eyeRig["top"]["crvList"][0], name="{0}_top_blinkTarget".format(self.name))[0]
        cmds.parent(topBlinkTgt, self.blinkCrvGrp)

        botBlinkWire = cmds.wire(botBlinkTgt, envelope=1, groupWithBase=False, crossingEffect=0, localInfluence=0, w=closeCrv, name="{0}_botBlink_WIRE".format(self.name))[0]
        # rename base wire crv
        wireBotBaseCrv = self.get_base_wire(botBlinkWire)
        self.eyeRig["bot"]["wireBases"].append(wireBotBaseCrv)
        cmds.setAttr("{0}.scale[0]".format(botBlinkWire), 0)

        cmds.setAttr(midTopAttr, 1)
        cmds.setAttr(midBotAttr, 0)
        topBlinkWire = cmds.wire(topBlinkTgt, envelope=1, groupWithBase=False, crossingEffect=0, localInfluence=0, w=closeCrv, name="{0}_topBlink_WIRE".format(self.name))[0]
        wireTopBaseCrv = self.get_base_wire(topBlinkWire)
        self.eyeRig["top"]["wireBases"].append(wireTopBaseCrv)
        cmds.setAttr("{0}.scale[0]".format(topBlinkWire), 0)

        #cmds.parent(self.eyeRig["top"]["crvList"][0], self.eyeRig["top"]["crvGrp"])
        # blend shape hires curves to top, bot blink curves
        topBlinkBlend = cmds.blendShape(topBlinkTgt, self.eyeRig["top"]["crvList"][0], name="{0}_top_blink_BS".format(self.name))[0]
        topBlendAttr = "{0}.{1}".format(topBlinkBlend, topBlinkTgt)

        botBlinkBlend = cmds.blendShape(botBlinkTgt, self.eyeRig["bot"]["crvList"][0], name="{0}_bot_blink_BS".format(self.name))[0]
        botBlendAttr = "{0}.{1}".format(botBlinkBlend, botBlinkTgt)

        # put attrs on mid ctrls
        topCtrl = self.eyeRig["top"]["ctrlList"][2]
        botCtrl = self.eyeRig["bot"]["ctrlList"][2]

        cmds.addAttr(topCtrl, ln="__xtraAttrs__", at="enum", en="-----", k=True)
        cmds.addAttr(botCtrl, ln="__xtraAttrs__", at="enum", en="-----", k=True)
        cmds.setAttr("{0}.__xtraAttrs__".format(topCtrl), l=True)
        cmds.setAttr("{0}.__xtraAttrs__".format(botCtrl), l=True)

        cmds.addAttr(topCtrl, ln="blink", at="float", dv=0, min=0, max=1, k=True)
        cmds.connectAttr("{0}.blink".format(topCtrl), topBlendAttr)
        cmds.addAttr(botCtrl, ln="blink", at="float", dv=0, min=0, max=1, k=True)
        cmds.connectAttr("{0}.blink".format(botCtrl), botBlendAttr)

        # set up reverse node setup for moving the blink up/down
        upDownAttr = cmds.addAttr(topCtrl, ln="blendMidDownUp", at="float", dv=0.5, min=0, max=1.0, k=True)
        blinkReverse = cmds.shadingNode("reverse", asUtility=True, name="{0}_blink_reverse".format(self.name))
        cmds.connectAttr("{0}.blendMidDownUp".format(topCtrl), midTopAttr)
        cmds.connectAttr("{0}.blendMidDownUp".format(topCtrl), "{0}.inputX".format(blinkReverse))
        cmds.connectAttr("{0}.outputX".format(blinkReverse), midBotAttr)

        # clean up
        cmds.setAttr("{0}.blendMidDownUp".format(topCtrl), 0.5)

    def clean_up_rig(self):

        # make middel two ctrls half size
        for side in ["top", "bot"]:
            for ctrl in self.eyeRig[side]["ctrlList"]:
                rig.scale_nurbs_control(ctrl, 0.5, 0.5, 0.5)
            # parent constrain
            for x in [1, -2]:
                ctrl = self.eyeRig[side]["ctrlList"][x]
                rig.scale_nurbs_control(ctrl, 0.5, 0.5, 0.5)
                pc = cmds.parentConstraint([self.eyeRig[side]["ctrlList"][x - 1], self.eyeRig[side]["ctrlList"][x + 1]], cmds.listRelatives(ctrl, p=True)[0], mo=True)
                rig.assign_color(ctrl, "light{0}".format(self.color.capitalize()))

        # connect corners xforms
        for x in [0, -1]:
            botBufferGrp = rig.group_freeze(self.eyeRig["bot"]["ctrlList"][x])
            rig.connect_transforms(self.eyeRig["top"]["ctrlList"][x], botBufferGrp, f=True)
            cmds.addAttr(self.eyeRig["top"]["ctrlList"][x], ln="botCornerCtrlVis", at="short", min=0, max=1, dv=0, k=True)
            rig.scale_nurbs_control(self.eyeRig["bot"]["ctrlList"][x], 0.75, 0.75, 0.75)
            cmds.connectAttr("{0}.botCornerCtrlVis".format(self.eyeRig["top"]["ctrlList"][x]), "{0}.v".format(self.eyeRig["bot"]["ctrlList"][x]))

        # clean and hide attrs/vis
        for side in ["top", "bot"]:
            for ctrl in self.eyeRig[side]["ctrlList"]:
                rig.strip_to_rotate_translate(ctrl)
            for crv in self.eyeRig[side]["crvList"]:
                cmds.setAttr("{0}.v".format(crv), 0)
            for crv in self.blinkCrvs:
                cmds.setAttr("{0}.v".format(crv), 0)
            cmds.setAttr("{0}.v".format(self.blinkCrvGrp), 0)
            cmds.setAttr("{0}.v".format(self.eyeRig[side]["ctrlJntGrps"]), 0)
            cmds.setAttr("{0}.v".format(self.eyeRig[side]["proxyGrp"]), 0)
            cmds.setAttr("{0}.v".format(self.eyeRig[side]["locGrp"]), 0)
            cmds.setAttr("{0}.v".format(self.eyeRig[side]["crvGrp"]), 0)

        # start parenting things
        noXformGrp = cmds.group(empty=True, name="{0}_noTransform_GRP".format(self.name))
        cmds.setAttr(noXformGrp + ".inheritsTransform", 0)
        xformGrp = cmds.group(empty=True, name="{0}_transform_GRP".format(self.name))
        ctrlGrp = cmds.group(empty=True, name="{0}_ctrls_GRP".format(self.name))
        topGrp = cmds.group(empty=True, name="{0}_GRP".format(self.name))

        cmds.parent(ctrlGrp, xformGrp)
        cmds.parent(self.blinkCrvs[0], noXformGrp)
        cmds.parent([xformGrp, noXformGrp], topGrp)

        # if we're doing a blend shape setup
        if self.blend:
            for side in self.sides:
                cmds.parent(self.eyeRig[side]["crvList"][1], noXformGrp)
                cmds.parent(self.eyeRig[side]["ctrlsGrp"], ctrlGrp)
                cmds.parent(self.eyeRig[side]["fineCtrlGrp"], ctrlGrp)
                noxform = [self.eyeRig[side]["crvGrp"], self.eyeRig[side]["locGrp"], self.eyeRig[side]["bindJntGrp"], self.eyeRig[side]["ctrlJntGrps"]]
                cmds.parent(self.eyeRig[side]["proxyGrp"], xformGrp)
                cmds.parent(noxform, noXformGrp)
            cmds.parent(self.blinkCrvGrp, noXformGrp)

        # if we're doing a starndard joint rig
        if not self.blend:
            for side in self.sides:
                cmds.parent(self.eyeRig[side]["crvList"][1], noXformGrp)
                cmds.parent(self.eyeRig[side]["ctrlsGrp"], ctrlGrp)
                cmds.parent(self.eyeRig[side]["fineCtrlGrp"], ctrlGrp)
                xform = [self.eyeRig[side]["crvGrp"], self.eyeRig[side]["locGrp"], self.eyeRig[side]["bindJntGrp"], self.eyeRig[side]["ctrlJntGrps"], self.eyeRig[side]["proxyGrp"]]
                cmds.parent(xform, xformGrp)
            cmds.parent(self.blinkCrvGrp, xformGrp)

        cmds.xform(topGrp, ws=True, rp=self.centerPos)
        cmds.xform(topGrp, ws=True, sp=self.centerPos)
