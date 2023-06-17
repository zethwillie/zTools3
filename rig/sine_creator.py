import maya.cmds as cmds
from functools import partial


class SineCreatorUI(object):

    def __init__(self):
        self.sine_creator_ui()

    def sine_creator_ui(self):
        if cmds.window("sineWin", exists=True):
            cmds.deleteUI("sineWin", window=True)
            cmds.windowPref("sineWin", remove=True)

        self.win = cmds.window("sineWin", widthHeight=(400, 200))

        cl = cmds.columnLayout()
        cmds.text(l="DriveAttr = obj.attr that drives sine")
        cmds.text(l="TgtAttr = obj.attr we're attaching result to")
        cmds.text(l="Prefix = what we're calling the attrs on ctrl obj")
        cmds.separator(h=10)

        rcl = cmds.rowColumnLayout(numberOfColumns=2, cw=([1, 60], [2, 200]), cal=([1, "left"], [2, "left"]))
        cmds.text(l="Prefix:")
        self.prefixTF = cmds.textField()
        cmds.setParent(cl)

        # ctrl obj
        self.ctrlTFBG = cmds.textFieldButtonGrp(l="Sine Driver:", cal=([1, "left"], [2, "left"], [3, "left"]), cw=([1, 60], [2, 300]), bl="SEL", bc=partial(self.set_selected_obj_attr, "ctrl"))
        # target object
        self.targetObjTFBG = cmds.textFieldButtonGrp(l="Target Attr:", cal=([1, "left"], [2, "left"], [3, "left"]), cw=([1, 60], [2, 300]), bl="SEL", bc=partial(self.set_selected_obj_attr, "target"))

        cmds.separator(h=10)
        button = cmds.button(l="Create Sine Nodes", c=self.execute_sine_nodes, h=40, w=380, bgc=(.5, .7, .5))

        cmds.showWindow(self.win)

    def set_selected_obj_attr(self, ui, *args):
        objattr = self.get_selected_obj_attr()
        if not objattr:
            cmds.warning("Couldn't find resulting obj - attribute")
            return()
        if ui == "ctrl":
            cmds.textFieldButtonGrp(self.ctrlTFBG, e=True, tx=objattr)
        if ui == "target":
            cmds.textFieldButtonGrp(self.targetObjTFBG, e=True, tx=objattr)

    def get_selected_obj_attr(self):
        sel = cmds.ls(sl=True)
        if not sel:
            cmds.warning("No obj selected!")
            return
        obj = sel[0]
        cb = cmds.channelBox('mainChannelBox', q=True, mainObjectList=True)
        if not cb:
            cmds.warning("Couldn't find main channel box")
            return()

        attr = cmds.channelBox('mainChannelBox', q=True, selectedMainAttributes=True)
        if not attr:
            cmds.warning("No attribute selected in channel box!")
            return()
        if len(attr) > 1:
            cmds.warning("Only one attr to connect to should be selected!")
            return()
        return("{0}.{1}".format(sel[0], attr[0]))

    def execute_sine_nodes(self, *args):
        prefix = cmds.textField(self.prefixTF, q=True, tx=True)
        ctrlAttr = cmds.textFieldButtonGrp(self.ctrlTFBG, q=True, tx=True)
        tgtAttr = cmds.textFieldButtonGrp(self.targetObjTFBG, q=True, tx=True)

        # check for values
        # get values
        create_sine_nodes(prefix, ctrlAttr, tgtAttr)


# obj - phaseAdd - freqMult - (unit conv 0.017) - eulerToQuat - ampMult - envMult - targetObj
def create_sine_nodes(prefix, ctrlAttr, tgtAttr, globalamp=True, globalfreq=True, globalenv=True, globaldrag=True):
    if not cmds.pluginInfo("quatNodes", loaded=True, q=True):
        cmds.loadPlugin("quatNodes", qt=False)
    # create the "time" drive attr on the ctrl obj
    create_control_attrs(ctrlAttr, prefix, globalamp, globalfreq, globalenv, globaldrag)
    ctrlObj = ctrlAttr.split(".")[0]
    dadl = cmds.createNode("addDoubleLinear", name=prefix + "_drag_adl")
    cmds.connectAttr("{0}".format(ctrlAttr), "{0}.input1".format(dadl))
    cmds.connectAttr("{0}.{1}".format(ctrlObj, "{0}_drag".format(prefix)), "{0}.input2".format(dadl))

    fmdl = cmds.createNode("multDoubleLinear", name=prefix + "_freq_mdl")
    cmds.connectAttr("{0}.output".format(dadl), "{0}.input1".format(fmdl))
    cmds.connectAttr("{0}.{1}".format(ctrlObj, "{0}_freq".format(prefix)), "{0}.input2".format(fmdl))

    mdl2 = cmds.createNode("multDoubleLinear", name=prefix + "_multby2")
    cmds.connectAttr("{0}.output".format(fmdl), "{0}.input1".format(mdl2))
    cmds.setAttr("{0}.input2".format(mdl2), 2)

    etq = cmds.createNode("eulerToQuat", name=prefix + "_etq")
    cmds.connectAttr("{0}.output".format(mdl2), "{0}.inputRotateX".format(etq))

    amdl = cmds.createNode("multDoubleLinear", name=prefix + "_amp_mdl")
    cmds.connectAttr("{0}.outputQuat.outputQuatX".format(etq), "{0}.input1".format(amdl))
    cmds.connectAttr("{0}.{1}".format(ctrlObj, "{0}_amp".format(prefix)), "{0}.input2".format(amdl))

    emdl = cmds.createNode("multDoubleLinear", name=prefix + "_env_mdl")
    cmds.connectAttr("{0}.output".format(amdl), "{0}.input1".format(emdl))
    cmds.connectAttr("{0}.{1}".format(ctrlObj, "{0}_envelope".format(prefix)), "{0}.input2".format(emdl))

    if tgtAttr:
        cmds.connectAttr("{0}.output".format(emdl), "{0}".format(tgtAttr))

    # add in global overrides
    if globalfreq:
        gfmdl = cmds.createNode("multDoubleLinear", name="{0}_global_freq_mdl".format(prefix))
        cmds.connectAttr("{0}.global_speed".format(ctrlObj), "{0}.input1".format(gfmdl))
        cmds.connectAttr("{0}.{1}".format(ctrlObj, "{0}_freq".format(prefix)), "{0}.input2".format(gfmdl))
        cmds.connectAttr("{0}.output".format(gfmdl), "{0}.input2".format(fmdl), force=True)

    if globalamp:
        gamdl = cmds.createNode("multDoubleLinear", name="{0}_global_amp_mdl".format(prefix))
        cmds.connectAttr("{0}.global_amp".format(ctrlObj), "{0}.input1".format(gamdl))
        cmds.connectAttr("{0}.{1}".format(ctrlObj, "{0}_amp".format(prefix)), "{0}.input2".format(gamdl))
        cmds.connectAttr("{0}.output".format(gamdl), "{0}.input2".format(amdl), force=True)

    if globalenv:
        gemdl = cmds.createNode("multDoubleLinear", name=prefix + "_global_env_mdl")
        cmds.connectAttr("{0}.global_envelope".format(ctrlObj), "{0}.input1".format(gemdl))
        cmds.connectAttr("{0}.{1}".format(ctrlObj, "{0}_envelope".format(prefix)), "{0}.input2".format(gemdl))
        cmds.connectAttr("{0}.output".format(gemdl), "{0}.input2".format(emdl), force=True)

    if globaldrag:
        gdmdl = cmds.createNode("multDoubleLinear", name=prefix + "_global_drag_mdl")
        cmds.connectAttr("{0}.global_drag".format(ctrlObj), "{0}.input1".format(gdmdl))
        cmds.connectAttr("{0}.{1}_global_drag_mult".format(ctrlObj, prefix), "{0}.input2".format(gdmdl))

        gdadl = cmds.createNode("addDoubleLinear", name=prefix + "_global_drag_adl")
        cmds.connectAttr("{0}.output".format(gdmdl), "{0}.input1".format(gdadl))
        cmds.connectAttr("{0}.{1}".format(ctrlObj, "{0}_drag".format(prefix)), "{0}.input2".format(gdadl))
        cmds.connectAttr("{0}.output".format(gdadl), "{0}.input2".format(dadl), force=True)


def create_control_attrs(ctrlAttr, prefix, amp, freq, env, drag):
    """
    create the attrs on the control obj.
    ctrlAttr (string): the obj.attr that drives the sine nodes
    prefix (string): what is the prefix on the all the attrs we're making (ie. "tail2" --> obj.tail2_phase)
    amp (bool): is there a global amp attr
    freq (bool): is there a global freq attr
    env (bool): is there a global envelope attr
    drag (bool): do we set up a global drag attr (and a mult attr on tgt)
    """
    ctrlObj, driveAttr = ctrlAttr.split(".")
    if not cmds.attributeQuery(driveAttr, node=ctrlObj, exists=True):
        cmds.addAttr(ctrlObj, ln=driveAttr, at="float", dv=0, k=True)
    if amp:
        if not cmds.attributeQuery("global_amp", node=ctrlObj, exists=True):
            cmds.addAttr(ctrlObj, ln="global_amp", at="float", dv=1, k=True)
    if freq:
        if not cmds.attributeQuery("global_speed", node=ctrlObj, exists=True):
            cmds.addAttr(ctrlObj, ln="global_speed", at="float", dv=1, k=True)

    if drag:
        if not cmds.attributeQuery("global_drag", node=ctrlObj, exists=True):
            cmds.addAttr(ctrlObj, ln="global_drag", at="float", dv=0, k=True)

    if env:
        if not cmds.attributeQuery("global_envelope", node=ctrlObj, exists=True):
            cmds.addAttr(ctrlObj, ln="global_envelope", at="float", min=0, max=1, dv=1, k=True)

    if not cmds.attributeQuery("__{0}_ctrls__".format(prefix), node=ctrlObj, exists=True):
        cmds.addAttr(ctrlObj, ln="__{0}_ctrls__".format(prefix), at="enum", en="-----", k=True)
        cmds.setAttr("{0}.{1}".format(ctrlObj, "__{0}_ctrls__".format(prefix)), l=True)

    atts = ["{0}_{1}".format(prefix, x) for x in ["amp", "freq", "drag", "global_drag_mult", "envelope"]]
    for att in atts:
        if not cmds.attributeQuery(att, node=ctrlObj, exists=True):
            if att == "{0}_drag".format(prefix):
                cmds.addAttr(ctrlObj, ln="{0}_drag".format(prefix), at="short", dv=0, k=True)
            elif att == "{0}_envelope".format(prefix):
                cmds.addAttr(ctrlObj, ln="{0}_envelope".format(prefix), at="float", min=0, max=1, dv=1, k=True)
            elif att == "{0}_global_drag_mult".format(prefix):
                if drag:
                    cmds.addAttr(ctrlObj, ln="{0}_global_drag_mult".format(prefix), at="float", min=0, dv=1, k=True)
            else:
                cmds.addAttr(ctrlObj, ln="{0}".format(att), at="float", dv=1, k=True)


def sine_creator():
    x = SineCreatorUI()
