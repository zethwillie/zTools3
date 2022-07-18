import maya.cmds as cmds
import zTools.rig.zbw_rig as rig

sel = cmds.ls(sl=True)

def make_locs(selList, *args):
    for crv in selList:
        cvs = cmds.ls("{0}.cv[*]".format(crv), fl=True)
        locs = []
        locGrps = []
        for x in range(len(cvs)):
            # make loc
            name = str(crv)+"_loc_"+str(x)
            loc = cmds.spaceLocator(name=name)[0]
            pos = cmds.pointPosition(cvs[x])
            cmds.xform(loc, ws=True, t=pos)
            locGrp = rig.group_freeze(loc)
            locShp = cmds.listRelatives(loc, s=True)[0]
            
            cmds.connectAttr(locShp + ".worldPosition[0]", cvs[x])
            
            locs.append(loc)
            locGrps.append(locGrp)
            
        return(locs, locGrp)
            
def make_controls(locs, *args):
    ctrls = []
    ctrlGrp = []
    for loc in locs:
        name = loc.replace("loc", "CTRL")
        ctrl = rig.create_control(type="sphere", name=name, color="red")
        grp = rig.group_freeze(ctrl)
        
        rig.snap_to(loc, grp)
        
        cmds.connectAttr(ctrl+".t", loc+".t")
        cmds.connectAttr(ctrl+".r", loc+".r")
        cmds.connectAttr(ctrl+".s", loc+".s")
        
        locGrp = cmds.listRelatives(loc, p=True)
        rig.snap_to(grp, locGrp)
        
        ctrls.append(ctrl)
        ctrlGrp.append(grp)    
        
    return(ctrls, ctrlGrp)
    
locs, locGrps = make_locs(sel)
ctrls, ctrlGrps = make_controls(locs) 
    
        