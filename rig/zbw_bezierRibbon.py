

import maya.cmds as cmds
from . import zbw_rig as rig



#----------------create a bezier version of this (4 divisions, don't need control joints, create cluster setups and attrs to use them, create aim constraints for end joints)

#start by grabbing the joints that we'll use?

#create nurbs plane with 4 division in u (deg 3 in u, 1 in v)
#add follicles, create a joint at each follicle, parent to follicle

#cluster each pair of cv's, name the clusters - not relative (cv's come in array pairs like [(0,0), (0,1)])

#create a control for each cluster and parent the cluster under it

#group the control twice (at the location) and name bottom grp "constrain" and top "attach"

#parent the two middle clusters to the center cluster

#parent the two endish top grps to the end clusters

#work out the constraints. . .
#on/off for an aim constraint
#create an up vector for that constraint that goes under the ?end controller/cluster?

#to localize the bend at the elbow . . .
#create an extra loc that's parallel with the ceneter bezier handles on either side, put the center handles in a group w/ pivot at the center and adn up loc too and have the bezier handle groups point at either the locs (flat tangent) or the end controls (broken tangent). This stuff all goes in a group that still leaves the bezier handle controls free. ORRRR figure out some way to have the bezier handles go down in y via an sdk or something (so they straighten with the arm)

#in order to hook it up you could
#a) just constrain or hook up the cluster/control grps to the control skel
#ooooorrrrrrr
#b) bind a copy of the surface to the joints and use the clustered one as a blend shape
#control that with either dialing the blend shape at the arm angles, or using sdks to drive the clusters at arm angles. probably the latter?


import zTools.rig.zbw_rig as rig
import zbw_window as win
import maya.OpenMaya as om
import maya.cmds as cmds


#----------------create a bezier version of this (4 divisions, don't need control joints, create cluster setups and attrs to use them, create aim constraints for end joints)


#----------figure out how to make midpoint adjustable (visually???) . . .
class RibbonUI(win.Window):
    def __init__(self):
        self.windowName = "zbw_bezierRibbon"
        self.windowSize = [420, 280]
        self.sizeable = 1

        self.createUI()

    def commonUI(self):
        pass

    def customUI(self):
        self.widgets["ribbonNameTFG"] = cmds.textFieldGrp(l="Ribbon Rig Name", cal=[(1, "left"), (2, "left")], cw=[(1, 100), (2, 200)], tx="ribbon")
        cmds.separator(h=10, style="single")
        self.widgets["jointsIFG"] = cmds.intFieldGrp(l="Number of Jnts (3 min)", cal=([1,"left"]), cw=([1, 125], [2,100]),v1=5)
        #self.widgets["axis"] = cmds.radioButtonGrp(l="Ribbon Ctrl Axis", nrb=3, l1="x", l2="y", l3="z", cal=([1,"left"]), cw=([1, 125], [2,50], [3,50]), sl=2, en=True)
        #self.widgets["fkSetupCB"] = cmds.checkBox(l="Setup FK Controls", v=1)
        self.widgets["heightFFG"] = cmds.floatFieldGrp(l="Ribbon Height", cal= [(1, "left"), (2, "left")], cw= [(1, 125), (2, 100)], v1=10.0)
        self.widgets["ratioFFG"] = cmds.floatFieldGrp(l="Heigth/width Ratio", cal= [(1, "left"), (2, "left")], cw= [(1, 125), (2, 100)], v1=5)
        #create a slider for where we want the middle piece of the ribbon
        #self.widgets["centerPosFSG"] = cmds.floatSliderGrp(l="Center Ctrl Position", f=True, cal = [(1, "left"), (2,"left"), (3,"left")], cw=[(1, 125), (2, 50), (3, 200)], min=0, max=1, fmn=0, fmx=1, v=0.5, pre=3)
        #option for making (or not) control structure
        #-------option to use my own surface?
        #self.widgets["existingGeoCB"] = cmds.checkBox(l="Use existing nurbs curve", v=0, cc=self.geoEnable)
        #this will reveal text field grp w button
        #checking and unchecking will activate options (and deactivate)
        #self.widgets["geoTFBG"] = cmds.textFieldButtonGrp(l="Select Geometry", bl="<<<", en=False, cal=[(1,"left"), (2, "left"), (3, "left")], cw=[(1, 100), (2, 250), (3, 50)], bc=self.getGeo)
        #self.widgets["directionRBG"] = cmds.radioButtonGrp(l="Along U or V?", nrb=2, l1="u", l2="v", cal=[(1, "left"), (2, "left")], cw=[(1, 100), (2,50), (3,50)], sl=2, en=False)

#----------------deal better with the x, y, z (should be "+x", "-x", etc)
        #option for indiv follicle controls?

    def action(self, close, *args):
        #do the action here
        self.createRibbon()

        #close window
        if close:
            self.closeWindow()
        pass

    def printHelp(self, *args):
        #########  modify for inheritence ###########
        print("this is your help, yo")

    def resetValues(self, *args):
        #########  modify for inheritence ###########
        print("test values reset")

    def saveValues(self, *args):
        #########  modify for inheritence ###########
        print("test save values")

    def loadValues(self, *args):
        #########  modify for inheritence ###########
        print("test load values")

    def geoEnable(self, *args):
        #toggle the enable
        #get the state of the button
        state = cmds.checkBox(self.widgets["existingGeoCB"], q=True, v=True)
        if state:
            cmds.textFieldButtonGrp(self.widgets["geoTFBG"], e=True, en=True)
            cmds.radioButtonGrp(self.widgets["directionRBG"], e=True, en=True)
            cmds.floatFieldGrp(self.widgets["heightFFG"], e=True, en=False)
            cmds.floatFieldGrp(self.widgets["ratioFFG"] , e=True, en=False)
            #cmds.textFieldGrp(self.widgets["ribbonNameTFG"], e=True, en=False)
        else:
            cmds.textFieldButtonGrp(self.widgets["geoTFBG"], e=True, en=False)
            cmds.radioButtonGrp(self.widgets["directionRBG"], e=True, en=False)
            cmds.floatFieldGrp(self.widgets["heightFFG"], e=True, en=True)
            cmds.floatFieldGrp(self.widgets["ratioFFG"] , e=True, en=True)
            #cmds.textFieldGrp(self.widgets["ribbonNameTFG"], e=True, en=True)

    def getGeo(self, *args):
        #get selection and put it's full path into the tfbg
        sel = cmds.ls(sl=True, type="transform", l=True)
        print(sel)
        if len(sel) != 1:
            cmds.warning("yo. Select one and only one nurbs surface")
        else:
            #check for nurbsy-ness
            if (cmds.objectType(cmds.listRelatives(sel[0], shapes=True)[0])!="nurbsSurface"):
                cmds.error("Selected is not a nurbs surface")
            else:
                cmds.textFieldButtonGrp(self.widgets["geoTFBG"], e=True, tx=sel[0])


    def createRibbon(self, *args):
        self.name = cmds.textFieldGrp(self.widgets["ribbonNameTFG"], q=True, tx=True)
        self.numDiv = (cmds.intFieldGrp(self.widgets["jointsIFG"], q=True, v=True)[0]) -1
        #self.fk = cmds.checkBox(self.widgets["fkSetupCB"], q=True, v=True)
        self.height = cmds.floatFieldGrp(self.widgets["heightFFG"], q=True, v1=True)
        self.ratio = cmds.floatFieldGrp(self.widgets["ratioFFG"], q=True, v1=True)
        #self.axis = cmds.radioButtonGrp(self.widgets["axis"] , q=True, sl=True)

        #print("axis = :%s"%self.axis)
        self.ribbonName = "%s_ribbonGeo"%self.name
        self.numJoints = self.numDiv
        self.follicleList = []
        self.follicleJntList = []
        #self.own = cmds.checkBox(self.widgets["existingGeoCB"], q=True, v=True)
        #self.myGeo = cmds.textFieldButtonGrp(self.widgets["geoTFBG"], q=True, tx=True)
        #self.dir = cmds.radioButtonGrp(self.widgets["directionRBG"], q=True, sl=True )
        #print("dir: %s"%self.dir)
        #self.centerPos = cmds.floatSliderGrp(self.widgets["centerPosFSG"], q=True, v=True )
        self.follicleGrpList = []

#-----------make sure the num of divisions is at least 1
#-----------create the nurbs plane in the correct axis (just make the plane in the axis and figure out how to rotate joint local rotational axes to match it) DON'T WORRY ABOUT THIS SO MUCH (IT'S HIDDEN), WORRY ABOUT THE CONTROLS BEING ORIENTED CORRECTLY!!!

        # if self.own == 0:
        # 	self.dir = 2
        # if self.dir == 1:
        # 	dir = "u"
        # 	uDiv = self.numDiv
        # 	vDiv = 1
        # else:
        # 	dir = "v'"
        # 	uDiv = 1
        # 	vDiv = self.numDiv

        # if self.axis  == 1:
        axis = [0, 0, 1]
        # elif self.axis  == 2:
        # 	axis = [0, 1, 0]
        # elif self.axis  == 3:
        # 	axis = [0, 0, 1]

        #if self.own == 0:
        width = self.height/self.ratio

        #create the nurbsPlane
        cmds.nurbsPlane(ax=axis, w=width, lr=self.ratio, d=3, u=1, v=4, ch=0, n=self.ribbonName)
        cmds.rebuildSurface (self.ribbonName, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kc=0, su=1, du=1, sv=4, dv=3, tol=0.1, fr=0, dir=2)
        cmds.move(0, self.height/2, 0, self.ribbonName)

        cmds.xform(self.ribbonName, ws=True, rp=[0, 0, 0])

        # else:
        # 	self.ribbonName = self.myGeo

        #find the ratio for the uv's (one dir will be .5, the other a result of the num joints)
        factor = 1.0/self.numJoints

#-------keep follicle joints separate, not parente under each follicle, separate group for those
#-------follicle jnts each go under a ctrl (star) that is under a group. That group gets parent constrained to the follicles
#-------these joints should be aligned with the follicles??? does that make a difference?

        #create the follicles on the surface, joints on the follicles
        for x in range (self.numJoints+1):
            val = x * factor
            folName = "%s_follicle%s"%(self.name, x)
            #create a follicle in the right direction
            # if self.dir ==1:
            # 	follicle = rig.follicle(self.ribbonName, folName, val, 0.5)[0]
            # else:
            follicle = rig.follicle(self.ribbonName, folName, 0.5, val)[0]

            self.follicleList.append(follicle)

            #create joint and parent to follicle
            jointName = "%s_fol%s_JNT"%(self.name, x)
#---------have to figure out how to orient this correctly (just translate and rotate the joints (or the controls they're under))
            #create joint control? then move the control and the joint under it to the correct rot and pos
            folPos = cmds.xform(follicle, q=True, ws=True, t=True)
            folRot = cmds.xform(follicle, q=True, ws=True, ro=True)
            cmds.select(cl=True)
            folJoint = cmds.joint(n=jointName, p=(0,0,0))
            folGroup = cmds.group(folJoint, n="%s_GRP"%folJoint) #this could become control for the joint
            cmds.xform(folGroup, a=True, ws=True, t=folPos)
            cmds.xform(folGroup, a=True ,ws=True, ro=folRot)
            self.follicleJntList.append(folJoint)
            self.follicleGrpList.append(folGroup)
            cmds.parent(folGroup, follicle)

        #create controls here:
        #create a loop that runs through the cvs in v, 0 to 6
        origClusterList = ["top_CLS", "topBez_CLS", "centerTop_CLS","center_CLS", "centerEnd_CLS", "endBez_CLS" ,"end_CLS"]
        origControlList = ["top_CTRL", "topBez_CTRL", "centerTop_CTRL", "center_CTRL", "centerEnd_CTRL", "endBez_CTRL", "end_CTRL"]

        clusterList = []
        controlList = []
        constrGrpList = []
        attachGrpList = []

        for v in range(0, 7):
            cmds.select(clear=True)
            clusNodeName = self.name + "_" + origClusterList[v] + "Base"
            #select u (0 and 1) for each v and cluster them
            fullCls = cmds.cluster("%s.cv[0:1][%d]"%(self.ribbonName, v), relative=False, n=clusNodeName)[0]
            clusHandle = clusNodeName + "Handle"
            clusName = clusHandle.rstrip("BaseHandle")
            cmds.rename(clusHandle, clusName)
            clusterList.append(clusName)
            #now setup the controls and groups for the clusters
            #goes control,group (const), group(attach)
            control = self.name + "_" + origControlList[v]
            constrGrp = self.name + "_" + origControlList[v] + "_const_GRP"
            attachGrp = self.name + "_" + origControlList[v] + "_attach_GRP"

            rig.create_control(name=control, type="circle", axis="y", color="darkGreen", *args)
            grp = rig.group_freeze(ctrl)
            rig.snap_to(clusName, grp)
            cmds.rename(oldGrp, constrGrp)

            #parent clus to control
            cmds.parent(clusName, control)

            #get cluster position
            clusPos = cmds.pointPosition(clusName + ".rotatePivot")
            cmds.xform(constrGrp, ws=True, piv=(clusPos[0], clusPos[1], clusPos[2]))

            cmds.group(constrGrp, n=attachGrp)
            cmds.xform(attachGrp, ws=True, piv=(clusPos[0], clusPos[1], clusPos[2]))

            controlList.append(control)
            constrGrpList.append(constrGrp)
            attachGrpList.append(attachGrp)

#----------------better solution! create two locators. One is a bezier handle of the center cluster, one is point constrained between the two joints. The locs "slide" in and out towards the center cluster. The "local" attribute for the elbow simply controls parent constraints (no offset) between the two. This controls the "localness" of the elbow bend...



        #this is to put the constraint group of the center bez handles at the center for aiming
        # for v in range(0,7):
        # 	if v == 2 or v == 4:
        # 		#get the center constr group
        # 		constrGrp = constrGrpList[v]
        # 		centerPos = cmds.pointPosition("%s.rotatePivot"%constrGrpList[3])
        # 		#put the pivot of the constr group at the center cluster
        # 		cmds.xform(constrGrp, ws=True, piv=(centerPos[0], centerPos[1], centerPos[2]))

        # 	else:
        # 		pass

#----------------then setup aim constraints and up vectors for them

#----------------bendy wrists would have an orient constraint on, turn off for not (always point constrained)





thisRibbon = RibbonUI()