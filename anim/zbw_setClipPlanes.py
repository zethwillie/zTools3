import maya.cmds as cmds

def setClipUI(*args):
    """ UI for the whole thing"""

    if cmds.window("SCPwin", exists=True):
        cmds.deleteUI("SCPwin")
    cmds.window("SCPwin", t="Set Clip Planes", w=200, h=100)
    cmds.columnLayout("colLO")
    cmds.radioButtonGrp("camRBG", l="Cameras:", nrb=2, l1="All", l2="Selected", sl=1, cal=[(1,"left"),(2,"left"),(3,"left")], cw=[(1,70),(2,50),(3,50)])
    cmds.floatFieldGrp("nearFFG", l="nearClip", v1=1, cal=([1,"left"], [2,"left"]), cw=([1,50], [2,150]))
    cmds.floatFieldGrp("farFFG", l="farClip", v1=100000, cal=([1,"left"], [2,"left"]), cw=([1,50], [2,150]))
    cmds.separator(h=10,style="single")
    cmds.button("button", l="Set Clip Planes", h=50, w=200, bgc=(.8, .6,.6), c=setPlanes)

    cmds.showWindow("SCPwin")
    cmds.window("SCPwin", e=True, w=200, h=100)


def setPlanes(*args):
    """sets clipping planes for cameras based on float fields in UI. Depending on radio button, it will either do all camera or only selected"""

    all = cmds.radioButtonGrp("camRBG", q=True, sl=True)
    far = cmds.floatFieldGrp("farFFG", q=True, v1=True)
    near = cmds.floatFieldGrp("nearFFG", q=True, v1=True)

    cams = []
    if all==1:
        cams.extend(cmds.ls(type="camera"))
    elif all==2:
        transf = cmds.ls(sl=True, type="transform")
        for each in transf:
            shape = cmds.listRelatives(each, s=True)
            if shape:
                if cmds.objectType(shape) == "camera":
                    cams.extend(shape)
    #for each, set shape.farClipPlane 100000
    if cams:
        print(cams)
        for cam in cams:
            try:
                cmds.setAttr("%s.farClipPlane"%cam, far)
                cmds.setAttr("%s.nearClipPlane"%cam, near)

            except:
                cmds.warning("Couldn't change the farClipPlane of %s"%cam)


def setClipPlanes(*args):
    """Use this to start the script!"""

    setClipUI()
