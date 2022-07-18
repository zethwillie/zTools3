import maya.cmds as cmds
"""
takes anim on selected, applies it two levels down (ctrl-->grp-->ctrl), then removes it from first,
then parent/scale constrains selected to a loc at the origin (get rid of this part for making generic)
"""
sel = cmds.ls(sl=True)
if sel:
    loc = cmds.spaceLocator(name="groupMoveLocator")      
    for src in sel:
        chld = cmds.listRelatives(src, c=True, type="transform")
        if chld:
            tgtList = cmds.listRelatives(chld, c=True, f=True, pa=True, type="transform")
        if tgtList:
            tgt = tgtList[0]
            print(tgt)
            params = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
            for param in params:
                val = cmds.getAttr("{0}.{1}".format(src, param))
                cmds.setAttr("{0}.{1}".format(tgt, param), val)

            anmList = cmds.listConnections(src, s=True, d=False, p=True, type="animCurve")
    
            if anmList:
                for anm in anmList:
                    conList = cmds.listConnections(anm, s=False, d=True, p=True)
                    if conList:
                        for con in conList:
                            attr = con.partition(".")[2]
                            print("{0}.{1}".format(src, attr), " --> ", "{0}.{1}".format(tgt, attr))
                            old = "{0}.{1}".format(src, attr)
                            new = "{0}.{1}".format(tgt, attr)
                            # dupe anim crv here and then apply that
                            cmds.connectAttr(anm, new)
                            cmds.disconnectAttr(anm, old)
                            for param in params:
                                if param in ["sx", "sy", "sz"]:
                                    cmds.setAttr("{0}.{1}".format(src, param), 1)
                                else:
                                    cmds.setAttr("{0}.{1}".format(src, param), 0)
                            
            try:
                cmds.parentConstraint(loc, src, mo=True)
            except:
                warning("couldn't parent constrain {0} to the locator! Skipping".format(src))
            try:
                cmds.scaleConstraint(loc, src, mo=True)
            except:
                warning("couldn't scale constrain {0} to the locator! Skipping".format(src))                     
                            
                            