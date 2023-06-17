import maya.cmds as cmds

import zTools3.rig.zbw_rigger_utils as zrt
import zTools3.rig.zbw_rigger_baseLimb as BL
import zTools3.rig.zbw_rig as rig
import zTools3.rig.zbw_rigger_window as zrw


class LegRigUI(zrw.RiggerWindow):
    def __init__(self):
        self.width = 300
        self.height = 600

        self.winInitName = "zbw_legRiggerUI"
        self.winTitle = "Leg Rigger UI"
        # common
        self.defaultLimbName = "leg"
        self.defaultOrigPrefix = "L"
        self.defaultMirPrefix = "R"
        self.pts = [(5, 12, 0), (5, 7, 1), (5, 2, 0), (5, 1, 3), (5, 1, 4)]
        self.baseNames = ["thigh", "knee", "ankle", "ball", "ballEnd"]
        self.secRotOrderJnts = []
        self.ikShape = "box"
        self.make_UI()

    def create_rigger(self, *args):
        self.rigger = LegRig()
        self.get_values_for_rigger()
        self.set_values_for_rigger()


class LegRig(BL.BaseLimb):
    def __init__(self):
        BL.BaseLimb.__init__(self)
        # can add this in tht ui? need to?
        self.revFootPts = [(5, 1, 3), (5, 0, 4), (5, 0, -2)]

        # Here we should turn these into joints and parent them into the ball joint
        self.revFootNames = ["{0}_ball".format(self.origPrefix), "{0}_toe".format(self.origPrefix), "{0}_heel".format(self.origPrefix)]
        self.revFootJnt = {"orig": [], "mir": []}
        self.footPivots = {}
        self.ikShape = "box"
        self.ikOrient = False
        self.reverseFootBallCtrls = {"orig": None, "mir": None}

    def pose_initial_joints(self):
        BL.BaseLimb.pose_initial_joints(self)
        # need to work on orienting the joints here. . . which attrs to lock (just unlock all?)
        cmds.setAttr("{0}.rx".format(self.octrls[1]), 180)
        for i in range(len(self.revFootNames)):
            cmds.select(cl=True)
            jnt = cmds.joint(name="{0}_pivot_JNT".format(self.revFootNames[i]))
            cmds.xform(jnt, ws=True, t=self.revFootPts[i])
            self.revFootJnt["orig"].append(jnt)
            cmds.parent(jnt, self.joints[3])

    def make_limb_rig(self):
        self.detach_reverse_joints()
        self.clean_initial_joints()
        # add manual adjust joint orientation here. . .
        if self.mirror:
            self.mirror_joints()
        self.setup_dictionaries()
        self.create_duplicate_chains()
        self.create_fk_rig()
        self.create_fkik_switch()
        self.connect_deform_joints()
        self.create_ik_rig()
        self.create_ik_stretch()
        self.create_rigSide_groups()
        if self.twist:
            self.create_twist_extraction_rig()
        self.create_ik_group()
        self.create_reverse_foot()
        self.clean_up_rig()
        self.create_sets()
        self.label_deform_joints()

    def create_ik_rig(self):
        BL.BaseLimb.create_ik_rig(self, leg=True)

    def detach_reverse_joints(self):
        for i in range(len(self.revFootJnt["orig"])):
            self.revFootJnt["orig"][i] = cmds.parent(self.revFootJnt["orig"][i], w=True)[0]

        # parent stuff, unparent in reverse foot after mirroring
        cmds.parent(self.revFootJnt["orig"][2], self.revFootJnt["orig"][1])
        cmds.parent(self.revFootJnt["orig"][1], self.revFootJnt["orig"][0])

    def create_reverse_foot(self):
        mirJnt = None
        if self.mirror:
            if self.mirrorAxis == "yz":
                mirJnt = cmds.mirrorJoint(self.revFootJnt["orig"][0], mirrorBehavior=True, mirrorYZ=True, searchReplace=[self.origPrefix, self.mirPrefix])
                for jnt in mirJnt:
                    self.revFootJnt["mir"].append(jnt)
            elif self.mirrorAxis == "xy":
                mirJnt = cmds.mirrorJoint(self.revFootJnt["orig"][0], mirrorBehavior=True, mirrorXY=True, searchReplace=[self.origPrefix, self.mirPrefix])
                for jnt in mirJnt:
                    self.revFootJnt["mir"].append(jnt)
            elif self.mirrorAxis == "xz":
                mirJnt = cmds.mirrorJoint(self.revFootJnt["orig"][0], mirrorBehavior=True, mirrorXZ=True, searchReplace=[self.origPrefix, self.mirPrefix])
                for jnt in mirJnt:
                    self.revFootJnt["mir"].append(jnt)

        for side in list(self.fkJoints.keys()):
            if side == "orig":
                sideName = self.origPrefix
            if side == "mir":
                sideName = self.mirPrefix
            self.footPivots[side] = []

            # add attrs to ankle ctrl
            cmds.addAttr(self.ikCtrls[side][0], ln="__RevFootAttrs__",
                         at="enum", en="-----", k=True)
            cmds.setAttr("{0}.__RevFootAttrs__".format(self.ikCtrls[side][0]),
                         l=True)
            rollAttrs = ["ballRoll", "toeRoll", "heelRoll"]
            twistAttrs = ["ballTwist", "toeTwist", "heelTwist"]
            for attr in rollAttrs:
                cmds.addAttr(self.ikCtrls[side][0], ln=attr, at="float", dv=0.0,
                             k=True)
            for attr in twistAttrs:
                cmds.addAttr(self.ikCtrls[side][0], ln=attr, at="float", dv=0.0,
                             k=True)
            cmds.addAttr(self.ikCtrls[side][0], ln="toeFlap", at="float",
                         dv=0.0, k=True)

            # create grp for each loc
            for jnt in self.revFootJnt[side]:
                grp = cmds.group(em=True, name="{0}_{1}_{2}".format(sideName, self.part, jnt.replace("JNT", "PIV")))
                rig.snap_to(jnt, grp)
                self.footPivots[side].append(grp)

            # parent all to world
            for piv in self.footPivots[side]:
                cmds.parent(piv, self.ikCtrls[side][0])
                cmds.setAttr(piv + ".r", 0, 0, 0)

            # parent ball to toe, toe to heel, heel to to ctrl
            cmds.parent(self.footPivots[side][0], self.footPivots[side][1])
            cmds.parent(self.footPivots[side][1], self.footPivots[side][2])
            # cmds.parent(self.footPivots[side][2], self.ikCtrls[side][0])

            # parent ik to ball grp
            cmds.parent(self.ikHandles[side][0], self.footPivots[side][0])
            # create new ik from ankle to ball, parent under
            ikName = "{0}_{1}_ballIK".format(sideName, self.part)
            ballHandle = cmds.ikHandle(startJoint=self.ikJoints[side][2], endEffector=self.ikJoints[side][3], name=ikName, solver="ikRPsolver")[0]
            self.ikHandles[side].append(ballHandle)
            cmds.parent(ballHandle, self.footPivots[side][0])
            cmds.setAttr("{0}.visibility".format(ballHandle), 0)
            # create ctrl at ball, grpFreeze, orient constrain ikBall to this
            ballCtrl, ballGrp = zrt.create_control_at_joint(self.ikJoints[side][3], "circle", "x", "{0}_ball_{1}".format(sideName, self.ctrlSuffix), self.groupSuffix, orient=True)
            cmds.setAttr("{0}.v".format(ballCtrl), 0)
            self.reverseFootBallCtrls[side] = ballCtrl
            cmds.parent(ballGrp, self.footPivots[side][1])
            cmds.orientConstraint(ballCtrl, self.ikJoints[side][3])

            # connect attrs
            for i in range(len(rollAttrs)):
                cmds.connectAttr("{0}.{1}".format(self.ikCtrls[side][0], rollAttrs[i]), "{0}.rx".format(self.footPivots[side][i]))
                cmds.connectAttr("{0}.{1}".format(self.ikCtrls[side][0], twistAttrs[i]), "{0}.ry".format(self.footPivots[side][i]))
            cmds.connectAttr("{0}.toeFlap".format(self.ikCtrls[side][0]), "{0}.rz".format(self.reverseFootBallCtrls[side]))
            # delete pv locs
            cmds.delete(self.revFootJnt[side])

            # connect pv to foot, follow attr etc

    def create_twist_extraction_rig(self):
        for side in list(self.deformJoints.keys()):
            if side == "orig":
                sideName = self.origPrefix
            if side == "mir":
                sideName = self.mirPrefix

            upTwistAttr = zrt.create_twist_extractor(rotJnt=self.deformJoints[side][0], tgtCtrl=self.switchCtrls[side], parObj=self.sideGroups[side][0], tgtAttr="upperTwist")

            twistJointsUp, twistHooksUp = zrt.create_twist_joints(self.twistNum, self.deformJoints[side][0], self.deformJoints[side][0], self.deformJoints[side][1], upTwistAttr, "{0}_{1}_up".format(sideName, self.part), self.primaryAxis, grpSuffix=self.groupSuffix, jntSuffix=self.jntSuffix, reverse=True)
            for jnt in twistJointsUp:
                self.twistJoints[side].append(jnt)

            loTwistAttr = zrt.create_twist_extractor(rotJnt=self.deformJoints[side][2], tgtCtrl=self.switchCtrls[side], parObj=self.deformJoints[side][1], tgtAttr="lowerTwist", axis="y")

            twistJointsLo, twistHooksLo = zrt.create_twist_joints(self.twistNum, self.deformJoints[side][2], self.deformJoints[side][1], self.deformJoints[side][2], loTwistAttr, "{0}_{1}_low".format(sideName, self.part), self.primaryAxis, grpSuffix=self.groupSuffix, jntSuffix=self.jntSuffix, reverse=False)
            for jnt in twistJointsLo:
                self.twistJoints[side].append(jnt)

        # add locator at actual elbow that is parent of other two?

    def clean_up_rig(self):
        BL.BaseLimb.clean_up_rig(self)
        for side in list(self.fkJoints.keys()):
            cmds.setAttr("{0}.fkik".format(self.switchCtrls[side]), 1)
