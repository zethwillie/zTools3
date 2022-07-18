########################
# file: zbw_attributes.py
# Author: zeth willie
# Contact: zeth@catbuks.com, www.williework.blogspot.com
# Date Modified: 01/27/17
# To Use: type in python window  "import zbw_attributes as att; att.attributes()"
# Notes/Descriptions: Some basic functions for manipulating channels, attrs and connections
########################

import maya.cmds as cmds
from functools import partial
import maya.mel as mel

# to do . . .
# ----------------add "breakConnections"? disconnect and if they're anim curves delete them.

widgets = {}
colors = {}
colors["red"] = 13
colors["blue"] = 6
colors["green"] = 14
colors["darkRed"] = 4
colors["lightRed"] = 31
colors["darkBlue"] = 5
colors["medBlue"] = 15
colors["lightBlue"] = 18
colors["royalBlue"] = 29
colors["darkGreen"] = 7
colors["medGreen"] = 27
colors["lightGreen"] = 19
colors["yellowGreen"] = 26
colors["yellow"] = 17
colors["darkYellow"] = 21
colors["lightYellow"] = 22
colors["purple"] = 30
colors["lightPurple"] = 9
colors["darkPurple"] = 8
colors["black"] = 1
colors["white"] = 16
colors["brown"] = 10
colors["darkBrown"] = 11
colors["lightBrown"] = 24
colors["pink"] = 20
colors["orange"] = 12


def attrUI(*args):
    """
    UI for the script
    """

    if cmds.window("attrWin", exists=True):
        cmds.deleteUI("attrWin")

    widgets["win"] = cmds.window("attrWin", t="zbw_attributes", h=450, w=250, s=True, rtf=True)
    widgets["tabLO"] = cmds.tabLayout(h=300)
    widgets["channelColLO"] = cmds.columnLayout("Object/Attr Controls", w=250, bgc=(.8, .8, .8))

    widgets["lockFrLO"] = cmds.frameLayout(l="Lock/Hide", cll=True, w=250, bgc=(.7, .6, .6))
    widgets["lockColLO"] = cmds.columnLayout(bgc=(.8, .8, .8))
    # lock and hide controls

    # switch to Row column layout to break up the channels
    widgets["attrRCLO"] = cmds.rowColumnLayout(nc=2, cw=([1, 100], [2, 150]))
    widgets["transCB"] = cmds.checkBox(l="Translates", v=0, cc=partial(enable_channel, "transCB", "translateCBG"))
    widgets["translateCBG"] = cmds.checkBoxGrp(w=150, cw3=(50, 50, 50), ncb=3, l1="TX", l2="TY", l3="TZ", l4="Vis",
                                               va3=(0, 0, 0), bgc=(.5, .5, .5), en=False)
    widgets["rotCB"] = cmds.checkBox(l="Rotates", v=0, cc=partial(enable_channel, "rotCB", "rotateCBG"))
    widgets["rotateCBG"] = cmds.checkBoxGrp(w=150, cw3=(50, 50, 50), ncb=3, l1="RX", l2="RY", l3="RZ", l4="Vis",
                                            va3=(0, 0, 0), bgc=(.5, .5, .5), en=False)
    widgets["scaleCB"] = cmds.checkBox(l="Scales", v=1, cc=partial(enable_channel, "scaleCB", "scaleCBG"))
    widgets["scaleCBG"] = cmds.checkBoxGrp(w=150, cw3=(50, 50, 50), ncb=3, l1="SX", l2="SY", l3="SZ", l4="Vis",
                                           va3=(1, 1, 1), bgc=(.5, .5, .5), en=True)
    widgets["visCB"] = cmds.checkBox(l="Visibility", v=1)

    # back to frame layout
    cmds.setParent(widgets["lockFrLO"])
    widgets["topOneCLO"] = cmds.columnLayout()
    cmds.separator(h=5, st="none")
    widgets["lockRBG"] = cmds.radioButtonGrp(nrb=2, l1="Unlock", l2="Lock", sl=2)
    widgets["hideRBG"] = cmds.radioButtonGrp(nrb=2, l1="Show", l2="Hide", sl=2)
    widgets["channelsBut"] = cmds.button(l="Lock/Hide Channels", w=250, h=30, bgc=(.5, .5, .5), rs=True,
                                         c=channel_lock_hide)
    cmds.separator(h=5, st="none")

    cmds.separator(h=5, st="none")
    widgets["channelsBut"] = cmds.button(l="Move Selected Attr Up", w=250, h=30, bgc=(.5, .7, .5), rs=True,
                                         c=partial(shift_attr, 1))
    widgets["channelsBut"] = cmds.button(l="Move Selected Attr Down", w=250, h=30, bgc=(.7, .5, .5), rs=True,
                                         c=partial(shift_attr, 0))
    cmds.separator(h=5, st="none")

    cmds.setParent(widgets["channelColLO"])
    widgets["addAttrFrLO"] = cmds.frameLayout(l="Add Attrs", cll=True, w=250, bgc=(.7, .6, .6))
    widgets["addAttrLockCLO"] = cmds.columnLayout()
    widgets["lockAttrTFBG"] = cmds.textFieldButtonGrp(l="Locked Attr", tx="__xtraAttrs__", bl="Create",
                                                      cal=[(1, "left"), (2, "left"), (3, "left")], cw3=[60, 135, 50],
                                                      bc=locked_attr)

    cmds.text("Add an attribute with a range of 0-1. . . ")
    cmds.separator(h=5)
    widgets["newAttrTFG"] = cmds.textFieldGrp(l="Attr Name:", w=250, cal=(1, "left"), cw=[(1, 55), (2,185)])
    cmds.setParent(widgets["addAttrFrLO"])
    widgets["addAttrRCLO"] = cmds.rowColumnLayout(nc = 2, cs = [(1, 0), (2,5)])
    widgets["addIntBut"] = cmds.button(l="Add 0-1 Int Attr", w= 120, h=30, bgc = (.5, .5, .5), c= partial(
        add_zero_one_attribute, "short"))
    widgets["addFltBut"] = cmds.button(l="Add 0-1 Float Attr", w= 120, h=30, bgc = (.5, .5, .5), c=partial(
        add_zero_one_attribute, "float"))

    # back to columnLayout
    cmds.setParent(widgets["channelColLO"])
    widgets["colorFrLO"] = cmds.frameLayout(l="Object Color", cll=True, w=250, bgc=(.7, .6, .6))
    widgets["colorRCLO"] = cmds.rowColumnLayout(nr=4, bgc=(.8, .8, .8))

    # color controls (red, green, blue, yellow, other)
    cmds.canvas(w=50, h=20, rgb=(1, 0, 0), pc=partial(change_color, colors["red"]))
    cmds.canvas(w=50, h=20, rgb=(.5, .1, .1), pc=partial(change_color, colors["darkRed"]))
    cmds.canvas(w=50, h=20, rgb=(.659, .275, .449), pc=partial(change_color, colors["lightRed"]))
    cmds.canvas(w=50, h=20, rgb=(1, .8, .965), pc=partial(change_color, colors["pink"]))

    cmds.canvas(w=50, h=20, rgb=(0, 1, 0), pc=partial(change_color, colors["green"]))
    cmds.canvas(w=50, h=20, rgb=(0, .35, 0), pc=partial(change_color, colors["darkGreen"]))
    cmds.canvas(w=50, h=20, rgb=(0, .55, .335), pc=partial(change_color, colors["medGreen"]))
    cmds.canvas(w=50, h=20, rgb=(.35, .635, .15), pc=partial(change_color, colors["yellowGreen"]))

    cmds.canvas(w=50, h=20, rgb=(0, 0, 1), pc=partial(change_color, colors["blue"]))
    cmds.canvas(w=50, h=20, rgb=(0, 0, .35), pc=partial(change_color, colors["darkBlue"]))
    cmds.canvas(w=50, h=20, rgb=(0, .2, .6), pc=partial(change_color, colors["medBlue"]))
    cmds.canvas(w=50, h=20, rgb=(.65, .8, 1), pc=partial(change_color, colors["lightBlue"]))

    cmds.canvas(w=50, h=20, rgb=(1, 1, 0), pc=partial(change_color, colors["yellow"]))
    cmds.canvas(w=50, h=20, rgb=(.225, .1, 0), pc=partial(change_color, colors["darkBrown"]))
    cmds.canvas(w=50, h=20, rgb=(.5, .275, 0), pc=partial(change_color, colors["brown"]))
    cmds.canvas(w=50, h=20, rgb=(.922, .707, .526), pc=partial(change_color, colors["darkYellow"]))

    cmds.canvas(w=50, h=20, rgb=(.33, 0, .33), pc=partial(change_color, colors["purple"]))
    cmds.canvas(w=50, h=20, rgb=(.2, 0, .25), pc=partial(change_color, colors["darkPurple"]))
    cmds.canvas(w=50, h=20, rgb=(.0, 0, .0), pc=partial(change_color, colors["black"]))
    cmds.canvas(w=50, h=20, rgb=(1, 1, 1), pc=partial(change_color, colors["white"]))

    cmds.setParent(widgets["tabLO"])
    widgets["connectColLO"] = cmds.columnLayout("Connections", w=250, bgc=(.8, .8, .8))
    widgets["connectFrame"] = cmds.frameLayout(l="Make General Connections", cll=True, bgc=(.6, .8, .6))
    widgets["connectionColLO"] = cmds.columnLayout(bgc=(.8, .8, .8))

    # connection stuff
    cmds.text("Select a source object and a channel:")
    cmds.rowColumnLayout(nc=2, cw=[60, 190])
    cmds.button(l="Connector", bgc=(.8, .8, .8), w=60, c=partial(select_tfbg_obj, "connector", True))
    widgets["connector"] = cmds.textFieldButtonGrp(l="", w=180, bl="<<<", cal=[(1, "left"), (2, "left"), (3, "left")], cw3=[1, 140, 30], bc=partial(get_selected_channel, "connector"))
    cmds.setParent(widgets["connectionColLO"])
    cmds.separator(h=3, st="none")
    cmds.text("Select a target object(s)'s channel:")
    widgets["connectee"] = cmds.textFieldButtonGrp(l="Connectee", w=250, bl="<<<", cal=[(1, "left"), (2, "left"), (3, "left")], cw3=[60, 140, 30], bc=partial(get_selected_channel, "connectee", attrOnly=True))
    cmds.separator(h=3, st="none")
    widgets["connectBut"] = cmds.button(l="Connect Channels", w=240, h=20, bgc=(.5, .5, .5), c=connect_channels)
    cmds.separator(h=3, st="none")

    cmds.setParent(widgets["connectColLO"])
    widgets["shapeFrame"] = cmds.frameLayout(l="Connect to Shape Visibility", cll=True, bgc=(.6, .8, .6))
    widgets["shapeColLO"] = cmds.columnLayout(bgc=(.8, .8, .8))

    widgets["toShapeVis"] = cmds.textFieldButtonGrp(l="Vis Driver", w=250, bl="<<<", cal=[(1, "left"), (2, "left"), (3, "left")], cw3=[60, 140, 30], bc=partial(get_selected_channel, "toShapeVis"))
    cmds.separator(h=5, st="none")
    cmds.text("Now select the objs to drive:")
    widgets["shapeBut"] = cmds.button(l="Connect to Shapes' vis", w=240, h=20, bgc=(.5, .5, .5), c=connectShapeVis)
    cmds.separator(h=5, st="none")

    cmds.setParent(widgets["connectColLO"])
    widgets["inoutFrame"] = cmds.frameLayout(l="Select Connections (and print)", cll=True, bgc=(.6, .8, .6))
    widgets["inOutColLO"] = cmds.columnLayout(bgc=(.8, .8, .8))

    widgets["conversionCB"] = cmds.checkBox(l="Skip 'conversion' nodes?", v=1)
    cmds.text("Select an attribute in the channel box:")
    widgets["getInputBut"] = cmds.button(l="Select inConnection object", w=240, h=20, bgc=(.5, .5, .5), c=getInput)
    cmds.separator(h=3, st="none")
    widgets["getOutputBut"] = cmds.button(l="Select outConnection objects", w=240, h=20, bgc=(.5, .5, .5), c=getOutput)

    cmds.setParent(widgets["connectColLO"])
    widgets["functionFrame"] = cmds.frameLayout(l="Some functions", cll=True, bgc=(.6, .8, .6))
    widgets["inOutColLO"] = cmds.columnLayout(bgc=(.8, .8, .8))
    widgets["hideShapeVisBut"] = cmds.button(l="Toggle selected shape vis", w=240, h=20, bgc=(.5, .5, .5),
                                             c=toggle_sel_shape_vis)
    cmds.separator(h=3, st="none")
    widgets["segSclBut"] = cmds.button(l="toggle JntSegmentScaleComp", w=240, h=20, bgc=(.5, .5, .5), c=JntSegScl)
    cmds.separator(h=3, st="none")
    widgets["inhXformBut"] = cmds.button(l="Toggle inherit transforms", w=240, bgc=(.5, .5, .5),
                                           c=toggle_inherit_transforms)
    cmds.separator(h=3, st="none")
    cmds.text("First sel is source, next are targets:")
    widgets["connectRCL"] = cmds.rowColumnLayout(nc=3, cs=[(1, 0), (2, 5), (3, 5)])
    widgets["cnctTBut"] = cmds.button(l="conn Transl", w=75, h=20, bgc=(.7, .5, .5), c=partial(connect_attrs, "t"))
    widgets["cnctRBut"] = cmds.button(l="conn Rot", w=75, h=20, bgc=(.5, .7, .5), c=partial(connect_attrs, "r"))
    widgets["cnctSBut"] = cmds.button(l="conn Scl", w=75, h=20, bgc=(.5, .5, .7), c=partial(connect_attrs, "s"))
    cmds.setParent(widgets["inOutColLO"])
    cmds.separator(h=3, st="none")
    widgets["xyzCBG"] = cmds.checkBoxGrp(l="Connect Attr: ", ncb=3, la3=("x", "y", "z"), cal=[(1,"left"),(2, "left")], cw=[(1, 100),(2, 40),(3,40), (4,40)], va3=[1, 1, 1])
    cmds.separator(h=3, st="none")
    widgets["trnsfrAttrBut"] = cmds.button(l="Transfer Attributes (tgt, src)", w=240, bgc=(.5, .5, .5), c=transfer_attrs)

    # show window
    cmds.showWindow(widgets["win"])
    cmds.window(widgets["win"], e=True, w=250, h=400, rtf=True)


def get_source_and_targets(*args):
    """
    checks current selection, first sel is source, remaining are targets
    args:
        None
    Return:
        list (string, list): [0] is the source, [1] is the list of targets
        or 
        None
    """
    sel = cmds.ls(sl=True)
    if sel and len(sel) > 1:
        src = sel[0]
        tgts = sel[1:]
        return (src, tgts)
    else:
        cmds.warning("You need to select at least two objects!")
        return (None, None)


def connect_param(src, tgt, attrType, prm, force=False, *args):
    """
    connects the indiv chnls based on the checkbox sorting in connect_attrs
    args:
        src (string): source object
        tgt (string): target object
        attrType (string): attr short name (t, r, s)
        prm (string): specific channel name (x, y, z)
        force (bool): value for force flag. Defaults to False
    return:
        None
    """
    try:
        cmds.connectAttr("{0}.{1}{2}".format(src, attrType, prm), "{0}.{1}{2}".format(tgt, attrType, prm), force=force)
    except:
        cmds.warning(
            "there was an issue connecting to {0}{1} of {2}. Make sure the channels are free!".format(attrType, prm,
                                                                                                      tgt))

def connect_attrs(attrType=None, force = False, *args):
    """attrType is 't', 'r', 's'."""
    src, tgts = get_source_and_targets()
    x, y, z = cmds.checkBoxGrp(widgets["xyzCBG"], q=True, va3=True)
    if src:
        for tgt in tgts:
            if x:
                connect_param(src, tgt, attrType, "x", False)
            if y:
                connect_param(src, tgt, attrType, "y", False)
            if z:
                connect_param(src, tgt, attrType, "z", False)


def get_channel_attributes(obj, chnl):
    """
    gets and returns attributes of given channel on given object
    """
    attrType = cmds.attributeQuery(chnl, node=obj, at=True)
    hasMin = cmds.attributeQuery(chnl, node=obj, mne=True)
    hasMin = cmds.attributeQuery(chnl, node=obj, mne=True)
    hasMax = cmds.attributeQuery(chnl, node=obj, mxe=True)
    attrMin = None
    if hasMin:
        attrMin = cmds.attributeQuery(chnl, node=obj, min=True)
    attrMax = None
    if hasMax:
        attrMax = cmds.attributeQuery(chnl, node=obj, max=True)
    value = cmds.getAttr("{0}.{1}".format(obj, chnl))
    inConnection = cmds.listConnections("{0}.{1}".format(obj, chnl), plugs=True, destination=False, source=True)
    outConnection = cmds.listConnections("{0}.{1}".format(obj, chnl), plugs=True, destination=True, source=False)
    locked = cmds.getAttr("{0}.{1}".format(obj, chnl), lock=True)

    return (attrType, hasMin, attrMin, hasMax, attrMax, value, inConnection, outConnection, locked)


def transfer_attrs(*args):
    """
    transfers attrs and connections from second obj to first object selected 
    """
    tgt, src = get_source_and_targets()
    if not tgt or len(src) > 1:
        cmds.warning("Select only one target then one source obj to transfer the attributes and connections!")
        return ()

    attrs = cmds.channelBox('mainChannelBox', q=True, selectedMainAttributes=True)
    if not attrs:
        cmds.warning("You have to select at least one attr on last object selected to transfer!")
        return ()
    for attr in attrs:
        attrType, hasMin, attrMin, hasMax, attrMax, value, inConnection, outConnection, locked = get_channel_attributes(
            src[0], attr)
        if not attrType == "enum":
            # create attribute
            if not cmds.attributeQuery(attr, node=tgt, exists=True):
                if hasMin and not hasMax:
                    cmds.addAttr(tgt, ln=attr, at=attrType, min=attrMin[0], dv=value, k=True)
                elif hasMax and not hasMin:
                    cmds.addAttr(tgt, ln=attr, at=attrType, max=attrMax[0], dv=value, k=True)
                elif hasMin and hasMax:
                    cmds.addAttr(tgt, ln=attr, at=attrType, min=attrMin[0], max=attrMax[0], dv=value, k=True)
                else:
                    cmds.addAttr(tgt, ln=attr, at=attrType, dv=value, k=True)
            else:
                cmds.warning("The attribute: {0} already exists. Skipping creation!".format(attr))
            # lock
            if locked:
                cmds.setAttr("{0}.{1}".format(tgt, attr), l=True)
        else:
            cmds.warning("I don't do enums at the moment!")

        # connect tgt attr to connection, forced
        if inConnection:
            cmds.connectAttr(inConnection[0], "{0}.{1}".format(tgt, attr))
        if outConnection:
            for conn in outConnection:
                cmds.connectAttr("{0}.{1}".format(tgt, attr), conn, force=True)


def enable_channel(source, target, *args):
    """
    This function enables or disables the indiv channel checkboxes when attr is toggled
    Args:
        source - widgets key for checkbox grp that switches the targets checkbox grps
        target - the target checkbox grp to have values toggled
    """

    CBG = widgets[target]
    on = cmds.checkBox(widgets[source], q=True, v=True)
    if on:
        cmds.checkBoxGrp(CBG, e=True, en=True, va3=(1, 1, 1))
    else:
        cmds.checkBoxGrp(CBG, e=True, en=False, va3=(0, 0, 0))


def channel_lock_hide(*args):
    """
    this is the function to actually do the locking and hiding of the attrs selected in the UI
    """

    sel = cmds.ls(sl=True, type="transform")
    if sel:
        channels = []
        tx = cmds.checkBoxGrp(widgets["translateCBG"], q=True, v1=True)
        ty = cmds.checkBoxGrp(widgets["translateCBG"], q=True, v2=True)
        tz = cmds.checkBoxGrp(widgets["translateCBG"], q=True, v3=True)

        rx = cmds.checkBoxGrp(widgets["rotateCBG"], q=True, v1=True)
        ry = cmds.checkBoxGrp(widgets["rotateCBG"], q=True, v2=True)
        rz = cmds.checkBoxGrp(widgets["rotateCBG"], q=True, v3=True)

        sx = cmds.checkBoxGrp(widgets["scaleCBG"], q=True, v1=True)
        sy = cmds.checkBoxGrp(widgets["scaleCBG"], q=True, v2=True)
        sz = cmds.checkBoxGrp(widgets["scaleCBG"], q=True, v3=True)

        v = cmds.checkBox(widgets["visCB"], q=True, v=True)

        lock = cmds.radioButtonGrp(widgets["lockRBG"], q=True, sl=True)
        key = cmds.radioButtonGrp(widgets["hideRBG"], q=True, sl=True)

        if lock == 1:
            lock = 0
        elif lock == 2:
            lock = 1
        if key == 1:
            key = 1
        elif key == 2:
            key = 0

        attrs = {"tx": tx, "ty": ty, "tz": tz, "rx": rx, "ry": ry, "rz": rz, "sx": sx, "sy": sy, "sz": sz, "v": v}
        for attr in attrs:
            if attrs[attr]:
                channels.append("%s" % attr)

        for obj in sel:
            for channel in channels:
                cmds.setAttr("%s.%s" % (obj, channel), l=lock)
                cmds.setAttr("%s.%s" % (obj, channel), k=key)
    else:
        cmds.warning("You haven't selected anything!")


def locked_attr(*args):
    """
    creates a locked attr (I use as a separator). Uses the long name as the nice name (literal name in channel box)
    """
    attrName = cmds.textFieldButtonGrp(widgets["lockAttrTFBG"], q=True, tx=True)

    if attrName:
        sel = cmds.ls(sl=True)

        if sel:
            for obj in sel:
                try:
                    cmds.addAttr(obj, ln=attrName, nn=attrName, at="enum", en="-----", k=True)
                    cmds.setAttr("%s.%s" % (obj, attrName), l=True)
                except:
                    cmds.warning("Failed to add %s to %s, skipping!" % (attrName, obj))
        else:
            cmds.warning("Please select some objects to add attr to!")
    else:
        cmds.warning("Please enter a name for the attr!")


def add_zero_one_attribute(attrType, *args):
    """
    adds an attribute with range of 0 to 1 to each selected obj
    :param attrType: either "short" or "float"
    :param args:
    :return:
    """
    sel = cmds.ls(sl=True)
    if not sel:
        cmds.warning("You need to select an object add attrs to!")
        return()
    attrName = cmds.textFieldGrp(widgets["newAttrTFG"], q=True, tx=True)
    if not attrName:
        cmds.warning("Please enter a name for the attribute in the field!")
        return()
    for obj in sel:
        try:
            cmds.addAttr(obj, ln=attrName, at=attrType, min=0, max=1, dv=0, k=True)
        except:
            cmds.warning("Couldn't add attr: {0} to object: {1}. Skipping.".format(attrName, obj))


def shift_attr(mode, *args):
    """
    shifts the selected attr up or down
    """

    obj = cmds.channelBox('mainChannelBox', q=True, mainObjectList=True)
    if obj:
        attr = cmds.channelBox('mainChannelBox', q=True, selectedMainAttributes=True)
        if attr:
            for eachObj in obj:
                udAttr = cmds.listAttr(eachObj, ud=True)
                if not attr[0] in udAttr:
                    sys.exit('selected attribute is static and cannot be shifted')
                # temp unlock all user defined attributes
                attrLock = cmds.listAttr(eachObj, ud=True, l=True)
                if attrLock:
                    for alck in attrLock:
                        cmds.setAttr(eachObj + '.' + alck, lock=0)
                # shift down
                if mode == 0:
                    if len(attr) > 1:
                        attr.reverse()
                        sort = attr
                    if len(attr) == 1:
                        sort = attr
                    for i in sort:
                        attrLs = cmds.listAttr(eachObj, ud=True)
                        attrSize = len(attrLs)
                        attrPos = attrLs.index(i)
                        cmds.deleteAttr(eachObj, at=attrLs[attrPos])
                        cmds.undo()
                        for x in range(attrPos + 2, attrSize, 1):
                            cmds.deleteAttr(eachObj, at=attrLs[x])
                            cmds.undo()
                # shift up
                if mode == 1:
                    for i in attr:
                        attrLs = cmds.listAttr(eachObj, ud=True)
                        attrSize = len(attrLs)
                        attrPos = attrLs.index(i)
                        if attrLs[attrPos - 1]:
                            cmds.deleteAttr(eachObj, at=attrLs[attrPos - 1])
                            cmds.undo()
                        for x in range(attrPos + 1, attrSize, 1):
                            cmds.deleteAttr(eachObj, at=attrLs[x])
                            cmds.undo()
                # relock all user defined attributes
                if attrLock:
                    for alck in attrLock:
                        cmds.setAttr(eachObj + '.' + alck, lock=1)


def change_color(color, *args):
    """
    changes the shape node color of the selected objects
    """

    sel = cmds.ls(sl=True, type="transform")
    if sel:
        for obj in sel:
            shapes = cmds.listRelatives(obj, s=True)
            for shape in shapes:
                cmds.setAttr("%s.overrideEnabled" % shape, 1)
                cmds.setAttr("%s.overrideColor" % shape, color)


def toggle_sel_shape_vis(*args):
    """toggles the selected transforms' shape visibility"""
    sel = cmds.ls(sl=True, type="transform")
    if sel:
        for obj in sel:
            shp = cmds.listRelatives(obj, s=True)
            if not shp:
                return ()
            for s in shp:
                currVal = cmds.getAttr("{0}.visibility".format(s))
                newVal = 0
                if currVal == 0:
                    newVal = 1
                elif currVal == 1:
                    newVal = 0
                cmds.setAttr("{0}.visibility".format(s), newVal)


def toggle_inherit_transforms(*args):
    """
    toggles on/off inherit transforms for each selected object
    """
    sel = cmds.ls(sl=True, type="transform")
    for obj in sel:
        curr = cmds.getAttr("{0}.inheritsTransform".format(obj))
        new = not curr
        cmds.setAttr("{0}.inheritsTransform".format(obj), new)



def JntSegScl(*args):
    """turns on/off selected jnts seg scale compensate attr"""

    jnts = cmds.ls(sl=True, type="joint")
    if not jnts:
        cmds.warning("No joints selected!")
        return ()

    for jnt in jnts:
        currVal = cmds.getAttr("{0}.segmentScaleCompensate".format(jnt))
        if currVal == 0:
            newVal = 1
        elif currVal == 1:
            newVal = 0

        cmds.setAttr("{0}.segmentScaleCompensate".format(jnt), newVal)


def breakConnections(*args):
    # disconnectAttr
    pass


def get_selected_channel(tfbg, attrOnly=False, *args):
    """
    gets the selected channel of the selected objects
    tfbg = the key of the widget for the ui (from widgets dict). string
    """

    cBox = mel.eval('$temp=$gChannelBoxName')
    objs = cmds.ls(sl=True, l=True)

    if objs and not attrOnly:
        # replace objs with the first in objs
        if not len(objs) == 1:
            cmds.warning("You have to select ONE node!")
        else:
            objs = [objs[0]]

    if objs:
        # get selected channel
        channels = cmds.channelBox(cBox, q=True, sma=True, ssa=True, sha=True, soa=True)

        if channels:
            if not len(channels) == 1:
                cmds.warning("You have to select ONE channel!")
            else:
                channel = channels[0]
        else:
            cmds.warning("You have to select ONE channel!")

    if attrOnly:
        if objs and channel:
            cmds.textFieldButtonGrp(widgets[tfbg], e=True, tx=channel)
    else:
        if objs and channel:
            full = "{0}.{1}".format(objs[0], channel)
            cmds.textFieldButtonGrp(widgets[tfbg], e=True, tx=full)


def select_tfbg_obj(tfbgKey, split=False, *args):
    """split means split the text on '.' (to get rid of the attr)"""
    tfbg = widgets[tfbgKey]
    obj = cmds.textFieldButtonGrp(tfbg, q=True, tx=True)
    if obj:
        try: 
            if split:
                obj = obj.split(".")[0]
            cmds.select(obj, r=True)
        except:
            cmds.warning("couldn't select: {0}".format(obj))


def connect_channels(*args):
    """connects two channels together from the test fields"""

    sel = cmds.ls(sl=True)
    connector = cmds.textFieldButtonGrp(widgets["connector"], q=True, tx=True)
    connectee = cmds.textFieldButtonGrp(widgets["connectee"], q=True, tx=True)
    for obj in sel:
        try:
            cmds.connectAttr(connector, "{0}.{1}".format(obj, connectee), f=True)
            print(("Connected {0} -----> {1}.{2}".format(connector, obj, connectee)))
        except:
            cmds.warning("Couldn't connect: {0} -----> {1}".format(connector, obj + "." + connectee))


def getInput(*args):
    """ collects the input from the selected obj.channel"""

    obj = ""
    channel = ""
    conv = cmds.checkBox(widgets["conversionCB"], q=True, v=True)

    cBox = mel.eval('$temp=$gChannelBoxName')
    sel = cmds.ls(sl=True, l=True)

    if sel:
        if not len(sel) == 1:
            cmds.warning("You have to select ONE node!")
        else:
            obj = sel[0]
    else:
        cmds.warning("You have to select ONE node!")

    if sel:
        channels = cmds.channelBox(cBox, q=True, sma=True, ssa=True, sha=True, soa=True)

        if channels:
            if not len(channels) == 1:
                cmds.warning("You have to select ONE channel!")
            else:
                channel = channels[0]
        else:
            cmds.warning("You have to select ONE channel!")

    if obj and channel:
        full = "%s.%s" % (obj, channel)
        inAttr = cmds.listConnections(full, plugs=True, scn=conv, d=False, s=True)
        if inAttr:
            for each in inAttr:
                print(("%s -----> %s" % (each, full)))
        else:
            cmds.warning("No input connections on this attr!")
        inNodes = cmds.listConnections(full, scn=conv, d=False, s=True)
        if inNodes:
            cmds.select(cl=True)
            for node in inNodes:
                cmds.select(node, add=True)


def getOutput(*args):
    """ collects the outputs from the selected obj.channel"""

    obj = ""
    channel = ""
    conv = cmds.checkBox(widgets["conversionCB"], q=True, v=True)

    cBox = mel.eval('$temp=$gChannelBoxName')
    sel = cmds.ls(sl=True, l=True)

    if sel:
        if not len(sel) == 1:
            cmds.warning("You have to select ONE node!")
        else:
            obj = sel[0]
    else:
        cmds.warning("You have to select ONE node!")

    if sel:
        channels = cmds.channelBox(cBox, q=True, sma=True, ssa=True, sha=True, soa=True)

        if channels:
            if not len(channels) == 1:
                cmds.warning("You have to select ONE channel!")
            else:
                channel = channels[0]
        else:
            cmds.warning("You have to select ONE channel!")

    if obj and channel:
        full = "%s.%s" % (obj, channel)
        outAttr = cmds.listConnections(full, plugs=True, scn=conv, d=True, s=False)
        if outAttr:
            for each in outAttr:
                print(("%s ----> %s" % (full, each)))
        else:
            cmds.warning("No output connections on this attr!")
        outNodes = cmds.listConnections(full, scn=conv, d=True, s=False)
        if outNodes:
            cmds.select(cl=True)
            for node in outNodes:
                cmds.select(node, add=True)


def connectShapeVis(*args):
    """Connects the attr from the assoc. text field to the shape Visibility of selected objects"""

    sel = cmds.ls(sl=True, type="transform")
    driver = cmds.textFieldButtonGrp(widgets["toShapeVis"], q=True, tx=True)

    if sel:
        if driver:
            for obj in sel:
                shapes = cmds.listRelatives(obj, s=True)
                for shape in shapes:
                    try:
                        cmds.connectAttr(driver, "%s.v" % shape, f=True)
                        cmds.warning("Connected %s to %s" % (driver, shape))
                    except:
                        cmds.warning("Couldn't connect %s to %s. Sorry! Check the Script Editor." % (driver, shape))
    else:
        cmds.warning("You need to select an object to connect the shape.vis!")


def attributes(*args):
    """Use this to start the script!"""
    attrUI()
