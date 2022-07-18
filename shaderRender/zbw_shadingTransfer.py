import maya.cmds as cmds
from functools import partial
import zTools.resources.mayaDecorators as md
# can delete above import if necessary

widgets = {}
def shadingTransferUI(*args):
    if cmds.window("win", exists=True):
        cmds.deleteUI("win")

    widgets["win"] = cmds.window("win", t="zbw_shadingTransfer", w=200, h=100, s=False)
    widgets["mainCLO"] = cmds.columnLayout()

    cmds.text(l="1. Select the source object (poly/nurbs)", al="left")
    cmds.text(l="2. Select the target object(s)", al="left")
    cmds.text(l="Note: deleteHistory on the transferUV\nwill try to avoid deleting deformers.\nNo promises:)", al="left")
    cmds.separator(h=10)
    widgets["shdBut"] = cmds.button(l="Copy Shaders to targets!", w=200, h=40, bgc=(.4, .7, .4), c=partial(getSelection, "copyShader"))
    cmds.separator(h=10)
    widgets["uvBut"] = cmds.button(l="Transfer UV's to targets!", w=200, h=40, bgc=(.7, .7, .5), c=partial(getSelection, "transferUV"))
    widgets["xferCBG"] = cmds.checkBoxGrp(l="Delete history after transfer?", v1=0, cal=[(1, "left"), (2,"left")], cw=[(1, 150), (2, 50)])
    cmds.window(widgets["win"], e=True, w=200, h=100)
    cmds.showWindow(widgets["win"])


def getSelection(func, *args):
    """
    gets the selection and passes it to the correct function for execution

    Args:
        func (string): the name of the function to call
    Return:
        None
    """
    sel = cmds.ls(sl=True)

    if sel:
        # filter out any non-poly, nurbs
        geo = cmds.filterExpand(sel, selectionMask=(10, 12))

        if len(geo) < 2:
            cmds.warning("You haven't selected two pieces of geometry!")
            return()

        src = geo[0]
        tgts = geo[1:]

        if func == "copyShader":
            copyShader(src, tgts)

        if func == "transferUV":
            deleteHistory = cmds.checkBoxGrp(widgets["xferCBG"], q=True, v1=True)
            transferUV(src, tgts, deleteHistory)
    else:
        cmds.warning("You need to select one geo as the source THEN more geo to transfer to!")
        return()

@md.d_unifyUndo
def copyShader(src = "", tgts = [], *args):
    """
    gets the shader from the src and assigns it to the tgt objs

    Args:
        src (string): the object we're getting the shader FROM
        tgts (list[strings]): the objects we're setting the shaders TO
    """
    confirm = confirmDialog("Should I copy shaders?")
    if confirm == "Yes":
        for tgt in tgts:
            shp = cmds.listRelatives(src, s=True)[0]
            sg = cmds.listConnections(shp, t="shadingEngine")[0]
            tshp = cmds.listRelatives(tgt, s=True)[0]
            cmds.sets(tshp, e=True, forceElement=sg)
    else:
        print("Copy shader assignment cancelled")
        return()


@md.d_unifyUndo
def transferUV(src, tgts, deleteHistory=False, *args):
    """
    gets the shader and uv's from the src and assigns to the tgt objs (transfer uv's)

    Args:
        src (string): the object we're getting the shader and uv's FROM
        tgts (list[strings]): the objects we're setting the shaders and uv's Return
        deleteHistory (boolean): delete constructionHistory? Will delete non-deformer history. . . 
    TO:
        None
    """ 
    message = ""
    if deleteHistory:
        message = "Should I copy transfer UV's?\nWarning: 'deleteHistory' will (duh) remove history,\ntho it SHOULD keep deformer history."
    if not deleteHistory:
        message = "Should I copy transfer UV's?"

    confirm = confirmDialog(message)
    if confirm == "Yes":
        if deleteHistory:
            srcShp = [x for x in cmds.listRelatives(src, s=True) if "Orig" not in x][0]

            for t in tgts:
                intObj = ""
                shps = cmds.listRelatives(t, s=True)
                for shp in shps:
                    # ----------- clean this up to only get the upstream-most orig node
                    if cmds.getAttr("{0}.intermediateObject".format(shp)):
                        intObj = shp
                        break
                if intObj:
                    print(("transferring uvs to {0}.intermediateObject".format(intObj)))
                    cmds.setAttr("{0}.intermediateObject".format(intObj), 0)
                # try this instead? Maybe don't need intermediate object?
                # cmds.polyTransfer(t, uv=1, ao=src)
                    cmds.transferAttributes(srcShp, intObj, uvs=2, sampleSpace=4)
                    cmds.delete(intObj, constructionHistory=True)
                    cmds.setAttr("{0}.intermediateObject".format(intObj), 1)
                else:
                    print("transferring uvs to {0} shape")
                    cmds.transferAttributes(srcShp, t, uvs=2, sampleSpace=4)
                    cmds.delete(t, ch=True)

        else:
            srcShp = [x for x in cmds.listRelatives(src, s=True) if "Orig" not in x][0]
            for t in tgts:
                cmds.transferAttributes(srcShp, t, uvs=2, sampleSpace=4)

    else:
        print("Transfer UVs cancelled!")
        return()


def confirmDialog(message = "confirm?", *args):
    """
    just returns Yes or No

    Args:
        message(string): the message to display
    Return:
        string: "Yes" or "No"
    """

    dial = cmds.confirmDialog(t="Confirm?", m=message, button=["Yes", "No"], dismissString="No")

    return(dial)


def shadingTransfer(*args):
    shadingTransferUI()