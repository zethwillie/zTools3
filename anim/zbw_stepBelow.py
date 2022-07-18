"""select master control and run script. It will take all nurbs curves under the master and step key them"""

#TO-DO----------------make zbw_anim as a base of code

#TO-DO---------------------make UI
#TO-DO---------------------using UI, give option for what type of tangents (so not just step) and time ranges(timeline or selected)
#TO-DO---------------------make sure it uses multiple selections (multiple objects selected)
#could just be option to select below? ? ? part of a bigger tool that does anim and blocking stuff. . . 


import maya.cmds as cmds

ctrls = []

startF = cmds.playbackOptions(query=True, min=True)
endF = cmds.playbackOptions(query=True, max=True)

#search for descendents to step. . . 
sel = cmds.ls(sl=True)

if sel:
    curveList = []
    for obj in sel:
        relsSh = cmds.listRelatives(obj, ad=True, f=True, type="nurbsCurve")
        for shape in relsSh:
            curve = cmds.listRelatives(shape, p=True, type="transform")
            curveList.append(curve)
        if curveList:
            for curve in curveList:
                ctrls.append(curve)
if ctrls:		
    for ctrl in ctrls:
        print(ctrl)
        cmds.keyTangent(ctrl, ott="step")