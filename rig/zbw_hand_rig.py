import maya.cmds as cmds
import json
import os
from functools import partial
import zTools3.rig.zbw_rig as rig
import importlib
import zTools3.zbw_tools as tools


# clean this up to be more elegant

# come up with a more elegant way to deal with joint/ctrl stuff. Maybe expand out to rig class stuff? Or bring that into here?
# add joint orient to window? for control creation
# add ik to fingers?


'''
# to serialize info
joint_dictionary = {}

savePath = r"path/to/file.txt"

sel = cmds.ls(sl=True)

for jnt in sel:
    name = jnt
    par = cmds.listRelatives(jnt, parent=True)
    if par:
        par = par[0]
    trans = cmds.xform(jnt, q=True, ws=True, t=True)
    rot = cmds.xform(jnt, q=True, ws=True, ro=True)
    scl = cmds.xform(jnt, q=True, ws=True, s=True)
    jo = cmds.joint(jnt, q=True, orientation=True)
    side = cmds.getAttr("{0}.side".format(jnt))
    part = cmds.getAttr("{0}.type".format(jnt))
    joint_dictionary[name] = {"parent":par, "translate":trans, "rotation":rot, "scale":scl, "orientation":jo, "side":side, "part":part}

with open(savePath, 'w') as outfile:
    json.dump(joint_dictionary, outfile)
'''


class HandRig(object):
    def __init__(self):
        self.joint_dictionary = {}
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open("{0}/handData.json".format(dir_path)) as json_file:
            data = json.load(json_file)
            self.joint_dictionary = data

        self.pose_dictionary = {}
        with open("{0}/handPoseData.json".format(dir_path)) as json_file:
            pdata = json.load(json_file)
            self.pose_dictionary = pdata

        self.colors = ["lightBlue", "pink", "darkBlue", "darkRed"]
        self.allJoints = []
        self.proxyList = []
        self.proxyJnts = []

        self.hand_rig_UI()

    def hand_rig_UI(self):
        if cmds.window("handWin", exists=True):
            cmds.deleteUI("handWin")

        self.win = cmds.window("handWin", t="zbw_hand_rig", w=280, s=True)
        cmds.columnLayout()
        self.mirror = cmds.checkBoxGrp(l="Mirror: ", ncb=1, v1=True, cal=[(1, "left"), (2, "left")], cw=[(1, 50), (2, 20)])
        cmds.text("1. Create joints, position/orient them, then create rig")
        cmds.button(l="Import Joints", w=280, h=50, bgc=(.7, .5, .5), c=self.joint_setup)
        cmds.separator(h=10)
        cmds.button(l="Rig Joints", w=280, h=50, bgc=(.5, .7, .5), c=self.build_rig)

        cmds.showWindow(self.win)
        cmds.window(self.win, e=True, rtf=True)

    def joint_setup(self, *args):
        for jnt in list(self.joint_dictionary.keys()):
            cmds.select(cl=True)
            cmds.joint(name=jnt, position=self.joint_dictionary[jnt]["translate"], a=True)

        for jnt in list(self.joint_dictionary.keys()):
            cmds.xform(jnt, ws=True, ro=self.joint_dictionary[jnt]["rotation"])

        for jnt in list(self.joint_dictionary.keys()):
            cmds.select(cl=True)
            try:
                cmds.parent(jnt, self.joint_dictionary[jnt]["parent"])
            except:
                pass

        for jnt in list(self.joint_dictionary.keys()):
            if jnt == "hand_JNT":
                continue
            jo = self.joint_dictionary[jnt]["orientation"]
            cmds.setAttr("{0}.jointOrient".format(jnt), jo[0], jo[1], jo[2])

        for jnt in list(self.joint_dictionary.keys()):
            cmds.makeIdentity(jnt)

    def build_rig(self, *args):

        self.mirrored = cmds.checkBoxGrp(self.mirror, q=True, v1=True)

        if self.mirrored:
            self.sides = ["lf", "rt"]
        else:
            self.sides = ["lf"]
        self.sideJnts = []

        # figure out which joints we have kept
        culledJnts = []
        for jnt in list(self.joint_dictionary.keys()):
            if cmds.objExists(jnt):
                culledJnts.append(jnt)

        self.leftJoints = [cmds.rename(x, "lf_{0}".format(x)) for x in culledJnts]
        self.sideJnts.append(self.leftJoints)
        self.add_to_bind_set(self.leftJoints)
        if self.mirrored:
            self.rightJoints = cmds.mirrorJoint("lf_hand_JNT", mirrorBehavior=True, mirrorYZ=True, searchReplace=["lf", "rt"])
            self.sideJnts.append(self.rightJoints)
            self.add_to_bind_set(self.leftJoints)

        self.create_ctrls()

    def create_ctrls(self, *args):
        self.bindJoints = []
        self.ctrlSides = []
        # build rig for self.sides
        for x in range(len(self.sides)):
            sideList = []
            self.ctrlSides.append(sideList)
            sideJntsComplete = []
            sideCtrl = rig.create_control("ctrl", "lollipop", "y", self.colors[x])
            if x == 1:
                self.reverse_control(sideCtrl)
            rig.scale_nurbs_control(sideCtrl, .2, .2, .2)

            # get rid of end joints
            for z in range(len(self.sideJnts[x])):
                if "End" not in self.sideJnts[x][z]:
                    sideJntsComplete.append(self.sideJnts[x][z])

            # connect jnts and ctrls
            cmds.select(sideCtrl, r=True)
            cmds.select(sideJntsComplete, add=True)
            ctrls, grps = tools.freeze_and_connect()

            # rename ctrls to get rid of "JNT"
            cmds.select("{0}_hand_JNTCtrl_GRP".format(self.sides[x]), r=True)
            cmds.select(hi=True)
            ctrlList = []
            sel = cmds.ls(sl=True)
            sel.reverse()
            list(set(sel))
            for y in sel:
                newCtrlObj = cmds.rename(y, y.replace("JNT", ""))
                self.ctrlSides[x].append(newCtrlObj)
            # add to set
            self.add_to_ctrl_set(self.ctrlSides[x])

        self.hand_control_setup()

    def hand_control_setup(self, *args):
        for x in range(len(self.sides)):
            # hide hand ctrl
            topShp = cmds.listRelatives("{0}_hand_Ctrl".format(self.sides[x]), s=True)[0]
            cmds.setAttr("{0}.v".format(topShp), 0)

            sideAutoGrpList = []
            sideManGrpList = []
            # create offset grps on ctrls
            for ctrl in self.ctrlSides[x]:
                shp = cmds.listRelatives(ctrl, s=True)
                if shp:
                    if cmds.objectType(shp) == "nurbsCurve":
                        autoGrp = rig.group_freeze(ctrl, "auto")
                        manualGrp = rig.group_freeze(ctrl, "manual")
                        sideAutoGrpList.append(autoGrp)
                        sideManGrpList.append(manualGrp)

            # create top groups for the left controls
            ctrlGrp = cmds.group("{0}_hand_Ctrl_GRP".format(self.sides[x]), name="{0}_hand_GRP".format(self.sides[x]))
            handPos = cmds.xform("{0}_hand_Ctrl_GRP".format(self.sides[x]), q=True, ws=True, rp=True)
            cmds.xform(ctrlGrp, ws=True, preserve=True, rp=handPos)
            attachGrp = cmds.group(ctrlGrp, name="{0}_hand_attach_GRP".format(self.sides[x]))
            cmds.xform(attachGrp, ws=True, preserve=True, rp=handPos)

            # create auto ctrls
            autoCtrl = rig.create_control("{0}_hand_auto_CTRL".format(self.sides[x]), "circle", "y", self.colors[x + 2])
            autoGrp = rig.group_freeze(autoCtrl)
            rig.snap_to("{0}_hand_Ctrl_GRP".format(self.sides[x]), autoGrp)
            cmds.parent(autoGrp, "{0}_hand_Ctrl".format(self.sides[x]))
            cmds.xform(autoGrp, ws=True, r=True, t=(0, 1, 0))
            rig.strip_transforms(autoCtrl)
            for attr in ["relax", "fist", "spread", "claw", "point"]:
                cmds.addAttr(autoCtrl, ln=attr, at="float", min=0, max=10, dv=0, k=True)

            # create attributes on the ctrl for finger ctrl
            self.create_finger_attrs(autoCtrl)

            self.hookup_auto(autoCtrl, sideAutoGrpList)
            self.hookup_manual(autoCtrl, sideManGrpList)

    def create_finger_attrs(self, ctrl):
        finger = [["index1", "index2", "index3", "index4"], ["middle1", "middle2", "middle3", "middle4"], ["ring1", "ring2", "ring3", "ring4"], ["pinky1", "pinky2", "pinky3", "pinky4"], ["thumb1", "thumb2", "thumb3"]]
        attrDir = ["curl", "spread", "rotate"]

        for adir in attrDir:
            for fing in finger:
                for knuck in fing:
                    attr = cmds.addAttr(ctrl, ln="{0}_{1}".format(knuck, adir), at="float", k=True)

    def add_to_bind_set(self, jlist):
        name = "BIND_SET"
        if not cmds.objExists(name):
            cmds.sets(name=name)
        cmds.sets(jlist, include=name)

    def add_to_ctrl_set(self, clist):
        name = "CTRL_SET"
        if not cmds.objExists(name):
            cmds.sets(name=name)
        cmds.sets(clist, include=name)
        cmds.select(name)
        sel = cmds.ls(sl=True)
        for x in sel:
            if not rig.type_check(x, "nurbsCurve"):
                cmds.sets(x, remove=name)
            if not rig.type_check(x, "transform"):
                cmds.sets(x, remove=name)

    def reverse_control(self, ctrl=None):
        cmds.setAttr("{0}.rz".format(ctrl), 180)
        cmds.makeIdentity(ctrl, apply=True)

    def hookup_auto(self, dctrl, grpList, *args):
        # setup a set driven key for each of fist, spread, claw, point to each elem in the group
        side = dctrl.partition("_")[0]
        pd = self.pose_dictionary

        grps = []
        ctrls = list(pd["fist"].keys())
        for ctrl in ctrls:
            if side == "rt":
                ctrl = ctrl.replace("lf_", "rt_")
            g = ctrl + "_auto"
            grps.append(g)

        for y in ["fist", "spread", "point", "relax", "claw"]:
            for d in grps:
                self.set_driven_key(dctrl + "." + y, d, 0, 0, 0)
            cmds.setAttr("{0}.{1}".format(dctrl, y), 10)
            for x in range(len(grps)):
                self.set_driven_key(dctrl + "." + y, grps[x], pd[y][ctrls[x]][0], pd[y][ctrls[x]][1], pd[y][ctrls[x]][2])
            cmds.setAttr("{0}.{1}".format(dctrl, y), 0)

    def set_driven_key(self, driver, driven, x, y, z):
        cmds.setDrivenKeyframe(driven + ".rx", cd=driver, value=x)
        cmds.setDrivenKeyframe(driven + ".ry", cd=driver, value=y)
        cmds.setDrivenKeyframe(driven + ".rz", cd=driver, value=z)

    def hookup_manual(self, ctrl, grpList, *args):
        # direct connections to group rotations
        finger = [["index1", "index2", "index3", "index4"], ["middle1", "middle2", "middle3", "middle4"], ["ring1", "ring2", "ring3", "ring4"], ["pinky1", "pinky2", "pinky3", "pinky4"], ["thumb1", "thumb2", "thumb3"]]
        attrDir = ["curl", "spread", "rotate"]

        side = ctrl.partition("_")[0]
        ax = ""

        for adir in attrDir:
            for fing in finger:
                for knuck in fing:
                    if adir == "curl":
                        ax = "z"
                    elif adir == "spread":
                        ax = "y"
                    elif adir == "rotate":
                        ax = "x"
                    cmds.connectAttr("{0}.{1}_{2}".format(ctrl, knuck, adir), "{0}_{1}_Ctrl_manual.r{2}".format(side, knuck, ax))
