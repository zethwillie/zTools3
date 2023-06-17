import maya.cmds as mc
import maya.mel as mel

"""
for copying skin weighting and/or constraints from existing to new geo.

"""

def swap_bind_geo(namespace="", levels=2, longname=False):
    """
    select the top node and this will get all polys under that node and find the comparable geo under the given namspace. For each poly it will find the bind joints, bind to them, and copy the skinning (& weights) to the namespace geo
    ARGS:
        namespace (str): the namespace of the new geo to bind
        levels (int): number of hierarchy levels to discount (grps in the rig above the geo top group). This is to ignore groups in the rig before you get to the geo section
        longname (bool): should we use longnames for geo (i.e. with pipes |). Don't need this if we're checking for name clashing
    """
    if not namespace:
        return()
    # select top node and drill down to get all geo
    sel = mc.ls(sl=True)
    if not sel:
        return()
    top_node = sel[0]
    geo = select_hierarchy(top_node, "poly")

    for g in geo:
        if longname:
            origGeo = g
            split = g.split("|")[1:]
            ns_split = [namespace + ":" + x for x in split[levels:]]
            outGeo = "|" + "|".join(ns_split)
            if not mc.objExists(outGeo):
                print("Couldn't find namespace version: {0}".format(ns_geo))
                continue
        else:
            origGeo = g.split("|")[-1]
            outGeo = "{0}:{1}".format(namespace, origGeo)

        if bind_check(origGeo):
            copy_skinning(origGeo, outGeo)

    print("Skin copying done!")
    mc.select(sel)


def swap_constraint_geo(namespace="", levels=2, longname=False):
    """
    select the top node and this will get all nodes under that node and find the comparable node under the given namspace. For each node it will then find any (*not aim) constraints and add constraints to the new geo from the same sources w same weights.
    ARGS:
        namespace (str): the namespace of the new geo to bind
        levels (int): number of hierarchy levels to discount (grps in the rig above the geo top group)
        longname (bool): should we use longnames for geo (i.e. with pipes |). Don't need this if we're checking for name clashing
    """
    if not namespace:
        return()
    sel = mc.ls(sl=True)
    if not sel:
        return()
    mc.select(sel[0]) # assume first selection as our base
    mc.select(hi=True)
    nodes = mc.ls(sl=True)
    for n in nodes:
        if "Constraint" in mc.objectType(n):
            continue
        if longname:
            origNode = n
            split = n.split("|")[1:]
            ns_split = [namespace + ":" + x for x in split[levels:]]
            outNode = "|" + "|".join(ns_split)
            if not mc.objExists(outNode):
                print("Couldn't find namespace version: {0}".format(ns_geo))
                continue
        else:
            origNode = n.split("|")[-1]
            outNode = "{0}:{1}".format(namespace, origNode)

        if constraint_check(origNode):
            cons = copy_constraints(origNode, outNode)
            print("== {0} constraints create: ".format(origNode), cons)
    print("Constraint copying done!")
    # check. . . if good, remove skinning from old, delete old geo


def constraint_check(node):
    cons = mc.listConnections(node, type="constraint")
    if cons:
        return(True)
    return(False)


def copy_constraints(orig_node, target_node, *args):
    """
    copies parent, scale, point and orient constraints from orig_node to target_node, copying weights and offsets
    """
    cons_raw = mc.listConnections(orig_node, type="constraint")
    if not cons_raw:
        return()
    if constraint_check(target_node):
        print("Existing constraints on {0}. Skipping!".format(target_node))
        return()
    created_constraints = []
    cons = list(set(cons_raw)) # get all constraints
    for con in cons:
        if mc.objectType(con) == "parentConstraint":
            pc = copy_parent_constraint(con, target_node)
            created_constraints.append(pc)

        if mc.objectType(con) == "pointConstraint":
            ptc = copy_point_constraint(con, target_node)
            created_constraints.append(ptc)

        if mc.objectType(con) == "orientConstraint":
            oc = copy_orient_constraint(con, target_node)
            created_constraints.append(oc)

        if mc.objectType(con) == "scaleConstraint":
            sc = copy_scale_constraint(con, target_node)
            created_constraints.append(sc)

    return(created_constraints)


def copy_parent_constraint(con, target_node):
    tgtList = mc.parentConstraint(con, q=True, targetList=True)
    wgtAliasList = mc.parentConstraint(con, q=True, weightAliasList=True)
    weights = []
    for z, tgt in enumerate(tgtList):
        wgt = mc.getAttr("{0}.{1}".format(con, wgtAliasList[z]))
        weights.append(wgt)
    pc = mc.parentConstraint(tgtList, target_node, mo=True)
    newWeightAliasList = mc.parentConstraint(con, q=True, weightAliasList=True)
    for x in range(len(newWeightAliasList)):
        mc.setAttr("{0}.{1}".format(pc[0], newWeightAliasList[x]), weights[x])
        t = mc.getAttr(con+ f".target[{x}].targetOffsetTranslate")[0]
        r = mc.getAttr(con+ f".target[{x}].targetOffsetRotate")[0]
        mc.setAttr(pc[0] + f".target[{x}].targetOffsetTranslate", t[0], t[1], t[2])
        mc.setAttr(pc[0] + f".target[{x}].targetOffsetRotate", r[0], r[1], r[2])
    return(pc[0])


def copy_orient_constraint(con, target_node):
    tgtList = mc.orientConstraint(con, q=True, targetList=True)
    wgtAliasList = mc.orientConstraint(con, q=True, weightAliasList=True)
    weights = []
    for z, tgt in enumerate(tgtList):
        wgt = mc.getAttr("{0}.{1}".format(con, wgtAliasList[z]))
        weights.append(wgt)
    oc = mc.orientConstraint(tgtList, target_node, mo=True)
    newWeightAliasList = mc.orientConstraint(con, q=True, weightAliasList=True)
    for x in range(len(newWeightAliasList)):
        mc.setAttr("{0}.{1}".format(oc[0], newWeightAliasList[x]), weights[x])
    r = mc.getAttr(con + ".offset")[0]
    rr = mc.getAttr(con + ".restRotate")[0]
    mc.setAttr(oc[0] + ".offset", r[0], r[1], r[2])
    mc.setAttr(oc[0] + ".restRotate", rr[0], rr[1], rr[2])
    return(oc[0])


def copy_point_constraint(con, target_node):
    tgtList = mc.pointConstraint(con, q=True, targetList=True)
    wgtAliasList = mc.pointConstraint(con, q=True, weightAliasList=True)
    weights = []
    for z, tgt in enumerate(tgtList):
        wgt = mc.getAttr("{0}.{1}".format(con, wgtAliasList[z]))
        weights.append(wgt)
    ptc = mc.pointConstraint(tgtList, target_node, mo=True)
    newWeightAliasList = mc.pointConstraint(con, q=True, weightAliasList=True)
    for x in range(len(newWeightAliasList)):
        mc.setAttr("{0}.{1}".format(ptc[0], newWeightAliasList[x]), weights[x])
    t = mc.getAttr(con + ".offset")[0]
    p = mc.getAttr(con + ".constraintOffsetPolarity")
    mc.setAttr(ptc[0] + ".offset", t[0], t[1], t[2])
    mc.setAttr(ptc[0] + ".constraintOffsetPolarity", p)
    return(ptc[0])


def copy_scale_constraint(con, target_node):
    tgtList = mc.scaleConstraint(con, q=True, targetList=True)
    wgtAliasList = mc.scaleConstraint(con, q=True, weightAliasList=True)
    weights = []
    for z, tgt in enumerate(tgtList):
        wgt = mc.getAttr("{0}.{1}".format(con, wgtAliasList[z]))
        weights.append(wgt)
    sc = mc.scaleConstraint(tgtList, target_node, mo=True)
    newWeightAliasList = mc.scaleConstraint(con, q=True, weightAliasList=True)
    for x in range(len(newWeightAliasList)):
        mc.setAttr("{0}.{1}".format(sc[0], newWeightAliasList[x]), weights[x])
    s = mc.getAttr(con+ ".offset")[0]
    mc.setAttr(sc[0] + ".offset", s[0], s[1], s[2])
    return(sc[0])


def bind_check(geo):
    try:
        mc.skinCluster(geo, q=True, influence=True)
        return(True)
    except:
        # print("Couldn't find bind on {0}".format(geo))
        return(False)


def select_hierarchy(top_node, sType, *args):
    selectList = []

    xforms = []
    cshps = None

    if sType == "poly":
        cshps = mc.listRelatives(top_node, allDescendents=True, f=True, type="mesh")
    if cshps:
        for cshp in cshps:
            if not "Orig" in cshp:
                xf = mc.listRelatives(cshp, p=True, f=True)[0]
                xforms.append(xf)

    if xforms:
        # sort list by greatest number of path splits first (deepest)
        xforms.sort(key=lambda a: a.count("|"), reverse=True)
        list(set(xforms))
        for x in xforms:
            selectList.append(x)
    return(selectList)


def copy_skinning(orig_geo, new_geo, *args):
    """select the orig bound mesh, then the new unbound target mesh and run"""
    try:
        jnts = mc.skinCluster(orig_geo, q=True, influence=True)
        method = mc.skinCluster(orig_geo, q=True, skinMethod=True)
    except:
        mc.warning("couldn't get skin weights from {0}".format(orig_geo))
    try:
        targetClus = mc.skinCluster(
            jnts,
            new_geo,
            bindMethod=0,
            skinMethod=method,
            normalizeWeights=1,
            maximumInfluences=3,
            obeyMaxInfluences=False,
            tsb=True,
        )[0]
    except:
        mc.warning("couln't bind to {}".format(new_geo))
    origClus = mel.eval("findRelatedSkinCluster " + orig_geo)
    # copy skin weights from orig_geo to new_geo
    try:
        mc.copySkinWeights(
            ss=origClus,
            ds=targetClus,
            noMirror=True,
            sa="closestPoint",
            ia="closestJoint",
        )
        print("=== copied skin from {0} to {1}".format(orig_geo, new_geo))
    except:
        mc.warning(
            "couldn't copy skin weights from {0} to {1}".format(orig_geo, new_geo)
        )