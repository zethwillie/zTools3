import maya.cmds as cmds

# transfers anim from top level down from selection 1 to selection 2. 
# Anim curves will now have TWO outputs, one to each rig

sel = cmds.ls(sl=True)

sel1 = sel[0]
sel1all = cmds.listRelatives(sel1, ad=True, f=True, type="nurbsCurve")
sel1crvs = [cmds.listRelatives(x, p=True)[0] for x in sel1all]

sel2 = sel[1]
sel2all = cmds.listRelatives(sel2, ad=True, f=True, type="nurbsCurve")
sel2crvs = [cmds.listRelatives(x, p=True)[0] for x in sel2all]

# ideally duplicate the existing anim curve and THEN apply
for y in range(len(sel1crvs)):
    attrs = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
    for attr in attrs:
        val = cmds.getAttr("{0}.{1}".format(sel1crvs[y], attr))
        cmds.setAttr("{0}.{1}".format(sel2crvs[y], attr), val) 
    anmList = cmds.listConnections(sel1crvs[y], s=True, d=False, p=True, type="animCurve")
    if anmList:
        for x in range(len(anmList)):
            cons = cmds.listConnections(anmList[x], s=False, d=True, p=True)
            if cons:
                for con in cons:
                    # should instead of this, dupe anim crv here and then apply that
                    cmds.connectAttr(anmList[x], "{0}.{1}".format(sel2crvs[y], con.partition(".")[2]))