#create a follicle on the specified uv location
import maya.cmds as cmds
import maya.mel as mel

#here create a UI that will just pass info into the main func. So you can call function if you want with args or use the UI


def zbw_follicle(surface="none", folName="none", u=0.5, v=0.5, *args):

#------------do a bit more checking here to make sure the shapes, numbers etc work out
    if surface=="none":
        #decide if surface is polymesh or nurbsSurface
        surfaceXform = cmds.ls(sl=True, dag=True, type="transform")[0]
        surfaceShape = cmds.listRelatives(surfaceXform, shapes=True)[0]
    else:
        surfaceXform = surface
        surfaceShape = cmds.listRelatives(surfaceXform, shapes=True)[0]

    if folName == "none":
        folShapeName = "myFollicleShape"
        folXformName = "myFollicle"
    else:
        folShapeName = "%sShape"%folName
        folXformName = folName

    #create the follicle
    folShape = cmds.createNode("follicle", n=folShapeName)
    folXform = cmds.listRelatives(folShape, p=True, type="transform")[0]
    cmds.rename(folXform, folXformName)

    #connect up the follicle!
    #connect the matrix of the surface to the matrix of the follicle
    cmds.connectAttr("%s.worldMatrix[0]"%surfaceShape, "%s.inputWorldMatrix"%folShape)

    #check for surface type, poly or nurbs and connect the matrix into the follicle
    if (cmds.nodeType(surfaceShape)=="nurbsSurface"):
        cmds.connectAttr("%s.local"%surfaceShape, "%s.inputSurface"%folShape)
    elif (cmds.nodeType(surfaceShape)=="mesh"):
        cmds.connectAttr("%s.outMesh"%surfaceShape, "%s.inputMesh"%folShape)
    else:
        cmds.warning("not the right kind of selection. Need a poly or nurbs surface")

    #connect the transl, rots from shape to transform of follicle
    cmds.connectAttr("%s.outTranslate"%folShape, "%s.translate"%folXform)
    cmds.connectAttr("%s.outRotate"%folShape, "%s.rotate"%folXform)

    cmds.setAttr("%s.parameterU"%folShape, u)
    cmds.setAttr("%s.parameterV"%folShape, v)

    cmds.setAttr("%s.translate"%folXform, l=True)
    cmds.setAttr("%s.rotate"%folXform, l=True)

    return(folXform, folShape)


zbw_follicle()