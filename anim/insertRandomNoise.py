import maya.cmds as cmds
import random

widgets = {}

def isrUI(*args):
    if cmds.window("irnWin", exists=True):
        cmds.deleteUI("irnWin")

    widgets["win"] = cmds.window("irnWin", t="zbw_insertRandomNoise", w=200, h=100)
    widgets["CLO"] = cmds.columnLayout()
    cmds.text("select the controls you want to add\nrandom motion to.\nThis will add a group above and some\nattrs on the controls", al="left")
    cmds.separator(h=10)
    widgets["but"] = cmds.button(l="add to selected control", w=200, h=40, bgc=(.5, .7, .5), c=irnDo)

    cmds.window(widgets["win"], e=True, wh=(5,5),rtf=True)
    cmds.showWindow(widgets["win"])

def irnDo(*args):
    sel = cmds.ls(sl=True, type="transform")

    if not sel:
        return()


    for obj in sel:
        grp = insertGroupAbove(obj)

        anim = cmds.createNode("animCurveTU", name="{0}_irnAnim".format(obj))
        cmds.setAttr("{0}.postInfinity".format(anim), 4)
        cmds.setAttr("{0}.preInfinity".format(anim), 4)
        cmds.setKeyframe(anim, t=0, v=0, itt="linear", ott="linear")
        cmds.setKeyframe(anim, t=1, v=1, itt="linear", ott="linear")

        rawSpeedMult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_spdMult".format(obj))
        cmds.setAttr("{0}.input1".format(rawSpeedMult), .002, 0, 0)
        cmds.connectAttr("{0}.output".format(anim), "{0}.input2X".format(rawSpeedMult))

        usrSpeedMult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_usrMult".format(obj))
        cmds.connectAttr("{0}.outputX".format(rawSpeedMult), "{0}.input2X".format(usrSpeedMult))

        ramp = cmds.shadingNode("ramp", asTexture=True, name="{0}_ramp".format(obj))
        cmds.setAttr("{0}.type".format(ramp), 0)
        cmds.setAttr("{0}.interpolation".format(ramp), 4)
        colorDict = {}
        for i in range(6):
            j = i*0.2
            if (j == 1.0):
                cmds.setAttr("{0}.colorEntryList[{1}].color".format(ramp, i), colorDict[0][0], colorDict[0][1], colorDict[0][2])
            else:
                xrand = rand(0,1)
                yrand = rand(0,1)
                zrand = rand(0,1)
                cmds.setAttr("{0}.colorEntryList[{1}].color".format(ramp, i), xrand, yrand, zrand)
                colorDict[i] = [xrand, yrand, zrand]
            cmds.setAttr("{0}.colorEntryList[{1}].position".format(ramp, i), j)

        cmds.connectAttr("{0}.outputX".format(usrSpeedMult), "{0}.uvCoord.vCoord".format(ramp))

        setR = cmds.shadingNode("setRange", name="{0}_setRange".format(obj), asUtility=True)
        cmds.setAttr("{0}.min".format(setR), -1, -1, -1)
        cmds.setAttr("{0}.max".format(setR), 1, 1, 1)
        cmds.setAttr("{0}.oldMax".format(setR), 1, 1, 1)
        cmds.connectAttr("{0}.outColor".format(ramp), "{0}.value".format(setR))

        usrAmpMult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_ampMult".format(obj))
        cmds.connectAttr("{0}.outValue".format(setR), "{0}.input1".format(usrAmpMult))

        cmds.addAttr(obj, ln="motionSpeed", at="float", min=0.0, max=2.0, dv=1.0, k=True)
        cmds.addAttr(obj, ln="motionStrengthX", at="float", min=-1, max=10, dv=1.0,k=True)
        cmds.addAttr(obj, ln="motionStrengthY", at="float", min=-1, max=10, dv=1.0,k=True)
        cmds.addAttr(obj, ln="motionStrengthZ", at="float", min=-1, max=10, dv=1.0,k=True)
        # add controls to selected obj, "motion(Speed)", "motionAmplitude"
        cmds.connectAttr("{0}.motionSpeed".format(obj), "{0}.input1X".format(usrSpeedMult))
        cmds.connectAttr("{0}.motionStrengthX".format(obj), "{0}.input2X".format(usrAmpMult))
        cmds.connectAttr("{0}.motionStrengthY".format(obj), "{0}.input2Y".format(usrAmpMult))
        cmds.connectAttr("{0}.motionStrengthZ".format(obj), "{0}.input2Z".format(usrAmpMult))

        cmds.connectAttr("{0}.output".format(usrAmpMult), "{0}.translate".format(grp))

    cmds.select(sel, r=True)

def rand(a, b):
    return(random.uniform(a, b))

def insertGroupAbove(obj, *args):
    par = cmds.listRelatives(obj, p=True)
    
    grp = cmds.group(em=True, n="{}_Grp".format(obj))
    
    pos = cmds.xform(obj, q=True, ws=True, rp=True)
    rot = cmds.xform(obj, q=True, ws=True, ro=True)
    
    cmds.xform(grp, ws=True, t=pos)
    cmds.xform(grp, ws=True, ro=rot) 
     
    cmds.parent(obj, grp)
    if par:
        cmds.parent(grp, par[0])

    return(grp)

def insertRandomNoise(*args):
    isrUI()