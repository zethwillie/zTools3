import maya.cmds as cmds
import maya.mel as mel

# create option for using lattice?

def copy_skinning_multiple(*args):
    """select the orig bound mesh, then the new unbound target mesh and run"""

    sel = cmds.ls(sl=True)
    orig = sel[0]
    targets = sel[1:]

    for target in targets:
        try:
            jnts = cmds.skinCluster(orig, q=True, influence=True)
        except:
            cmds.warning("couldn't get skin weights from {}".format(orig))
        try:
            targetClus = cmds.skinCluster(jnts, target, bindMethod=0, skinMethod=0,normalizeWeights=1, maximumInfluences=3,obeyMaxInfluences=False, tsb=True)[0]
        except:
            cmds.warning("couln't bind to {}".format(target))
        
        origClus = mel.eval("findRelatedSkinCluster " + orig)
        # copy skin weights from orig to target
        try:
            cmds.copySkinWeights(ss=origClus, ds=targetClus, noMirror=True,
                                 sa="closestPoint", ia="closestJoint")
        except:
            cmds.warning(
                "couldn't copy skin weights from {0} to {1}".format(orig, target))