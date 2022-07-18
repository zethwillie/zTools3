import maya.cmds as cmds
import os

widgets = {}

def camExportUI(*args):
    """UI for the camera export function"""

    if cmds.window("cwin", exists=True):
        cmds.deleteUI("cwin")

    widgets["cwin"] = cmds.window("cwin", t="Camera Exporter", w=200, h=455)
    widgets["mainFLO"] = cmds.formLayout(w=200, h=455, bgc = (.4, .4, .4))

    widgets["camText"] = cmds.text(l="Cameras", al="left", font = "boldLabelFont")
    widgets["camTSL"] = cmds.textScrollList(w=200, h=100, bgc = (0,0,0), ams = True)
    widgets["refreshBut"] = cmds.button(w=200, h=20, l="Refresh All", bgc = (.5,.3,.3), c= refreshCameras)
    widgets["locRBG"] = cmds.radioButtonGrp(nrb = 2, l="Save Directory: ", en=True, l1="Default", l2="Custom", sl=2, cal=[(1, "left"), (2,"left"),(3, "left")], cw=[(1,75),(2,60),(3,60)])
    widgets["locTFBG"] = cmds.textFieldButtonGrp(l="", cw = [(1, 0),(2, 170),(3, 30)], tx = "click button to choose", eb = True, ed = True, cal=[(1, "left"), (2,"left"),(3, "left")], bl="...", bc = chooseLocation)
    widgets["nameText"] = cmds.text(l="File Name:", al="left")
    widgets["nameTF"] = cmds.textField(w= 195,  tx = "fileName")
    widgets["exportBut"] = cmds.button(l="Export Selected Cams!", w=200, h=50, bgc = (.3, .5,.3), c=dupeBakeObjects)
    widgets["otherCBG"] = cmds.checkBoxGrp(l="Export other selected objects:", ncb = 1, v1=0, cw = [(1, 150),(2, 50)], cal = [(1,"left"), (2,"left")])
    widgets["convertCBG"] = cmds.checkBoxGrp(l="Convert objs to locators?", ncb = 1, v1=1, cw = [(1, 150),(2, 50)], cal = [(1,"left"), (2,"left")])
    widgets["timeRBG"] = cmds.radioButtonGrp(nrb = 2, l="Range: ", l1="TimeSlider", l2="Custom", sl=1, cal=[(1, "left"), (2,"left"),(3, "left")], cw=[(1,50),(2,75),(3,60)], cc=toggleRange)
    widgets["timeIFG"] = cmds.intFieldGrp(nf=2, l="Start/End:", cal=[(1, "left"), (2,"left"),(3, "left")], en=False, cw=[(1,75),(2,60),(3,60)], v1=1, v2=10)

    cmds.formLayout(widgets["mainFLO"], e=True, af = [
        (widgets["camText"], "top", 5),
        (widgets["camText"], "left", 72),		
        (widgets["camTSL"], "top", 20),
        (widgets["camTSL"], "left", 0),
        (widgets["refreshBut"], "top", 125),
        (widgets["refreshBut"], "left", 0),
        (widgets["locRBG"], "top", 160),
        (widgets["locRBG"], "left", 2),
        (widgets["locTFBG"], "top", 185),
        (widgets["locTFBG"], "left", 0),
        (widgets["nameText"], "top", 220),
        (widgets["nameText"], "left", 4),
        (widgets["nameTF"], "top", 235),
        (widgets["nameTF"], "left", 0),
        (widgets["otherCBG"], "top", 285),
        (widgets["otherCBG"], "left", 0),
        (widgets["convertCBG"], "top", 305),
        (widgets["convertCBG"], "left", 0),
        (widgets["timeRBG"], "top", 345),
        (widgets["timeRBG"], "left", 0),
        (widgets["timeIFG"], "top", 365),
        (widgets["timeIFG"], "left", 0),					
        (widgets["exportBut"], "top", 405),
        (widgets["exportBut"], "left", 0),
        ])


    cmds.showWindow(widgets["cwin"])

    refreshCameras()
    getSceneName()
    getProjectExportDir()


def getProjectExportDir(*args):
    proj = cmds.workspace(q=True, act=True)
    scenes = proj + "/scenes"
    if os.path.isdir(scenes):
        cmds.textFieldButtonGrp(widgets["locTFBG"], e=True, tx=scenes)


def refreshCameras(*args):
    """refreshes the list of cameras in the scene"""

    cmds.textScrollList(widgets["camTSL"], e=True, ra=True)

    cams = []
    camShps = cmds.ls(type="camera")
    for shp in camShps:
        trns = cmds.listRelatives(shp, parent = True)
        cams.append(trns)

    for cam in cams:
        cmds.textScrollList(widgets["camTSL"], e=True, a=cam)

    getSceneName()


def chooseLocation(*args):
    """populates the save location (only directories)"""
    loc = cmds.fileDialog2(ds = 2, cap = "Save Cam Export", fm =2)[0]
    cmds.textFieldButtonGrp(widgets["locTFBG"], e=True, tx = loc)


def getSceneName(*args):
    """gets the scene name for a default"""

    sPath = cmds.file(q=True, sn=True)
    sName = os.path.basename(sPath).rpartition(".")[0]
    if sName:
        sName = sName + "_camExport"
    else:
        sName = "untitled_camExport"

    cmds.textField(widgets["nameTF"], e=True, tx=sName)

def  getFrameRange(*args):
    """returns the start and end frmaes depending on the mode selected"""
    mode = cmds.radioButtonGrp(widgets["timeRBG"], q=True, sl=True)
    sFrame = 1
    eFrame = 2

    if mode == 1:
        sFrame = cmds.playbackOptions(q=True, min = True)
        eFrame = cmds.playbackOptions(q=True, max = True)
    elif mode == 2:
        sFrame = cmds.intFieldGrp(widgets["timeIFG"], q=True, v1=True)
        eFrame = cmds.intFieldGrp(widgets["timeIFG"], q=True, v2=True)

    return(sFrame, eFrame)

def toggleRange(*args):
    """toggles the state of the frame range int field group"""
    sel = cmds.radioButtonGrp(widgets["timeRBG"], q=True, sl=True)
    if sel == 1:
        cmds.intFieldGrp(widgets["timeIFG"], e=True, en = False)
    if sel == 2:
        cmds.intFieldGrp(widgets["timeIFG"], e=True, en = True)

def getWindowValues(*args):
    #Here we SHOULD capture all of the values we would need from the window and pass those to our
    #dupeBakeObjects() function. That way we can use that as standalone or batch operation
    pass

def dupeBakeObjects(*args):
    #args should include -name, path, objects?, frame range, camera list
    sFrame, eFrame = getFrameRange()
    cams = cmds.textScrollList(widgets["camTSL"], q=True, si=True)
    attrs = ["focalLength", "focusDistance", "fStop", "horizontalFilmOffset", "verticalFilmOffset"]
    export = []
    sel = cmds.ls(sl=True, type = "transform")
    goodSel = []
    objMode = cmds.checkBoxGrp(widgets["otherCBG"], q=True, v1=True)
    convert = cmds.checkBoxGrp(widgets["convertCBG"], q=True, v1=True)
    expPath = cmds.textFieldButtonGrp(widgets["locTFBG"], q=True, tx=True)
    expName = cmds.textField(widgets["nameTF"], q=True, tx =True)

    pcs = []
    if cams:
        for cam in cams:
            dupeCam = cmds.duplicate(cam)[0]
            newDupe = cmds.rename(dupeCam, cam+"_exp")
            export.append(newDupe)
            pc = cmds.parentConstraint(cam, newDupe)[0]

            camShape = cmds.listRelatives(cam, shapes = True)[0]
            dupeShape = cmds.listRelatives(newDupe, shapes = True)[0]
            #connect dupe cam to orig
            for attr in attrs:
                cmds.connectAttr("%s.%s"%(camShape, attr), "%s.%s"%(dupeShape, attr))

            pcs.append(pc)

        if objMode:
            for obj in sel:
                try:
                    shp = cmds.listRelatives(obj, shapes = True)[0]
                    if (cmds.objectType(shp) != "camera"):
                        goodSel.append(obj)
                    else:
                        cmds.warning("%s is a camera. You should use the list to select that instead. Skipping"%obj)
                except:
                    pass
        
            for this in goodSel:
                if convert:
                    pos = cmds.xform(this, q=True, ws=True, rp=True)
                    rot = cmds.xform(this, q=True, ws=True, ro=True)
                    loc = cmds.spaceLocator(n="%sLoc"%this)[0]
                    cmds.xform(loc, ws=True, t=pos)
                    cmds.xform(loc, ws=True, ro=rot)
                    pco = cmds.parentConstraint(this, loc)[0]
                    pcs.append(pco)
                    export.append(loc)
                else:
                    dupeObj = cmds.duplicate(this)[0]
                    pco = cmds.parentConstraint(this, dupeObj)[0]
                    pcs.append(pco)
                    export.append(dupeObj)

        #bake
        cmds.bakeResults(export, sb=1, t=(sFrame, eFrame),sm=True, s=True)
        cmds.delete(pcs)
        #select
        cmds.select(export, r=True)

        #export
        dest = "%s/%s.ma"%(expPath, expName)
        cmds.file(dest, es=True, con=False, ch=False, chn=True, sh=False, typ="mayaAscii")

        #delete dupes
        cmds.delete(export)
        cmds.warning("Finished baking & exporting objects!")

    else:
        cmds.warning("No cameras were selected from the list!")


def camExporter(*args):
    camExportUI()