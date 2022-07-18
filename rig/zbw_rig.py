########################
# file: zbw_rig.py
# author: zeth willie
# contact: zethwillie@gmail.com, www.williework.blogspot.com
# date modified: 08/01/18
#
# notes: helper scripts for rigging
########################

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om

from . import zbw_controlShapes as cshp
import importlib
importlib.reload(cshp)

colors = {
    "red": 13,
    "blue": 6,
    "green": 14,
    "darkRed": 4,
    "lightRed": 31,
    "darkBlue": 5,
    "medBlue": 15,
    "lightBlue": 18,
    "royalBlue": 29,
    "darkGreen": 7,
    "medGreen": 27,
    "lightGreen": 19,
    "yellowGreen": 26,
    "yellow": 17,
    "darkYellow": 2,
    "lightYellow": 22,
    "purple": 30,
    "lightPurple": 9,
    "darkPurple": 8,
    "black": 1,
    "white": 16,
    "brown": 10,
    "darkBrown": 11,
    "lightBrown": 24,
    "pink": 20,
    "orange": 12}


def select_hierarchy(topNode=None, sType=None, *args):
    """
    select hierarchy by type
    if top node not given, will take each selection
    sTypes = ["curve", "poly", "joint"]
    Args:
        topNode (string): top level object of hierarchy
        sType (string): "curve", "poly", or "joint"
    """
    sel = None
    if topNode:
        sel = topNode
    else:
        sel = cmds.ls(sl=True, type="transform")
    if not sel:
        return()
    
    selectList = []
    for top in sel:
        xforms = []
        cshps = None
        if sType == "curve":
            cshps = cmds.listRelatives(top, allDescendents=True , f=True, type="nurbsCurve")
        elif sType == "poly":
            cshps = cmds.listRelatives(top, allDescendents=True , f=True, type="mesh")
        if cshps:
            for cshp in cshps:
                xf = cmds.listRelatives(cshp, p=True, f=True)[0]
                xforms.append(xf)
        elif sType == "joint":
            jnts = cmds.listRelatives(top, allDescendents=True, f=True, type="joint")
            if rig.type_check(top, "joint"):
                jnts.append(top)
            xforms = jnts

        if xforms:
            # sort list by greatest number of path splits first (deepest)
            xforms.sort(key=lambda a: a.count("|"), reverse=True)
            list(set(xforms))
            for x in xforms:
                selectList.append(x)

    cmds.select(selectList, r=True)
    return(selectList)


def get_two_selection(*args):
    """
    gets two objects (only first 2) from selection and returns them in selected order as a list
    """
    sel = cmds.ls(sl=True)
    if sel:
        objs = sel[:1]
    else:
        objs = []
    return objs


def joint_from_list(xformList=[], orient="xyz", secAxis="zup", strip="",
                    suffix="", *args):
    """
    uses the xformlist arg (a list of transforms in scene) to create a joint chain in order.
    Arguments: xformList (a list), orient ("xyz", etc), secAxis ("xup", "zdown", etc), strip (string to strip off), suffix (string to add to the joints)
    """
    jointList = []

    if not xformList:
        sel = getSelection()

        if sel:
            xformList = sel
        else:
            cmds.error(
                "you must provide a list of transforms or have the transforms selected in order")

    cmds.select(cl=True)
    for xform in xformList:
        xformPos = cmds.xform(xform, q=True, ws=True, t=True)
        jointName = "%s%s" % (xform.rstrip(strip), suffix)
        thisJoint = cmds.joint(n=jointName, p=xformPos)
        jointList.append(thisJoint)

    cmds.joint(jointList[0], e=True, ch=True, oj=orient, sao=secAxis)
    return (jointList)


def follicle(surface="none", name="none", u=0.5, v=0.5, *args):
    """
    creates a follicle on a surface based on the uv input.
    Args are: surface, name, u, v
    """
    # TODO------------ get from make follicle. that works for sure
    if surface == "none":
        # decide if surface is polymesh or nurbsSurface
        surfaceXform = cmds.ls(sl=True, dag=True, type="transform")[0]
        surfaceShape = cmds.listRelatives(surfaceXform, shapes=True)[0]
    else:
        surfaceXform = surface
        surfaceShape = cmds.listRelatives(surfaceXform, shapes=True)[0]

    if name == "none":
        folShapeName = "newFollicleShape"
        folXformName = "newFollicle"
    else:
        folShapeName = "%sShape" % name
        folXformName = name

        # ------------test if follicle exists - FIX THE INCREMENT SCRIPT TO WORK BETTER
        # if cmds.objExists(folXformName):
        #     increment_name(folXformName)

    # rename follicle xform (will rename shape, get shape name)

    # create the follicle
    folShape = cmds.createNode("follicle", n=folShapeName)
    folXform = cmds.listRelatives(folShape, p=True, type="transform")[0]
    # cmds.rename(folXform, folXformName)

    # connect up the follicle!
    # connect the matrix of the surface to the matrix of the follicle
    cmds.connectAttr("%s.worldMatrix[0]" % surfaceShape,
                     "%s.inputWorldMatrix" % folShape)

    # check for surface type, poly or nurbs and connect the matrix into the follicle
    if (cmds.nodeType(surfaceShape) == "nurbsSurface"):
        cmds.connectAttr("%s.local" % surfaceShape,
                         "%s.inputSurface" % folShape)
    elif (cmds.nodeType(surfaceShape) == "mesh"):
        cmds.connectAttr("%s.outMesh" % surfaceShape, "%s.inputMesh" % folShape)
    else:
        cmds.warning(
            "not the right kind of selection. Need a poly or nurbs surface")

    # connect the transl, rots from shape to transform of follicle
    cmds.connectAttr("%s.outTranslate" % folShape, "%s.translate" % folXform)
    cmds.connectAttr("%s.outRotate" % folShape, "%s.rotate" % folXform)

    cmds.setAttr("%s.parameterU" % folShape, u)
    cmds.setAttr("%s.parameterV" % folShape, v)

    cmds.setAttr("%s.translate" % folXform, l=True)
    cmds.setAttr("%s.rotate" % folXform, l=True)

    attrsToHide = ["restPose", "pointLock", "simulationMethod",
                   "startDirection", "flipDirection",
                   "overrideDynamics", "collide", "damp", "stiffness",
                   "lengthFlex", "clumpWidthMult",
                   "startCurveAttract", "attractionDamp", "densityMult",
                   "curlMult", "clumpTwistOffset",
                   "braid", "colorBlend", "colorR", "colorG", "colorB",
                   "fixedSegmentLength", "segmentLength",
                   "sampleDensity", "degree", "clumpWidth"]
    for attr in attrsToHide:
        cmds.setAttr("{0}.{1}".format(folShape, attr), k=False)

    return (folXform, folShape)


def axis_to_vector(axis="+x"):
    """
    takes an arg ("+x", "-x", "+y", "-y", "+z", "-z") and converts it to a vector (ex. (1,0,0))
    """
    axisDict = {
        "+x": (1, 0, 0), "-x": (-1, 0, 0), "+y": (0, 1, 0), "-y": (0, -1, 0),
        "+z": (0, 0, 1), "-z": (0, 0, -1)
    }
    if axis in list(axisDict.keys()):
        return (axisDict[axis])
    else:
        cmds.error("you need to enter an axis (i.e. '+x' or '-x'")


def create_fk_on_joint_chain(ctrlType="circle", color="red", axis="x", *args):
    """
    puts a correctly oriented control onto each joint of selected chain. Will name the controls after the joint names and parent them according to the joint order
    Select the top joint of a chain and call fkChain(ARGS)
    Arguments: ctrlType ("sphere", "circle", "cube", etc), color ("red", "darkRed",etc. See zbw_rig.createControl for full list), axis ("x", "y", "x")
    """

    sel = cmds.ls(sl=True, type="joint")

    ctrlList = []
    groupList = []

    if len(sel) != 1:
        cmds.error("please select only the top level joint of one chain")
    else:
        chain = cmds.ls(sl=True, type="joint")
        chainSize = len(chain)

        for jnt in chain:
            rotOrder = cmds.getAttr("%s.rotateOrder" % jnt)
            ctrlName = jnt + "_CTRL"
            ctrl = create_control(ctrlName, ctrlType, axis, color)
            grp = group_freeze(ctrl)
            snap_to(jnt, grp)
            cmds.orientConstraint(ctrl, jnt)
            cmds.setAttr("%s.rotateOrder" % ctrl, rotOrder)
            cmds.setAttr("%s.rotateOrder" % group, rotOrder)
            ctrlList.append(ctrl)
            groupList.append(group)

        for i in range(chainSize - 1, 0, -1):
            cmds.parent(groupList[i], ctrlList[i - 1])


# TODO   --- correct errors/warnings
def create_control(name="default", type="circle", axis="x", color="darkBlue",
                   *args):
    """
    creates control namemed by first arg, at origin.
    shape is determined by second arg: "cube", "octagon", "sphere", "diamond", "barbell", "lollipop", "cross", "bentCross", "arrow", "bentArrow", "halfCircle", "splitCircle", "cylinder", "square", "circle", "arrowCross"
    third arg can be 'x',, 'y', , 'z'  and is the axis along which the control lies.
    The colors are: 'lightBlue', 'darkGreen', 'lightPurple', 'yellow', 'darkPurple', 'pink', 'blue', 'purple', 'lightGreen', 'black', 'orange', 'white', 'darkYellow', 'brown', 'lightYellow', 'darkBlue', 'royalBlue', 'darkBrown', 'lightRed', 'medBlue', 'lightBrown', 'darkRed', 'yellowGreen', 'medGreen', 'green', 'red'
    ARGS:
        name(string):
        type(string): 
        axis(string): x, y or z
        color(string):
    RETURN:
        string: control name
    """

    # deal with axis, x is default
    if axis == "x":
        rot = (0, 0, 0)
    elif axis == "y":
        rot = (0, 0, 90)
    elif axis == "z":
        rot = (0, 90, 0)
    else:
        cmds.warning(
            'createControl: you entered an incorrect axis. Must be x, y or z')

    if type == "star":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["star"])

        cmds.closeCurve(ctrl, ps=0, rpo=1, bb=0.5, bki=0, p=0.1)

    elif type == "box" or type == "cube":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["cube"])

    elif type == "octagon":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["octagon"])

    elif type == "square":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["square"])

    elif type == "triangle":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["triangle"])

    elif type == "squarePyramid":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["squarePyramid"])

    elif type == "tetrahedron":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["tetrahedron"])

    elif type == "octahedron":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["octahedron"])

    elif type == "circle":
        ctrl = cmds.curve(n=name, d=3, p=cshp.shapes["circle"])
        cmds.closeCurve(ctrl, ps=0, rpo=1, bb=0.5, bki=0, p=0.1)

    elif type == "lollipop":
        ctrl = cmds.curve(n=name, d=3, p=cshp.shapes["lollipop"])

    elif type == "barbell":
        ctrl = cmds.curve(n=name, d=3, p=cshp.shapes["barbell"])
        cmds.closeCurve(name, ch=False, ps=False, rpo=True, bki=True)

    elif type == "sphere":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["sphere"])

    elif type == "arrowCross":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["arrowCross"])

    elif type == "diamond":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["diamond"])

    elif type == "cross":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["cross"])

    elif type == "bentCross":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["bentCross"])

    elif type == "arrow":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["arrow"])

    elif type == "bentArrow":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["bentArrow"])

    elif type == "halfCircle":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["halfCircle"])

    elif type == "splitCircle":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["splitCircle"])

    elif type == "cylinder":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["cylinder"])
    
    elif type == "arrowCircle":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["arrowCircle"])
    
    elif type == "arrowSquare":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["arrowSquare"])
    
    elif type == "4arrowSquare":
        ctrl = cmds.curve(n=name, d=1, p=cshp.shapes["4arrowSquare"])
    else:
        cmds.warning("createControl doesn't know shape - '%s'" % type)

    # rotate to axis
    cmds.select("{0}.cv[*]".format(ctrl))
    cmds.rotate(rot[0], rot[1], rot[2], r=True)
    cmds.select(cl=True)
    shapes = cmds.listRelatives(ctrl, shapes=True)
    for shape in shapes:
        cmds.setAttr("%s.overrideEnabled" % shape, 1)
        cmds.setAttr("%s.overrideColor" % shape, colors[color])
        cmds.rename(shape, "{0}Shape".format(ctrl))

    cmds.select(ctrl, r=True)
    return (ctrl)


def swap_shape(type="circle", axis="x", scale = 1.0, color=None, *args):
    """
    swaps the shape of selected obj for given shape type
    """
    sel = cmds.ls(sl=True)

    for obj in sel:
        # get color
        newColor = color
        shp = cmds.listRelatives(obj, s=True)[0]
        if not shp:
            return()
        shpColor = None
        try:
            shpColor = convert_number_color_to_text(cmds.getAttr("{0}.overrideColor".format(shp)))
        except:
            pass
        if not newColor:
            newColor = shpColor
        if not newColor:
            newColor = "yellow"
        #print "{0} --- {1} ---- {2}".format(obj, shpColor, newColor)
        if type_check(obj, "nurbsCurve"):
            shapes = cmds.listRelatives(obj, s=True)
            ctrl = create_control(type=type, color = newColor, axis=axis)
            ctrlShape = cmds.listRelatives(ctrl)[0]
            scale_nurbs_control(ctrl, scale, scale, scale)
            cmds.parent(ctrlShape, obj, relative=True, shape=True)
            if shapes:
                cmds.delete(shapes)
            cmds.delete(ctrl)


def convert_number_color_to_text(num, *args):
    # given an int, convert it to color based on our dict
    return(list(colors.keys())[list(colors.values()).index(num)])


def create_message(host="none", attr="none", target="none", *args):
    """creates a message attr on object with target as value. Args are: 'host'-some object to hold the message attr, 'attr'-the name of the message attribute to create, and 'target'-the host to be the value of the message attr"""
    cmds.addAttr(host, at='message', ln=attr)
    cmds.connectAttr("%s.message" % target, "%s.%s" % (host, attr))
    return ("%s.%s" % (host, attr))


def get_vert_uv(vertsList=[], *args):
    """use a vert input to get the UV value"""
    uvVals = []
    for v in vertsList:
        uv = cmds.polyListComponentConversion(v, fv=True, tuv=True)
        uvVal = cmds.polyEditUV(uv, q=True, u=True, v=True)
        uvVals.append(uvVal)
    return (uvVals)


def align_to_uv(targetObj="none", sourceObj="none", sourceU=0.0, sourceV=0.0,
                mainAxis="+z", secAxis="+x", UorV="v"):
    """
    inputs should be 1. targetObj 2. sourceObj 3. sourceU 4. sourceV 5. mainAxis(lowerCase, + or -, i.e."-x" 8. secAxis (lowcase, + or -) 7, UorV ("u" or "v" for the direction along surface for the sec axis)
    """

    axisDict = {
        "+x": (1, 0, 0), "+y": (0, 1, 0), "+z": (0, 0, 1), "-x": (-1, 0, 0),
        "-y": (0, -1, 0), "-z": (0, 0, -1)
    }

    # Does this create a new node? no To create a node, use the flag "ch=True". That creates a pointOnSurface node
    pos = cmds.pointOnSurface(sourceObj, u=sourceU, v=sourceV, position=True)
    posVec = om.MVector(pos[0], pos[1], pos[2])
    cmds.xform(targetObj, ws=True, t=pos)

    # get normal, tanU and tanV at selected UV position on source surface
    tanV = cmds.pointOnSurface(sourceObj, u=sourceU, v=sourceV, tv=True)
    tanU = cmds.pointOnSurface(sourceObj, u=sourceU, v=sourceV, tu=True)
    norm = cmds.pointOnSurface(sourceObj, u=sourceU, v=sourceV, nn=True)

    # decide where up axis is on normal constraint, u or v tangent
    if UorV == "v":
        wup = tanV
    elif UorV == "u":
        wup = tanU

    # create normal constraint
    nc = cmds.normalConstraint(sourceObj, targetObj,
                               aimVector=axisDict[mainAxis],
                               upVector=axisDict[secAxis], worldUpVector=(wup))
    cmds.delete(nc)  # delete constraint


def strip_to_rotate(first="none", *args):
    attrs = ["tx", "ty", "tz", "sx", "sy", "sz", "visibility"]
    objs = []
    if first == "none":
        objs = getSelection()
    else:
        objs.append(first)
        if args:
            for each in args:
                objs.append(each)
            ##    print(objs)
    for me in objs:
        for attr in attrs:
            objAttr = me + "." + attr
            cmds.setAttr(objAttr, lock=True, k=False)


def strip_to_translate(first="none", *args):
    """strips for all selected or entered as args, sets all attrs but translate to locked and hidden"""
    attrs = ["rx", "ry", "rz", "sx", "sy", "sz", "visibility"]
    objs = []
    if first == "none":
        objs = getSelection()
    else:
        objs.append(first)
        if args:
            for each in args:
                objs.append(each)
            ##    print(objs)
    for me in objs:
        for attr in attrs:
            objAttr = me + "." + attr
            cmds.setAttr(objAttr, lock=True, k=False)


def strip_to_rotate_translate(first="none", *args):
    """strips for all selected or entered as args, sets all attrs but translate rotate to locked and hidden"""
    attrs = ["sx", "sy", "sz", "visibility"]
    objs = []
    if first == "none":
        objs = getSelection()
    else:
        objs.append(first)
        if args:
            for each in args:
                objs.append(each)
            ##    print(objs)
    for me in objs:
        for attr in attrs:
            objAttr = me + "." + attr
            cmds.setAttr(objAttr, lock=True, k=False)


def lock_translate(first="none", *args):
    attrs = ["tx", "ty", "tz"]
    objs = []
    if first == "none":
        objs = getSelection()
    else:
        objs.append(first)
        if args:
            for each in args:
                objs.append(each)
    for me in objs:
        for attr in attrs:
            objAttr = me + "." + attr
            cmds.setAttr(objAttr, lock=True)


def strip_transforms(first="none", *args):
    """locks and hides all transforms from channel box. can call multiple objs as arguments or use selection of objects"""
    attrs = ["rx", "ry", "rz", "tx", "ty", "tz", "sx", "sy", "sz", "visibility"]
    objs = []
    if first == "none":
        objs = getSelection()
    else:
        objs.append(first)
        if args:
            for each in args:
                objs.append(each)
    print(objs)
    for me in objs:
        for attr in attrs:
            objAttr = me + "." + attr
            cmds.setAttr(objAttr, lock=True, k=False)


def restore_transforms(first="none", *args):
    """restores all the default locked and hidden channels back to the channels box"""
    attrs = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "visibility"]
    objs = []
    if first == "none":
        objs = getSelection()
    else:
        objs.append(first)
        for each in args:
            objs.append(each)
    print(objs)
    for me in objs:
        for attr in attrs:
            objAttr = me + "." + attr
            cmds.setAttr(objAttr, lock=False, k=True)


def create_add(name, input1, input2):
    """creates an addDoubleLinear node with name, object.attr, object.attr as args"""
    adl = cmds.shadingNode("addDoubleLinear", asUtility=True, name=name)
    cmds.connectAttr(input1, "%s.input1" % adl)
    cmds.connectAttr(input2, "%s.input2" % adl)
    return (adl)


# ------------- BELOW CAN BE COMBINED (SEE RIGGER TOOLS) - look into animblend nodes
def blend_rotation(name="none", sourceA="none", sourceB="none", target="none",
                   sourceValue="none"):
    # add input and *args?
    """name is first arg, then three objects. Blends rotation from first two selected into third selected. SourceValue (last input) is for the driving obj.attr. First source is active at '1', second at '2'"""
    if name == "none":
        name = "blendColors"
    if sourceA == "none":
        sel = getSelection()
        if len(sel) != 3:
            cmds.error("Error: blendRotation, select three transforms")
            # inert some kind of break here
        sourceA = sel[0]
        sourceB = sel[1]
        target = sel[2]
    blend = cmds.shadingNode("blendColors", asUtility=True, name=name)
    sourceAOut = sourceA + ".rotate"
    sourceBOut = sourceB + ".rotate"
    targetIn = target + ".rotate"
    blend1 = name + ".color1"
    blend2 = name + ".color2"
    blendOut = name + ".output"
    cmds.connectAttr(sourceAOut, blend1)
    cmds.connectAttr(sourceBOut, blend2)
    cmds.connectAttr(blendOut, targetIn)
    if not sourceValue == "none":
        cmds.connectAttr(sourceValue, "%s.blender" % name)

    return (name)


def blend_translate(blend="none", sourceA="none", sourceB="none", target="none",
                    sourceValue="none"):
    """name is first arg, then three objects. Blends translation from first two selected into third selected. SourceValue (last input) is for the driving obj.attr. First source is active at '1', second at '2'"""
    # add input and *args
    if blend == "none":
        blend = "blendColors"
    if sourceA == "none":
        sel = getSelection()
        if len(sel) != 3:
            cmds.error("Error: blendRotation, select three transforms")
            # inert some kind of break here
        sourceA = sel[0]
        sourceB = sel[1]
        target = sel[2]
    blend = cmds.shadingNode("blendColors", asUtility=True, name=blend)
    sourceAOut = sourceA + ".translate"
    sourceBOut = sourceB + ".translate"
    targetIn = target + ".translate"
    blend1 = blend + ".color1"
    blend2 = blend + ".color2"
    blendOut = blend + ".output"
    cmds.connectAttr(sourceAOut, blend1)
    cmds.connectAttr(sourceBOut, blend2)
    cmds.connectAttr(blendOut, targetIn)
    if not sourceValue == "none":
        cmds.connectAttr(sourceValue, "%s.blender" % blend)

    return (blend)


def blend_scale(blend="none", sourceA="none", sourceB="none", target="none",
                sourceValue="none"):
    """name is first arg, then three objects. Blends translation from first two selected into third selected. SourceValue (last input) is for the driving obj.attr. First source is active at '1', second at '2'"""
    # add input and *args
    if blend == "none":
        blend = "blendColors"
    if sourceA == "none":
        sel = getSelection()
        if len(sel) != 3:
            cmds.error("Error: blendRotation, select three transforms")
            # inert some kind of break here
        sourceA = sel[0]
        sourceB = sel[1]
        target = sel[2]
    blend = cmds.shadingNode("blendColors", asUtility=True, name=blend)
    sourceAOut = sourceA + ".scale"
    sourceBOut = sourceB + ".scale"
    targetIn = target + ".scale"
    blend1 = blend + ".color1"
    blend2 = blend + ".color2"
    blendOut = blend + ".output"
    cmds.connectAttr(sourceAOut, blend1)
    cmds.connectAttr(sourceBOut, blend2)
    cmds.connectAttr(blendOut, targetIn)
    if not sourceValue == "none":
        cmds.connectAttr(sourceValue, "%s.blender" % blend)

    return (blend)


def add_group_below(*args):
    ############----------fix lots of stuff here, but basic idea works
    sel = cmds.ls(sl=True)

    for obj in sel:
        pos = cmds.xform(obj, ws=True, q=True, rp=True)
        rot = cmds.xform(obj, ws=True, q=True, ro=True)

        children = cmds.listRelatives(obj, children=True)

        grp = cmds.group(em=True, name=obj.replace("Auto", "Manual"))

        cmds.xform(grp, ws=True, t=pos)
        cmds.xform(grp, ws=True, ro=rot)

        cmds.parent(grp, obj)
        for child in children:
            cmds.parent(child, grp)


def reverse_setup(inAttr, strAttr, revAttr, rName, *args):
    """
    4 arguments, the (node.attr) that enters the rev, straight conn,
    the reversed, then the reverse node name
    """
    cmds.shadingNode("reverse", asUtility=True, name=rName)
    rIn = rName + ".input"
    rOut = rName + ".output"
    cmds.connectAttr(inAttr, strAttr)
    cmds.connectAttr(inAttr, rIn)
    cmds.connectAttr(rOut, revAttr)
    cmds.select(cl=True)


def measure_distance_nodes(mName="none", *args):
    """first the name of the measure node, then the 2 objects ORRRR select the two objects and run (will give name 'distanceBetween'"""
    objs = []
    if mName == "none":
        mName = "distanceBetween"
        objs = get_two_selection()
    else:
        for each in args:
            objs.append(each)
    # add check for 2 selectiont
    if len(objs) != 2:
        cmds.error(
            "you must enter either a measure name and 2 objects OR no arguments and manually select 2 objs")
    dist = cmds.shadingNode("distanceBetween", asUtility=True, name=mName)
    objA = objs[0]
    objB = objs[1]
    objAMatrix = objA + ".worldMatrix"
    objBMatrix = objB + ".worldMatrix"
    objAPoint = objA + ".rotatePivot"
    objBPoint = objB + ".rotatePivot"
    distPoint1 = dist + ".point1"
    distPoint2 = dist + ".point2"
    distMatrix1 = dist + ".inMatrix1"
    distMatrix2 = dist + ".inMatrix2"
    cmds.connectAttr(objAPoint, distPoint1)
    cmds.connectAttr(objBPoint, distPoint2)
    cmds.connectAttr(objAMatrix, distMatrix1)
    cmds.connectAttr(objBMatrix, distMatrix2)
    cmds.select(clear=True)
    return (dist)


def measure_distance(objA, objB, *args):
    """returns distance of two given transform nodes"""
    a = cmds.xform(objA, ws=True, q=True, rp=True)
    b = cmds.xform(objB, ws=True, q=True, rp=True)
    apos = om.MVector(a[0], a[1], a[2])
    bpos = om.MVector(b[0], b[1], b[2])
    vec = bpos - apos
    return (vec.length())


# - this should be pulled from rigger tools if necessary
def create_scale_stretch(limbName="none", ikTop="none", ikMid="none",
                         ikLow="none", jntMeasure="none", IKMeasure="none",
                         IKCtrl="none", axis="none", *args):
    """creates a stretch setup for 3 joint IK chain. Inputs (strings) are the limbName, 3 ik joints (top to bottom), the measure input for the whole chain (add up from measure joints), the measure for the ikCtrl, the ik handle or ctrl (which must have 'scaleMin', 'upScale' and 'lowScale' attrs, the axis letter. Returns . . . """

    ratioMult = cmds.shadingNode("multiplyDivide", asUtility=True,
                                 n="%s_stretchRatioMult" % limbName)
    cmds.setAttr(ratioMult + ".operation", 2)
    cmds.connectAttr(jntMeasure, "%s.input2X" % ratioMult)
    cmds.connectAttr(IKMeasure, "%s.input1X" % ratioMult)

    # could put this default stuff (next two paragraphs) after the conditional and use another conditional so that minScale is bundled up in "autostretch"
    # create default setting of 1 when autostretch is off
    defaultMult = cmds.shadingNode("multiplyDivide", asUtility=True,
                                   n="%s_stretchDefaultMult" % limbName)
    cmds.setAttr("%s.input1X" % defaultMult, 1)

    # create blend node to blend ratio mult and default values, based on blender attr of ikctrl.autoStretch
    defaultBlend = cmds.shadingNode("blendColors", asUtility=True,
                                    n="%s_stretchBlend" % limbName)
    cmds.connectAttr("%s.outputX" % defaultMult, "%s.color2R" % defaultBlend)
    cmds.connectAttr("%s.outputX" % ratioMult, "%s.color1R" % defaultBlend)
    cmds.connectAttr("%s.autoStretch" % IKCtrl, "%s.blender" % defaultBlend)

    # blend goes into condition node - firstTerm, secondTerm=ikctrl scaleMin value, operation=2(greaterthan), colorIfTrue is blend, colorIfFalse is scaleMin attr
    conditional = cmds.shadingNode("condition", asUtility=True,
                                   n="%s_upStretchCondition" % limbName)
    cmds.setAttr("%s.operation" % conditional, 2)
    cmds.connectAttr("%s.outputR" % defaultBlend, "%s.firstTerm" % conditional)
    cmds.connectAttr("%s.scaleMin" % IKCtrl, "%s.secondTerm" % conditional)
    cmds.connectAttr("%s.outputR" % defaultBlend,
                     "%s.colorIfTrueR" % conditional)
    cmds.connectAttr("%s.scaleMin" % IKCtrl, "%s.colorIfFalseR" % conditional)

    # factor in the upScale/lowScale attrs
    upScaleMult = cmds.shadingNode('multiplyDivide', asUtility=True,
                                   n="%s_upScaleMult" % limbName)
    cmds.connectAttr("%s.outColorR" % conditional, "%s.input1X" % upScaleMult)
    cmds.connectAttr("%s.upScale" % IKCtrl, "%s.input2X" % upScaleMult)
    loScaleMult = cmds.shadingNode('multiplyDivide', asUtility=True,
                                   n="%s_loScaleMult" % limbName)
    cmds.connectAttr("%s.outColorR" % conditional, "%s.input1X" % loScaleMult)
    cmds.connectAttr("%s.lowScale" % IKCtrl, "%s.input2X" % loScaleMult)

    # hook up the scales of the joints
    cmds.connectAttr("%s.outputX" % upScaleMult, "%s.s%s" % (ikTop, axis))
    cmds.connectAttr("%s.outputX" % loScaleMult, "%s.s%s" % (ikMid, axis))

    return (
    ratioMult, defaultMult, defaultBlend, conditional, upScaleMult, loScaleMult)


def translate_stretch_ik(limbName=None, ikTop=None, ikMid=None, ikLow=None,
                         jntMeasure=None, IKMeasure=None, IKCtrl=None,
                         axis=None, posNeg=None, *args):
    """creates a stretch setup for 3 joint IK chain. Inputs (strings) are the limbName, 3 ik joints (top to bottom), the measure input for the whole chain (add up from measure joints?), the measure for the ikCtrl, the ik handle or ctrl (which must have 'scaleMin' attr, the axis letter, and PosNeg, which is +1 or -1 (minus for things in negative direction/mirror). Returns . . . """
    # set up the ratio of ctrl to measure
    ratioMult = cmds.shadingNode("multiplyDivide", asUtility=True,
                                 n="%s_stretchRatioMult" % limbName)
    cmds.setAttr(ratioMult + ".operation", 2)
    cmds.connectAttr(jntMeasure, "%s.input2X" % ratioMult)
    cmds.connectAttr(IKMeasure, "%s.input1X" % ratioMult)

    # create default setting of 1 when autostretch is off
    default = cmds.shadingNode("multiplyDivide", asUtility=True,
                               n="%s_stretchDefaultMult" % limbName)
    cmds.setAttr("%s.input1X" % default, 1)

    # create blend node to blend ratio mult and default values, based on blender attr of ikctrl.autoStretch
    defaultBlend = cmds.shadingNode("blendColors", asUtility=True,
                                    n="%s_stretchBlend")
    cmds.connectAttr("%s.outputX" % default, "%s.color2R" % defaultBlend)
    cmds.connectAttr("%s.outputX" % ratioMult, "%s.color1R" % defaultBlend)
    cmds.connectAttr("%s.autoStretch" % IKCtrl, "%s.blender" % defaultBlend)

    # get the top joint length
    tAxis = "t%s" % axis
    topLength = cmds.getAttr("%s.%s" % (ikMid, tAxis))
    # do I need measure joints?

    # create length factor for top
    topFactorMult = cmds.shadingNode("multiplyDivide", asUtility=True,
                                     n="%s_stretchFactorTopMult" % limbName)
    cmds.setAttr("%s.input1X" % topFactorMult, topLength)
    cmds.connectAttr("%s.outputR" % defaultBlend, "%s.input2X" % topFactorMult)

    # set up for clamp
    topClamp = cmds.shadingNode("clamp", asUtility=True,
                                n="%s_stretchTopClamp" % limbName)
    cmds.connectAttr("%s.outputX" % topFactorMult, "%s.inputR" % topClamp)

    # create min, max, connect to clamp
    topMin = cmds.shadingNode("multiplyDivide", asUtility=True,
                              n="%s_topMinMult" % limbName)
    topMax = cmds.shadingNode("multiplyDivide", asUtility=True,
                              n="%s_topMaxMult" % limbName)
    if posNeg == 1:
        cmds.setAttr("%s.input1X" % topMin, topLength)
        cmds.connectAttr("%s.scaleMin" % IKCtrl, "%s.input2X" % topMin)
        cmds.setAttr("%s.input1X" % topMax, topLength)
        cmds.setAttr("%s.input2X" % topMax, 4)
        cmds.connectAttr("%s.outputX" % topMin, "%s.minR" % topClamp)
        cmds.connectAttr("%s.outputX" % topMax, "%s.maxR" % topClamp)
    if posNeg == -1:
        cmds.setAttr("%s.input1X" % topMax, topLength)
        cmds.connectAttr("%s.scaleMin" % IKCtrl, "%s.input2X" % topMax)
        cmds.setAttr("%s.input1X" % topMin, topLength)
        cmds.setAttr("%s.input2X" % topMin, 4)
        cmds.connectAttr("%s.outputX" % topMin, "%s.minR" % topClamp)
        cmds.connectAttr("%s.outputX" % topMax, "%s.maxR" % topClamp)

    # connect to joints
    cmds.connectAttr("%s.outputR" % topClamp, "%s.%s" % (ikMid, tAxis))

    # do lower half
    # get the low joint length
    tAxis = "t%s" % axis
    lowLength = cmds.getAttr("%s.%s" % (ikLow, tAxis))
    # do I need measure joints?

    # create length factor for low
    lowFactorMult = cmds.shadingNode("multiplyDivide", asUtility=True,
                                     n="%s_stretchFactorLowMult" % limbName)
    cmds.setAttr("%s.input1X" % lowFactorMult, lowLength)
    cmds.connectAttr("%s.outputR" % defaultBlend, "%s.input2X" % lowFactorMult)

    # set up for clamp
    lowClamp = cmds.shadingNode("clamp", asUtility=True,
                                n="%s_stretchlowClamp" % limbName)
    cmds.connectAttr("%s.outputX" % lowFactorMult, "%s.inputR" % lowClamp)

    # create min, max, connect to clamp
    lowMin = cmds.shadingNode("multiplyDivide", asUtility=True,
                              n="%s_lowMinMult" % limbName)
    lowMax = cmds.shadingNode("multiplyDivide", asUtility=True,
                              n="%s_lowMaxMult" % limbName)
    if posNeg == 1:
        cmds.setAttr("%s.input1X" % lowMin, lowLength)
        cmds.connectAttr("%s.scaleMin" % IKCtrl, "%s.input2X" % lowMin)
        cmds.setAttr("%s.input1X" % lowMax, (lowLength * posNeg))
        cmds.setAttr("%s.input2X" % lowMax, 4)
        cmds.connectAttr("%s.outputX" % lowMin, "%s.minR" % lowClamp)
        cmds.connectAttr("%s.outputX" % lowMax, "%s.maxR" % lowClamp)
    if posNeg == (-1):
        cmds.setAttr("%s.input1X" % lowMax, lowLength)
        cmds.connectAttr("%s.scaleMin" % IKCtrl, "%s.input2X" % lowMax)
        cmds.setAttr("%s.input1X" % lowMin, lowLength)
        cmds.setAttr("%s.input2X" % lowMin, 4)
        cmds.connectAttr("%s.outputX" % lowMin, "%s.minR" % lowClamp)
        cmds.connectAttr("%s.outputX" % lowMax, "%s.maxR" % lowClamp)
    # connect to joints
    cmds.connectAttr("%s.outputR" % lowClamp, "%s.%s" % (ikLow, tAxis))

    return (
    ratioMult, topFactorMult, lowFactorMult, topMin, topMax, lowMin, lowMax,
    topClamp, lowClamp)


def create_curve_info_node(crv, *args):
    cin = cmds.arclen(crc, ch=True)
    return (cin)


def parent_check(obj):
    """ checks whether there's a parent and if so returns it (otherwise returns None)"""
    if obj:
        plist = cmds.listRelatives(obj, p=True)
        if plist:
            return (plist)[0]
    return (None)


def type_check(obj, typeToCheck, *args):
    """
    returns boolean
    give an object and type of object and this will look at a) the node itself and b) if node is transform, will look at shape node
    """
    # somethings not working with the transform bit here
    if cmds.objExists(obj):
        tempType = cmds.objectType(obj)
        if typeToCheck == "transform":
            if tempType == "transform":
                return (True)
            else:
                return (False)

        if not tempType == "transform":
            if tempType == typeToCheck:
                return True
        else:
            shp = cmds.listRelatives(obj, s=True)
            if shp:
                tempType = cmds.objectType(shp[0])

        if tempType == typeToCheck:
            return True

        return False
    return False


def snap_to(target, obj, rot=True, trans=True):
    """
    TODO: make it apply to points and verts, etc
    """
    if trans:
        pos = cmds.xform(target, q=True, ws=True, rp=True)
        cmds.xform(obj, ws=True, t=pos)
    if rot:
        rot = cmds.xform(target, q=True, ws=True, ro=True)
        cmds.xform(obj, ws=True, ro=rot)


# -------------- rfactor with snap_to
def swap_dupe(obj, target, delete=True, name="", *args):
    """
    replaces an target with a duplicate of the obj
    select the object you want to duplicate, then the target(s), delete bool, name optional
    [obj] is the object to duplicate
    [target] is the target to match and delete(?)
    [delete] is bool to tell whether to delete the target or not
    [name] is string to rename to
    """

    if not name:
        name = obj

    # get pos, rot, scale of target
    pos = cmds.xform(target, q=True, ws=True, rp=True)
    rot = cmds.xform(target, q=True, ws=True, ro=True)
    scl = cmds.getAttr("{0}.scale".format(target))

    # duplicate the object and rename to name, if no name just use unique names
    dupe = cmds.duplicate(obj, name=name, returnRootsOnly=True,
                          renameChildren=True)
    cmds.xform(dupe, ws=True, t=pos)
    cmds.xform(dupe, ws=True, ro=rot)
    cmds.xform(dupe, ws=True, s=scl[0])

    parent = cmds.listRelatives(target, parent=True)
    if parent:
        cmds.parent(dupe, parent[0])

    if delete:
        cmds.delete(target)

    return (dupe[0])


def positions_along_curve(crv="", numPts=3, *args):
    """
    returns list (len of numPts) world positions evenly distributed along given nurbs crv
    """
    # - ---- also should orient along curve (do cross math based on
    if not crv:
        return

    if type_check(crv, "nurbsCurve"):
        posList = []
        shp = cmds.listRelatives(crv, s=True)[0]
        poc = cmds.shadingNode("pointOnCurveInfo", asUtility=True,
                               name="tmpPOCInfo")
        cmds.connectAttr("{}.local".format(shp), "{}.inputCurve".format(poc))
        cmds.setAttr("{}.turnOnPercentage".format(poc), 1)
        lineLen = cmds.arclen(crv, ch=False)
        dist = float(numPts) / lineLen  

        for x in range(0, numPts):
            perc = 1.0 / (numPts-1)
            cmds.setAttr("{}.parameter".format(poc), x * perc)
            pos = cmds.getAttr("{}.position".format(poc))[0]
            posList.append(pos)

        cmds.delete(poc)
        return (posList)


def rebuild_curve(curve="", num=5, keep=False, ch=False, name="", *args):
    """
    rebuilds curve (checks validity, min cvs, keep/history, etc)
    
    Args:
        curve (string): a valid nurbs curve
        num (int):  int number of pts
        keep (bool):    whether to keep original
        ch (bool):  whether to keep history
        name (string):  name of new curve (left blank will try to keep orig name)

    Returns:
        string: the name of the created curves (could be same as original!)
    """

    newCurve = ""
    if curve:
        if type_check(curve, "nurbsCurve"):
            if not name:
                name = curve
            if not keep or not ch:
                ch = False
            if num < 3:
                num = 3

            newCurve = cmds.rebuildCurve(curve, rebuildType=0, spans=num, keepRange=0, replaceOriginal=not keep, name=name, ch=ch)[0]

    return newCurve


def create_space_buffer_grps(ctrl="", *args):
    """
    creates a pair of groups parent constrained to selected ctrl (and it's group). 
    Basically is proxy to switch spaces (from rig part space to world space) for direct connections.
    ctrl should be located in place with a group above (group frozen)
    Args:
        ctrl (string): the name of the ctrl(transform) to create the proxy for. Assumes a group above (group freeze)
    Returns:
        string, string: returns the names of the created ctrl group and the created parent group
    """
    # grab the ctrl (must have group above)?
    ctrlParent = parent_check(ctrl)
    if not ctrlParent:
        cmds.error("zbw_rig.create_space_buffer_grps: don't have a parent group on the ctrl!")
        return

    # create groups for the proxy
    ctrlGrp = cmds.group(empty=True, n="{0}_proxyCtrl".format(ctrl))
    parGrp = cmds.group(empty=True, n="{0}_proxyGrp".format(ctrlParent))
    # snap groups to the parent and child
    snap_to(ctrlParent, parGrp)
    snap_to(ctrl, ctrlGrp)
    cmds.parent(ctrlGrp, parGrp)
    # constrain groups
    cmds.parentConstraint(ctrlParent, parGrp, mo=True)
    cmds.parentConstraint(ctrl, ctrlGrp, mo=True)
    # return groups
    return (ctrlGrp, parGrp)


def group_freeze(obj, suffix="GRP", *arg):
    """
    takes an object in worldspace and snaps a group to it, then parents obj to that group. Also parents back under orig parent of the obj
    i.e. zeros out the obj's translates and rotations
    Args:
        obj (string): the object to put under the group (to zero it's transforms)
    Returns:
        string: returns the new group
    """
    parent = cmds.listRelatives(obj, p=True)
    if parent:
        parent = parent[0]

    grpname = "{0}_{1}".format(obj, suffix)
#---------------- don't like this incrementing    
    grpname = increment_name(grpname)
    grp = cmds.group(empty=True, name=grpname)
    snap_to(obj, grp)
    cmds.parent(obj, grp)

    if parent:
        cmds.parent(grp, parent)

    return (grp)


def connect_transforms(source="", target="", t=True, r=True, s=True, f=False, *args):
    """
    simple direct connection between transform attrs
    Args:
        source (string): object connections come FROM
        target (string): object connections go to
        t (bool): do translates?
        r (bool): do rotations?
        s (bool): do scales?
    Return: 
        None
    """
    if source and target:
        if t:
            cmds.connectAttr("{0}.t".format(source), "{0}.t".format(target), f=f)
        if r:
            cmds.connectAttr("{0}.r".format(source), "{0}.r".format(target), f=f)
        if s:
            cmds.connectAttr("{0}.s".format(source), "{0}.s".format(target), f=f)


def get_frame_range(*args):
    """
    returns the (min, max) frames of the current playback range in the scene
    """
    min = cmds.playbackOptions(q=True, min=True)
    max = cmds.playbackOptions(q=True, max=True)
    return (min, max)


def insert_group_above(obj, suffix="GRP", *args):
    par = cmds.listRelatives(obj, p=True)
    grp = cmds.group(em=True, n="{0}_{1}".format(obj, suffix))
    snap_to(obj, grp)
    cmds.parent(obj, grp)
    if par:
        cmds.parent(grp, par[0])

    return (grp)


def create_negate_group(obj=None, suffix="GRP", t=True, r=True, s=True, *args):
    if not obj:
        "zbw_rig.create_negate_group: please provide some transform to negate"
        return()
    par = cmds.listRelatives(obj, p=True)
    grp = cmds.group(em=True, n="{0}_neg_{1}".format(obj, suffix))
    snap_to(obj, grp)
    cmds.parent(obj, grp)

    if t:
        mult = cmds.createNode("multiplyDivide", name="{0}_t_neg_MD".format(obj))
        cmds.setAttr(mult+".input2", -1.0, -1.0, -1.0)
        cmds.connectAttr(obj+".t", mult+".input1")
        cmds.connectAttr(mult+".output", grp+".t")
    if r:
        mult = cmds.createNode("multiplyDivide", name="{0}_r_neg_MD".format(obj))
        cmds.setAttr(mult+".input2", -1.0, -1.0, -1.0)
        cmds.connectAttr(obj+".r", mult+".input1")
        cmds.connectAttr(mult+".output", grp+".r")
    if s:
        mult = cmds.createNode("multiplyDivide", name="{0}_t_neg_MD".format(obj))
        cmds.setAttr(mult+".operation", 2)
        cmds.setAttr(mult+".input1", 1.0, 1.0, 1.0)
        cmds.connectAttr(obj+".s", mult+".input2")
        cmds.connectAttr(mult+".output", grp+".s")
    if par:
        cmds.parent(grp, par[0])


def bounding_box_ctrl(sel=[], prnt=True, *args):
    """
    creates a control based on the bounding box
    selList (list) - list of obj to use to create control
    prnt (bool) - whether you want to parent the obj to the ctrl
    """
    if not sel:
        sel = cmds.ls(sl=True, type="transform")

    if sel:
        box = cmds.exactWorldBoundingBox(
            sel)  # [xmin, ymin, zmin, xmax, ymax, zmax]
        X = om.MVector(box[0], box[3])
        Y = om.MVector(box[1], box[4])
        Z = om.MVector(box[2], box[5])

        # get bbox lengths along axes
        lenX = (X.y - X.x)
        lenY = (Y.y - Y.x)
        lenZ = (Z.y - Z.x)
        # print lenX, lenY, lenZ

        ctrl = create_control(name="ctrl", type="cube", color="pink")

        cvs = {
            "xyz": [5, 15], "-xyz": [0, 4], "xy-z": [10, 14], "x-yz": [6, 8],
            "-x-yz": [3, 7], "-x-y-z": [2, 12], "x-y-z": [9, 13],
            "-xy-z": [1, 11]
        }

        for a in cvs["xyz"]:
            cmds.xform("{0}.cv[{1}]".format(ctrl, a), ws=True,
                       t=(X.y, Y.y, Z.y))
        for a in cvs["-xyz"]:
            cmds.xform("{0}.cv[{1}]".format(ctrl, a), ws=True,
                       t=(X.x, Y.y, Z.y))
        for a in cvs["x-yz"]:
            cmds.xform("{0}.cv[{1}]".format(ctrl, a), ws=True,
                       t=(X.y, Y.x, Z.y))
        for a in cvs["-x-yz"]:
            cmds.xform("{0}.cv[{1}]".format(ctrl, a), ws=True,
                       t=(X.x, Y.x, Z.y))
        for a in cvs["xy-z"]:
            cmds.xform("{0}.cv[{1}]".format(ctrl, a), ws=True,
                       t=(X.y, Y.y, Z.x))
        for a in cvs["-xy-z"]:
            cmds.xform("{0}.cv[{1}]".format(ctrl, a), ws=True,
                       t=(X.x, Y.y, Z.x))
        for a in cvs["-x-y-z"]:
            cmds.xform("{0}.cv[{1}]".format(ctrl, a), ws=True,
                       t=(X.x, Y.x, Z.x))
        for a in cvs["x-y-z"]:
            cmds.xform("{0}.cv[{1}]".format(ctrl, a), ws=True,
                       t=(X.y, Y.x, Z.x))

        cmds.xform(ctrl, cp=True)

        wsPos = cmds.xform(ctrl, ws=True, q=True, rp=True)
        cmds.xform(ctrl, ws=True, t=(-wsPos[0], -wsPos[1], -wsPos[2]))
        cmds.makeIdentity(ctrl, apply=True)
        cmds.xform(ctrl, ws=True, t=wsPos)

        if prnt:
            cmds.parent(sel, ctrl)
        cmds.select(ctrl)

        return (ctrl)


def scale_nurbs_control(ctrl=None, x=1, y=1, z=1, origin=False, *args):
    """
    scales cvs from rotate pivot of obj
    ARGS:
        origin(bool)- scale from origin
    """
    if not ctrl or not type_check(ctrl, "nurbsCurve"):
        cmds.warning(
            "zbw_rig.scaleNurbsCtrl: I wasn't passed a nurbsCurve object")
        return ()

    piv = cmds.xform(ctrl, q=True, ws=True, rp=True)
    if origin:
        piv = (0, 0, 0)
    cvs = cmds.ls("{0}.cv[*]".format(ctrl), fl=True)
    cmds.scale(x, y, z, cvs, pivot=piv)


def assign_color(obj=None, clr="yellow", *args):
    if cmds.objectType(obj) != "transform":
        return ()

    shp = cmds.listRelatives(obj, s=True)
    if shp:
        for s in shp:
            cmds.setAttr("{0}.overrideEnabled".format(s), 1)
            cmds.setAttr("{0}.overrideColor".format(s), colors[clr])


def add_geo_to_deformer(deformer, geo, *args):
    """
    Args:
        deformer: string, the deformer to add to
        geo: string or list, the transform(s) of the geo to add
        *args:

    Returns:

    """
##----------------need to add a function to put the xform matrix of the geometry into the geomMatrix of the deformer (in the right index)
# first get the affected geo from the deformer
# then take all those geos and get set the geomMatrix of the deformer for each index

    # make geo a list if it's only one object (ie. a string)
    if isinstance(geo, str):
        geo = [geo]

# this doesn't work in terms of getting the object type (lattice needs to get shape, cluster needs to get cluster, etc)
    defType = cmds.objectType(deformer)
    if defType == "lattice":
        for g in geo:
            cmds.lattice(deformer, edit=True, geometry=g)
    elif defType == "nonLinear":
        for g in geo:
            cmds.nonLinear(deformer, edit=True, geometry=g)
    elif defType == "softMod":
        for g in geo:
            cmds.softMod(deformer, edit=True, geometry=g)
    elif defType == "cluster":
        for g in geo:
            cmds.cluster(deformer, edit=True, geometry=g)
    else:
        cmds.warning("I don't recognize the deformer type of: {0}".format(deformer))


def remove_geo_from_deformer(deformer, geo, *args):
    """
    Args:
        deformer: string, the deformer to add to
        geo: string or list, the transform(s) of the geo to add
        *args:

    Returns:

    """
    # make geo a list if it's only one object (ie. a string)
    if isinstance(geo, str):
        geo = [geo]

    defType = cmds.objectType(deformer)
    if defType == "lattice":
        for g in geo:
            cmds.lattice(deformer, edit=True, geometry=g, remove=True)
    elif defType == "nonLinear":
        for g in geo:
            cmds.nonLinear(deformer, edit=True, geometry=g, remove=True)
    elif defType == "softMod":
        for g in geo:
            cmds.softMod(deformer, edit=True, geometry=g, remove=True)
    elif defType == "cluster":
        for g in geo:
            cmds.cluster(deformer, edit=True, geometry=g, remove=True)


def get_selected_channels(full=True, long=True, *args):
    """
    for ONE object selected, return all selected channels from channel box
    :param full: (boolean) return the full name of the object.attr?, if false then returns only the attr names
    :param long: (boolean) whether we should get the long name of the attr. False will give us "short" names
    :return: list of full obj.channel names selected, or (if not "full") just the channnel names
    """
    cBox = mel.eval('$temp=$gChannelBoxName')

    sel = cmds.ls(sl=True, l=True)
    if len(sel) != 1:
        cmds.warning("You have to select ONE node!")
        return (None)

    obj = sel[0]

    channelsRaw = cmds.channelBox(cBox, q=True, selectedMainAttributes=True,
                                  selectedShapeAttributes=True,
                                  selectedHistoryAttributes=True,
                                  selectedOutputAttributes=True)

    channels = []
    if channelsRaw:
        if int:
            for ch in channelsRaw:
                newC = cmds.attributeQuery(ch, node=obj, longName=True)
                channels.append(newC)
        else:
            for ch in channelsRaw:
                newC = cmds.attributeQuery(ch, node=obj, shortName=True)
                channels.append(newC)
    else:
        return (None)

    returnList = []
    if channels:
        if full:
            for c in channels:
                full = "{0}.{1}".format(obj, c)
                returnList.append(full)
        else:
            returnList = channels

        return (returnList)
    else:
        cmds.warning(
            "zbw_rig.get_selected_channels: I didn't detect any channels selected!")
        return (None)


def average_vectors(vecList, *args):
    """
    returns the average (x, y, z, . . . ) of a list of given vectors
    :param vecList: a list of vectors
    :param args:
    :return:
    """
    avg = [float(sum(x) / len(x)) for x in zip(*vecList)]
    return (avg)


def integer_test(digit):
    """
    tests whether digit is an integer or not
    :param obj: some value
    :param args:
    :return:  boolean
    """
    try:
        int(digit)
        return (True)
    except ValueError:
        return(False)


def increment_name(name, *args):
    """
    increments the given name string by adding 1 to last digit
    note: will not respect padding at the moment, so '_09' will become '_010'
    :param name:
    :param args:
    :return:
    """
    # --------- figure out version that will add padding? Use zfill
    if not cmds.objExists(name):
        return(name)
    else:
        if integer_test(name[-1]):
            newname = "{0}{1}".format(name[:-1], int(name[-1])+1)
        else:
            newname = "{0}_1".format(name)
        return(increment_name(newname))


def get_soft_selection():
    """
    should be a softSelection already selected (components). This returns list of cmpts and list of weights
    :return: list of components, and list of weights
    """
    # Grab the soft selection
    selection = om.MSelectionList()
    softSelection = om.MRichSelection()
    om.MGlobal.getRichSelection(softSelection)
    softSelection.getSelection(selection)

    dagPath = om.MDagPath()
    component = om.MObject()

    # Filter Defeats the purpose of the else statement
    iter = om.MItSelectionList(selection, om.MFn.kMeshVertComponent)
    elements, weights = [], []
    while not iter.isDone():
        iter.getDagPath(dagPath, component)
        dagPath.pop()  # Grab the parent of the shape node
        node = dagPath.fullPathName()
        fnComp = om.MFnSingleIndexedComponent(component)
        getWeight = lambda i: fnComp.weight(
            i).influence() if fnComp.hasWeights() else 1.0

        for i in range(fnComp.elementCount()):
            elements.append('%s.vtx[%i]' % (node, fnComp.element(i)))
            weights.append(getWeight(i))
        next(iter)

    return elements, weights


def closest_point_on_mesh_position(point, mesh, *args):
    """
    point - either a transform (will use rotate pivot), or array 3
    mesh - either shape of poly, or transform of poly
    rtrns position of closest pt
        #--------------------
        #inputs and outputs for "closestPointOnMesh":

        #inputs:
        #"mesh"->"inputMesh" (mesh node of transform)
        #"clusPos"->"inPosition"
        #"worldMatrix"(transform of point)->"inputMatrix"

        #outputs:
        #"position"->surfacepoint in space
        #"u"->parameter u
        #"v"->parameter v
        #"normal"->normal vector
        #"closestFaceIndex"->index of closest face
        #"closestVertexIndex"->index of closet vertex
        #---------------------
    """
    if isinstance(point, str):
        if type_check(point, "transform"):
            # cmds.select(point, r=True)
            ptPos = cmds.xform(point, ws=True, q=True, rp=True)
            name = point
        else:
            cmds.warning(
                "zbw_rig.closest_pt_on_mesh_position: the string you gave me isn't a transform")
            return ()
    elif isinstance(point, (list, tuple)):
        if len(point) == 3:
            ptPos = point
            name = mesh
        else:
            cmds.warning(
                "zbw_rig.closest_pt_on_mesh_position: there are not the right number of indices in the "
                "iterable you gave me. Need 3, you gave {0}".format(len(point)))
    else:
        cmds.warning(
            "zbw_rig.closest_pt_on_mesh_position: You didn't give me a name of transform or position(array["
            "3])")
        return ()

    cpomNode = cmds.shadingNode("closestPointOnMesh", asUtility=True,
                                n="{0}_CPOM".format(name))
    cmds.connectAttr("{0}.outMesh".format(mesh), "{0}.inMesh".format(cpomNode))
    cmds.setAttr("{0}.inPosition".format(cpomNode), ptPos[0], ptPos[1],
                 ptPos[2])
    cmds.connectAttr("{0}.worldMatrix".format(mesh),
                     "{0}.inputMatrix".format(cpomNode))

    cpomPos = cmds.getAttr("{0}.position".format(cpomNode))[0]
    cmds.delete(cpomNode)

    return (cpomPos)


def closest_point_on_mesh_rotation(point, mesh, *args):
    # TODO - generalize for various orientations, and various rotation orders
    """
    takes a point (can be name of transform or iterable(3) of rotations and a poly mesh and gives the rotation [rot
    order xyz] (for
    aim along y) align to surface of
    the xform at that point
    """
    if isinstance(point, str):
        if type_check(point, "transform"):
            cmds.select(point, r=True)
            ptPos = cmds.xform(point, ws=True, q=True, rp=True)
            name = point
        else:
            cmds.warning(
                "zbw_rig.closest_pt_on_mesh_position: the string you gave me isn't a transform")
            return ()
    elif isinstance(point, (list, tuple)):
        if len(point) == 3:
            ptPos = point
            name = mesh
        else:
            cmds.warning(
                "zbw_rig.closest_pt_on_mesh_position: there are not the right number of entries in the "
                "list you gave me")

    # get the rotations to align to normal at this point
    loc = cmds.spaceLocator()
    CPOMesh = closest_point_on_mesh_position(point, mesh)
    cmds.xform(loc, ws=True, t=CPOMesh)
    aimVec = (0, 1, 0)
    upVec = (0, 1, 0)
    nc = cmds.normalConstraint(mesh, loc, aim=aimVec, upVector=upVec)
    rot = cmds.xform(loc, ws=True, q=True, ro=True)
    cmds.delete(nc, loc)
    return (rot)


def calibrate_size(xform, scale=0.2, *args):
    """
    will take the bounding box of given transform and return *scale it's longest edge
    or option to do volume and return some portion of that. . .
    just to give scale factor for controls and such
    :param xform:
    :param args:
    :return:
    """
    if not type_check(xform, "transform"):
        cmds.warning(
            "zbw_rig.calibrate_size: You didn't pass me a transform ({0})".format(
                xform))
        return (None)

    box = cmds.exactWorldBoundingBox(
        xform)  # [xmin, ymin, zmin, xmax, ymax, zmax]
    X = om.MVector(box[0], box[3])
    Y = om.MVector(box[1], box[4])
    Z = om.MVector(box[2], box[5])

    # get bbox lengths along axes
    lenX = (X.y - X.x)
    lenY = (Y.y - Y.x)
    lenZ = (Z.y - Z.x)
    lgst = max([lenX, lenY, lenZ])

    outScale = float(lgst) * float(scale)

    return (outScale)


def average_point_positions(points, *args):
    """
    uses a list of points and gets the average position
    :param points: list of points to average
    :param args:
    :return: a vector of the average position of given elemenets
    """
    positions = []

    for pt in points:
        pos = cmds.pointPosition(pt)
        positions.append(pos)

    avgPos = average_vectors(positions)
    return (avgPos)


def get_deformers(obj, *args):
    """
    gets a list of deformers on the passed obj
    :param obj: string - the transform to get deformers on
    :param args:
    :return:
    """
    history = cmds.listHistory(obj)
    deformerList = []
    if history:
        for node in history:
            types = cmds.nodeType(node, inherited=True)
            if "geometryFilter" in types:
                deformerList.append(types[1])

    return (deformerList)


def bounding_box_center(geo, *args):
    """
    gets center from bounding box
    :param geo: string - the transform to get bbox info from
    :param args:
    :return: vector/list of bounding box center (or None)
    """

    if type_check(geo, "transform"):
        box = cmds.exactWorldBoundingBox(
            geo)  # [xmin, ymin, zmin, xmax, ymax, zmax]
        X = om.MVector(box[0], box[3])
        Y = om.MVector(box[1], box[4])
        Z = om.MVector(box[2], box[5])

        cx = (box[0] + box[3]) / 2
        cy = (box[1] + box[4]) / 2
        cz = (box[2] + box[5]) / 2

        return ([cx, cy, cz])

    return (None)


def new_joint_bind_at_center(tform, *args):
    """
    create a new joint at the boudnign box center of pts and bind all pts to 1
    :param tform - string - the geo to bind
    :param args:
    :return: string - skinCluster
    """
    cmds.select(cl=True)
    jnt = cmds.joint(name="{0}_base_JNT".format(tform))
    center = bounding_box_center(tform)
    cmds.xform(jnt, ws=True, t=center)
    skinCl = cmds.skinCluster(jnt, tform, normalizeWeights=1)[0]

    return (jnt, skinCl)


def plugin_load(plugin, *args):
    """
    checks whether plugin is loaded. Loads it if not
    Args: 
        plugin (string): actual name of plugin to check for
    """
    loaded = cmds.pluginInfo(plugin, q=True, loaded=True)
    if not loaded:
        cmds.loadPlugin(plugin)
        cmds.warning("loaded: {0}".format(plugin))
    else:
        print(("{0} is already loaded!".format(plugin)))


def align_to_curve(crv=None, obj=None, param=None, *args):
    """
    places the obj on the curve aligned to . . .
    Args:
        obj (string): object to align
        crv: (string): curve TRANSFORM to align to
        param (float): parameter along curve to position and orient to
        *args:

    Returns:
        void

    """
    # TODO - check on non-orig geo, check the matrix plugin is loaded
    if not obj and crv and param:
        cmds.warning(
            "zbw_rig.align_to_curve: Didnt' get all the correct params! (obj, crv, param)")
        return ()

    if not type_check(crv, "nurbsCurve"):
        cmds.warning("zbw_rig.align_to_curve: crv param wasn't a curve!")
        return ()

    crvShp = cmds.listRelatives(crv, s=True)[0]
    tempObj = cmds.group(empty=True, name="tempCrvNull")

    poci = cmds.shadingNode("pointOnCurveInfo", asUtility=True, name="tempPOCI")
    cmds.connectAttr("{0}.worldSpace[0]".format(crvShp),
                     "{0}.inputCurve".format(poci))
    cmds.setAttr("{0}.parameter".format(poci), param)
    cmds.connectAttr("{0}.position".format(poci),
                     "{0}.translate".format(tempObj))
    sideVal = cmds.getAttr("{0}.normalizedNormal".format(poci))[0]
    side = om.MVector(sideVal[0], sideVal[1], sideVal[2])
    frontVal = cmds.getAttr("{0}.normalizedTangent".format(poci))[0]
    front = om.MVector(frontVal[0], frontVal[1], frontVal[2])

    up = side ^ front

    mat4 = cmds.shadingNode("fourByFourMatrix", asUtility=True, name="temp4x4")
    decomp = cmds.shadingNode("decomposeMatrix", asUtility=True, name="tempDM")
    yrow = [side[0], side[1], side[2], 0]
    xrow = [front[0], front[1], front[2], 0]
    zrow = [up[0], up[1], up[2], 0]

    for col in range(3):
        cmds.setAttr("{0}.in0{1}".format(mat4, col), xrow[col])
        cmds.setAttr("{0}.in1{1}".format(mat4, col), yrow[col])
        cmds.setAttr("{0}.in2{1}".format(mat4, col), zrow[col])
    cmds.setAttr("{0}.in33".format(mat4), 1)

    cmds.connectAttr("{0}.output".format(mat4),
                     "{0}.inputMatrix".format(decomp))
    cmds.connectAttr("{0}.outputRotate".format(decomp),
                     "{0}.rotate".format(tempObj))
    snap_to(tempObj, obj)

    cmds.delete(tempObj, poci, decomp, mat4)


def get_nonOrig_shapes(*args):
    pass

    # def increment_names(name, nameList?, *args):
    #     """
    #     2 different ways at the moment to increment some names
    #     """
    # backfilling

    # import fnmatch

    # a = ["cat", "cat1", "cat2", "cat3", "cat5"]
    # x = "cat"

    # outName = None
    # matches = fnmatch.filter(a, "{0}*".format(x))
    # lastNums = [y.strip(x) for y in matches]
    # newNum = None

    # if not lastNums[0]:
    #     lastNums[0] = "0"

    # if len(lastNums) > 1:    
    #     for d in range(len(lastNums)-1):
    #         if int(lastNums[d]) + 1 != int(lastNums[d+1]):
    #             newNum = int(lastNums[d])+1
    # else:
    #     newNum = 1

    # outName = x + str(newNum)
    # print outName


    # # no backfilling
    # import fnmatch

    # a = ["cat", "cat1", "cat2", "cat33"]

    # x = "cat"

    # outName = None

    # matches = fnmatch.filter(a, "{0}*".format(x))
    # if matches:
    #     lastNum = matches[-1].strip(x)

    #     if lastNum:
    #         lastInt = int(lastNum)
    #         newNum = lastInt + 1
    #         outName = x + str(newNum)
    #     else:
    #         outName = x + "1"
    # else:
    #     outName = x

    # print outName
    pass


def get_top_nodes(objects=[], *args):
    """
    from given list of objects return a list of the top nodes in DAG hierarchy
    Args:
        objects (list): list of scene objects
    Return:
        list: any top level nodes of the given objects
    """
    roots = []

    for objs in objects:
        obj = ""
        if cmds.objectType(objs) == "transform":
            obj = cmds.ls(objs, l=True, dag=True)[0]
        if obj:
            root = (obj.split("|")[:2])
        if root:
            if len(root) > 1 and root[1] not in roots:
                roots.append(root[1])

    return (roots)


def zero_pivot(objects=None, *args):
    """
    from given list of objects (or selected objs if no list given), puts the pivot at the origin
    This is essentially the same as freezing transforms, just with the pivot at origin
    Args:
        objects (list): list of scene transforms
    """
    if not objects:
        objects = cmds.ls(sl=True)

    if not objects:
        return ()

    for obj in objects:
        cmds.xform(obj, ws=True, p=True, pivots=(0, 0, 0))
        cmds.makeIdentity(obj, apply=True)


def average_transform_position(srcList):
    """gets the average of the xforms in worldspace"""
    positions = []
    for src in srcList:
        srcPos = cmds.xform(src, ws=True, q=True, rp=True)
        positions.append(srcPos)

    avgPos = average_vectors(positions)
    return (avgPos)


def linear_interpolate_vector(v1, v2, percent):
    """
    percent is 0-1 float
    """
    v1Vec = om.MVector(v1[0], v1[1], v1[2])
    v2Vec = om.MVector(v2[0], v2[1], v2[2])
    outVec = ((v2Vec - v1Vec) * percent) + v1Vec

    return (outVec.x, outVec.y, outVec.z)


def linear_interpolate_scalar(a, b, percent):
    """
    percent is 0-1 float
    """
    return ((float(b) - float(a)) * percent + a)


def create_joint_chain(startVec, endVec, numJnts, name="joint", suffix="JNT"):
    """
    Creates a chain of joints from startVec to endVec 
    ARGS:
        startVec(vector): position of first joint
        endVec(vector): position of second joint
        numJnts(int): number of joints to create
        name(str): base name for joints
        suffix(str): suffix to add after name (a '_' will be added inbetween)
    RETURN:
        list: joint names in order
    """
    cmds.select(cl=True)
    joints = []
    start = om.MVector(startVec[0], startVec[1], startVec[2])
    end = om.MVector(endVec[0], endVec[1], endVec[2])
    vec = end-start

    for x in range(numJnts):
        factor = 1/float(numJnts-1)
        pos = linear_interpolate_vector(start, end, factor*x)
        jnt = cmds.joint(name="{0}{1}_{2}".format(name, x, suffix),  p=pos)
        joints.append(jnt)

    cmds.joint(joints[0], e=True, ch=True, orientJoint="xyz", secondaryAxisOrient="yup")
    cmds.select(joints[0], r=True)
    
    return(joints)


def clean_joint_chain(jnt, *args):
    """removes rotation from jnts leaving them free to be oriented"""
    sel = cmds.ls(sl=True)
    cmds.select(jnt, hi=True, r=True)
    jntList = cmds.ls(sl=True)
    if len(jntList)>1:
        worldList = [cmds.parent(x, world=True)[0] for x in jntList[1:]]
        worldList.insert(0, jnt)

        for k in worldList:
            cmds.setAttr("{0}.r".format(k), 0, 0, 0)

        for i in range(len(worldList)-1, 0, -1):
            cmds.parent(worldList[i], worldList[i-1])
    else:
        cmds.setAttr("{0}.r".format(jnt), 0, 0, 0)
    cmds.select(sel)


def create_set(name=None, *args):
    """creates a set with selected objs"""
    sel = cmds.ls(sl=True)
    if not name:
        name = "userSet1"
    sets = cmds.sets(sel, name=name)


def display_layer_from_selection(*args):
    """creates a display layer using maya's autosettings from the selection"""
    cmds.createDisplayLayer(name="auto_DL")


def remove_front_pipe(name, *args):
    """remove a leading pipe in given name, returns cleaned name"""
    if name[0] == "|":
        cleanName = name[1:]
    else:
        cleanName = name
    return(cleanName)


def get_bind_joints_from_geo(geo=None, *args):
    """returns bind joints from all selected geometry"""
    if not geo:
        geo = cmds.ls(sl=True, type="transform")
    if not geo:
        return()
    allJnts = []
    
    for g in geo:
        jnts = cmds.skinCluster(g, q=True, influence=True)
        allJnts.extend(jnts)
    
    jnts = list(set(allJnts))    
    return(jnts)


def create_proxy_geo(jnts=[], geoType="cylinder", axis=[1, 0, 0], pivot="base", scale=1.0, *args):
    """
    creates basic geo for proxies from a given list of joints, one geo per joint. Geo is of type 'geoType', along axis 'axis' and has a pivot at either the center or base of geo. Scale is 'scale' along axis and 0.5*scale along other axes
    ARGS:
        jnts(list): the joints to operate on
        geoType(string): "cylinder", "cube"
        axis(tuple): generally (1, 0, 0), (0, 1, 0), (0, 0, 1)
        pivot(string): "base", "center"
    RETURN:
        list: the geo list
    """
    geoList = []

    for jnt in jnts:
        if geoType == "cylinder":
            geo = cmds.polyCylinder(axis=axis, name="{0}_ProxyGeo".format(jnt), radius=0.5*scale, height=scale, ch=0)[0]
        if geoType == "cube":
            geo = cmds.polyCube(axis=axis, name="{0}_ProxyGeo".format(jnt), w=0.5*scale, h=1*scale, d=0.5*scale, ch=0)[0]

        if pivot == "base":
            cmds.xform(geo, ws=True, r=True, t=[axis[0]*0.5*scale, axis[1]*0.5*scale, axis[2]*0.5*scale])
            cmds.xform(geo, ws=True, a=True, rp=[0, 0, 0])
            cmds.xform(geo, ws=True, a=True, sp=[0, 0, 0])
            cmds.makeIdentity(geo, apply=True)
        cmds.DeleteHistory(geo)
        snap_to(jnt, geo)
        geoList.append(geo)

    return(geoList)


def bind_combine_proxy_geo(jntList=[], geoList=[], *args):
    """
    takes matching joint and geo lists and binds each geo to the respective joint. Freezes geos.
    Then combines all geo into one called 'proxyCombined_GEO'
    ARGS:
        jntList(list)
        geoList(list)
    """
    for x in range(len(jntList)):
        geo = geoList[x]
        jnt = jntList[x]
        cmds.makeIdentity(geo, apply=True)
        cmds.skinCluster(jnt, geo, bindMethod=0, skinMethod=0, normalizeWeights=1, maximumInfluences=1, obeyMaxInfluences=True, tsb=True)

    combined = cmds.polyUniteSkinned(geoList, ch=0, mergeUVSets=True, centerPivot=True)[0]
    proxyCombined = cmds.rename(combined, "proxyCombined_GEO")
    return(proxyCombined)


def is_close(a, b, rel_tol=1e-07, abs_tol=0.0):
    """
    tests if numbers are within the given (or absolute) tolerance
    Return: boolean
    """
    return(abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol))