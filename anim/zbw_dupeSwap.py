########################
#file: zbw_dupeSwap.py
#Author: zeth willie
#Contact: zeth@catbuks.com, www.williework.blogspot.com
#Date Modified: 04/27/13
#To Use: type in python window  "import zbw_dupeSwap as zds; zds.dupeSwap()"
#Notes/Descriptions: use to swap out objects for duplicates of the original object
########################

import maya.cmds as cmds

def dupeSwapUI():
    """UI for script"""

    if cmds.window("dupeWin", exists=True):
        cmds.deleteUI("dupeWin")

    cmds.window("dupeWin", t="zbw_dupeSwap", w=250, h=100)
    cmds.columnLayout("dupeCLO")
    cmds.text("Select the initial object. then select the", al="center", w=250)
    cmds.text("duplicates and press button", al="center", w=250)
    cmds.separator(h=5, style ="single")
    cmds.radioButtonGrp("inputsRBG", l="inputs:", nrb=3, l1="none", l2="connect", l3="duplicate", cw=[(1, 50), (2,47), (3,63), (4,40)], cal=[(1,"left"), (2,"left"), (3,"left"), (4,"left")], sl=1)
    cmds.separator(h=5, style ="single")

    cmds.button("dupeButton", l="Swap Elements", w=250, h=50, bgc=(.6, .8,.6), c=dupeIt)

    cmds.showWindow("dupeWin")
    cmds.window("dupeWin", e=True, w=250, h=100)

def dupeIt(*args):
    """uses the first selection and duplicates it to the transforms of the rest of the selected objects, with or without connections"""

    sel=cmds.ls(sl=True, type="transform", l=True)
    inputs = cmds.radioButtonGrp("inputsRBG", q=True, sl=True)
    if sel:
        base=sel[0]
        if len(sel)>1:
            objs=sel[1:]
            transforms = {}
            x=0

            for obj in objs:
                #get pos, rot, scale
                pos = cmds.xform(obj, ws=True, q=True, t=True)
                rot = cmds.xform(obj, ws=True, q=True, ro=True)
                scal = cmds.getAttr("%s.scale"%obj)[0]
                transforms[x] = [pos, rot, scal]

                #delete the obj
                cmds.delete(obj)
                x=x+1

            for key in list(transforms.keys()):
                if inputs == 1:
                    dupe = cmds.duplicate(base)[0]
                elif inputs == 3:
                    dupe = cmds.duplicate(base, un=True, rr=True)[0]
                elif inputs == 2:
                    dupe = cmds.duplicate(base, ic=True)[0]
                print(dupe)
                cmds.xform(dupe, ws=True, t=transforms[key][0])
                cmds.xform(dupe, ws=True, ro=transforms[key][1])
                cmds.setAttr("%s.scale"%dupe, transforms[key][2][0], transforms[key][2][1], transforms[key][2][2])

#TODO - checkbox to copy inputs on orig objects to corresponding inputs on top level of duplicates

        else:
            cmds.warning("You need to select more than one object in order to swap!")
    else:
        cmds.warning("Please select some transform nodes to dupe!")


def dupeSwap():
    """Use this to start the script!"""

    dupeSwapUI()