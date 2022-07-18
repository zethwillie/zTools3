########################
#file: zbw_snap.py
#Author: zeth willie
#Contact: zeth@catbuks.com, www.williework.blogspot.com
#Date Modified: 01/17/17
#To Use: type in python window  "import zbw_snap; zbw_snap.snap()"
#Notes/Descriptions: use to simply snap one object to another. Option for translate, rotate or both. Two options for multi-select: either snap all to the first selection or snap the last selection to the average of the first selections
########################

import maya.cmds as cmds
from functools import partial

widgets = {}

def snapUI():
    """simple snap UI for snapping"""

    if cmds.window("snapWin", exists=True):
        cmds.deleteUI("snapWin", window=True)
        cmds.windowPref("snapWin", remove=True)

    widgets["win"] = cmds.window("snapWin", t="zbw_snap", w=210, h=100, rtf=True)
    widgets["mainCLO"] = cmds.columnLayout(w=210, h=100)
    cmds.text("Select the target object(s),\nthen the object(s) you want to snap", al="center", w=210)
    cmds.separator(h=5, style="single")
    widgets["cbg"] = cmds.checkBoxGrp(l="Options: ", ncb=2, v1=1, v2=1, l1="Translate", l2="Rotate", cal=[(1,"left"),(2,"left"), (3,"left")], cw=[(1,50),(2,75),(3,75)])
    widgets["avgRBG"] = cmds.radioButtonGrp(nrb=2, l1="Snap all to first", l2="Snap last to avg", cal=[(1,"left"),(2,"left"),(3,"left")], cw=[(1,100),(2,100)],sl=1)
    widgets["rpCB"] = cmds.checkBox(l="Use Rotate Pivot To Query Position?", v=1)
    widgets["snapPivCB"] = cmds.checkBox(l="Snap via pivot? (vs. translate value)", v=1)
    cmds.separator(h=5, style="single")
    widgets["snapButton"] = cmds.button(l="Snap obj(s)!", w=210, h=40, bgc=(.6,.8,.6), c=partial(snapIt, False))
    widgets["snapPivButton"] = cmds.button(l="Snap pivot!", w=210, h=20, bgc=(.8,.6,.6), c=partial(snapIt, True))

    cmds.window(widgets["win"], e=True, w=5, h=5)
    cmds.showWindow(widgets["win"])    

def snapIt(pivt=False, *args):
    """
    Does the snapping by xform. Should work with any rotation order, etc
    
    Args:
        piv (bool): a boolean for whether to snap the actual object or just pivot. True = Pivot only, False = Transform

    """
    
    mode = cmds.radioButtonGrp(widgets["avgRBG"], q=True, sl=True)

    translate = cmds.checkBoxGrp(widgets["cbg"], q=True, v1=True)
    rotate = cmds.checkBoxGrp(widgets["cbg"], q=True, v2=True)
    pivot = cmds.checkBox(widgets["rpCB"], q=True, v=True)
    moveViaPivot = cmds.checkBox(widgets["snapPivCB"], q=True, v=True)

    sel = cmds.ls(sl=True, fl=True)
    if len(sel) < 2:
        return()
    # get pt components for later
    selPts = cmds.filterExpand(sm=(31, 28, 30, 35, 46, 47, 51), ex=True)
    # remove these from selection (faces and edges)
    selEdgeFace = cmds.filterExpand(sm=(32, 34))
    
    if mode==1: # all to first

        target = sel[0]
        objects = sel[1:]
        
        for x in objects: # get rid of faces and edges (return weird positions)
            if selEdgeFace and (x in selEdgeFace):
                objects.remove(x)
            if selEdgeFace and (x in selPts):
                objects.remove(x)

        targetPos = (0,0,0)
        
        if selPts and (target in selPts):
            targetPos = cmds.pointPosition(target)
        elif pivot:
            targetPos = cmds.xform(target, ws=True, q=True, rp=True)
        else:
            targetPos = cmds.xform(target, ws=True, q=True, t=True)


        tarRot = cmds.xform(target, ws=True, q=True, ro=True)
        tarRO = cmds.xform(target, q=True, roo=True)

        for obj in objects:
            if rotate:
                cmds.select(obj, r=True)                
                objRO = cmds.xform(obj, q=True, roo=True)
                # if not pivt:
                cmds.xform(obj, roo=tarRO)
                cmds.xform(obj, ws=True, ro=tarRot)
                cmds.xform(obj, roo=objRO, p=True)

            if translate:
                if pivt:
                    cmds.xform(obj, ws=True, a=True, piv=targetPos, p=True)
                else:
                    if not moveViaPivot:
                        cmds.xform(obj, ws=True, t=targetPos)
                    else:
                        objPiv = cmds.xform(obj, q=True, ws=True, rp=True)
                        objTrans = cmds.xform(obj, q=True, ws=True, t=True)
                        endPos = (objTrans[0]-objPiv[0]+targetPos[0], objTrans[1]-objPiv[1]+targetPos[1], objTrans[2]-objPiv[2]+targetPos[2])
                        cmds.xform(obj, ws=True, t=endPos)

        cmds.select(objects, r=True)

    else:
        if (len(sel)>=2):
            objects = sel[0:-1]
            target = sel[-1:][0]

            for x in objects:
                if selEdgeFace and (x in selEdgeFace):
                    objects.remove(x)

            tarRO = cmds.xform(target, q=True, roo=True)

            txList = []
            tyList = []
            tzList = []
            rxList = []
            ryList = []
            rzList = []
            TX, TY, TZ, RX, RY, RZ = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            for obj in objects:
                component = False
                if selPts and (obj in selPts):
                     component = True

                if pivot and not component:
                    objPos = cmds.xform(obj, q=True, ws=True, rp=True)
                if (not pivot and not component) or component:
                    objPos = cmds.xform(obj, q=True, ws=True, t=True)

                txList.append(objPos[0])
                tyList.append(objPos[1])
                tzList.append(objPos[2])

                #convert it to the rot order of the target
                objRO = cmds.xform(obj, q=True, roo=True)
                cmds.xform(obj, p=True, roo=objRO)
                #get the rotation
                objRot = cmds.xform(obj, q=True, ws=True, ro=True)
                rxList.append(objRot[0])
                ryList.append(objRot[1])
                rzList.append(objRot[2])
                #convert it back
                cmds.xform(obj, p=True, roo=objRO)

            #now average them all
            for tx in txList:
                TX += tx
            for ty in tyList:
                TY += ty
            for tz in tzList:
                TZ += tz
            for rx in rxList:
                RX += rx
            for ry in ryList:
                RY += ry
            for rz in rzList:
                RZ += rz

            avgTx = TX/len(txList)
            avgTy = TY/len(tyList)
            avgTz = TZ/len(tzList)
            avgRx = RX/len(rxList)
            avgRy = RY/len(ryList)
            avgRz = RZ/len(rzList)

            if rotate:
                cmds.select(target, r=True)
                cmds.xform(target, ws=True, ro=(avgRx, avgRy, avgRz))

            if translate:
                cmds.select(target, r=True)
                if not pivt:
                    cmds.xform(target, ws=True, t=(avgTx, avgTy,avgTz))
                else:
                    cmds.xform(target, ws=True, piv=(avgTx, avgTy, avgTz), p=True)

        else:
            cmds.warning("You need to select two objects or more!")

        cmds.select(target, r=True)

def snap(*args):
    """function to run the script"""
    snapUI()