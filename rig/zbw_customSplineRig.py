import zTools3.rig.zbw_rig as rig

sel = cmds.ls(sl=True)

"""
for obj in sel[1:]:
    #cmds.connectAttr("{0}.local".format(sel[0]), "{0}.inputCurve".format(obj))
    cmds.connectAttr("{0}.position".format(sel[0]), "{0}.translate".format(obj))
    
"""

"""
for x in range(len(sel)):
    cmds.select(cl=True)
    jnt = cmds.joint(name="jnt_{0}".format(x))
    grp = cmds.group(em=True, name="jnt_{0}_grp".format(x))
    cmds.parent(jnt, grp)
    ctrl = rig.createControl("ctrl_{0}".format(x), type="star", color="yellow")
    ctrlGrp = rig.groupFreeze(ctrl)
    cmds.parent(grp, ctrl)
    cmds.parent(ctrlGrp, sel[x])
    cmds.setAttr("{0}.t".format(ctrlGrp), 0, 0, 0)
"""
cmds.delete(cmds.ls(type="aimConstraint"))

sel = cmds.ls(sl=True)
for x in range(9):
    grp = cmds.listRelatives(sel[x], c=True, ad=False, s=False)[1]
    if x != 8:
        cmds.aimConstraint(sel[x+1], grp, aim=(0,1,0), wuo=sel[x+9], u=(0, 0, 1), wut="object")


#---------------- aim constraints are a problem. . . .
