########################
#file: zbw_spaceBuffer.py
#Author: zeth willie
#Contact: zethwillie@gmail.com, www.williework.blogspot.com
#Date Modified: 2/1/17
#To Use: type in python window  "import zTools.zbw_spaceBuffer as zspb; reload(zspb); zspb.spaceBuffer()"
#Notes/Descriptions:  used to create a chain a grps that is parent constrained to the original obj/parent hierarchy.
########################

#---------------- give option to include the upper group
#---------------- WHAT AM I DOING WITH THE GROUP ABOVE? ONLY TO ZERO OUT THE THING UNDER? 

#---------------- should I create joint and group at the control?

import maya.cmds as cmds

widgets = {}


def spaceBufferUI(*args):
    if cmds.window("spaceBufferWin", exists=True):
        cmds.deleteUI("spaceBufferWin")

    widgets["win"] = cmds.window("spaceBufferWin", rtf=True, wh=(200, 20))
    widgets["mainCLO"] = cmds.columnLayout(w=200)

    widgets["jntCreateBut"] = cmds.button(l="Create Joint/Grps at Selection!", w=200, h=30, bgc=(.6, .8,.6), c=createJointFromObj)
    widgets["makeBuffer"] = cmds.button(l="Create Space Buffer!", w=200, h=30, bgc=(.4, .6, .8), c=createSpaceBuffers)

    cmds.window(widgets["win"], e=True, wh=(5, 5), rtf=True)
    cmds.showWindow(widgets["win"])


def createJointFromObj(objs = [], *args):
    """
    creates a joint at obj location/orientation. Can be arg[list] or selection
    :param objs: a list of objects to operate on
    :param args:
    :return:
    """
    
    if not objs:
        objs = cmds.ls(sl=True, type="transform")

    if objs:
        for obj in objs:
            pos = cmds.xform(obj, q=True, ws=True, rp=True)
            rot = cmds.xform(obj, q=True, ws=True, ro=True)

            jnt = cmds.joint(name="{0}_JNT".format(obj))
            grp = cmds.group(jnt, n="{0}_JNT_GRP".format(obj))
            
            if cmds.listRelatives(grp, p=True):
                cmds.parent(grp, w=True)
            
            cmds.xform(grp, ws=True, t=pos)
            cmds.xform(grp, ws=True, ro=rot)
    else:
        cmds.warning("You need to select object(s)")


def createSpaceBuffers(*args):
    """
    selection 1,2 = source parent, source obj
    selection 3 = target obj

    create two groups parented - named after source p,o
    snap them to source obj
    parentConstrain pGrp to sourceparent, oGrp to sourceobj

    connectAttrs of oGrp to target obj(make sure values are zeroed)

    """
    sel = cmds.ls(sl=True)

    src1 = sel[0] # parent of Ctrl (or thing you want to relate it to)
    src2 = sel[1] # ctrl
    tgt = sel[2]  # joint (should be in a group)

    tgtGrp = cmds.group(em=True, name="{0}_spaceBuffer".format(src2))
    tgtParGrp = cmds.group(em=True, name="{0}_spaceBuffer".format(src1))
    cmds.parent(tgtGrp, tgtParGrp)

    src1PC = cmds.parentConstraint(src1, tgtParGrp)
    src2PC = cmds.parentConstraint(src2, tgtGrp)

    if cmds.getAttr("{0}.t".format(tgt))[0]==(0,0,0):
        cmds.connectAttr("{0}.t".format(src2), "{0}.t".format(tgt))
    else:
        cmds.warning("{0} had non-zero translate values! Skipping connection.".format(tgt))
    
    if cmds.getAttr("{0}.r".format(tgt))[0]==(0,0,0):
        cmds.connectAttr("{0}.r".format(src2), "{0}.r".format(tgt))
    else:
        cmds.warning("{0} had non-zero rotate values! Skipping connection.".format(tgt))

def spaceBuffer():
    spaceBufferUI()