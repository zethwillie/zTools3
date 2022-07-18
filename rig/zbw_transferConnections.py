import maya.cmds as cmds

#---------------- maybe we should exclude: create nodes, figure out shader nodes (index up?)
#---------------- then we need to test for binding and do the copy skin weights. . . 
#---------------- get the top node, not just the shape node

#---------------- deal with the idea of copying the same shape to a different object (where is the shape coming from? tweak? orig? 
#---------------- which connections to exclude?)

#---------------- maybe have option to get everything downstream (get objs below selected)

#---------------- ui: 
#---------------- options for xform, shape, all below or just selected (or just based on namespace? like framestore) etc. . , 
#---------------- window to show exceptions

#---------------- If there are deformers do those separately . . . lattice, etc. see cmds.lattice(lat, e=True, geometry=True)

widgets = {}

def transfer_connections_UI(*args):
    if cmds.window("xferConWin", exists=True):
        cmds.deleteUI("xferConWin")

    widgets["win"] = cmds.window("xferConWin", w=200, rtf=True)
    widgets["clo"] = cmds.columnLayout()
    cmds.separator(h=10)
    widgets["shapeCBG"] = cmds.checkBoxGrp(ncb=2, labelArray2=("transforms?", "shapes?"), cw=[(1, 100),(2, 100)], valueArray2=(1, 1), cal=[(1,"left"), (2,"left")])
    cmds.separator(h=10)
    widgets["inOutCBG"] = cmds.checkBoxGrp(ncb=2, labelArray2=("inputs?", "outputs?"), cw=[(1, 100),(2, 100)], valueArray2=(0, 1), cal=[(1,"left"), (2,"left")])
    cmds.separator(h=10)
    widgets["xferBut"] = cmds.button(l="Transfer Connections", w=200, h=40, bgc=(.7, .5, .5), c=options_pass)

    cmds.window(widgets["win"], e=True, w=5, h=5, rtf=True)
    cmds.showWindow(widgets["win"])


def options_pass(*args):
    xfersDo, shpsDo = cmds.checkBoxGrp(widgets["shapeCBG"], q=True, valueArray2=True)
    inputs, outputs = cmds.checkBoxGrp(widgets["inOutCBG"], q=True, valueArray2=True)

    sel = cmds.ls(sl=True)
    if len(sel) != 2:
        cmds.warning("You don't have two things selected! (source, then target)")
        return()    

    srcX = sel[0]
    tgtX = sel[1]

    if xfersDo:
        transfer_connections_do(srcX, tgtX, inputs, outputs)

    if shpsDo:
        # options for checkbox would go here. . . 
        srcShp = cmds.listRelatives(srcX, s=True)[0]
        tgtShp = cmds.listRelatives(tgtX, s=True)[0]
        transfer_connections_do(srcShp, tgtShp, inputs, outputs)


def transfer_connections_do(srcIn, tgtIn, inputs, outputs, *args):
    """
    the source obj is first selected, tgt obj (move connections to this) is second
    inputs/outputs are bools to say which side we'll do
    """
#---------------- exlude stuff going to "inMesh" attr?
    excludeList = ["polyCube", "polySphere", "polyCylinder", "polyCone", "polyTorus", "polyPlane", "polyPipe", "polyPyramid"]

    cncts = get_connections(srcIn)

    if not cncts:
        cmds.warning("No connections on {0}".format(srcIn))
        return()
    # in cncts
#---------------- here we might have to parse the type of inputs (instead of just getting connections) for the shape node
#---------------- use other scripts. For skin clusters we need to use the other scripts also. . . 
    if inputs:
        if cncts[0]:
            print((cncts[0]))
            return()
            for cnct in cncts[0]:
                src = cnct[0]
                tgtRaw = cnct[1]
                tgt = tgtRaw.replace(srcIn, tgtIn)
                print((src + "  =======>  " + tgt))
                try: 
                    cmds.connectAttr(src, tgt, f=True)
                except Exception as e:
                    print(e)
        else:
            cmds.warning("No connections on input side of {0}".format(srcIn))

    # should be good here. . . 
    if outputs:
        if cncts[1]:
            for cnct in cncts[1]:
                srcRaw = cnct[0]
                tgt = cnct[1]
                src = srcRaw.replace(srcIn, tgtIn)
                print((src + "  ======>  " + tgt))
                try:
                    cmds.connectAttr(src, tgt, f=True)
                except Exception as e:
                    print(e)
        else:
            cmds.warning("No connections on output side of {0}".format(srcIn))


def get_connections(sourceObj, *args):
    """
    sourceObj can be transform or shape. 
    returns two lists of lists->first is inCons, second is outCons, [[source1, destination1], [s2, d2]. . .]
    """

    otherSources = cmds.listConnections(sourceObj, s=True, d=False, p=True)
    otherDestinations = cmds.listConnections(sourceObj, s=False, d=True, p=True)

    myInCons = []
    myOutCons = []

    if otherSources:
        for source in otherSources:
            inCons = []
            outConList = cmds.connectionInfo(source, destinationFromSource=True)
            for oc in outConList:
                if "{0}.".format(sourceObj) in oc:
                    inCons.append(oc)
                    myInCons.append([source, oc])

    if otherDestinations:
        for dest in otherDestinations:
            outCons = []
            outConList = cmds.connectionInfo(dest, sourceFromDestination=True)
            myOutCons.append([outConList, dest])

    return(myInCons, myOutCons)


def transfer_connections(*args):
    transfer_connections_UI()