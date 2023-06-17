########################
#file: zbw_makeFollicle.py
#Author: zeth willie
#Contact: zeth@catbuks.com, www.williework.blogspot.com
#Date Modified: 04/27/13
#To Use: type in python window  "import zbw_makeFollicle as fol; fol.makeFollicle()"
#Notes/Descriptions: select a poly vertex and run to create a follicle stuck to the mesh at that location
########################

#create a follicle on the specified uv location
import maya.cmds as cmds
import zTools3.rig.zbw_rig as rig
import maya.mel as mel

widgets = {}

#here create a UI that will just pass info into the main func. So you can call function if you want with args or use the UI
def follicleUI(*args):
    """UI for the script"""

    if cmds.window("folWin", exists=True):
        cmds.deleteUI("folWin")

    widgets["win"] = cmds.window("folWin", t="zbw_makeFollicle", w=300, h=100)
    widgets["mainCLO"] = cmds.columnLayout()
    # widgets["polyFrame"] = cmds.frameLayout(l="Polygon Vert(s) Follicle")
    # widgets["polyCLO"] = cmds.columnLayout()
    widgets["text"] = cmds.text("Select one or two vertices (2 will get avg position) and run")
    widgets["nameTFG"] = cmds.textFieldGrp(l="FollicleName:", cal=([1, "left"],[2,"left"]), cw=([1,100],[2,200]), tx="follicle")
    cmds.separator(h=10)
    widgets["button"] = cmds.button(w=300, h=50, bgc=(0.6,.8,.6), l="Add follicle to vert(s)", c=getUV)
    # cmds.setParent(widgets["mainCLO"])
    # widgets["nurbsFrame"] = cmds.frameLayout(l="Nurbs select")
    cmds.showWindow(widgets["win"])
    cmds.window(widgets["win"], e=True, w=300, h=100)
#-------could also select edit point????
#-------multiple selection and average uv position? Orrrr option to create multiple UV's, one on each vertex
#-------grab an edge and convert to 2 verts and get average. . .
#-------have option for distributed (select 2 verts and number of follicles, spread that num between the two uv positions)

def getUV(*args):
    """takes a selection of one or two verts and returns one UV position. If just the surface is selected, it will return UV vals of (.5, .5)"""

    #get vertex
    sel = cmds.ls(sl=True)
    #------filter for vertices (or cvs?)
    vertices = cmds.filterExpand(sm=(31), fp=True, ex=True)
    try:
        if len(vertices)>2:
            cmds.warning("You've selected more than two verts. Two is the max number I can take")
    except:
        cmds.warning("Please select one or two vertices!")
    uvs = []

    if vertices:
        #here deal with option to use one or average uv values of two selections (shouldn't be more than two)?
        for vert in vertices:
            #convert vertex to uvs
            thisUV = cmds.polyListComponentConversion(vert, fv=True, tuv=True)[0]
            uvs.append(thisUV)
    else:
        cmds.warning("You haven't selected any verts! Select one or two to place a follicle")

        #convert vertices to uvs and get their value
        if uvs:
            uvList = []
            for uv in uvs:
                #grab first (cuz verts can be multiple uv's)
                thisUV = cmds.ls(uv)[0]
                #convert the uv index to u and v values
                uvVal = cmds.polyEditUV(uv, q=True)
                uvList.append(uvVal)

            U = []
            V = []
            sizeUV = len(uvList)
            #print uvList
            for uv in uvList:
                U.append(uv[0])
                V.append(uv[1])
            #print "U = %s"%U
            #print "V = %s"%V
            #DO THE AVERAGING HERE
            x = 0
            y = 0
            for a in U:
                x = x + a
            for b in V:
                y = y + b
            u = x/sizeUV
            v = y/sizeUV
            uvVal = [u,v]

            cmds.select(vertices)

            shapeName = vertices[0].rpartition(".vtx")[0]
            meshName = cmds.listRelatives(shapeName, p=True)[0]
            folName = cmds.textFieldGrp(widgets["nameTFG"], q=True, tx=True)
            uValue = uvVal[0]
            vValue = uvVal[1]

            follicle(meshName, folName, uValue, vValue)

        else:
            pass
            
#---------------- use the rig version
def follicle(surface="none", folName="none", u=0.5, v=0.5, *args):
    """not quite finished here. . . takes the surface/mesh, a name for the follicle and u & v positions as args and creates a follicle at that uv position on that surface"""

#------------do a bit more checking here to make sure the shapes, numbers etc work out
#------------i.e. make sure the name of the follicle isn't already taken before trying to create the new one
    # print "surface is: %s"%surface
    # print "folName is: %s"%folName
    if not (cmds.objExists(folName)):
        if surface=="none":
            #decide if surface is polymesh or nurbsSurface
            #TO-DO----------------make this more generic so I can use it elsewhere
            surfaceXform = cmds.ls(sl=True, dag=True, type="transform")[0]
            surfaceShape = cmds.listRelatives(surfaceXform, shapes=True)[0]
        else:
            surfaceXform = surface
            surfaceShape = cmds.listRelatives(surfaceXform, shapes=True)[0]

        if folName == "none":
            folShapeName = "myFollicleShape"
            folXformName = "myFollicle"
        else:
            folShapeName = "{0}Shape".format(folName)
            folXformName = folName

        #create the follicle
        folShape = cmds.createNode("follicle", n=folShapeName)
        folXform = cmds.listRelatives(folShape, p=True, type="transform")[0]
        cmds.rename(folXform, folXformName)

        cmds.connectAttr("{0}.worldMatrix[0]".format(surfaceShape), "{0}.inputWorldMatrix".format(folShape))

        #check for surface type, poly or nurbs and connect the matrix into the follicle
        if (cmds.nodeType(surfaceShape)=="nurbsSurface"):
            cmds.connectAttr("{0}.local".format(surfaceShape), "{0}.inputSurface".format(folShape))
        elif (cmds.nodeType(surfaceShape)=="mesh"):
            cmds.connectAttr("%s.outMesh"%surfaceShape, "%s.inputMesh"%folShape)
        else:
            cmds.warning("not the right kind of selection. Need a poly or nurbs surface")

        #connect the transl, rots from shape to transform of follicle
        cmds.connectAttr("{0}.outTranslate".format(folShape), "{0}.translate".format(folXform))
        cmds.connectAttr("{0}.outRotate".format(folShape), "{0}.rotate".format(folXform))

        cmds.setAttr("{0}.parameterU".format(folShape), u)
        cmds.setAttr("{0}.parameterV".format(folShape), v)

        cmds.setAttr("{0}.translate".format(folXform), l=True)
        cmds.setAttr("{0}.rotate".format(folXform), l=True)

        attrsToHide = ["restPose", "pointLock", "simulationMethod", "startDirection", "flipDirection",
                         "overrideDynamics", "collide", "damp", "stiffness", "lengthFlex", "clumpWidthMult",
                         "startCurveAttract", "attractionDamp", "densityMult", "curlMult", "clumpTwistOffset",
                         "braid", "colorBlend", "colorR", "colorG", "colorB", "fixedSegmentLength", "segmentLength",
                         "sampleDensity", "degree", "clumpWidth"]
        for attr in attrsToHide:
            cmds.setAttr("{0}.{1}".format(folShape, attr), k=False)

        newName = rig.increment_name(folName)
        cmds.textFieldGrp(widgets["nameTFG"], tx=newName, e=True)

    else:
        cmds.warning("That name already exists! Choose another name!")

def integerTest(test, *args):
    """use to test if the arg is an integer"""

    try:
        int(test)
        return True
    except:
        return False

def makeFollicle():
    """Use this to start the script!"""

    follicleUI()