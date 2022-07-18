import maya.cmds as cmds
from functools import partial

#quick UI
def ipMoverUI():
    if (cmds.window('zbw_ipMoverUI', exists=True)):
        cmds.deleteUI('zbw_ipMoverUI', window=True)
        cmds.windowPref('zbw_ipMoverUI', remove=True)
    window=cmds.window('zbw_ipMoverUI', widthHeight=(400,200), title='zbw_imagePlane')
    cmds.columnLayout('zbw_ipmMainColumn')

    cam = cmds.ls(sl=True,dag=True,s=True, type="camera")
    if cam:
        ip = cmds.listConnections(cam[0], type="imagePlane")
        if ip:
            imagePlane = ip[0]
            ipText = imagePlane
        else:
            cmds.warning("there's no image plane on this camera")
            ipText = "no image plane"
    else:
        cmds.warning("select a camera")
        ipText = "no image plane"

    cmds.text(ipText)
    cmds.separator(h=20, style="double")

    if cam and ip:

        #---------------store original values somewhere . . .

        cmds.floatSliderGrp("alphaFSG", label='alpha',cal = [1,"left"], cw3=[50, 50, 300],width=400, field=True, minValue=0, maxValue=1, fieldMinValue=0, fieldMaxValue=1, value=1, pre=3, dc=partial(changeValue, (imagePlane + ".alphaGain"), "alphaFSG"))

        cmds.separator(h=20, style = "double")

        cmds.floatSliderGrp("centerXFSG", label='centerX',cal = [1,"left"], cw3=[50, 50, 300],width=400, field=True, minValue=-20.0, maxValue=20.0, fieldMinValue=-100.0, fieldMaxValue=100.0, value=0, pre=3, dc=partial(changeValue, (imagePlane + ".centerX"), "centerXFSG"))

        cmds.floatSliderGrp("centerYFSG", label='centerY',cal = [1,"left"], cw3=[50, 50, 300],width=400, field=True, minValue=-20.0, maxValue=20.0, fieldMinValue=-100.0, fieldMaxValue=100.0, value=0, pre=3, dc=partial(changeValue, (imagePlane + ".centerY"), "centerYFSG"))

        cmds.floatSliderGrp("centerZFSG", label='centerZ',cal = [1,"left"], cw3=[50, 50, 300],width=400, field=True, minValue=-20.0, maxValue=20.0, fieldMinValue=-100.0, fieldMaxValue=100.0, value=0, pre=3, dc=partial(changeValue, (imagePlane + ".centerZ"), "centerZFSG"))

        cmds.floatSliderGrp("widthFSG", label='width',cal = [1,"left"], cw3=[50, 50, 300],width=400, field=True, minValue=0, maxValue=20.0, fieldMinValue=0, fieldMaxValue=100.0, pre=3, dc=partial(changeValue, (imagePlane + ".width"), "widthFSG"))

        cmds.floatSliderGrp("heightFSG", label='height',cal = [1,"left"], cw3=[50, 50, 300],width=400, field=True, minValue=0, maxValue=20.0, fieldMinValue=0, fieldMaxValue=100.0, pre=3, dc=partial(changeValue, (imagePlane + ".height"), "heightFSG"))


    cmds.showWindow(window)

    cmds.window('zbw_ipMoverUI', e=True, w=400, h=200)

def changeValue(attr, slider, *args):

    value = cmds.floatSliderGrp(slider, q=True, v=True)
    cmds.setAttr(attr, value)

# def focusToCamera():

    #get camera from focus window
    # panel = cmds.getPanel(wf=True)
    # cam = cmds.modelEditor(panel, q=True, camera=True)

#----------get camera from focus . . .
#----------have camera list to select from . . .

# (coverageX)
# (coverageY)


def zbw_ipMover():
    ipMoverUI()

