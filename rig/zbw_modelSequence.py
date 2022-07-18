import maya.cmds as cmds

"""bake sequence of objects to use for blend shapes or stop mo or whatever"""

widgets = {}

def modelSequenceUI(*args):
    if (cmds.window("modSeq", exists=True)):
        cmds.deleteUI("modSeq")
        
    widgets["win"] = cmds.window("modSeq", w = 300, h = 220, t = "zbw_modelSequence")
    widgets["mainCLO"] = cmds.columnLayout(w = 300,h = 220)

    cmds.separator(h=10)
    cmds.text("Select ONE object to be duplicated \nThis will duplicate it for frames selected and group", al="left")
    cmds.separator(h=20)

    #textFieldGRP - name of objs
    widgets["sufTFG"] = cmds.textFieldGrp(l="Sequence Suffix:", cw = [(1, 100), (2,200)], cal = [(1, "left"),(2, "right")])
    #radioButtonGrp - timeslider or frame range
    widgets["frmRBG"] = cmds.radioButtonGrp(l="Get Frames From:", nrb=2, sl=2, l1="Time Slider", l2="Frame Range", cw = [(1, 120), (2,80), (3,80)], cal = [(1, "left"),(2, "left")], cc=enableFR)
    #textFieldGrp - framerange (enable)
    widgets["frmRngIFG"] = cmds.intFieldGrp(l="Range:", nf=2, en=True, v1=0, v2 = 9, cw = [(1, 120), (2,80), (3,80)], cal = [(1, "left"),(2, "left")])
    #int = by frame step
    widgets["stepIFG"] = cmds.intFieldGrp(l="Step By (frames):", v1 = 1, cw = [(1, 120), (2,80)], cal = [(1, "left"),(2, "right")])
    
    cmds.separator(h=30)
    widgets["doBut"] = cmds.button(l="Create duplicates of objects!", w= 300, h=40, bgc = (0,.8, 0), c=getValues)
    
    
    cmds.showWindow(widgets["win"])
        
        
def enableFR(*args):
    """switches enabling of frame range int field grp"""
    
    sel = cmds.radioButtonGrp(widgets["frmRBG"], q=True, sl=True)
    if sel == 1:
        enable = False
    else:
        enable = True 
        
    cmds.intFieldGrp(widgets["frmRngIFG"], e=True, en=enable)    

def getValues(*args):
    try: 
        obj = cmds.ls(sl=True, transforms = True)[0]
        
        #currentFrame = cmds.currentTime(q = True)
        
        step = cmds.intFieldGrp(widgets['stepIFG'], q = True, v1 = True)
        frmVal = cmds.radioButtonGrp(widgets["frmRBG"], q=True, sl=True)
        suffix = cmds.textFieldGrp(widgets["sufTFG"], q = True, tx = True)
        name = "%s_%s"%(obj, suffix)
        
        if frmVal == 1:
            frameStart = int(cmds.playbackOptions(query=True, min=True))
            frameEnd = int(cmds.playbackOptions(query=True, max=True))
        
        else: 
            frameStart = cmds.intFieldGrp(widgets["frmRngIFG"], q = True, v1 = True)
            frameEnd = cmds.intFieldGrp(widgets["frmRngIFG"], q = True, v2 = True)
            
        makeSequence(obj, name, frameStart, frameEnd, step) 
            
    except:
        cmds.warning("Select one object with a transform")            
   
def makeSequence(obj = "", name = "", frameStart = 0, frameEnd = 1, step = 1):
    """duplicate selected geo based on settings from UI"""
    
    dupes = []
    
    numCopies = (frameEnd-frameStart)/step
    #check here if we want to create more than 25 duplicates?
    confirm = cmds.confirmDialog(t="Confirm", m= "This will create %d copies of %s. \nFrames: %d to %d\nFor dense meshes, this could get heavy\nAre you sure you want to do this?"%(numCopies, obj, frameStart, frameEnd), button = ["Yes", "No"], cancelButton = "No")
    
    if confirm == "Yes":
        for frame in range(frameStart, frameEnd + 1, step):
            cmds.currentTime(frame, edit=True)
            dupe = cmds.duplicate(obj, n="%s_%d"%(name, frame), ic = False, un = False)
            dupes.append(dupe)
            
    if dupes:
        grp = cmds.group(em = True, n = "%s_GRP"%name)
        for dupe in dupes:
            cmds.parent(dupe, grp)
            
    #cmds.currentTime(currentFrame, e=True)
                
def modelSequence(*args):
    modelSequenceUI()
    
modelSequence()