import maya.cmds as cmds
import zTools.rig.zbw_rig as rig
import importlib
importlib.reload(rig)
import zTools.zbw_tools as tools
importlib.reload(tools)

#---------------- Don't scale top two joints? THen have to figure out how to grow or shrink the remaining (use a ramp value node or set range?) 
#---------------- add a copy of last joint and put in there for ik spline
#---------------- SET ROTATION ORDERS ON JOINTS AND CONTROLS (AND TWIST?)
#---------------- put rotate order in ui, then also add it to controls. Connect the control RO to all the joint RO's
#---------------- clamp top chest to control (Don't scale top?)
#----------------translate stretch controls


#---------------- maybe a switch for dual quat skinning in fk mode and normal in ik mode?


class IkFkRig(object):
    def __init__(self):
        self.JntAxisWorldUpDict = {
        0:(0, 1, 0),
        1:(0, -1, 0),
        2:(0, 1, 0),
        3:(0, 0, 1),
        4:(0, 0, -1),
        5:(0, 0, 1), 
        6:(1, 0, 0),
        7:(-1, 0, 0),
        8:(1, 0, 0)
        } # based on 'self.upAxis' order

        self.ikfk_spline_rigUI()

        
    def ikfk_spline_rigUI(self):
        if cmds.window("splineRigWin", exists=True):
            cmds.deleteUI("splineRigWin")

        self.window = cmds.window("splineRigWin")
        cmds.columnLayout(w=300, h=150)
        cmds.text(l="Select all of the ik joints in order(first->last)\nNOTE: These don't have to be first->last of the chain\nJoints will be renamed, but should be oriented already", align="left")
        cmds.separator(h=10)
        self.nameTFG = cmds.textFieldGrp(l="Name:", cw=[(1, 50), (2, 200)], cal=[(1, "left"),(2, "left")], tx="spine")
        self.topTanFFG = cmds.floatFieldGrp(l="Top Tan Pos:", cw=[(1, 100), (2,50)], cal=[(1, "left"), (2, "left")], v1=0.9, cc=self.check_float_valid)
        self.baseTanFFG = cmds.floatFieldGrp(l="Base Tan Pos:", cw=[(1, 100), (2,50)], cal=[(1, "left"), (2, "left")], v1=0.3, cc=self.check_float_valid)

        self.axis = cmds.optionMenu(l="Jnt Orient Axis:")
        cmds.menuItem(l="x")
        cmds.menuItem(l="-x")
        cmds.menuItem(l="y")
        cmds.menuItem(l="-y")
        cmds.menuItem(l="z")
        cmds.menuItem(l="-z")
        cmds.optionMenu(self.axis, e=True, v="x")
        cmds.separator(h=10)    
        self.upAxis = cmds.optionMenu(l="Jnt Orient Up Axis:")
        cmds.menuItem(l="y")
        cmds.menuItem(l="-y")
        cmds.menuItem(l="closest y")
        cmds.menuItem(l="z")
        cmds.menuItem(l="-z")
        cmds.menuItem(l="closest z")
        cmds.menuItem(l="x")
        cmds.menuItem(l="-x")
        cmds.menuItem(l="closest x")
        cmds.optionMenu(self.upAxis, e=True, v="z")
        cmds.separator(h=10)

        self.curveBut = cmds.button(l="Setup Spline Curve", bgc=(.5, .7, .5), h=40, w=300, c=self.setup_rig)
        cmds.text(l="Adjust the tan ctrl grps to align the curve\nwith the joints using grps above the ctrls", align="left")

        self.createBut = cmds.button(l="Create IK FK Rig", bgc=(.5, .7, .5), h=40, w=300, c=self.create_rig)

        cmds.window(self.window, e=True, w=5, h=5, rtf=True)
        cmds.showWindow(self.window)


    def check_float_valid(self, *args):
        num = cmds.floatFieldGrp(widgets["midJntFFG"], q=True, v1=True)
        if num < 0.0 or num > 1.0:
            cmds.warning("Value is from 0-1 (base-end)")
            cmds.floatFieldGrp(widgets["midJntFFG"], e=True, v1=.5)


    def get_object(self, uiVal, *args):
        sel = cmds.ls(sl=True, l=True, type="transform")
        if sel:
            obj = sel[0]
            cmds.textFieldButtonGrp(widgets[uiVal], e=True, tx=obj)
        else: 
            cmds.warning("you need to select a transform!")


    def setup_rig(self, *args):
        self.name = cmds.textFieldGrp(self.nameTFG, q=True, tx=True)
        self.baseVal = cmds.floatFieldGrp(self.baseTanFFG, q=True, v1=True)
        self.topVal = cmds.floatFieldGrp(self.topTanFFG, q=True, v1=True)
        self.jntList = cmds.ls(sl=True, type="joint")
        if (not self.jntList) or (len(self.jntList)<3) or (not self.name):
            cmds.warning("You need to select joints in a chain!")
            return()

        # get info from axes
        self.jntAxis = cmds.optionMenu(self.axis, q=True, sl=True)
        self.jntUpAxis = cmds.optionMenu(self.upAxis, q=True, sl=True)
        # self.worldUpAxis = cmds.optionMenu(self.worldUpAxis, q=True, sl=True)
        spineRig = self.create_ik_spline_components()


    def create_ik_spline_components(self):
        self.build_ik_spline()
        self.create_ik_ctrls()
        self.position_ik_ctrls()
        self.connect_ik_ctrls()


    def create_rig(self, *args):
        self.create_ik_rig()
        self.duplicate_joint_hierachies()
        self.setup_spline_advanced_twist()
        self.create_attributes()
#---------------- setup stretch system (maybe squash stuff w three extra joint for nonuniform scaling? see blog post about that)
        self.setup_ik_scaling()

        self.create_fk_rig()
#---------------- add in system to turn on/off twist? lock these attrs?
        self.connect_bind_jnts()

        self.clean_up()


    def build_ik_spline(self):
        jntPosList = [cmds.xform(self.jntList[x], q=True, ws=True, rp=True) for x in range(len(self.jntList))]
        self.ikCrv = cmds.curve(n="self.ikCrv", d=1, p = jntPosList)
        cmds.rebuildCurve(self.ikCrv, constructionHistory=False, replaceOriginal=True, rebuildType=0, spans=2, degree=2, keepRange=False, keepEndPoints=True, keepTangents=False, keepControlPoints=False)
        self.crvShp = cmds.listRelatives(self.ikCrv, s=True)[0]
        return(self.ikCrv, self.crvShp)


    def create_ik_ctrls(self):
        self.ax = cmds.optionMenu(self.axis, q=True, v=True)
        if len(self.ax)==2:
            self.ax = self.ax[1]
        if self.ax == "x":
            vals = [0.2, 1, 1]
        if self.ax == "y":
            vals = [1, 0.2, 1]
        if self.ax == "z":
            vals = [1, 1, 0.2]
        self.topCtrl = rig.create_control("{0}_topIK_CTRL".format(self.name), "cube", self.ax, "yellow")
        rig.scale_nurbs_control(self.topCtrl, vals[0], vals[1], vals[2])
        self.topCtrlGrp = rig.group_freeze(self.topCtrl)
        self.topTan = rig.create_control("{0}_topIKTangent_CTRL".format(self.name), "cross", self.ax, "orange")
        self.topTanGrp = rig.group_freeze(self.topTan)
        cmds.parent(self.topTanGrp, self.topCtrl)

        self.baseCtrl = rig.create_control("{0}_baseIK_CTRL".format(self.name), "cube", self.ax, "yellow")
        rig.scale_nurbs_control(self.baseCtrl, vals[0], vals[1], vals[2])
        self.baseCtrlGrp = rig.group_freeze(self.baseCtrl)
        self.baseTan = rig.create_control("{0}_baseIKTangent_CTRL".format(self.name), "cross", self.ax, "orange")
        self.baseTanGrp = rig.group_freeze(self.baseTan)
        cmds.parent(self.baseTanGrp, self.baseCtrl)

        rig.snap_to(self.jntList[-1], self.topCtrlGrp)
        rig.snap_to(self.jntList[0], self.baseCtrlGrp)


    def position_ik_ctrls(self):
        poc = cmds.shadingNode("pointOnCurveInfo", asUtility=True, name="IKNAME_POC")
        cmds.connectAttr("{0}.worldSpace[0]".format(self.crvShp), "{0}.inputCurve".format(poc))
        cmds.setAttr("{0}.parameter".format(poc), .9)
        topTanPos = cmds.getAttr("{0}.result.position".format(poc))[0]
        cmds.setAttr("{0}.parameter".format(poc), .4)
        baseTanPos = cmds.getAttr("{0}.result.position".format(poc))[0]
        cmds.xform(self.baseTanGrp, ws=True, t=baseTanPos)
        cmds.xform(self.topTanGrp, ws=True, t=topTanPos)
        cmds.delete(poc)


    def connect_ik_ctrls(self):
        self.decompList = []
        for ctrl in [self.baseCtrl, self.baseTan, self.topTan, self.topCtrl]:
            dcm = cmds.shadingNode("decomposeMatrix", asUtility=True, name=ctrl+"_DCM")
            cmds.connectAttr("{0}.worldMatrix[0]".format(ctrl), "{0}.inputMatrix".format(dcm))
            self.decompList.append(dcm)

        for x in range(len(self.decompList)):
            cmds.connectAttr("{0}.outputTranslate".format(self.decompList[x]), "{0}.controlPoints[{1}]".format(self.crvShp, x))


    def create_ik_rig(self):
        self.ikHandle, self.ikEffector = cmds.ikHandle(startJoint=self.jntList[0], ee=self.jntList[-1], sol="ikSplineSolver", rootTwistMode=True, ccv=False, curve=self.ikCrv, name="{0}_IK".format(self.name))
        self.ikCrv = cmds.rename(self.ikCrv, "{0}_ikSpl_CRV".format(self.name))    


    def duplicate_joint_hierachies(self):
        fkJntList = cmds.duplicate(self.jntList[0], rc=True)
        del fkJntList[len(self.jntList):]
        bindJntList = cmds.duplicate(self.jntList[0], rc=True)
        del bindJntList[len(self.jntList):]
        ikList = self.jntList
        del ikList[len(self.jntList):]
        self.ikJntList = self.rename_joint_list(self.jntList, "IK", -1)
        self.fkJntList = self.rename_joint_list(fkJntList, "FK", -1)
        self.bindJntList = self.rename_joint_list(bindJntList, "bind", -1)


    def rename_joint_list(self, jntList, prefix, offset):
        #HOW TO DEAL WITH JOINTS AT END?
        thisList = []
        for x in range(len(jntList)+offset, -1, -1):
            newJnt = cmds.rename(jntList[x], "{0}_{1}{2}_JNT".format(prefix, self.name, x))
            thisList.append(newJnt)
        return(thisList)


    def setup_spline_advanced_twist(self):
        ax = self.JntAxisWorldUpDict[self.jntUpAxis -1]
        
        cmds.setAttr("{0}.dWorldUpType".format(self.ikHandle), 4) # sets twist to objRotUpStartEnd
        cmds.setAttr("{0}.dTwistControlEnable".format(self.ikHandle), 1)
        cmds.setAttr("{0}.dForwardAxis".format(self.ikHandle), self.jntAxis-1)
        cmds.setAttr("{0}.dWorldUpAxis".format(self.ikHandle), self.jntUpAxis-1)

        cmds.setAttr("{0}.dWorldUpVector".format(self.ikHandle), ax[0], ax[1], ax[2])
        cmds.setAttr("{0}.dWorldUpVectorEnd".format(self.ikHandle), ax[0], ax[1], ax[2])

        cmds.connectAttr("{0}.worldMatrix[0]".format(self.baseCtrl), "{0}.dWorldUpMatrix".format(self.ikHandle))
        cmds.connectAttr("{0}.worldMatrix[0]".format(self.topCtrl), "{0}.dWorldUpMatrixEnd".format(self.ikHandle))

        cmds.setAttr("{0}.dTwistValueType".format(self.ikHandle), 0) # sets to total


    def create_attributes(self):
        cmds.addAttr(self.topCtrl, ln="xtra_attrs", at="enum", en="-----", k=True)
        cmds.setAttr("{0}.xtra_attrs".format(self.topCtrl), l=True)
        cmds.addAttr(self.topCtrl, ln="auto_stretch", at="double", min=0, max=1, k=True, dv=0)
        cmds.addAttr(self.topCtrl, ln="fkIk", at="double", min=0, max=1, k=True, dv=1)
        self.ikReverse = cmds.shadingNode("reverse", asUtility=True, name="{0}_fkik_REV".format(self.name))
        cmds.connectAttr("{0}.fkIk".format(self.topCtrl), "{0}.inputX".format(self.ikReverse))


    def setup_ik_scaling(self):
        # attr
        if self.ax == "x":
            ax = "sx"
        if self.ax == "y":
            ax = "sy"
        if self.ax == "z":
            ax = "sz"
        self.measureCrv = cmds.duplicate(self.ikCrv,name="{0}_measure_CRV".format(self.name))[0]
        splPoc = cmds.arclen(self.ikCrv, ch=True)
        msrPoc = cmds.arclen(self.measureCrv, ch=True)
        ratioMult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_ratio_mult".format(self.name))
        cmds.setAttr("{0}.operation".format(ratioMult), 2)
        cmds.connectAttr("{0}.arcLength".format(splPoc), "{0}.input1.input1X".format(ratioMult))
        cmds.connectAttr("{0}.arcLength".format(msrPoc), "{0}.input2.input2X".format(ratioMult))
        scaleDefaultMult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_envelope_mult".format(self.name))
        cmds.setAttr("{0}.input1X".format(scaleDefaultMult), 1.0)
        envelopeBlend = cmds.shadingNode("blendColors", asUtility=True, name="{0}_scaleBlClr".format(self.name))
        cmds.connectAttr("{0}.auto_stretch".format(self.topCtrl), "{0}.blender".format(envelopeBlend))
        cmds.connectAttr("{0}.outputX".format(ratioMult), "{0}.color1.color1R".format(envelopeBlend))
        cmds.connectAttr("{0}.outputX".format(scaleDefaultMult), "{0}.color2.color2R".format(envelopeBlend))

        for jnt in self.ikJntList:
            cmds.connectAttr("{0}.output.outputR".format(envelopeBlend), "{0}.{1}".format(jnt, ax))


    def create_fk_rig(self):
        ctrl = rig.create_control(name="CTRL".format(self.name), type="splitCircle", axis=self.ax, color="pink")
        cmds.select(ctrl, self.fkJntList, r=True)
        self.fkCtrlList = []
        self.fkGrpList = []
        fkCtrlList, fkGrpList = tools.freeze_and_connect()
        
        for obj in fkCtrlList:
            newName = cmds.rename(obj, obj.replace("JNT", ""))
            self.fkCtrlList.append(newName)
        for obj in fkGrpList:
            newName = cmds.rename(obj, obj.replace("JNT", ""))
            self.fkGrpList.append(newName)
        self.fkGrpList.reverse()
        self.fkCtrlList.reverse()


    def connect_bind_jnts(self):
        self.bindPointCons = []
        self.bindOrientCons = []
        # for each bind joint up to [:-1]:
        for x in range(len(self.bindJntList)-1, 0, -1):
            #point and orient constrain to ik, fk joint
            pc = cmds.pointConstraint([self.ikJntList[x], self.fkJntList[x]], self.bindJntList[x])[0]
            self.bindPointCons.append(pc)
            oc = cmds.orientConstraint([self.ikJntList[x], self.fkJntList[x]], self.bindJntList[x])[0]
            self.bindOrientCons.append(oc)
        # for last joint:
        topPc = cmds.pointConstraint([self.ikJntList[0], self.fkJntList[0]], self.bindJntList[0])[0]
        self.bindPointCons.append(topPc)
        topOc = cmds.orientConstraint([self.topCtrl, self.fkJntList[0]], self.bindJntList[0], maintainOffset=False)[0]
        self.bindOrientCons.append(topOc)

        # hook up attrs to switch from topCtrl
        for x in range(len(self.bindJntList)):
            cmds.connectAttr("{0}.fkIk".format(self.topCtrl), "{0}.w0".format(self.bindPointCons[x]))
            cmds.connectAttr("{0}.outputX".format(self.ikReverse), "{0}.w1".format(self.bindPointCons[x]))
            cmds.connectAttr("{0}.fkIk".format(self.topCtrl), "{0}.w0".format(self.bindOrientCons[x]))
            cmds.connectAttr("{0}.outputX".format(self.ikReverse), "{0}.w1".format(self.bindOrientCons[x]))


    def clean_up(self):
        # hide spline ikhandle, measure curve, ikCrv 
        toHide = [self.ikHandle, self.measureCrv, self.ikCrv]
        for obj in toHide:
            cmds.setAttr("{0}.v".format(obj), 0)

        # clean up attributes (hide scale, etc)
        for ctrl in self.fkCtrlList:
            rig.strip_to_rotate_translate(ctrl)
        for ctrl in [self.topCtrl, self.baseCtrl, self.topTan, self.baseTan]:
            rig.strip_to_rotate_translate(ctrl)
        # create no transfofm group (ik, ik crv)
        noXformGrp = cmds.group(em=True, name="{0}_noTransform_GRP".format(self.name))
        cmds.setAttr("{0}.inheritsTransform".format(noXformGrp), 0)
        cmds.parent([self.ikHandle, self.ikCrv], noXformGrp)
        # create world grp (ik controls)
        worldGrp = cmds.group(em=True, name="{0}_worldTransform_GRP".format(self.name))
        cmds.parent([self.topCtrlGrp, self.baseCtrlGrp], worldGrp)
        # create transform grp (jnts, fk controls, measure crv)
        xformGrp = cmds.group(em=True, name="{0}_transform_GRP".format(self.name))
        cmds.parent([self.fkJntList[-1], self.ikJntList[-1], self.bindJntList[-1], self.fkGrpList[0], self.measureCrv], xformGrp)