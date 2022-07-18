"""
poseReader
to use: in python pane, type:
"import zbw_poseReader as zpr
 pr = zpr.PoseReader()"

Follow object is the thing you want to read the pose of
Parent object is a parent of the follow object that is stationary relative to the follow obj when only the follow object moves
This will create a sphere (in a group) that is constrained to the parent at the location of the follow obj.
Also creates a locator constrained to the follow obj. 
This reads the U and V parameters of the loc relative to the sphere, then normalizes that relative to the midpoint of the UV's (2, 2). It does this for forward, backwards, up and down
The normalized value is what you would plug into the blend shapes (or whatever else you want)
If you've created ramps (the checkbox), you can adjust the "ease in/out" of the various directions by tweaking the corresponding vramp colors, either by adjusting the interpolation or by chaging the actual colors on the ramp. There will be one ramp feeding in to each normalized value
You can dial the values to match your start and end points by adjusting the mins and maxs for each direction (forward and up start at 2 and go up to 4, back and down have a "min" at 2 and have a "max" of 0, ie. 0 uv pos = 1 normalized out)
You can also freely move/rotate the sphere to better align with what you want (just pay attention to what's fwd/bk/up/dwn once you do)
You can also detach and move the locator as you see fit. Just reattach it somehow to a moving part to measure that part's relationship to the sphere
"""

#---------------- figure out ramp nodes not updating correctly w/o a AE or node editor

import maya.cmds as cmds
from functools import partial
import maya.mel as mel

class PoseReader(object):

    def __init__(self):
        self.pose_reader_UI()


    def pose_reader_UI(self, *args):
        if cmds.window("poseReaderWin", exists=True):
            cmds.deleteUI("poseReaderWin")
        # need to get name for all, joint to measure, parent for sphere
        self.win = cmds.window("poseReaderWin", w=300, h=200, s=False)
        cmds.columnLayout(w=300, h=200)
        self.nameTFG = cmds.textFieldGrp(l="Name: ", cl2=["left", "left"], cw2=[100, 190])
        self.followTFBG = cmds.textFieldButtonGrp(l="Follow Obj: ", cl3=["left", "left", "right"], cw3=[100, 150, 50], bl="<<<", bc = partial(self.get_object,"follow"))
        self.parentTFBG = cmds.textFieldButtonGrp(l="Parent Obj: ", cl3=["left", "left", "right"], cw3=[100, 150, 50], bl="<<<", bc=partial(self.get_object,"parent"))
        cmds.separator(h=10)

        self.rampCB = cmds.checkBox(l="Create Ramps?", v=False)
        cmds.separator(h=10)

        cmds.button(l="Create Reader", w=300, h=50, bgc=(.5, .7,.5),c=self.create_pose_reader)

        cmds.window(self.win, e=True, w=5, h=5, rtf=True)
        cmds.showWindow(self.win)


    def get_object(self, ui, *args):
        sel = cmds.ls(sl=True)
        if not sel:
            return()
        if ui == "follow":
            gui = self.followTFBG
        if ui == "parent":
            gui = self.parentTFBG
        
        cmds.textFieldButtonGrp(gui, e=True, tx=sel[0])


    def create_pose_reader(self, parent=None, follow=None, *args):
        if not parent:
            self.parent = cmds.textFieldButtonGrp(self.parentTFBG, q=True, tx=True)
        if not follow:
            self.follow = cmds.textFieldButtonGrp(self.followTFBG, q=True, tx=True)
        self.name = cmds.textFieldGrp(self.nameTFG, q=True, tx=True) + "_pose"
        self.ramp = cmds.checkBox(self.rampCB, q=True, v=True)

        self.create_sphere()
        self.attach_rig()
        self.setup_attributes()
        self.build_connections()
        self.temp_dirty_ramps()


    def create_sphere(self, *args):
        self.sphere = cmds.sphere(name=self.name+"_sphere", ax=[0, 1, 0], ssw=0, esw=360, r=1, d=3, ut=0, s=4, nsp=4, ch=0)[0]
        self.grp = self.group_freeze(self.sphere)
        self.loc = cmds.spaceLocator(name=self.name+"_Loc")
        cmds.xform(self.grp, ws=True, ro=(0, 180, 0))
        cmds.makeIdentity(self.grp, apply=True)
        cmds.parent(self.loc, self.grp)
        cmds.xform(self.loc, ws=True, t=(2, 0, 0))


    def attach_rig(self, *args):
        self.snap_to(self.follow, self.grp)
        cmds.parentConstraint(self.parent, self.grp, mo=True)
        # todo: maybe don't connect the locator here?       
        cmds.parentConstraint(self.follow, self.loc, mo=True)


    def setup_attributes(self, *args):
        cmds.addAttr(self.sphere, ln="__current__", nn="__current__", at="enum", en="-----", k=True)
        cmds.setAttr(self.sphere+".__current__", l=True)
        cmds.addAttr(self.sphere, ln="currentU", at="float", k=True, dv=0)
        cmds.addAttr(self.sphere, ln="currentV", at="float", k=True, dv=0)
        cmds.addAttr(self.sphere, ln="__adjustment__", nn="__adjustment__", at="enum", en="-----", k=True)
        cmds.setAttr(self.sphere+".__adjustment__", l=True)
        cmds.addAttr(self.sphere, ln="min_V_Forward", at="float", k=True, dv=2)
        cmds.addAttr(self.sphere, ln="max_V_Forward", at="float", k=True, dv=4)
        cmds.addAttr(self.sphere, ln="min_V_Backward", at="float", k=True, dv=0)
        cmds.addAttr(self.sphere, ln="max_V_Backward", at="float", k=True, dv=2)        
        cmds.addAttr(self.sphere, ln="min_U_Upward", at="float", k=True, dv=2)
        cmds.addAttr(self.sphere, ln="max_U_Upward", at="float", k=True, dv=4)
        cmds.addAttr(self.sphere, ln="min_U_Downward", at="float", k=True, dv=0)
        cmds.addAttr(self.sphere, ln="max_U_Downward", at="float", k=True, dv=2)
        cmds.addAttr(self.sphere, ln="__outputs__", nn="__outputs__", at="enum", en="-----", k=True)
        cmds.setAttr(self.sphere+".__adjustment__", l=True)
        cmds.addAttr(self.sphere, ln="normalized_V_Forward", at="float", k=True, dv=0)
        cmds.addAttr(self.sphere, ln="normalized_V_Backward", at="float", k=True, dv=0)
        cmds.addAttr(self.sphere, ln="normalized_U_Upward", at="float", k=True, dv=0)
        cmds.addAttr(self.sphere, ln="normalized_U_Downward", at="float", k=True, dv=0)


    def build_connections(self, *args):
        cpos = cmds.createNode("closestPointOnSurface", name=self.name+"_CPOS")
        sphereShp = cmds.listRelatives(self.sphere, s=True)[0]
        locShp = cmds.listRelatives(self.loc, s=True)[0]
        cmds.connectAttr(sphereShp+".worldSpace", cpos+".inputSurface")
        cmds.connectAttr(locShp+".worldPosition", cpos+".inPosition")

        cmds.connectAttr(cpos+".result.parameterV", self.sphere+".currentV")
        cmds.connectAttr(cpos+".result.parameterU", self.sphere+".currentU")

        names = ["_vFwd_SR", "_vBck_SR", "_uUpw_SR", "_uDwn_SR"]
        cout = [".result.parameterV", ".result.parameterV", ".result.parameterU", ".result.parameterU"]
        oldMins = [".min_V_Forward", ".min_V_Backward", ".min_U_Upward", ".min_U_Downward"]
        oldMaxs = [".max_V_Forward", ".max_V_Backward", ".max_U_Upward", ".max_U_Downward"]
        returns = [".normalized_V_Forward", ".normalized_V_Backward", ".normalized_U_Upward", ".normalized_U_Downward"]
        mins = [0, 1, 0, 1]
        maxs = [1, 0, 1, 0]
        self.ramps = []
        for i in range(4):
            sRange = cmds.createNode("setRange", name=self.name + names[i])
            cmds.connectAttr(cpos+cout[i], sRange+".value.valueX")
            cmds.connectAttr(self.sphere+oldMins[i], sRange+".oldMin.oldMinX")
            cmds.connectAttr(self.sphere+oldMaxs[i], sRange+".oldMax.oldMaxX")
            cmds.setAttr(sRange+".minX", mins[i])
            cmds.setAttr(sRange+".maxX", maxs[i])
            if self.ramp:
                ramp = cmds.createNode("ramp", name="{0}_{1}_RMP".format(self.name, returns[i][1:]))
                cmds.connectAttr(sRange + ".outValueX", ramp + ".uvCoord.vCoord")
                cmds.connectAttr(ramp+".outColor.outColorR", self.sphere+returns[i])
                self.ramps.append(ramp)
            else:
                cmds.connectAttr(sRange+".outValue.outValueX", self.sphere+returns[i])


    def snap_to(self, target, obj, rot=True, trans=True):
        if trans:
            pos = cmds.xform(target, q=True, ws=True, rp=True)
            cmds.xform(obj, ws=True, t=pos)
        if rot:
            rot = cmds.xform(target, q=True, ws=True, ro=True)
            cmds.xform(obj, ws=True, ro=rot)


    def group_freeze(self, obj, suffix="Grp", *arg):
        parent = cmds.listRelatives(obj, p=True)
        if parent:
            parent = parent[0]

        grpname = "{0}_{1}".format(obj, suffix)
  
        grpname = self.increment_name(grpname)
        grp = cmds.group(empty=True, name=grpname)
        self.snap_to(obj, grp)
        cmds.parent(obj, grp)

        if parent:
            cmds.parent(grp, parent)

        return (grp)


    def increment_name(self, name, *args):
        """
        increments the given name string by adding 1 to last digit
        note: will not respect padding at the moment, so '_09' will become '_010'
        :param name:
        :param args:
        :return:
        """
        if not cmds.objExists(name):
            return(name)
        else:
            if self.integer_test(name[-1]):
                newname = "{0}{1}".format(name[:-1], int(name[-1])+1)
            else:
                newname = "{0}_1".format(name)
            return(increment_name(newname))


    def integer_test(self, digit):
        """
        tests whether digit is an integer or not
        :param obj: some value
        :param args:
        :return:  boolean
        """
        try:
            int(digit)
            return (True)
        except ValueError:
            return(False)


    def temp_dirty_ramps(self):
        # just trying this to dirty the plugs of the ramps? Is there a better way?
        ramp = cmds.listConnections(self.sphere+".normalized_V_Forward", s=True)
        mel.eval("ShowAttributeEditorOrChannelBox;")
        cmds.select(ramp[0])