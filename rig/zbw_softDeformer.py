########################

########################


import maya.cmds as cmds
from functools import partial
import maya.mel as mel

import zTools.rig.zbw_rig as rig
import zTools.resources.zbw_window as zwin

#----------------one file should be softMod def, another should be softSelect (clusetr, jnt)

widgets= {}
class SoftDeformerUI(zwin.Window):
    def __init__(self):
        super(SoftDeformerUI, self).__init__(title="Soft Mod Deformer", w=320, h=240, winName="softWin", buttonLabel="Create")

    def common_UI(self):
        cmds.text("By default, this works with already bound geo.\nFor non_deformed geo, tick the box below")
        self.softNameTFG = cmds.textFieldGrp(l="Deformer Name", w=300, cw=[(1, 100), (2, 190)], cal=[(1, "left"), (2, "left")], placeholderText="softMod_DEF")
        self.frontChainCBG = cmds.checkBoxGrp(l="Create at front of chain?", v1=0, cw=[(1, 200)],cal=[(1, "left"), (2, "left")])
        self.ctrlScaleFFG = cmds.floatFieldGrp(l="Control Scale", v1=1, pre=2, cw=[(1, 150), (2, 50)], cal=[(1, "left"), (2, "left")])
        self.autoScaleCBG = cmds.checkBoxGrp(l="Autoscale control?", v1=1, cw=[(1, 200)], cal=[(1, "left"), (2, "left")])
        self.waveCBG = cmds.checkBoxGrp(l="Add wave shape?", v1=0, cw=[(1, 200)], cal=[(1, "left"), (2, "left")])        
        self.geoCBG = cmds.checkBoxGrp(l="non-deformed geo?", v1=0, cw=[(1, 200)], cal=[(1, "left"), (2, "left")])
        self.parentTFBG = cmds.textFieldButtonGrp(l="Parent Object:", cw=[(1, 75), (2, 175), (3, 75)], cal=[(1, "left"), (2, "left"), (3, "left")], bl="<<<", bc=self.set_parent_object)


    def custom_UI(self):
        pass


    def action(self, close, *args):
        # gather the data from UI
        smdName = cmds.textFieldGrp(self.softNameTFG, q=True, tx=True)
        foc = cmds.checkBoxGrp(self.frontChainCBG, q=True, v1=True)
        ctrlScl = cmds.floatFieldGrp(self.ctrlScaleFFG, q=True, v1=True)
        autoScale = cmds.checkBoxGrp(self.autoScaleCBG, q=True, v1=True)
        parent = cmds.textFieldButtonGrp(self.parentTFBG, q=True, tx=True)
        wave = cmds.checkBoxGrp(self.waveCBG, q=True, v1=True)
        nonDefGeo = cmds.checkBoxGrp(self.geoCBG, q=True, v1=True)
        # create the rig
        smdRig = SoftModRig(parent=parent, name=smdName, frontOfChain=foc, ctrlScale=ctrlScl, autoScale=autoScale, wave=wave, nonDefGeo=nonDefGeo)

        if close:
            self.close_window()


    def set_parent_object(self, *args):
        """
        gets selection and puts it in the given text field button grp
        """
        ctrl = None
        sel = cmds.ls(sl=True, type="transform", l=True)
        if sel:
            ctrl = sel[0]
        else:
            cmds.warning("need to select a transform as the parent object!")
            return()

        cmds.textFieldButtonGrp(self.parentTFBG, e=True, tx=ctrl)


class SoftModRig(object):
    def __init__(self, parent, name="softMod", frontOfChain=False, ctrlScale=1, autoScale=True, wave=False, nonDefGeo=False, obj=None):
        """
        only args REQUIRED is parent control (or follicle). Others are optional (obj to apply to (xform of mesh))
        """
        self.name = name
        self.frontOfChain = frontOfChain # deformer should go at end of chain. . . 
        self.ctrlScale = ctrlScale
        self.autoScale = autoScale
        self.wave = wave
        self.nonDefGeo = nonDefGeo

        self.parent = parent
        self.obj = obj
        self.initPos = None
        self.onSurface = False

        self.gather_info()


    def gather_info(self):
        if self.obj:
            if rig.type_check(self.obj, "mesh"):
                self.initPos = cmds.xform(self.obj, q=True, ws=True, rp=True)
            else:
                cmds.warning("Select only one polygon or verts from one polygon")
                return()

        if not self.obj:
            sel = cmds.ls(sl=True, fl=True)

            if sel:
                # check if using verts or the xform
                verts = cmds.filterExpand(sm=31)
                if verts:
                    # make sure vtx's just from one object
                    objList = [v.split(".")[0] for v in verts]
                    if len(set(objList))>1:
                        cmds.warning("need to select verts from only one object")
                        return()
                    self.initPos = rig.average_point_positions(verts)
                    self.obj = objList[0]
                    self.onSurface = True
                else:
                    if len(sel)>1:
                        cmds.warning("Select only one transform or verts from one transform")
                        return()
                    obj = sel[0]
                    if rig.type_check(obj, "mesh"):
                        self.initPos = cmds.xform(obj, q=True, ws=True, rp=True)
                        self.obj = obj
                    else:
                        cmds.warning("SoftModRig.gather_info: had an issue with your selection. Select only one polygon or verts from one polygon")
                        return()
            else:
                cmds.warning("Select only one polygon or verts from one polygon")
                return()

        self.create_soft_mod_rig()


    def create_soft_mod_rig(self):
        """
        create softmod rig on obj at initPosition, if self.onSurface: align to surface of obj
        """
        pos = (0, 0, 0)
        rot = (0, 0, 0)
        if self.onSurface:
            # get surface pos and rot
            pos = rig.closest_point_on_mesh_position(self.initPos, self.obj)
            rot = rig.closest_point_on_mesh_rotation(self.initPos, self.obj)

        # create controls
        self.baseGrp, self.baseCtrl, self.moveGrp, self.moveCtrl = self.create_controls(self.name)
        cmds.xform(self.baseGrp, ws=True, t=pos)
        cmds.xform(self.baseGrp, ws=True, ro=rot)

        # create softmod
        cmds.select(self.obj, r=True)
        self.softList = cmds.softMod(relative=False, falloffCenter=self.initPos, falloffRadius=5.0, n="{0}_softMod".format(self.name), frontOfChain=self.frontOfChain, weightedNode = [self.moveCtrl, self.moveCtrl])

        # link controls to softmod
        self.connect_ctrls_to_softmod()

        cmds.parent(self.baseGrp, self.parent)

        if self.autoScale:
            self.autosize_controls()

#---------------- need to neutralize the transforms on the geometry node.
        rig.scale_nurbs_control(self.moveCtrl, self.ctrlScale, self.ctrlScale, self.ctrlScale)
        rig.scale_nurbs_control(self.baseCtrl, self.ctrlScale, self.ctrlScale, self.ctrlScale)

        if self.wave:
            self.add_wave_to_softmod()

    def connect_ctrls_to_softmod(self):
        cmds.addAttr(self.moveCtrl, ln="__XTRA__", at="enum", k=True)
        cmds.setAttr("{0}.__XTRA__".format(self.moveCtrl), l=True)
        cmds.addAttr(self.moveCtrl, ln="envelope", at="float", k=True, min=0, max=1, dv=1)
        cmds.addAttr(self.moveCtrl, ln="falloffRadius", at="float", k=True, min=0, dv=3.0)
        cmds.addAttr(self.moveCtrl, ln="mode", at="enum", enumName= "volume=0:surface=1", k=True)

        dm = cmds.shadingNode("decomposeMatrix", asUtility=True, name="{0}_dm".format(self.name))
        mm = cmds.shadingNode("multMatrix", asUtility=True, name="{0}_mm".format(self.name))
        falloffMult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_falloffMult".format(self.name))
        cmds.connectAttr("{0}.outputScale".format(dm), "{0}.input1".format(falloffMult))
        cmds.connectAttr("{0}.falloffRadius".format(self.moveCtrl), "{0}.input2.input2X".format(falloffMult))
        cmds.connectAttr("{0}.output.outputX".format(falloffMult), "{0}.falloffRadius".format(self.softList[0]), f=True)
        cmds.connectAttr("{0}.worldMatrix[0]".format(self.baseCtrl), "{0}.inputMatrix".format(dm))
        cmds.connectAttr("{0}.worldInverseMatrix[0]".format(self.baseCtrl), "{0}.postMatrix".format(self.softList[0]))
        cmds.connectAttr("{0}.worldMatrix[0]".format(self.baseCtrl), "{0}.preMatrix".format(self.softList[0]))
        cmds.connectAttr("{0}.worldMatrix[0]".format(self.moveCtrl), "{0}.matrixIn[0]".format(mm))
        cmds.connectAttr("{0}.parentInverseMatrix[0]".format(self.moveCtrl), "{0}.matrixIn[1]".format(mm))
        cmds.connectAttr("{0}.matrixSum".format(mm), "{0}.weightedMatrix".format(self.softList[0]))
        cmds.connectAttr("{0}.outputTranslate".format(dm), "{0}.falloffCenter".format(self.softList[0]))

        cmds.connectAttr("{0}.envelope".format(self.moveCtrl), "{0}.envelope".format(self.softList[0]), f=True)
        cmds.connectAttr("{0}.mode".format(self.moveCtrl), "{0}.falloffMode".format(self.softList[0]), f=True)
#---------------- here I need to get the actual connection index?        
        if self.nonDefGeo:
            cmds.connectAttr("{0}.worldMatrix[0]".format(self.obj), "{0}.geomMatrix[0]".format(self.softList[0]))


    def create_controls(self, name):
        # size here
        baseCtrl = rig.create_control("{0}_base".format(name), type="cube", color="green")
        baseGrp = rig.group_freeze(baseCtrl)
        moveCtrl = rig.create_control("{0}_move".format(name), type="sphere", color="red")
        moveGrp = rig.group_freeze(moveCtrl)
        cmds.parent(moveGrp, baseCtrl)

        return(baseGrp, baseCtrl, moveGrp, moveCtrl)


    def add_wave_to_softmod(self):
        positions = [0.0, 0.3, 0.6, 0.9, 0.95]
        values = [1.0, -0.3, 0.1, -0.05, 0.01]
        for i in range(len(positions)):
            cmds.setAttr("{0}.falloffCurve[{1}].falloffCurve_Position".format(self.softList[0], i), positions[i])
            cmds.setAttr("{0}.falloffCurve[{1}].falloffCurve_FloatValue".format(self.softList[0], i), values[i])
            cmds.setAttr("{0}.falloffCurve[{1}].falloffCurve_Interp".format(self.softList[0], i), 2)

        cmds.addAttr(self.moveCtrl, ln="WaveAttrs", at="enum", k=True)
        cmds.setAttr("{0}.WaveAttrs".format(self.moveCtrl), l=True)

        # expose these on the control
        for j in range(5):
            cmds.addAttr(self.moveCtrl, ln="position{0}".format(j), at="float", min=0.0, max=1.0, dv=positions[j], k=True)
            cmds.connectAttr("{0}.position{1}".format(self.moveCtrl, j),
                             "{0}.falloffCurve[{1}].falloffCurve_Position".format(self.softList[0], j))

        for j in range(5):
            cmds.addAttr(self.moveCtrl, ln="value{0}".format(j), at="float", min=-1.0, max=1.0, dv=values[j], k=True)
            cmds.connectAttr("{0}.value{1}".format(self.moveCtrl, j),
                             "{0}.falloffCurve[{1}].falloffCurve_FloatValue".format(self.softList[0], j))
            cmds.setAttr("{0}.position{1}".format(self.moveCtrl, j), l=True)
            cmds.setAttr("{0}.value{1}".format(self.moveCtrl, j), l=True)


    def autosize_controls(self):
        calsz = rig.calibrate_size(self.obj, .15)
        if calsz:
            rig.scale_nurbs_control(self.moveCtrl, calsz, calsz, calsz)
            rig.scale_nurbs_control(self.baseCtrl, calsz, calsz, calsz)
            cmds.setAttr("{0}.falloffRadius".format(self.moveCtrl), 2*calsz)
        else:
            cmds.warning("I had an issue getting the calibrated scale of {0}".format(self.obj))


def softDeformer():
    """Use this to start the script!"""
    sd = SoftDeformerUI()
