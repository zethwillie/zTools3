########################
# File: zbw_jointsOnCurveSetup.py
# Date Modified: 17 Mar 2017
# creator: Zeth Willie
# Contact: zethwillie@gmail.com, catbuks.com, williework.blogspot.com
# Description: puts joints along a curve and binds them. Fine ctrls and large ctrls.
# To Run: type "import zTools.zbw_jointsOnCurveSetup as zbw_jointsOnCurveSetup; reload(zbw_jointsOnCurveSetup);zbw_jointsOnCurveSetup.jointsOnCurveSetup()"
########################


import maya.cmds as cmds
import maya.mel as mel
import zTools3.rig.zbw_rig as rig

#---------------- first bind to a joint with post weighting
#---------------- after all, then set initial joint to zero

#---------------- ui should have the abil to change num of cv's per fine ctrl, and num of fine ctrls per large ctrl and weight all accordingly
#================= need to orient the joints along the curve

def create_ctrls():
    sel = cmds.ls(sl=True)[0]

    cvs = cmds.ls("{0}.cv[*]".format(sel), fl=True)
    jnts = []
    ctrls = []
    grps = []

    masterGrp = cmds.group(em=True, name="{0}_fineCtrls_GRP".format(sel))

    cmds.select(cl=True)
    initialJnt = cmds.joint(name="{0}_initJnt".format(sel), p=(0, 0, 0))
    cmds.setAttr("{0}.v".format(initialJnt), 0)
    cls = cmds.skinCluster(initialJnt, sel, normalizeWeights=2)[0]
    print(("++++++++++++++++++ ", cls))

    for i in range(0, len(cvs), 3):
        nextCvs = []
        weights = []        
        if i == 0:
            # create a joint with those 3
            nextCvs = [cvs[0], cvs[1], cvs[2]]
            weights = [1.0, .67, .33]
            # create_joints(nextCvs, weights)
        else:
            nextCvs = [cvs[i]]
            weights = [1, .33, .33, .67, .67]
            for j in range(2, 0, -1):
                nextCvs.append(cvs[i-j])
                try:
                    nextCvs.append(cvs[i+j])
                except:
                    pass
        jnt, ctrl, grp = create_joint(nextCvs, weights)
        jnts.append(jnt)
        ctrls.append(ctrl)
        grps.append(grp)

        cmds.parent(grp, masterGrp)

    # cls = mel.eval("findRelatedSkinCluster " + sel)
    for cv in cvs:
        cmds.skinPercent(cls, cv, transformValue=[initialJnt, 0])

    cmds.skinCluster(cls, e=True, forceNormalizeWeights=True)
    cmds.parent(initialJnt, masterGrp)

    geoGrp = cmds.group(em=True, name="{0}_geo_grp".format(sel))
    cmds.setAttr("{0}.inheritsTransform".format(geoGrp), 0)
    cmds.parent(sel, geoGrp)

    l_ctrls = larger_ctrls(grps, sel)

    # create master ctrl
    master = rig.create_control(type="star", color="blue", name="{0}_master_CTRL".format(sel))
    rig.group_freeze(master)

    cmds.addAttr(master, ln="showFineCtrls", at="long", min=0, max=1, dv=0, k=True)
    cmds.addAttr(master, ln="showLargeCtrls", at="long", min=0, max=1, dv=0, k=True)

    for g in grps:
        cmds.connectAttr("{0}.showFineCtrls".format(master), "{0}.v".format(g))
    for l in l_ctrls[1]:
        cmds.connectAttr("{0}.showLargeCtrls".format(master), "{0}.v".format(l))

    cmds.parent(l_ctrls[0], master)
    cmds.parent(geoGrp, master)
    cmds.parent(masterGrp, master)


def larger_ctrls(grps, sel):
    # create controls for every 10? ctrls, get center then get nearest point on curve?
    ctrlNodes = []
    bigCtrls = []
    l_ctrl_grp = cmds.group(em=True, name="{0}_ctrlRigGrp".format(sel))

    ctrlNodes.append(grps[-1]) # add last grp
    for i in range(0, len(grps)-1, 10):
        local = []
        pos = (0,0,0)
        # print "-------- I'm on i: {0}".format(i)
        if grps[i] not in ctrlNodes: # if not (last), add grp to ctrlNodes
            ctrlNodes.insert(-1, grps[i])
        if i == 0:
            # set pc from 0-10
            pcwgts = [1, .9, .8, .7, .6, .5, .4, .3, .2 ,.1]
            local = grps[0:10]
            list(set(local))
            pos = get_center_point(local)
            box = rig.create_control(name="{0}_largeCtrl_{1}".format(sel, i), type="cube", color="green")
            grp = cmds.group(em=True, name="{0}_GRP".format(box))
            cmds.parent(box, grp)
            cmds.xform(grp, ws=True, t=pos)
            for k in range(len(local)):
                pc = cmds.parentConstraint(box, local[k], mo=True, w=pcwgts[k])
            bigCtrls.append(grp)
            # print "zero: ({0}): ".format(len(local))+ str(local)
        elif i == 10:
            # only set front from 5-9, back from 10-19
            pcwgts = [.1, .2, .4, .6, .8, 1, .9, .8, .7, .6, .5, .4, .3, .2, .1]              
            for j in grps[5:10]:
                local.append(j)
            for j in grps[10:20]:
                local.append(j)
            list(set(local))
            pos = get_center_point(local)
            box = rig.create_control(name="{0}_largeCtrl_{1}".format(sel, i), type="cube", color="green")
            grp = cmds.group(em=True, name="{0}_GRP".format(box))
            cmds.parent(box, grp)
            cmds.xform(grp, ws=True, t=pos)           
            for k in range(len(local)):
                pc = cmds.parentConstraint(box, local[k], mo=True, w=pcwgts[k])
            bigCtrls.append(grp)                
            # print "one ({0}): ".format(len(local)) + str(local)
        elif i == len(ctrlNodes)-1: # last
            pcwgts = [.2, .4, .6, .8, 1]              
            local = grps[-5:]
            list(set(local))
            pos = get_center_point(local)
            box = rig.create_control(name="{0}_largeCtrl_{1}".format(sel, i), type="cube", color="green")
            grp = cmds.group(em=True, name="{0}_GRP".format(box))
            cmds.parent(box, grp)
            cmds.xform(grp, ws=True, t=pos)
            for k in range(len(local)):
                pc = cmds.parentConstraint(box, local[k], mo=True, w=pcwgts[k])
            bigCtrls.append(grp)                
            # print "second ({0}): ".format(len(local)) + str(local)
        elif i == len(ctrlNodes)-2: # second to last
            pcwgts = [.1, .2, .3, .4, .5, .6, .7, .8, .9, 1, .9, .8, .7, .6, .5, .4, .3, .2, .1]        
            for j in grps[i-1:i-10]:
                local.append(j)
            for j in grps[i:len(grps)-4]:
                local.append(j)
            list(set(local))
            pos = get_center_point(local)
            box = rig.create_control(name="{0}_largeCtrl_{1}".format(sel, i), type="cube", color="green")
            grp = cmds.group(em=True, name="{0}_GRP".format(box))
            cmds.parent(box, grp)
            cmds.xform(grp, ws=True, t=pos)           
            for obj in local:
                pc = cmds.parentConstraint(box, local[k], mo=True, w=pcwgts[k])
            bigCtrls.append(grp)                
            # print "second ({0}): ".format(len(local)) + str(local)
        else:
            pcwgts = [.1, .2, .3, .4, .5, .6, .7, .8, .9, 1, .9, .8, .7, .6, .5, .4, .3, .2, .1]
            for j in grps[i-10:i]: # all of these go from grps-9, ctrlNode, grps+9
                local.append(j)
            for j in grps[i:i+9]:
                local.append(j)
            list(set(local))
            pos = get_center_point(local)
            box = rig.create_control(name="{0}_largeCtrl_{1}".format(sel, i), type="cube", color="green")
            grp = cmds.group(em=True, name="{0}_GRP".format(box))
            cmds.parent(box, grp)
            cmds.xform(grp, ws=True, t=pos)           
            for k in range(len(local)):
                pc = cmds.parentConstraint(box, local[k], mo=True, w=pcwgts[k])
            bigCtrls.append(grp)
            # print "{0} ({1}): ".format(len(local), i) + str(local) 

    for c in bigCtrls:
        cmds.parent(c, l_ctrl_grp)

    return(l_ctrl_grp, bigCtrls)


def get_center_point(objs):
    positions = []
    for obj in objs:
        positions.append(cmds.xform(obj, ws=True, q=True, rp=True))
    center = [sum(y)/len(y) for y in zip(*positions)]
    return(center)


def create_joint(cvs, wts):
    tform = cvs[0].partition(".")[0]
    curve = cmds.listRelatives(tform, f=True, s=True)[0]
    
    ps = []
    center = []
    for cv in cvs:
        ps.append(cmds.pointPosition(cv))
        center = [sum(y)/len(y) for y in zip(*ps)]
    
    #create joint at location
    # ----------- should get closest point on surface   
    cmds.select(cl=True)    
    jnt = cmds.joint()
    cmds.xform(jnt, ws=True, t=center)
    
#---------------- orient the joint along the curve?
#---------------- here create the ctrl set up for the joint
    
    ctrl = rig.create_control(name="{0}Ctrl".format(jnt), type="sphere", color="red")
    grp = cmds.group(name="{0}Grp".format(ctrl), em=True)
    cmds.parent(ctrl, grp)
    cmds.xform(grp, ws=True, t=center)
    cmds.parent(jnt, ctrl)

    # scale the control
    comps = cmds.ls("{0}.cv[*]".format(ctrl))
    cmds.select(comps, r=True)
    cmds.scale(.2,.2,.2)

    #add influence to skin Cluster
    cmds.select(tform, r=True)
    cmds.skinCluster(e=True, ai=jnt, wt=0)
    
    cmds.setAttr("{0}.v".format(jnt), 0)

    #apply weights to that joint
    cls = mel.eval("findRelatedSkinCluster " + tform)
    for v in range(len(cvs)):
        cmds.skinPercent(cls, cvs[v], transformValue=[jnt, wts[v]])

    return(jnt, ctrl, grp)