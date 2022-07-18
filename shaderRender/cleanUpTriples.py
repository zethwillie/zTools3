import maya.cmds as cmds

myShape = "extrudedSurfaceShape3"
ts = "blinn1_TripleSwitch"
list = cmds.listAttr(ts, m=True, st=["*input*"])
for input in list:
    shp = cmds.connectionInfo("{0}.{1}.inShape".format(ts, input), sfd=True).partition(".")[0]
    print(shp)
    if shp == myShape:
        # clear out the shape node
        cmds.disconnectAttr("{0}.instObjGroups[0]".format(shp), "{0}.{1}.inShape".format(ts, input))
        # clear out the texture (delete if we can)
        txt = cmds.connectionInfo("{0}.{1}.inTriple".format(ts, input), sfd=True).partition(".")[0]
        p2d = cmds.connectionInfo("{0}.uvCoord".format(txt), sfd=True).partition(".")[0]
        cmds.delete(txt, p2d)