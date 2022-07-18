import maya.cmds as cmds

"""
select the simmed objects (preferably in order) and run this. Will put at loc at the pivot point, parent constain to
    follow it, then bake the sim and delete the constraint
"""

# create a UI?

objList = cmds.ls(sl=True)

locList = []
pcList = []

# get the timeslider range
startF = cmds.playbackOptions(q=1, min=1)
endF = cmds.playbackOptions(q=1, max=1)

for x in range(0, len(objList)):
    obj = objList[x]
    locName = "unnamed_%i_LOC" % x

    trans = cmds.xform(obj, q=1, ws=1, rp=1)
    rot = cmds.xform(obj, q=1, ws=1, ro=1)
    scl = cmds.xform(obj, q=1, ws=1, s=1)

    try:
        locName = obj.partition("_obj")[0] + "_LOC_%i" % x
    except:
        pass

    print()
    "%s --->%s" % (locName, obj)

    # create a locator at obj pivot
    loc = cmds.spaceLocator(n=locName)
    cmds.xform(loc, ws=1, t=trans)
    cmds.xform(loc, ws=1, ro=rot)
    cmds.xform(loc, ws=1, s=scl)
    print()
    loc
    locList.append(loc[0])

    # parent constrain the each loc to the object
    pc = cmds.parentConstraint(obj, loc, mo=1)
    pcList.append(pc)

cmds.select(cl=1)
cmds.select(locList, r=True)
cmds.bakeResults(sm=1, t=(startF, endF))

for pc in pcList:
    cmds.delete(pc)
