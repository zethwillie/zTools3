import maya.cmds as cmds
from functools import partial
import random

widgets = {}

#todo: add color picker for controls (will be normal and light for each)

def isrUI(*args):
    if cmds.window("irnWin", exists=True):
        cmds.deleteUI("irnWin")

    widgets["win"] = cmds.window("irnWin", t="zbw_insertRandomNoise", w=225, h=100)
    widgets["CLO"] = cmds.columnLayout()
    cmds.text(
        "select the controls you want to add random\n motion to. This will add a group above \nand some attrs on the controls",
        al="left")
    cmds.separator(h=10)
    widgets["offsetCBG"] = cmds.checkBoxGrp(l="Offset randomize?", v1=True, cw=[(1, 125), (2, 50)],
                                            cal=[(1, "left"), (2, "left")],
                                            cc=partial(toggleOnOff, "offsetCBG", "offsetIFG"))
    widgets["offsetIFG"] = cmds.intFieldGrp(l="Offset Min/Max:", numberOfFields=2, cw=[(1, 125), (2, 50), (3, 50)],
                                            cal=[(1, "left"), (2, "left"), (3, "left")], v1=-200, v2=200)
    widgets["speedCBG"] = cmds.checkBoxGrp(l="Speed randomize?", v1=True, cw=[(1, 125), (2, 50)],
                                           cal=[(1, "left"), (2, "left")],
                                           cc=partial(toggleOnOff, "speedCBG", "speedFFG"))
    widgets["speedFFG"] = cmds.floatFieldGrp(l="Speed Min/Max:", numberOfFields=2, cw=[(1, 125), (2, 50), (3, 50)],
                                             cal=[(1, "left"), (2, "left"), (3, "left")], v1=-2, v2=2, pre=2,
                                             cc=partial(limitFloatField, "speedFFG", -10, 10))
    widgets["ampCBG"] = cmds.checkBoxGrp(l="Amplitude randomize?:", v1=True, cw=[(1, 125), (2, 50)],
                                         cal=[(1, "left"), (2, "left")], cc=partial(toggleOnOff, "ampCBG", "ampFFG"))
    widgets["ampFFG"] = cmds.floatFieldGrp(l="Amplitude Min/Max", numberOfFields=2, cw=[(1, 125), (2, 50), (3, 50)],
                                           cal=[(1, "left"), (2, "left"), (3, "left")], v1=.5, v2=1.5, pre=2,
                                           cc=partial(limitFloatField, "ampFFG", -10, 10))
    widgets["noiseCBG"] = cmds.checkBoxGrp(l="Noise randomize?:", v1=True, cw=[(1, 125), (2, 50)],
                                           cal=[(1, "left"), (2, "left")],
                                           cc=partial(toggleOnOff, "noiseCBG", "noiseFFG"))
    widgets["noiseFFG"] = cmds.floatFieldGrp(l="Noise Min/Max", numberOfFields=2, cw=[(1, 125), (2, 50), (3, 50)],
                                             cal=[(1, "left"), (2, "left"), (3, "left")], v1=.1, v2=.3, pre=2,
                                             cc=partial(limitFloatField, "noiseFFG", 0, 1))
    widgets["freqCBG"] = cmds.checkBoxGrp(l="Noise Freq randomize?:", v1=True, cw=[(1, 125), (2, 50)],
                                          cal=[(1, "left"), (2, "left")], cc=partial(toggleOnOff, "freqCBG", "freqFFG"))
    widgets["freqFFG"] = cmds.floatFieldGrp(l="Noise Freq Min/Max", numberOfFields=2, cw=[(1, 125), (2, 50), (3, 50)],
                                            cal=[(1, "left"), (2, "left"), (3, "left")], v1=0, v2=.25, pre=2,
                                            cc=partial(limitFloatField, "freqFFG", 0, 1))
    cmds.separator(h=5)

    cmds.separator(h=10)

    widgets["but"] = cmds.button(l="add to selected control", w=225, h=40, bgc=(.5, .7, .5), c=irnDo)

    cmds.window(widgets["win"], e=True, wh=(5, 5), rtf=True)
    cmds.showWindow(widgets["win"])


def toggleOnOff(cbg, ffg, *args):
    on = cmds.checkBoxGrp(widgets[cbg], q=True, v1=True)
    if ffg == "offsetIFG":
        cmds.intFieldGrp(widgets[ffg], e=True, en=on)
    else:
        cmds.floatFieldGrp(widgets[ffg], e=True, en=on)


def limitSingle(ffg, *args):
    widg = widgets[ffg]
    v1 = cmds.floatFieldGrp(widg, q=True, v1=True)
    if v1 < 0:
        v1 = 0
    if v1 > 1:
        v1 = 1

    cmds.floatFieldGrp(widg, e=True, v1=v1)


def limitFloatField(ffg, mn, mx, *args):
    widg = widgets[ffg]
    v1 = cmds.floatFieldGrp(widg, q=True, v1=True)
    v2 = cmds.floatFieldGrp(widg, q=True, v2=True)

    if v1 < mn:
        v1 = mn
    if v1 > mx:
        v1 = mx
    if v2 < mn:
        v2 = mn
    if v2 > mx:
        v2 = mx

    cmds.floatFieldGrp(widg, e=True, v1=v1)
    cmds.floatFieldGrp(widg, e=True, v2=v2)


def getFFG(ffg, val, *args):
    if val == 1:
        return (cmds.floatFieldGrp(widgets[ffg], q=True, v1=True))
    if val == 2:
        return (cmds.floatFieldGrp(widgets[ffg], q=True, v2=True))


def irnDo(*args):
    sel = cmds.ls(sl=True, type="transform")

    offMin = cmds.intFieldGrp(widgets["offsetIFG"], q=True, v1=True)
    offMax = cmds.intFieldGrp(widgets["offsetIFG"], q=True, v2=True)
    speedMin = getFFG("speedFFG", 1)
    speedMax = getFFG("speedFFG", 2)
    ampMin = getFFG("ampFFG", 1)
    ampMax = getFFG("ampFFG", 2)
    noiseMin = getFFG("noiseFFG", 1)
    noiseMax = getFFG("noiseFFG", 2)
    freqMin = getFFG("freqFFG", 1)
    freqMax = getFFG("freqFFG", 2)

    if not sel:
        return ()

    for obj in sel:
        grp = insertGroupAbove(obj)

        anim = cmds.createNode("animCurveTU", name="{0}_irnAnim".format(obj))
        cmds.setAttr("{0}.postInfinity".format(anim), 4)
        cmds.setAttr("{0}.preInfinity".format(anim), 4)
        cmds.setKeyframe(anim, t=0, v=0, itt="linear", ott="linear")
        cmds.setKeyframe(anim, t=1, v=1, itt="linear", ott="linear")

        offsetX = cmds.shadingNode("addDoubleLinear", asUtility=True, name="{0}_animOffsetX_add".format(obj))
        cmds.connectAttr("{0}.output".format(anim), "{0}.input1".format(offsetX))
        offsetY = cmds.shadingNode("addDoubleLinear", asUtility=True, name="{0}_animOffsetY_add".format(obj))
        cmds.connectAttr("{0}.output".format(anim), "{0}.input1".format(offsetY))
        offsetZ = cmds.shadingNode("addDoubleLinear", asUtility=True, name="{0}_animOffsetZ_add".format(obj))
        cmds.connectAttr("{0}.output".format(anim), "{0}.input1".format(offsetZ))

        rawSpeedMult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_rawSpdMult".format(obj))
        cmds.setAttr("{0}.input1".format(rawSpeedMult), .002, 0.002, 0.002)
        cmds.connectAttr("{0}.output".format(offsetX), "{0}.input2X".format(rawSpeedMult))
        cmds.connectAttr("{0}.output".format(offsetY), "{0}.input2Y".format(rawSpeedMult))
        cmds.connectAttr("{0}.output".format(offsetZ), "{0}.input2Z".format(rawSpeedMult))

        mstrSpeedMult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_mstrSpdMult".format(obj))
        cmds.connectAttr("{0}.output".format(rawSpeedMult), "{0}.input2".format(mstrSpeedMult))

        usrSpeedMult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_usrMult".format(obj))
        cmds.connectAttr("{0}.output".format(mstrSpeedMult), "{0}.input2".format(usrSpeedMult))

        rampX = cmds.shadingNode("ramp", asTexture=True, name="{0}_rampX".format(obj))
        rampY = cmds.shadingNode("ramp", asTexture=True, name="{0}_rampZ".format(obj))
        rampZ = cmds.shadingNode("ramp", asTexture=True, name="{0}_rampY".format(obj))
        for ramp in [rampX, rampY, rampZ]:
            cmds.setAttr("{0}.type".format(ramp), 0)
            cmds.setAttr("{0}.interpolation".format(ramp), 4)

            for i in range(5):
                poss = [0.0, .250, .5, .750, 1.0]

                ce = [0.5, 0.0, 0.5, 1.0, 0.5]
                cmds.setAttr("{0}.colorEntryList[{1}].position".format(ramp, i), poss[i])
                cmds.setAttr("{0}.colorEntryList[{1}].color".format(ramp, i), ce[i], ce[i], ce[i])

        cmds.connectAttr("{0}.outputX".format(usrSpeedMult), "{0}.uvCoord.vCoord".format(rampX))
        cmds.connectAttr("{0}.outputY".format(usrSpeedMult), "{0}.uvCoord.vCoord".format(rampY))
        cmds.connectAttr("{0}.outputZ".format(usrSpeedMult), "{0}.uvCoord.vCoord".format(rampZ))

        setR = cmds.shadingNode("setRange", name="{0}_setRange".format(obj), asUtility=True)
        cmds.setAttr("{0}.min".format(setR), -1, -1, -1)
        cmds.setAttr("{0}.max".format(setR), 1, 1, 1)
        cmds.setAttr("{0}.oldMax".format(setR), 1, 1, 1)
        cmds.connectAttr("{0}.outColorR".format(rampX), "{0}.valueX".format(setR))
        cmds.connectAttr("{0}.outColorR".format(rampY), "{0}.valueY".format(setR))
        cmds.connectAttr("{0}.outColorR".format(rampZ), "{0}.valueZ".format(setR))

        usrAmpMult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_ampMult".format(obj))
        cmds.connectAttr("{0}.outValue".format(setR), "{0}.input1".format(usrAmpMult))

        envelopeMult = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_envelope".format(obj))
        cmds.connectAttr("{0}.output".format(usrAmpMult), "{0}.input1".format(envelopeMult))

        cmds.addAttr(obj, ln="randomMotionCtrls", at="enum", k=True, en="------")
        cmds.setAttr("{0}.randomMotionCtrls".format(obj), l=True)
        cmds.addAttr(obj, ln="masterAmp", at="float", min=0, max=1, dv=1, k=True)
        cmds.addAttr(obj, ln="masterSpeed", at="float", min=0, max=1, dv=1, k=True)
        cmds.addAttr(obj, ln="offsetFrameX", at="long", dv=0, k=True)
        cmds.addAttr(obj, ln="offsetFrameY", at="long", dv=0, k=True)
        cmds.addAttr(obj, ln="offsetFrameZ", at="long", dv=0, k=True)
        cmds.addAttr(obj, ln="motionSpeedX", at="float", min=-10.0, max=10.0, dv=1.0, k=True)
        cmds.addAttr(obj, ln="motionSpeedY", at="float", min=-10.0, max=10.0, dv=1.0, k=True)
        cmds.addAttr(obj, ln="motionSpeedZ", at="float", min=-10.0, max=10.0, dv=1.0, k=True)
        cmds.addAttr(obj, ln="motionAmplitudeX", at="float", min=-10, max=10, dv=1, k=True)
        cmds.addAttr(obj, ln="motionAmplitudeY", at="float", min=-10, max=10, dv=1, k=True)
        cmds.addAttr(obj, ln="motionAmplitudeZ", at="float", min=-10, max=10, dv=1, k=True)
        cmds.addAttr(obj, ln="noiseStrengthX", at="float", min=0, max=1, dv=0, k=True)
        cmds.addAttr(obj, ln="noiseStrengthY", at="float", min=0, max=1, dv=0, k=True)
        cmds.addAttr(obj, ln="noiseStrengthZ", at="float", min=0, max=1, dv=0, k=True)
        cmds.addAttr(obj, ln="noiseFrequencyX", at="float", min=0, max=1, dv=0, k=True)
        cmds.addAttr(obj, ln="noiseFrequencyY", at="float", min=0, max=1, dv=0, k=True)
        cmds.addAttr(obj, ln="noiseFrequencyZ", at="float", min=0, max=1, dv=0, k=True)
        cmds.addAttr(obj, ln="rampTxt", at="message")

        # set some of the attributes on the obj
        if cmds.checkBoxGrp(widgets["offsetCBG"], q=True, v1=True):
            cmds.setAttr("{0}.offsetFrameX".format(obj), rand(offMin, offMax))
            cmds.setAttr("{0}.offsetFrameY".format(obj), rand(offMin, offMax))
            cmds.setAttr("{0}.offsetFrameZ".format(obj), rand(offMin, offMax))
        if cmds.checkBoxGrp(widgets["speedCBG"], q=True, v1=True):
            cmds.setAttr("{0}.motionSpeedX".format(obj), rand(speedMin, speedMax))
            cmds.setAttr("{0}.motionSpeedY".format(obj), rand(speedMin, speedMax))
            cmds.setAttr("{0}.motionSpeedZ".format(obj), rand(speedMin, speedMax))
        if cmds.checkBoxGrp(widgets["ampCBG"], q=True, v1=True):
            cmds.setAttr("{0}.motionAmplitudeX".format(obj), rand(ampMin, ampMax))
            cmds.setAttr("{0}.motionAmplitudeY".format(obj), rand(ampMin, ampMax))
            cmds.setAttr("{0}.motionAmplitudeZ".format(obj), rand(ampMin, ampMax))
        if cmds.checkBoxGrp(widgets["noiseCBG"], q=True, v1=True):
            cmds.setAttr("{0}.noiseStrengthX".format(obj), rand(noiseMin, noiseMax))
            cmds.setAttr("{0}.noiseStrengthY".format(obj), rand(noiseMin, noiseMax))
            cmds.setAttr("{0}.noiseStrengthZ".format(obj), rand(noiseMin, noiseMax))
        if cmds.checkBoxGrp(widgets["freqCBG"], q=True, v1=True):
            cmds.setAttr("{0}.noiseFrequencyX".format(obj), rand(freqMin, freqMax))
            cmds.setAttr("{0}.noiseFrequencyY".format(obj), rand(freqMin, freqMax))
            cmds.setAttr("{0}.noiseFrequencyZ".format(obj), rand(freqMin, freqMax))

        cmds.connectAttr("{0}.message".format(ramp), "{0}.rampTxt".format(obj))
        cmds.connectAttr("{0}.masterAmp".format(obj), "{0}.input2X".format(envelopeMult))
        cmds.connectAttr("{0}.masterAmp".format(obj), "{0}.input2Y".format(envelopeMult))
        cmds.connectAttr("{0}.masterAmp".format(obj), "{0}.input2Z".format(envelopeMult))
        cmds.connectAttr("{0}.masterSpeed".format(obj), "{0}.input1X".format(mstrSpeedMult))
        cmds.connectAttr("{0}.masterSpeed".format(obj), "{0}.input1Y".format(mstrSpeedMult))
        cmds.connectAttr("{0}.masterSpeed".format(obj), "{0}.input1Z".format(mstrSpeedMult))
        cmds.connectAttr("{0}.offsetFrameX".format(obj), "{0}.input2".format(offsetX))
        cmds.connectAttr("{0}.offsetFrameY".format(obj), "{0}.input2".format(offsetY))
        cmds.connectAttr("{0}.offsetFrameZ".format(obj), "{0}.input2".format(offsetZ))
        cmds.connectAttr("{0}.motionSpeedX".format(obj), "{0}.input1X".format(usrSpeedMult))
        cmds.connectAttr("{0}.motionSpeedY".format(obj), "{0}.input1Y".format(usrSpeedMult))
        cmds.connectAttr("{0}.motionSpeedZ".format(obj), "{0}.input1Z".format(usrSpeedMult))
        cmds.connectAttr("{0}.motionAmplitudeX".format(obj), "{0}.input2X".format(usrAmpMult))
        cmds.connectAttr("{0}.motionAmplitudeY".format(obj), "{0}.input2Y".format(usrAmpMult))
        cmds.connectAttr("{0}.motionAmplitudeZ".format(obj), "{0}.input2Z".format(usrAmpMult))
        cmds.connectAttr("{0}.noiseStrengthX".format(obj), "{0}.noise".format(rampX))
        cmds.connectAttr("{0}.noiseStrengthY".format(obj), "{0}.noise".format(rampY))
        cmds.connectAttr("{0}.noiseStrengthZ".format(obj), "{0}.noise".format(rampZ))
        cmds.connectAttr("{0}.noiseFrequencyX".format(obj), "{0}.noiseFreq".format(rampX))
        cmds.connectAttr("{0}.noiseFrequencyY".format(obj), "{0}.noiseFreq".format(rampY))
        cmds.connectAttr("{0}.noiseFrequencyZ".format(obj), "{0}.noiseFreq".format(rampZ))
        cmds.connectAttr("{0}.output".format(envelopeMult), "{0}.translate".format(grp))

    cmds.select(sel, r=True)


def rand(a, b):
    return (random.uniform(a, b))


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

    return (grp)


def insertRandomNoise(*args):
    isrUI()
