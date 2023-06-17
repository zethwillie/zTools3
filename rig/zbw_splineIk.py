# start to figure out how to create a spline IK from a line
# rebuildCurve (uniform, 0-1)

import maya.cmds as cmds
import maya.mel as mel
import zTools3.resources.zbw_math as mth
import zTools3.zbw_rig as rig


# name rig, num jnts
# get inputCurve
# rebuildCurve
# analyze curve 
# place joints, parent
# orient joints
# fix orientations
# dupe joint chain (rpJnts[aka bindjnts?])

# num main ctrls, num secondary ctrls
# ctrl system for rig

# second joints get rp_iks
# stretch per joint
# connect rpiks to controls (parent constraints)



def splineIkUI(*args):
    splineIkBuild()

#---------------- get crv or create? from selection, draw tool, or curveFromEdge

def getUIValues(*args):
    pass


def splineIkBuild(*args):

    sel = cmds.ls(sl=True, type="transform")
    crv = sel[0]
    numJnts = 10

    jnts = createJointsAlongCurve(crv, numJnts)


def createJointsAlongCurve(crv="", numJnts=3, *args):
    jnts = []
    crvShp = cmds.listRelatives(crv, s=True)[0]
    poc = cmds.shadingNode("pointOnCurveInfo", asUtility=True, name="tmpPOCInfo")
    cmds.connectAttr("{}.local".format(crvShp), "{}.inputCurve".format(poc))
    cmds.setAttr("{}.turnOnPercentage".format(poc), 1)
    lineLen = cmds.arclen(crv)
    dist = float(numJnts)/lineLen

    for x in range(0, numJnts+1):
        perc = 1.0/numJnts
        cmds.setAttr("{}.parameter".format(poc),x*perc)
        # print x*perc
        pos = cmds.getAttr("{}.position".format(poc))[0]
        jnt = cmds.joint(p=pos)
        jnts.append(jnt)
        # add one joint at the end to orient	
    return(jnts)		


def orientJointChain(*args):
#---------------- this doens't actually work. dot doesn't represent the relationship btw orients
    cmds.joint(jnts[0], e=True, oj="xyz", secondaryAxisOrient="ydown", ch=True, zso=True)
  
    #print cmds.getAttr("{}.jointOrient".format(cmds.ls(sl=True)[0]))
    for y in range(1, len(jnts)):
        v1 = cmds.getAttr("{}.jointOrient".format(jnts[0]))[0]
        v2 = cmds.getAttr("{}.jointOrient".format(jnts[y]))[0]

        dotN = mth.dotN(v1, v2) # figure out how to reverse joint orientation
        if dotN < 0:
            print((jnts[y], "dot neg"))
            pass
        # reorient (inverse secondary axis)

    # for jnt in jnts:
    # 	print mth.dotN(cmds.getAttr("{}.jointOrient".format(jnts[0]))[0], cmds.getAttr("{}.jointOrient".format(jnt))[0])

def splineIk(*args):
    splineIkUI()



