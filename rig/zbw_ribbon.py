########################
#file: zbw_ribbon.py
#author: zeth willie
#contact: zeth@catbuks.com, www.williework.blogspot.com
#date modified: 09/23/12
#
#notes: calls the class that creates the ribbon (instance is "ribbon"). The UI has options for a few things . . . .
#call with: import zbw_ribbon; zbw_ribbon.zbw_ribbon()
########################

import zTools.rig.zbw_rig as rig
import importlib
importlib.reload(rig)
import zTools.resources.zbw_window as win
importlib.reload(win)
import maya.OpenMaya as om
import maya.cmds as cmds


#---------------- only in U
#---------------- use a premade surface option, check that it's in U, swap if not (reverseSurface -d 3 -ch 1 -rpo 1 "nurbsPlane1"; )
#---------------- option for simple added in (for arms, etc)



##################
#---------------- DO WE EVEN NEED A MED RES RIBBON?
#---------------- OPTION: bind CTRL grp aim at the next bind CTRL top grp? (all except end jnt) Remember to add a new grp above the ctrl of bind jnts for the aiming
#---------------- will need a loc under each bind jnt grp. Then aim constrain each jnt to the group above it (so jnt 1 aim to grp 2), with loc in z as up object (push loc out in z 1 unit)
#---------------- option on ctrl to turn of aim of first jnt
#---------------- option to turn ALL off
#---------------- test palcement of up locators, maybe on the med controls? On its own group above it?
#---------------- option for just simple ribbon and bind and just controls (no aim locs?)
#---------------- reverse orientation of top joint to point inwards to middle? (or maybe just the group/loc that points in)

class RibbonUI(win.Window):
    def __init__(self):
        super(RibbonUI, self).__init__(w=420, h=350, winName="zRibWin")

    def common_UI(self):
        cmds.text("Add some basic instructions here?")
        self.ribbonNameTFG = cmds.textFieldGrp(l="Ribbon Rig Name", cal=[(1, "left"), (2, "left")], cw=[(1, 100), (2, 200)], tx="myRibbon")
        cmds.separator(h=10, style="single")
        self.bindJointsIFG = cmds.intFieldGrp(l="Number of Bind Joints (3 min)", cal=([1,"left"]), cw=([1, 125], [2,100]),v1=7)
        self.medJointsIFG = cmds.intFieldGrp(l="Number of Intermediate Joints (3 min)", cal=([1,"left"]), cw=([1, 125], [2,100]),v1=4)
        self.axisRBG = cmds.radioButtonGrp(l="Ribbon Ctrl Along Axis", nrb=3, l1="x", l2="y", l3="z", cal=([1,"left"]), cw=([1, 125], [2,50], [3,50]), sl=2, en=True)
        self.fkSetupCB = cmds.checkBox(l="Setup FK Controls", v=1)
        self.heightFFG = cmds.floatFieldGrp(l="Ribbon Height", cal= [(1, "left"), (2, "left")], cw= [(1, 125), (2, 100)], v1=10.0)
        self.ratioFFG = cmds.floatFieldGrp(l="Heigth/width Ratio", cal= [(1, "left"), (2, "left")], cw= [(1, 125), (2, 100)], v1=7)
        self.centerPosFSG = cmds.floatSliderGrp(l="Center Ctrl Position", f=True, cal = [(1, "left"), (2,"left"), (3,"left")], cw=[(1, 125), (2, 50), (3, 200)], min=0, max=1, fmn=0, fmx=1, v=0.5, pre=3)
        self.existingGeoCB = cmds.checkBox(l="Use existing nurbs curve", v=0, cc=self.geo_enable)
        self.geoTFBG = cmds.textFieldButtonGrp(l="Select Geometry", bl="<<<", en=False, cal=[(1,"left"), (2, "left"), (3, "left")], cw=[(1, 100), (2, 250), (3, 50)], bc=self.get_geo)
        self.directionRBG = cmds.radioButtonGrp(l="Along U or V?", nrb=2, l1="u", l2="v", cal=[(1, "left"), (2, "left")], cw=[(1, 100), (2,50), (3,50)], sl=2, en=False)

        cmds.text("Add option for how things should aim at each other")
#----------------deal better with the x, y, z (should be "+x", "-x", etc)

    def action(self, close, *args):
        self.create_ribbon()

        #close window
        if close:
            self.close_window()
        pass

    def print_help(self, *args):
        #########  modify for inheritence ###########
        print("this is your help, yo")

    def reset_values(self, *args):
        #########  modify for inheritence ###########
        print("test values reset")

    def save_values(self, *args):
        #########  modify for inheritence ###########
        print("test save values")

    def load_values(self, *args):
        #########  modify for inheritence ###########
        print("test load values")

    def geo_enable(self, *args):
        #toggle the enable
        #get the state of the button
        state = cmds.checkBox(self.existingGeoCB, q=True, v=True)
        if state:
            cmds.textFieldButtonGrp(self.geoTFBG, e=True, en=True)
            cmds.radioButtonGrp(self.directionRBG, e=True, en=True)
            cmds.floatFieldGrp(self.heightFFG, e=True, en=False)
            cmds.floatFieldGrp(self.ratioFFG , e=True, en=False)
        else:
            cmds.textFieldButtonGrp(self.geoTFBG, e=True, en=False)
            cmds.radioButtonGrp(self.directionRBG, e=True, en=False)
            cmds.floatFieldGrp(self.heightFFG, e=True, en=True)
            cmds.floatFieldGrp(self.ratioFFG , e=True, en=True)

    def get_geo(self, *args):
        """get selection and put it's full path into the tfbg"""

        sel = cmds.ls(sl=True, type="transform", l=True)
        print(sel)
        if len(sel) != 1:
            cmds.warning("yo. Select one and only one nurbs surface")
        else:
            #check for nurbsy-ness
            if (cmds.objectType(cmds.listRelatives(sel[0], shapes=True)[0])!="nurbsSurface"):
                cmds.error("Selected is not a nurbs surface")
            else:
                cmds.textFieldButtonGrp(self.geoTFBG, e=True, tx=sel[0])

#---------------- make this function less dependent on UI. Get this info either from UI or from code
    def create_ribbon(self, *args):
        self.name = cmds.textFieldGrp(self.ribbonNameTFG, q=True, tx=True)
        self.fk = cmds.checkBox(self.fkSetupCB, q=True, v=True)
        self.height = cmds.floatFieldGrp(self.heightFFG, q=True, v1=True)
        self.ratio = cmds.floatFieldGrp(self.ratioFFG, q=True, v1=True)
        self.axis = cmds.radioButtonGrp(self.axisRBG , q=True, sl=True)
        self.ribbonName = "{0}_ribbonGeo".format(self.name)
        self.numBindJnts = cmds.intFieldGrp(self.bindJointsIFG, q=True, v=True)[0]
        self.numMedJnts = cmds.intFieldGrp(self.medJointsIFG, q=True, v=True)[0]
        self.numBindDiv =  self.numBindJnts - 1
        self.numMedDiv = self.numMedJnts - 1 
        self.follicleList = []
        self.follicleJntList = []
        self.own = cmds.checkBox(self.existingGeoCB, q=True, v=True)
        self.myGeo = cmds.textFieldButtonGrp(self.geoTFBG, q=True, tx=True)
        self.dir = cmds.radioButtonGrp(self.directionRBG, q=True, sl=True )
        self.centerPos = cmds.floatSliderGrp(self.centerPosFSG, q=True, v=True )
        self.follicleGrpList = []

#-----------make sure the num of divisions is at least 1
        if self.own == 0:
            self.dir = 2
        if self.dir == 1:
            dir = "u"
            self.uBindDiv = self.numBindDiv
            self.vBindDiv = 1
            self.uMedDiv = self.numMedDiv
            self.vMedDiv = 1
        else:
            dir = "v'"
            self.uBindDiv = 1
            self.vBindDiv = self.numBindDiv
            self.uMedDiv = 1
            self.vMedDiv = self.numMedDiv

# option to not create other ribbons (only bind ribbon, or only bind and med ribbons)
        # make ribbons
        self.mainGeoGrp = cmds.group(em=True, name="{0}_ribbon_GEO_GRP".format(self.name))
        self.bindRibbon = self.create_ribbon_geo(self.numBindDiv, self.uBindDiv, self.vBindDiv, "bind")
        
        self.medRibbon = self.create_ribbon_geo(self.numMedDiv, self.uMedDiv, self.vMedDiv, "intermediate")
        self.simpleRibbon = self.create_simple_ribbon(self.bindRibbon)

        # create the follicles on the geo
        self.mainFolliclesGrp = cmds.group(em=True, name="{0}_ribbon_FOLLICLE_GRP".format(self.name))
        self.bindFollicles = self.create_follicles(self.bindRibbon, self.numBindJnts, "bind")
        
        self.medFollicles = self.create_follicles(self.medRibbon, self.numMedJnts, "intermediate")
        self.simpleFollicles = self.create_follicles(self.simpleRibbon, 3, "simple")

        # make joints for folls
        self.bindCtrlGrp, self.bindCtrls, self.bindJntGrp, self.bindJnts = self.create_joints_controls_for_follicles(self.bindFollicles, "bind")
        self.medCtrlGrp, self.medCtrls, self.medJntGrp, self.medJnts = self.create_joints_controls_for_follicles(self.medFollicles, "intermediate")
        self.simpleJntGrp, self.simpleJnts = self.create_joints_controls_for_follicles(self.simpleFollicles, "simple")

        self.create_controls()


        #base aim constrain to look at center
        #top aim constrain to look at center
        #mid parent constrain to either?, aim to either, point to either?
#---------------- parse these based on options to do or not in UI
        self.medSkinCluster = cmds.skinCluster(self.ctrlJntList, self.medRibbon, maximumInfluences=3, smoothWeights=0.5, obeyMaxInfluences=True, toSelectedBones=True, normalizeWeights=1)
        
        return()
        #start packaging stuff up
#-------hide the locators

        folGroup = cmds.group(empty=True, n="{0}_follicles_GRP".format(self.name))
        for fol in self.follicleList:
            cmds.parent(fol, folGroup)
        cmds.setAttr("%s.inheritsTransform"%folGroup, 0)

        ctrlsGroup = cmds.group(empty=True, n="%s_ctrls_GRP"%self.name)
        for grp in self.groupList:
            cmds.parent(grp, ctrlsGroup)

        geoGroup = cmds.group(empty=True, n="%s_geo_GRP"%self.name)
        cmds.parent(self.ribbonName, geoGroup)
        cmds.setAttr("%s.inheritsTransform"%geoGroup, 0)

        ribbonGroup = cmds.group(empty=True, n="%s_ribbon_GRP"%self.name)
        cmds.parent(folGroup, ribbonGroup)
        cmds.parent(ctrlsGroup, ribbonGroup)
        cmds.parent(geoGroup, ribbonGroup)

        cmds.select(ribbonGroup)


    def create_ribbon_geo(self, numDivs, uDiv, vDiv, ribType):
        if not self.own:
            name = "{0}_{1}_ribbon_GEO".format(self.name, ribType)
            width = self.height/self.ratio
            #create the nurbsPlane
            thisRib = cmds.nurbsPlane(name=name, axis=[0, 0, 1], width=width, lengthRatio=self.ratio, d=3, patchesU=uDiv, patchesV=vDiv, constructionHistory=0)[0]
            outRib = cmds.rebuildSurface (thisRib, constructionHistory=0, replaceOriginal=True, rebuildType=0, end=1, keepRange=0, keepControlPoints=0, keepCorners=0, spansU=1, degreeU=1, spansV=numDivs, degreeV=3, tolerance=0.1, fitRebuild=0, direction=0)[0]
            cmds.move(0, self.height/2, 0, outRib)

            cmds.xform(outRib, ws=True, pivots=[0, 0, 0])
            cmds.parent(outRib, self.mainGeoGrp)
        else:
            outRib = self.myGeo

        return(outRib)


    def create_simple_ribbon(self, inRibbon):
        width = self.height/self.ratio
        name  = "{0}_simple_ribbon_GEO".format(self.name)
        thisRib = cmds.nurbsPlane(name=name, axis=[0, 0, 1], width=width, lengthRatio=self.ratio, d=3, patchesU=1, patchesV=1, constructionHistory=0)[0]
        outRib = cmds.rebuildSurface (thisRib, constructionHistory=0, replaceOriginal=True, rebuildType=0, end=1, keepRange=0, keepControlPoints=0, keepCorners=0, spansU=0, degreeU=1, spansV=0, degreeV=1, tolerance=0.1, fitRebuild=0, direction=0)[0]
        # outRib = cmds.rebuildSurface (dupe, constructionHistory=0, replaceOriginal=True, rebuildType=0, end=1, keepRange=0, keepControlPoints=0, keepCorners=0, spansU=0, degreeU=1, spansV=0, degreeV=1, tolerance=0.1, fitRebuild=0, direction=2)[0]
        cmds.move(0, self.height/2, 0, outRib)
        cmds.xform(outRib, ws=True, pivots=[0, 0, 0])
        cmds.parent(outRib, self.mainGeoGrp)
        return(outRib)


    def create_follicles(self, ribbon, numFolls, ribType="bind"):
        """ribbon is the geo, numFolls is number of follicles, ribType is the 'type' if ribbon (used in naming)"""
        
        follicleList = []
        factor = 1.0/(numFolls-1)
        for x in range (numFolls):
            val = x * factor
            folName = "{0}_{1}_follicle{2}".format(self.name, ribType, x)
            #create a follicle in the right direction
            if self.dir ==1:
                follicle = rig.follicle(ribbon, folName, val, 0.5)[0]
            else:
                follicle = rig.follicle(ribbon, folName, 0.5, val)[0]

            follicleList.append(follicle)
            cmds.parent(follicle, self.mainFolliclesGrp)

        return(follicleList)


    def create_joints_controls_for_follicles(self, follicleList, ribType):
        jntList = []
        grplist = []
        ctrlList = []
        mainJointGrp = cmds.group(em=True, name="{0}_ribbon_jnt_GRP".format(ribType))
        if ribType != "simple":
            mainCtrlGrp = cmds.group(em=True, name="{0}_ribbon_ctrl_GRP".format(ribType))

        for x in range(len(follicleList)):
            baseName = "{0}_ribbon_{1}_{2}".format(self.name, ribType, x)
           
            cmds.select(cl=True)
            joint = cmds.joint(n=baseName + "_JNT", p=(0,0,0))
            jntGrp = cmds.group(joint, n="{0}_GRP".format(joint))
            rig.snap_to(follicleList[x], jntGrp)

            cmds.parent(jntGrp, mainJointGrp)
            jntList.append(joint)
            grplist.append(grplist)
        
            if ribType != "simple":
                if ribType == "bind":
                    ctrlType = "circle"
                    color = "purple"
                if ribType == "intermediate":
                    ctrlType = "star"
                    color = "orange"

                ctrl = rig.create_control("{0}_CTRL".format(baseName), ctrlType, "x", color)
                ctrlGrp = rig.group_freeze(ctrl)
                cmds.parentConstraint(follicleList[x], ctrlGrp, mo=False)
                cmds.parentConstraint(ctrl, jntGrp, mo=True)
                cmds.scaleConstraint(ctrl, jntGrp, mo=True)
                cmds.parent(ctrlGrp, mainCtrlGrp)
        
        if ribType == "simple":
            return(mainJointGrp, jntList)
        else:
            return(mainCtrlGrp, ctrlList, mainJointGrp, jntList)


    def create_main_joints(self):
        pass


    def create_controls(self):
        cmds.select(cl=True)
        prefixList = ["base", "mid", "top"]
        uvList = [0.0, self.centerPos, 1.0]
        self.groupList = []
        self.locList = []
        self.upLocList = []
        self.ctrlList = []
        self.ctrlJntList = []

        for i in range(3):
            groupName = "{0}_{1}_GRP".format(self.name, prefixList[i])
            self.groupList.append(groupName)

            grp = cmds.group(empty=True, n=groupName)
            locName = "{0}_{1}_constr_LOC".format(self.name, prefixList[i])
            loc = cmds.spaceLocator(n=locName)
            self.locList.append(loc)
            cmds.parent(loc, groupName)

            upLocName = "{0}_{1}_up_LOC".format(self.name, prefixList[i])
            upLoc = cmds.spaceLocator(n=upLocName)
            self.upLocList.append(upLoc)
#----------------axis here
            cmds.xform(upLocName, ws=True, t=[1,0,0])
            cmds.parent(upLocName, groupName)
            ctrlName = "{0}_{1}_CTRL".format(self.name, prefixList[i])
            self.ctrlList.append(ctrlName)
#----------------axis here
            cmds.circle(nr=(0, 1, 0), r=(self.height/10*3), n=ctrlName)
            cmds.parent(ctrlName, locName)
            jntName = "{0}_{1}_ctrl_JNT".format(self.name, prefixList[i])
            ctrlJoint = cmds.joint(n=jntName, p=(0,0,0))
            self.ctrlJntList.append(ctrlJoint)

            rig.align_to_uv(targetObj=groupName, sourceObj=self.simpleRibbon, sourceU=0.5, sourceV=uvList[i], mainAxis="+z", secAxis="+y", UorV="v")


def ribbon():
    ribbon = RibbonUI()