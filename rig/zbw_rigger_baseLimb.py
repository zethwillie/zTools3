import maya.cmds as cmds

import zTools.rig.zbw_rigger_utils as zrt
import importlib

importlib.reload(zrt)
import zTools.rig.zbw_rig as rig
importlib.reload(rig)
import maya.OpenMaya as om
import zTools.rig.zbw_rigger_window as zrw
importlib.reload(zrw)

#----------------# for sides create a list w "orig", if mirror add "mir", replace all self.fkJoints.keys(), etc. . 
#---------------- also create self.sideName with orig and mir prefixes. . . ?
#---------------- add meta data setup. . . network nodes with message multi attrs


class BaseLimbUI(zrw.RiggerWindow):
    def __init__(self):
        self.width = 300
        self.height = 600

        self.winInitName = "zbw_limbUI"
        self.winTitle="Base Limb UI"
        # common
        self.defaultLimbName = "limb"
        self.defaultOrigPrefix = "L"
        self.defaultMirPrefix = "R"
        self.pts = [(5,20, 0),(15, 20, -1), (25, 20, 0), (27, 20, 0)]
        self.baseNames = ["limb1", "limb2", "limb3", "limb4"]
        self.secRotOrderJnts = [2]
        self.ikShape = "arrowCross"
        self.ikOrient = True
        self.make_UI()

    def create_rigger(self, *args):
        self.rigger = BaseLimb()
        self.get_values_for_rigger()
        self.set_values_for_rigger()


class BaseLimb(object):

    def __init__(self, fromUI=True):
        self.origFkJnts = []
        self.mirrorFkJnts = []
        
        # turn on decompose matrix plugin

        # these are the default values of the limb
        self.pts = [(5,20, 0),(15, 20, -1), (25, 20, 0), (27, 20, 0)] # list of pt positions for initial jnts
        self.part = "arm" # ie. "arm"
        self.baseNames = ["shoulder", "elbow", "wrist", "wristEnd"] # list of names of joints (i.e ["shoulder", "elbow", etc]). xtra for orienting!
        self.jntSuffix = "JNT"      # what is the suffix for jnts
        self.ctrlSuffix = "CTRL"
        self.groupSuffix = "GRP"
        self.origPrefix = "lf"      # ie. "lf"
        self.mirror = True          # do we mirror?
        if self.mirror:
            self.mirPrefix = "rt"   # ie. "rt"
        self.mirrorAxis = "yz"      # what is axis for joint mirroing (ie. "yz")
        self.primaryAxis = "x"      # down the joint axis
        self.upAxis = "y"           # up axis for joints orient
        self.tertiaryAxis = "z"     # third axis
        # below needs to be created from main axis, up axis etc (ie. "x")
        self.orientOrder = "xyz"    # orient order for joint orient (ie. "xyz" or "zyx")
        self.upOrientAxis = "yup"   # joint orient up axis (ie. "yup" or "zup")
        self.createIK = True
        self.twist = True           # do we create twist joints?
        self.twistNum = 2           # how many (doesn't include top/bottom)?
        self.secRotOrder = "zyx"  # the 'other' rotation order (ie. for wrists, etc)
        self.secRotOrderJnts = [2]   # which joints get the secRotOrder. This is a list of the indices
        self.ikShape = "arrowCross"  # shape for createControl of ikCtrl
        self.ikOrient = True            # should we orient the ikctrl to the jnt?

# deal with joint labeling (cmds.setAttr("joint.side", 1)), left =1, right=2, center=0, None=3

        # initialize variables
        self.side = {}
        self.fkJoints = {}
        self.fkCtrls = {}
        self.fkCtrlGrps = {}
        self.ikJoints = {}
        self.ikCtrls = {}
        self.ikCtrlGrps = {}
        self.ikHandles = {}
        self.measureJoints = {}
        self.deformJoints = {}
        self.switchCtrls = {}
        self.twistJoints = {}
        self.sideGroups = {}


    def pose_initial_joints(self):
    # get and pass values for orient order and uporient axis
    # put joint in ref display layer temporarily
        self.joints, self.poseCtrls, self.poseGrps, self.octrls, self.ogrps, self.poseConstraints = zrt.initial_pose_joints(ptsList=self.pts, baseNames=self.baseNames, orientOrder=self.orientOrder, upOrientAxis=self.upOrientAxis, primaryAxis=self.primaryAxis, upAxis=self.upAxis)

        # put tmp joints in a display layer and set to reference
        cmds.select(self.joints, r=True)
        self.dl = cmds.createDisplayLayer(name="tmp_{0}_jnt_DL".format(self.part))
        cmds.setAttr("{0}.displayType".format(self.dl), 2)


    def make_limb_rig(self):
        """
        instructions to make the limb
        """
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
        self.clean_up_rig()
        self.create_sets()
        self.label_deform_joints()


    def clean_initial_joints(self):
        cmds.delete(self.dl)

        self.origFkJnts = zrt.clean_pose_joints(self.joints, self.poseConstraints, self.octrls, self.poseGrps[0], self.origPrefix, self.jntSuffix, deleteEnd=True)

        # set rotate orders on listed jnts
        for i in self.secRotOrderJnts:
            cmds.joint(self.origFkJnts[i], edit=True, rotationOrder=self.secRotOrder)
        
        # store orient data on joints for serialization. . . ?

    def mirror_joints(self):
        self.mirrorFkJnts = zrt.mirror_joint_chain(self.origFkJnts[0], self.origPrefix, self.mirPrefix, self.mirrorAxis)


    def setup_dictionaries(self):
        """initialize dictionaries for the actual rig content"""
        self.side["orig"] = self.origPrefix
        self.fkJoints["orig"] = self.origFkJnts
        self.fkCtrls["orig"] = None
        self.fkCtrlGrps["orig"] = None
        self.switchCtrls["orig"] = None
        self.ikCtrls["orig"] = None
        self.ikCtrlGrps["orig"] = None
        self.sideGroups["orig"] = None
        self.twistJoints["orig"] = []
        self.ikHandles["orig"] = []
        if self.mirror:
            self.side["mir"] = self.mirPrefix
            self.fkJoints["mir"] = self.mirrorFkJnts
            self.fkCtrls["mir"] = None # []
            self.fkCtrlGrps["mir"] = None
            self.switchCtrls["mir"] = None # []
            self.ikCtrls["mir"] = None # [ikCtrl, pvCtrl, pvLine]
            self.ikCtrlGrps["mir"] = None  # [ikCtrlGrp, pvCtrlGrp, pvLineGrp]
            self.sideGroups["mir"] = None   # [lf_arm_GRP, lf_arm_attach_GRP]
            self.twistJoints["mir"] = []   # [lf_arm_upTwist1_JNT, etc]
            self.ikHandles["mir"] = []      #[lf_leg_ikHandle, lf_ball_ikHandle]


    def create_duplicate_chains(self):
        # for key in jntDict, make duplicates. . . (put into dictionary)
        for side in list(self.fkJoints.keys()):
            topJnt = self.fkJoints[side][0] 
          
            # make deform jnts
            deforms = zrt.duplicate_and_rename_chain(topJnt, "deform")
            self.deformJoints[side] = deforms
            
            # if we're making IK stuff
            if self.createIK:
                # make IK
                iks = zrt.duplicate_and_rename_chain(topJnt, "IK")
                self.ikJoints[side] = iks
                # make measure
                measures = zrt.duplicate_and_rename_chain(topJnt, "measure")
                self.measureJoints[side] = measures


    def create_fk_rig(self):
        for side in list(self.fkJoints.keys()):
            fkJoints = self.fkJoints[side]
            ctrls = []
            grps = []
            for jnt in fkJoints:
                ctrl, grp = zrt.create_control_at_joint(jnt, "cube", self.primaryAxis, "{0}_FK_{1}_{2}".format(self.side[side], jnt.split("_")[1], self.ctrlSuffix), self.groupSuffix)
                ctrls.append(ctrl)
                grps.append(grp)
            zrt.parent_hierarchy_grouped_controls(ctrls, grps)

            self.fkCtrls[side] = ctrls
            self.fkCtrlGrps[side] = grps

        # should we keep track of these constraints?
            for i in range(len(fkJoints)):
                pc = cmds.parentConstraint(ctrls[i], fkJoints[i])
                sc = cmds.scaleConstraint(ctrls[i], fkJoints[i])
        
        # add gimble ctrls? just a group and control above each ctrl 
        # create group for arm to go in


    def create_fkik_switch(self):
        for side in list(self.deformJoints.keys()):
            # this defaults to the third joint in chain
            ctrl = rig.create_control(name="{0}_{1}_IkFkSwitch_{2}".format(self.side[side], self.part, self.ctrlSuffix), type="star", axis=self.primaryAxis)
            grp = rig.group_freeze(ctrl, self.groupSuffix)
        #get scale factor
            root = cmds.xform(self.deformJoints[side][0], q=True, ws=True, rp=True)
            mid = cmds.xform(self.deformJoints[side][1], q=True, ws=True, rp=True)
            end = cmds.xform(self.deformJoints[side][2], q=True, ws=True, rp=True)
            distVec = om.MVector(mid[0]-end[0], mid[1]-end[1], mid[2]-end[2])
            dist = distVec.length()
            mv = zrt.get_planar_position(root, mid, end, percent=0.05, dist=dist)
            rig.snap_to(self.deformJoints[side][2], grp)
            cmds.xform(grp, ws=True, t=(mv.x, mv.y, mv.z))
            
            rig.strip_transforms(ctrl)
            cmds.addAttr(ctrl, ln="fkik", at="float", min=0.0, max=1.0, defaultValue=0, keyable=True)

        # save this constraint?
            pc = cmds.parentConstraint(self.deformJoints[side][2], grp, mo=True)

            self.switchCtrls[side] = ctrl


    def create_ik_rig(self, leg=False):
        for side in list(self.ikJoints.keys()):
            jnts = self.ikJoints[side]
            if side == "orig":
                name = "{0}_{1}_IK".format(self.origPrefix, self.part)
            elif side == "mir":
                name = "{0}_{1}_IK".format(self.mirPrefix, self.part)

            handle = cmds.ikHandle(startJoint=jnts[0], endEffector=jnts[2], name=name, solver="ikRPsolver")[0]
            cmds.setAttr("{0}.visibility".format(handle), 0)
            ctrl, grp = zrt.create_control_at_joint(jnts[2], self.ikShape, self.primaryAxis, "{0}_{1}".format(name, self.ctrlSuffix), grpSuffix=self.groupSuffix, orient=self.ikOrient)
            # add option for aiming this only at the 'ball' jnt in y for leg
            if leg:
                ac = cmds.aimConstraint(self.deformJoints[side][3], grp, aim=[0, 0, 1], upVector=[0, 1, 0], skip=["x", "z"])
                cmds.delete(ac)
                
            cmds.parent(handle, ctrl)
            oc = cmds.orientConstraint(ctrl, jnts[2], mo=True)
            self.ikCtrls[side] = [ctrl]
            self.ikCtrlGrps[side] = [grp]
            self.ikHandles[side].append(handle)

            # create pole vec
            if side == "orig":
                pvname = "{0}_{1}_poleVector_{2}".format(self.origPrefix, self.part, self.ctrlSuffix)
            elif side == "mir":
                pvname = "{0}_{1}_poleVector_{2}".format(self.mirPrefix, self.part, self.ctrlSuffix)
            pv = rig.create_control(name=pvname, type="sphere", color="red", axis="x")
            self.ikCtrls[side].append(pv)
            pvgrp = rig.group_freeze(pv, suffix=self.groupSuffix)
            self.ikCtrlGrps[side].append(pvgrp)

            # place and constrain pole vec
            cmds.select(handle, r=True)
            pos = zrt.find_pole_vector_location(handle)
            cmds.xform(pvgrp, ws=True, t=(pos[0], pos[1], pos[2]))
            cmds.poleVectorConstraint(pv, handle)

            # add crv lines from shoulder to pv
            if side == "orig":
                pvline = "{0}_{1}_poleVec_Line".format(self.origPrefix, self.part)
            elif side == "mir":
                pvline = "{0}_{1}_poleVec_Line".format(self.mirPrefix, self.part)        
            pvLine = zrt.create_line_between(pv, jnts[1], pvline)
            pvGrp = cmds.group(em=True, name="{0}_{1}".format(pvLine, self.groupSuffix))
            cmds.parent(pvLine, pvGrp)
            self.ikCtrls[side].append(pvLine)
            self.ikCtrlGrps[side].append(pvGrp)
            # set line as reference override
            shp = cmds.listRelatives(pvLine, s=True)[0]
            cmds.setAttr("{0}.overrideEnabled".format(shp), 1)
            cmds.setAttr("{0}.overrideDisplayType".format(shp), 2)
            #connect to switch
            cmds.addAttr(self.switchCtrls[side], ln="poleVecLineVis", at="short", min=0, max=1, dv=1, k=True)
            cmds.connectAttr("{0}.poleVecLineVis".format(self.switchCtrls[side]), "{0}.overrideVisibility".format(shp))
        # option for no flip pv?

    def connect_deform_joints(self):
        # zip up fk, ik and deform joints for easier stuff
        for side in list(self.fkJoints.keys()):
            joints = list(zip(self.fkJoints[side], self.ikJoints[side], self.deformJoints[side]))
            # should we parent constraint these? 
            for grp in joints:
                zrt.create_parent_reverse_network(grp[:-1], grp[-1], "{0}.fkik".format(self.switchCtrls[side]), index=0)

    # a way to do gimbles in both ik and fk? create gimbel ctrl under grp. grp is parent constrained to ik/fk ctrls (like deform joint). ctrl then is what parent constrains to the deform joints


    def create_ik_stretch(self):
        # LET"S DO THIS SCALE-WISE FOR NOW
        for side in list(self.ikJoints.keys()):
            if side == "orig":
                sideName = self.origPrefix
            if side == "mir":
                sideName = self.mirPrefix

            self.upMult, self.loMult = zrt.create_stretch_setup(self.measureJoints[side][:3], self.ikCtrls[side][0], "{0}_{1}".format(sideName, self.part))

            cmds.addAttr(self.switchCtrls[side], ln="upperLength", at="float", k=False)
            cmds.addAttr(self.switchCtrls[side], ln="lowerLength", at="float", k=False)

            cmds.connectAttr("{0}_{1}_measure0_DB.distance".format(sideName, self.part), "{0}.upperLength".format(self.switchCtrls[side]))
            cmds.connectAttr("{0}_{1}_measure1_DB.distance".format(sideName, self.part), "{0}.lowerLength".format(self.switchCtrls[side]))
            cmds.setAttr("{0}.upperLength".format(self.switchCtrls[side]), l=True)
            cmds.setAttr("{0}.lowerLength".format(self.switchCtrls[side]), l=True)

            cmds.connectAttr("{0}.output.outputX".format(self.upMult), "{0}.sx".format(self.ikJoints[side][0]))
            cmds.connectAttr("{0}.output.outputX".format(self.loMult), "{0}.sx".format(self.ikJoints[side][1]))


    def create_rigSide_groups(self):
        for side in list(self.fkJoints.keys()):
            if side == "orig":
                sideName = self.origPrefix
            if side == "mir":
                sideName = self.mirPrefix
            sideGrp = cmds.group(em=True, name="{0}_{1}_{2}".format(sideName, self.part, self.groupSuffix))
            pos = cmds.xform(self.fkJoints[side][0], q=True, ws=True, rp=True)
            rot = cmds.xform(self.fkJoints[side][0], q=True, ws=True, ro=True)
            cmds.xform(sideGrp, ws=True, t=pos)
            cmds.xform(sideGrp, ws=True, ro=rot)

            attachGrp = cmds.duplicate(sideGrp, name="{0}_{1}_attach_{2}".format(sideName, self.part, self.groupSuffix))[0]

            cmds.parent(sideGrp, attachGrp)
            sideList =[self.fkJoints[side][0], self.ikJoints[side][0], self.measureJoints[side][0], self.deformJoints[side][0], self.fkCtrlGrps[side][0]]

            cmds.parent(sideList, sideGrp)

            self.sideGroups[side] = [sideGrp, attachGrp]


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

            loTwistAttr = zrt.create_twist_extractor(rotJnt=self.deformJoints[side][2], tgtCtrl=self.switchCtrls[side], parObj=self.deformJoints[side][1], tgtAttr="lowerTwist")

            twistJointsLo, twistHooksLo = zrt.create_twist_joints(self.twistNum, self.deformJoints[side][2], self.deformJoints[side][1], self.deformJoints[side][2], loTwistAttr, "{0}_{1}_low".format(sideName, self.part), self.primaryAxis, grpSuffix=self.groupSuffix, jntSuffix=self.jntSuffix, reverse=False)
            for jnt in twistJointsLo:
                self.twistJoints[side].append(jnt)

        # add locator at actual elbow that is parent of other two?


    def create_ik_group(self):
        ikName = "ik_world_rig_GRP"
        if not cmds.objExists(ikName):
            ikGrp = cmds.group(em=True, name=ikName)
        else:
            ikGrp = ikName

        for side in list(self.fkJoints.keys()):
            if side == "orig":
                sideName = self.origPrefix
            if side == "mir":
                sideName = self.mirPrefix

            ikStuff = [self.ikCtrlGrps[side], cmds.listRelatives(self.switchCtrls[side], p=True)[0]]

            for stuff in ikStuff:
                cmds.parent(stuff, ikGrp)


    def clean_up_rig(self):
    # clean up rig (hide jnts, connect vis, etc)
        # hide jnts
        for side in list(self.fkJoints.keys()):
            if side == "orig":
                sideName = self.origPrefix
            if side == "mir":
                sideName = self.mirPrefix

            hideJnts = [self.ikJoints[side][0], self.fkJoints[side][0], self.measureJoints[side][0]]
            for obj in hideJnts:
                cmds.setAttr("{0}.v".format(obj), 0)
        # no inherit stuff? 
            if not cmds.objExists("rig_noInherit_GRP".format(self.groupSuffix)):
                noInher = cmds.group(em=True, name="rig_noInherit_GRP")
                cmds.setAttr("{0}.inheritsTransform".format(noInher), 0)
            noInher = "rig_noInherit_GRP"
            cmds.parent(self.ikCtrlGrps[side][2], noInher)
        
        # color controls
            #how to do this? color attr from UI? 
            if side == "orig":
                color = "blue"
                secColor = "lightBlue"
            if side == "mir":
                color = "red"
                secColor = "pink"

            primColor = [self.fkCtrls[side], [self.ikCtrls[side][0]]]
            lightColor = [self.ikCtrls[side][1:], [self.switchCtrls[side]]]

            for obj in primColor:
                for ctrl in obj: 
                    rig.assign_color(obj=ctrl, clr=color)
            for obj in lightColor:
                for ctrl in obj:
                    rig.assign_color(obj=ctrl, clr=secColor)

        # set up visibility switching
            ikStuff = [self.ikCtrlGrps[side][0], self.ikCtrlGrps[side][1], self.ikCtrlGrps[side][2]]
            fkStuff = [self.fkCtrlGrps[side][0]]

            self.switchReverse = cmds.shadingNode("reverse", asUtility=True, name="{0}_{1}_ikfkVis_reverse".format(sideName, self.part))
            cmds.connectAttr("{0}.fkik".format(self.switchCtrls[side]), "{0}.input.inputX".format(self.switchReverse))
            for obj in fkStuff:
                cmds.connectAttr("{0}.output.outputX".format(self.switchReverse), "{0}.v".format(obj))
            for obj in ikStuff:
                cmds.connectAttr("{0}.fkik".format(self.switchCtrls[side]), "{0}.v".format(obj))

            # connect rotate orders
            for i in range(len(self.fkJoints[side])):
                roattr = zrt.create_rotate_order_attr(self.switchCtrls[side], "{0}RotateOrder".format(self.baseNames[i]))
                
                objList = [self.fkJoints[side][i], self.ikJoints[side][i], self.deformJoints[side][i], self.fkCtrls[side][i], self.fkCtrlGrps[side][i], self.ikCtrls[side][0], self.ikCtrlGrps[side][0]]

                for obj in objList:
                    cmds.connectAttr(roattr, "{0}.rotateOrder".format(obj), f=True)

                axes = ["x", "y", "z"]
                axes.remove(self.primaryAxis)
                axes.remove(self.upAxis)
                origRotOrder = "{0}{1}{2}".format(self.primaryAxis, self.upAxis, axes[0])

                roList = ["xyz", "yzx", "zxy", "xzy", "yxz", "zyx"]

                if i in self.secRotOrderJnts:
                    roindex = roList.index(self.secRotOrder)
                    cmds.setAttr(roattr, roindex)
                else:
                    roindex = roList.index(origRotOrder)
                    cmds.setAttr(roattr, roindex)



    def label_deform_joints(self):
        for side in list(self.fkJoints.keys()):
            jointType = 18
            if side == "orig":
                sideNum = 1
            if side == "mir":
                sideNum = 2

            for jnt in self.deformJoints[side]:
                joint = jnt.split("_")[1]
                cmds.setAttr("{0}.side".format(jnt), sideNum)
                cmds.setAttr("{0}.type".format(jnt), jointType)
                cmds.setAttr("{0}.otherType".format(jnt), joint, type="string")

            for jnt in self.twistJoints[side]:
                joint = "_".join(jnt.split("_")[2:4])
                cmds.setAttr("{0}.side".format(jnt), sideNum)
                cmds.setAttr("{0}.type".format(jnt), jointType)
                cmds.setAttr("{0}.otherType".format(jnt), joint, type="string")


    def create_sets(self):
        # set for all controls
        ctrlSet = "CTRL_SET"
        bindSet = "BIND_SET"
        if not cmds.objExists(ctrlSet):
            cmds.sets(name="CTRL_SET", em=True)
        if not cmds.objExists(bindSet):
            cmds.sets(name="BIND_SET", em=True)

        for side in list(self.fkJoints.keys()):
            if side == "orig":
                sideName = self.origPrefix
            if side == "mir":
                sideName = self.mirPrefix

            ctrls = [self.fkCtrls[side], self.ikCtrls[side][:2], self.switchCtrls[side]]
            for ctrlList in ctrls:
                cmds.sets(ctrlList, addElement="CTRL_SET")
            # bind joints set
    # if ribbon or ikSpline is added, remove these joints and add those
    # if NOT twist joints add all deform joints
            jnts = [self.deformJoints[side][2:], self.twistJoints[side]]
            for jntList in jnts:
                cmds.sets(jntList, addElement="BIND_SET")

    # add in game export rig
    # add option for game exportable joints QSS 
    # option for ribbon setup in here? 