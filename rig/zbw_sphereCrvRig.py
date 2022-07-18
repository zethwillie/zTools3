import maya.cmds as cmds
import zTools.rig.zbw_rig as rig
import importlib
importlib.reload(rig)
from functools import partial


#---------------- make this all a class? 

upJntProxyGrpCtrls = {}
downJntProxyGrpCtrls = {}
widgets = {}
lowResCurves = []
highResCurves = []
ctrlsUp = []
ctrlsDwn = []

def sphere_curve_rig_UI(*args):
    if cmds.window("crvRigJntWin", exists=True):
        cmds.deleteUI("crvRigJntWin")

    w, h= 400, 300

    widgets["win"] = cmds.window("crvRigJntWin", t="zbw_curveJntRig", w=w,h=h)
    widgets["mainCLO"] = cmds.columnLayout()


    widgets["numCtrlIFG"] = cmds.intFieldGrp(l="Number of Ctrls:", cal=[(1,"left"), (2,"left")], cw=[(1,120), (2,50)], v1=5)
    widgets["nameTFG"] = cmds.textFieldGrp(l="Rig Name (i.e. lfEye):", cal=[(1,"left"), (2,"left"), (3,"left")], cw=[(1,120), (2,280), (3,30)], tx="eye")
    widgets["cntrPivTFBG"] = cmds.textFieldButtonGrp(l="Center pivot object:", bl="<<<", cal=[(1,"left"), (2,"left"), (3,"left")], cw=[(1,120), (2,280), (3,30)], bc=partial(populate_curve_field, "cntrPivTFBG"), cc=partial(second_fill, "center"), tx="centerLoc")
    widgets["upLocTFBG"] = cmds.textFieldButtonGrp(l="Aim up object:", bl="<<<", cal=[(1,"left"), (2,"left"), (3,"left")], cw=[(1,120), (2,280), (3,30)], bc=partial(populate_curve_field, "upLocTFBG"), cc=partial(second_fill, "up"), tx="upLoc")
    cmds.separator(h=10)

    widgets["upCrvTFBG"] = cmds.textFieldButtonGrp(l="First Curve", bl="<<<", cal=[(1,"left"), (2,"left"), (3,"left")], cw=[(1,120), (2,280), (3,30)], bc=partial(populate_curve_field, "upCrvTFBG"), tx="topCrv")
    widgets["upNameTFG"] = cmds.textFieldGrp(l="1st Suffix (i.e.'Top')", cal=[(1,"left"), (2,"left")], cw=[(1,120), (2,280)], tx="Top")
    cmds.separator(h=10)

    widgets["secondCBG"] = cmds.checkBoxGrp(l="Create Second Curve?", ncb=1, v1=0, cal=[(1,"left"), (2,"left")], cc=toggle_second, en=True)
    widgets["downCrvTFBG"] = cmds.textFieldButtonGrp(l="Second Curve", bl="<<<", cal=[(1,"left"), (2,"left"), (3,"left")], en=False, cw=[(1,120), (2,280), (3,30)], bc=partial(populate_curve_field, "downCrvTFBG"), tx="downCrv")
    widgets["downNameTFG"] = cmds.textFieldGrp(l="2nd Suffix (i.e. 'Dwn')", cal=[(1,"left"), (2,"left")], cw=[(1,120), (2,280)], en=False, tx="Dwn")
    widgets["cntrPiv2TFBG"] = cmds.textFieldButtonGrp(l="Center pivot object:", bl="<<<", cal=[(1,"left"), (2,"left"), (3,"left")], cw=[(1,120), (2,280), (3,30)], bc=partial(populate_curve_field, "cntrPivTFBG"), en=False, tx="centerLoc")
    widgets["upLoc2TFBG"] = cmds.textFieldButtonGrp(l="Aim up object:", bl="<<<", cal=[(1,"left"), (2,"left"), (3,"left")], cw=[(1,120), (2,280), (3,30)], bc=partial(populate_curve_field, "upLoc2TFBG"), en=False, tx="upLoc")
    cmds.separator(h=10)

    widgets["execBut"] = cmds.button(l="create base rig!", w=w, c=pass_to_execute)
    widgets["cnctBut"] = cmds.button(l="connect ctrls to jnts", w=w, c=connect_proxies)
    widgets["closeBut"] = cmds.button(l="setup smart close", w=w, c=smart_close)

    cmds.separator(h=10)

    # widgets["scCBG"] = cmds.checkBoxGrp(l="Set up smart close?", ncb=1, v1=0, cal=[(1,"left"), (2,"left")], en=True)


    cmds.window(widgets["win"], e=True, w=5, h=5, resizeToFitChildren=True, sizeable=True)
    cmds.showWindow(widgets["win"])

def second_fill(tfg, *args):
    print("in center fill")
    if tfg == "center":
        obj = cmds.textFieldButtonGrp(widgets["cntrPivTFBG"], q=True, tx=True)
        cmds.textFieldButtonGrp(widgets["cntrPiv2TFBG"], e=True, tx=obj)

    elif tfg == "up":
        obj = cmds.textFieldButtonGrp(widgets["upLocTFBG"], q=True, tx=True)
        cmds.textFieldButtonGrp(widgets["upLoc2TFBG"], e=True, tx=obj)

def toggle_second(*args):
    state = cmds.checkBoxGrp(widgets["secondCBG"], q=True, v1=True)
    if state:
        cmds.textFieldButtonGrp(widgets["downCrvTFBG"], e=True, en=True)
        cmds.textFieldButtonGrp(widgets['cntrPiv2TFBG'], e=True, en=True)
        cmds.textFieldButtonGrp(widgets['upLoc2TFBG'], e=True, en=True)
        cmds.textFieldGrp(widgets["downNameTFG"], e=True, en=True)
        cmds.button(widgets["closeBut"], e=True, en=True)       
    else:
        cmds.textFieldButtonGrp(widgets['downCrvTFBG'], e=True, en=False)
        cmds.textFieldButtonGrp(widgets['cntrPiv2TFBG'], e=True, en=False)
        cmds.textFieldButtonGrp(widgets['upLoc2TFBG'], e=True, en=False)
        cmds.textFieldGrp(widgets["downNameTFG"], e=True, en=False)     
        cmds.button(widgets["closeBut"], e=True, en=False)  

def populate_curve_field(tfgKey="", *args):

#TODO   make this a message attr?
    if tfgKey not in ["cntrPivTFBG", "cntrPiv2TFBG", "upLoc2TFBG", "upLocTFBG"]:
        sel = cmds.ls(sl=True)
        if sel and len(sel)!=1:
            cmds.warning("only select the curve you want to rig up!")
        else:
            if rig.type_check(sel[0], "nurbsCurve"):
                cmds.textFieldButtonGrp(widgets[tfgKey], e=True, tx=sel[0])
            else:
                cmds.warning("That's not a curve!")
    else:
        sel = cmds.ls(sl=True)
        if sel and len(sel)!=1:
            cmds.warning("only select the object you want to rig up!")
        else:
            cmds.textFieldButtonGrp(widgets[tfgKey], e=True, tx=sel[0])
            if tfgKey == "upLocTFBG":
                cmds.textFieldButtonGrp(widgets["upLoc2TFBG"], e=True, tx=sel[0])
            if tfgKey == "cntrPivTFBG":
                cmds.textFieldButtonGrp(widgets["cntrPiv2TFBG"], e=True, tx=sel[0])         

def pass_to_execute(*args):
    
    lowResCurves = []
    highResCurves = []

    secCheck = cmds.checkBoxGrp(widgets["secondCBG"], q=True, v1=True)
    name = cmds.textFieldGrp(widgets["nameTFG"], q=True, tx=True)

    # get values from UI
#---------------- check that num is greater than 3, IN FACT MAKE SURE IT IS ODD
    num = cmds.intFieldGrp(widgets["numCtrlIFG"], q=True, v1=True)
    centerLoc = cmds.textFieldButtonGrp(widgets["cntrPivTFBG"], q=True, tx=True)
    firstCrv = cmds.textFieldButtonGrp(widgets["upCrvTFBG"], q=True, tx=True)
    firstNameSuf = cmds.textFieldGrp(widgets["upNameTFG"], q=True, tx=True)
    firstName = "{0}_{1}".format(name, firstNameSuf)

    if num and name and centerLoc and firstCrv and firstName:
        curve_joint_rig_execute(num, centerLoc, firstCrv, firstName, crvType="up")
    else:
        cmds.warning("Some fields weren't filled out for the first curve! Undo and try again!")
        return

    if secCheck:
        secondCrv = cmds.textFieldButtonGrp(widgets["downCrvTFBG"], q=True, tx=True)
        secondNameSuf = cmds.textFieldGrp(widgets["downNameTFG"], q=True, tx=True)
        secondName = "{0}_{1}".format(name, secondNameSuf)
        if num and centerLoc and secondCrv and secondName:
            curve_joint_rig_execute(num, centerLoc, secondCrv, secondName, crvType="down")
    else:
        cmds.warning("Some fields weren't filled out for the second curve! Undo and try again!")
        return

def curve_joint_rig_execute(numCtrls=5, centerLoc="", c="", name="", crvType="up", *args):
        
    #crv = cmds.curve(d=3, ep=pts)
    #---------------- create the curve, ideally from the geo
    #---------------- select the curve(s), maybe below is for each curve ( or option to do up and low curve at once with same center, etc )
    #---------------- UI shold do this stuff in steps so that one has time adjust the curves/controls, etc before moving onto the next step

#---------------- ui options:  up/down crvs or just one, smart close, how many ctsl?, option to create curve from vtx selection/make live? curve shoudl be linear
#----------------              selection/typein field grps for curves, maybe options for hooking directly or with groups


    hi = "HIGH"
    lo = "CTRL"

    centerPos = cmds.xform(centerLoc, q=True, ws=True, rp=True)

    crv = cmds.rename(c, "{0}_{1}_CRV".format(name, hi))
    eps = cmds.ls("{0}.ep[*]".format(crv), fl=True)

    locGrp = cmds.group(empty=True, n="{0}_AIMLOC_GRP".format(crv[:-9]))
    jntGrp = cmds.group(empty=True, n="{0}_BNDJNT_GRP".format(crv[:-9]))
    crvGrp = cmds.group(empty=True, n="{0}_CRVS_Grp".format(crv[:-9]))
    #ctrlJntGrp = cmds.group(empty=True, n="{0}ctrlJnt_Grp".format(crv))

    for x in range(0, len(eps)):
        loc = cmds.spaceLocator(n="LOC_{0}{1}".format(crv, x))[0]
        cmds.connectAttr(eps[x], "{0}.t".format(loc))
        locPos = cmds.xform(loc, q=True, ws=True, rp=True)
        cmds.select(cl=True)
        baseJnt = cmds.joint(n="baseJnt_{0}{1}".format(crv, x), position=centerPos)
        endJnt = cmds.joint(n="endJnt_{0}{1}".format(crv, x), position=locPos)
        cmds.select(cl=True)
        cmds.joint(baseJnt, e=True, oj="xyz", sao="yup", ch=True)
        
        cmds.parent(baseJnt, jntGrp)
        cmds.parent(loc, locGrp)
        
        ac = cmds.aimConstraint(loc, baseJnt, mo=False, wuo="upLoc", wut="object", aim=(1,0,0), u=(0,1,0))
    # put ctrls on the indiv jnts, if someone should want them

    # dupe curve, rebuild to 5
    ctrlCrv = rig.rebuild_curve(curve = crv, num =numCtrls - 1, name="{0}_{1}_Crv".format(name, lo), keep=True, ch=False)
# rebuild to 5
    # put jnts at the eps
    ctrlEps = cmds.ls("{0}.ep[*]".format(ctrlCrv), fl=True)

    bndGrps = []
    bndJnts = []
    for x in range(0, len(ctrlEps)):
        pos = cmds.getAttr(ctrlEps[x])[0]
        cmds.select(cl=True)
        jnt = cmds.joint(n="{0}_Jnt{1}".format(ctrlCrv, x), position=pos)
        jntGrp = rig.group_freeze(jnt)
        #cmds.parent(jntGrp, ctrlJntGrp)
        bndJnts.append(jnt)
        bndGrps.append(jntGrp)

    bndJntGrp = cmds.group(empty=True, name="{0}_CTRL_JNT_GRP".format(name))
    for g in bndGrps:
        cmds.parent(g, bndJntGrp)

    wireNode = cmds.wire(crv, en=1, gw=True, ce=0, li=0, w=ctrlCrv, name = "{0}_wire".format(name))[0]
    wireGroup = "{0}Group".format(ctrlCrv)
    
    cmds.parent(wireGroup, crvGrp)
    cmds.parent(crv, crvGrp)

    cmds.skinCluster(bndJnts, ctrlCrv, maximumInfluences=3, dropoffRate=4, skinMethod=0, normalizeWeights=2)

    ctrlsGrp = cmds.group(empty=True, name="{0}_CTRLS_GRP".format(name))
    proxyGrp = cmds.group(empty=True, name="{0}_PROXY_GRP".format(name))

#---------------- deal with the end ctrls . . . . second ones should follow the first ones. . . scale middle ctrls up, scale inBetweens smaller
#---------------- connect parent constraints to mid ctrls --> middle and end ctrls. . .

    # create the controls for the ctrl jnts
    for x in range(0, len(bndJnts)):
        jnt = bndJnts[x]
        ctrl = rig.create_control(name="{0}_CTRL_{1}".format(name, x), type="sphere", axis="x", color="red")
        ctrlGrp = rig.group_freeze(ctrl)
        rig.snap_to(jnt, ctrlGrp)
        cmds.parent(ctrlGrp, ctrlsGrp)

        # create the world space proxies
        prxyCtrl, prxyGrp = rig.create_space_buffer_grps(ctrl)
        cmds.parent(prxyGrp, proxyGrp)

        if crvType == "up":
            upJntProxyGrpCtrls[jnt] = prxyCtrl
            ctrlsUp.append(ctrl)
        if crvType == "down":
            downJntProxyGrpCtrls[jnt] = prxyCtrl
            ctrlsDwn.append(ctrl)

    lowResCurves.append(ctrlCrv)
    highResCurves.append(crv)


def connect_proxies(*args):
    for key in upJntProxyGrpCtrls:
        jnt = key
        prxy = upJntProxyGrpCtrls[key]
        # direct connect ctrl to jnt
        rig.connect_transforms(prxy, jnt, s=False)

    if upJntProxyGrpCtrls:
        upJntProxyGrpCtrls.clear()

    if downJntProxyGrpCtrls:
        for key in downJntProxyGrpCtrls:
            jnt = key
            prxy = downJntProxyGrpCtrls[key]

            # direct connect ctrl to jnt
            rig.connect_transforms(prxy, jnt, s=False)
        downJntProxyGrpCtrls.clear()


def smart_close(*args):
    name = cmds.textFieldGrp(widgets["nameTFG"], q=True, tx=True)
    upSuf = cmds.textFieldGrp(widgets["upNameTFG"], q=True, tx=True)
    dwnSuf = cmds.textFieldGrp(widgets["downNameTFG"], q=True, tx=True)
    topMidCtrl = ctrlsUp[len(ctrlsUp)/2]
    downMidCtrl = ctrlsUp[len(ctrlsDwn)/2]
    
    if len(lowResCurves)==2 and len(highResCurves)==2:
        tmpCloseLow = cmds.duplicate(lowResCurves[0], n="{0}_closeLowTmpCrv".format(name))[0]
        cmds.parent(tmpCloseLow, w=True)

        tmpLowBS = cmds.blendShape(lowResCurves[0], lowResCurves[1], tmpCloseLow)[0]
        tmpLowUpAttr = "{0}.{1}".format(tmpLowBS, lowResCurves[0])
        tmpLowDwnAttr = "{0}.{1}".format(tmpLowBS, lowResCurves[1])
        cmds.setAttr(tmpLowUpAttr, 0.5)
        cmds.setAttr(tmpLowDwnAttr, 0.5)
        closeLow = cmds.duplicate(tmpCloseLow, n="{0}_CLOSE_LOW_CRV".format(name))[0]
        cmds.delete([tmpCloseLow, tmpLowBS])
        lowBS = cmds.blendShape(lowResCurves[0], lowResCurves[1], closeLow)[0]
        lowUpAttr = "{0}.{1}".format(lowBS, lowResCurves[0])
        lowDwnAttr = "{0}.{1}".format(lowBS, lowResCurves[1])

#---------------- connect up down into reverse setup that drives lowclosecrv to go up/down
        cmds.addAttr(topMidCtrl, ln="__xtraAttrs__", )

        cmds.setAttr(lowUpAttr, 1)
        cmds.setAttr(lowDwnAttr, 0)
        closeUpHigh = cmds.duplicate(highResCurves[0], n="{0}_HI_{1}_CLOSE_CRV".format(name, upSuf.upper() ))[0]
        cmds.parent(closeUpHigh, w=True)
        upHighWire = cmds.wire(closeUpHigh, en=1, gw=True, ce=0, li=0, w=closeLow, name = "{0}_CLS_UP_WIRE".format(name))[0]
        wireUpBaseCrv = "{0}BaseWire".format(closeLow)
        cmds.setAttr("{0}.scale[0]".format(upHighWire), 0)
#---------------- set up blend shape on high res curve (drive high res with wire driven curve)
#---------------- set up the center ctrl to drive this BS

        cmds.setAttr(lowUpAttr, 0)
        cmds.setAttr(lowDwnAttr, 1)
        closeDwnHigh = cmds.duplicate(highResCurves[1], n="{0}_HI_{1}_CLOSE_CRV".format(name, dwnSuf.upper() ))[0]
        cmds.parent(closeDwnHigh, w=True)
        dwnHighWire = cmds.wire(closeDwnHigh, en=1, gw=True, ce=0, li=0, w=closeLow, name = "{0}_CLS_DWN_WIRE".format(name))[0]
        wireDwnBase = "{0}BaseWire".format(closeLow)
        cmds.setAttr("{0}.scale[0]".format(dwnHighWire), 0)
#---------------- set up blend shape on high res curve (drive high res with wire driven curve)
#---------------- set up the center ctrl to drive this BS

"""
dupe lores crv (upper?) and pump both low res crvs into that a blend shape (this is blinkcrv)
setup a reverse network (to some ctrl) so the BS drives blinkcrv from crv (hi/low) to the other
Dupe each hires crv and connect via wire deformer (set scale of wireDef to 0) to each hirez dupe
and push those hirez dupes as blend shapes (end of chain) into the existing hirez crvs. These blend drive the blinking of each hirez
also: like the two ends (maybe just have one control for both top and bottom if we're doing both)
"""

def sphereCrvRig():
    sphere_curve_rig_UI()

#---------------- create a script to take bones on a BS head (in place?) and make controls/inbetween groups to bs them from main rig to drive joints