import maya.cmds as mc

# run zbw_clash.clash(1) to fix clashes, run zbw_clash.clash(0) to just tell you about them


def nameFix(name, verbose):
    """
    for xforms - this will take a base name (ie.'pCube') and find all instances of that and rename by appending a number, starting with the deepest instances in the DAG hier, so as not to bollocks up the later searches by changing items on top of obj
    """
    mayaObjs = mc.ls(name)
    # print("---------\nI'm in nameFix for: {0}, and there are --{1}-- instances of this clash".format(name, mayaObjs.sort(key=lambda a: a.count("|"), reverse=True)))  # this sorts by greatest number of "|"

    # if mayaObjs:
    #     if len(mayaObjs) > 1:
    #         for x in range(0, len(mayaObjs) - 1):
    #             mc.rename(mayaObjs[x], "{0}_{1}".format(mayaObjs[x].rpartition("|")[2], x))
    #             if verbose:
    #                 print("zbw_clash.nameFix: Changed name of {0} --> {1}".format(mayaObjs[x], "{0}_{1}".format(mayaObjs[x].rpartition("|")[2], x)))
    for obj in mayaObjs:
        newName = make_unique_name(name)
        mc.rename(obj, newName)
        if verbose:
            print("changing name of {0} ---> {1}".format(obj, newName))


def make_unique_name(name):
    """
    if int not at end of namespace, we'll add it, then version up til we're good, this should insure a clean name in scene
    """
    if not mc.objExists(name):
        return(name)
    new_name = increment_by_training_int(name)  # increments by one
    return(make_unique_name(new_name))


def increment_by_training_int(name):
    """
    if doesn't end in int, put it there. If it does increment while keeping padding
    """
    index = None
    for i in range(len(name), 0, -1):
        try:
            int(name[i - 1])
            continue
        except:
            index = i - 1
            break
    if not index == len(name) - 1:
        incr = str(int(name[index + 1:]) + 1)
        pad = len(name) - (index + 1)
        paddedIncr = incr.zfill(pad)
        return("{0}{1}".format(name[:index + 1], paddedIncr))
    else:
        return("{0}1".format(name))


def detect_clashes(fixClashes=True, verbose=True):
    """
    look in the scene and returns a list of names that clash (transform only, as shapes will get taken care of by renaming or another pass of cleaning shapes)
    """
    clashingNames = []
    clashingFullNames = []
    mayaResolvedName = {}

    allDagNodes = mc.ls(dag=1)  # get all dag nodes
    for node in allDagNodes:
        if mc.objectType(node) == "transform":  # only transforms
            if len(node.split("|")) > 1:  # is it a dupe (split by "|")
                clashingNames.append(node.split("|")[-1])  # add it to the list
                clashingFullNames.append(node)
    clashes = set(clashingNames)  # get rid of dupes, so only one of each name
    if verbose:
        print("\n===========================")
        print(("Clashing objects: {}".format(list(clashes))))

    if fixClashes and clashes:
        fix_first_clash(clashes=clashes, shapes=False, verbose=verbose)

    elif clashes and not fixClashes and verbose:
        for clash in clashes:
            print(("CLASH -->", clash))
            print((mc.ls(clash)))
        return(clashingFullNames)

    elif clashes and not fixClashes and not verbose:
        return(clashingFullNames)

    if not clashes and verbose:
        mc.warning("No transform clashes found")

        return([])
    else:
        return([])


def detect_clash_shapes(fixClashes=False, verbose=True):
    """
    look in the scene and returns a list of shapes that clash. Instances will be skipped (shapes w/ >1 xforms)
    """
    clashingNames = []
    clashingFullNames = []

    allDagNodes = mc.ls(dag=1, shapes=True)  # get all shapes
    for node in allDagNodes:
        if len(node.split("|")) > 1:  # ie. if there are duplicate names
            if len(mc.listRelatives(node, ap=True)) == 1:  # if shape does NOT have more than 1 parent (ie. not an instance)
                clashingNames.append(node.split("|")[-1])
                clashingFullNames.append(node)

    clashes = list(set(clashingNames))
    if verbose:
        print("\n===========================")
        print(("Clashing shapes: {}".format(clashes)))

    if fixClashes and clashes:
        fix_shape_clashes(clashes=clashes, verbose=verbose)
        # fix_first_clash(clashes=clashes, shapes=True)

    if clashes and not fixClashes and verbose:
        for clash in clashes:
            print(("SHAPE CLASH -->", clash))
            print((mc.ls(clash)))
        return(clashingFullNames)
    elif clashes and not fixClashes and not verbose:
        return(clashingFullNames)

    if not clashes and verbose:
        mc.warning("No shape clashes found")


def fix_shape_clashes(clashes=[], verbose=True):
    for clashName in clashes:
        badShapes = mc.ls("*|{0}".format(clashName))
        for shape in badShapes:
            parent = mc.listRelatives(shape, p=True)[0]
            newShape = None
            if not newShape:
                newShape = "{0}Shape".format(parent)
            mc.rename(shape, newShape)
            if verbose:
                print("zbw_clash.fix_shape_clashes: Changed name of {0} ---> {1}".format(shape, newShape))


def fix_first_clash(clashes=[], shapes=True, verbose=True):
    """
    takes in list of base names that are clashing (ie. "pSphere1", meaning that there are multiple instances of this name), if there's more than one clash in the list, redo the clash detection to make sure names stay relevant
    """

    clashList = list(clashes)

    if shapes == 0:
        nameFix(clashList[0], verbose)

        if len(clashList) > 1:
            detect_clashes(fixClashes=True, verbose=True)

    if shapes:
        nameFix(clashList[0], verbose)

        if len(clashList) > 1:
            detect_clash_shapes()


def clash(fixClashes=True, verbose=True):
    """
    launch the clash detecting/fixing. Only argument is whether to fix the clashes or not (1/0)
    """

    clashes = detect_clashes(fixClashes, verbose)
    if fixClashes and clashes:  # if we are fixing things, do one more pass to make sure
        detect_clashes(fixClashes, verbose)

    detect_clash_shapes(fixClashes, verbose)
