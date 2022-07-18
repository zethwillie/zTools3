########################
#file: zbw_audioManager.py
#Author: zeth willie
#Contact: zeth@catbuks.com, www.williework.blogspot.com
#Date Modified: 04/27/13
#To Use: type in python window  "import zbw_audioManager as zam; zam.audioManager()"
#Notes/Descriptions: used to manage some of the audio in your scene
########################

#audio manager
import maya.cmds as cmds
import maya.mel as mel

widgets = {}
#create window to manage audio
def audioUI():
    """UI for the whole thing"""

    if (cmds.window("audioWin", exists=True)):
        cmds.deleteUI("audioWin")

    widgets["win"] = cmds.window("audioWin", t="zbw_audioManager", w=300, h=260)

    widgets["mainCLO"] = cmds.columnLayout()
    widgets["getAudioBut"] = cmds.button(l="Get All Audio In Scene", w=300, h=30, bgc=(.6, .6, .8), c=getAudio)
    cmds.text("Double-click item in list to enable sound and select it", al="left")

    widgets["audioTSL"] = cmds.textScrollList(h=100, w=300, dcc=selectAudio)
    widgets["buttonRCLO"] = cmds.rowColumnLayout(nc=2)
    widgets["deleteSelBut"] = cmds.button(l="Delete Selected", w=150, h=20, bgc=(.8,.6,.6), c=deleteSelected)
    widgets["deleteAllBut"] = cmds.button(l="Delete All Audio", w=150, h=20, bgc=(.8,.4,.4), c=deleteAll)

    cmds.setParent(widgets["mainCLO"])

    cmds.separator(h=20)

    widgets["newAudioBut"] = cmds.button(l="Import New Audio File!", w=300, h=30, bgc=(.6,.8,.6), c=importAudio)
    cmds.separator(h=20)

    widgets["offsetRCLO"] = cmds.rowColumnLayout(nc=2, cw=([1,175], [2, 125]), cal=([1,"left"], [2,"left"]))
    widgets["offsetIFG"] = cmds.intFieldGrp(l="Offset Selected By ", v1=1, cal=([1,"left"], [2,"left"]), cw=([1,100],[2,50]))
    widgets["offsetBut"] = cmds.button(l="Offset!", w=100, h=30, bgc=(.6,.8,.8), c=offsetAudio)

    cmds.showWindow(widgets["win"])
    cmds.window(widgets["win"], e=True, w=300, h=260)

def getAudio(*args):
    """gets audio in the scene and populates the list"""

    cmds.textScrollList(widgets["audioTSL"], e=True, ra=True)
    aud = cmds.ls(type="audio")
    if aud:
        for node in aud:
            #put the audio in the TSL
            cmds.textScrollList(widgets["audioTSL"], e=True, a=node)

def selectAudio(*args):
    """selects the audio from the list"""

    node = cmds.textScrollList(widgets["audioTSL"], q=True, si=True)[0]
    mel.eval("setSoundDisplay " + node + " 1;")
    cmds.select(node)

def deleteSelected(*args):
    """deletes audio from the list"""

    nodes = cmds.textScrollList(widgets["audioTSL"], q=True, si=True)
    if nodes:
        for node in nodes:
            cmds.delete(node)
    getAudio()

def importAudio(*args):
    """imports audio into your scene via file dialog2, type'audio'"""

    #do import
    cmds.file(cmds.fileDialog2(fm=1), i=True, typ="audio")
    getAudio()

def deleteAll(*args):
    """deletes all audio in the scene"""

    nodes = cmds.textScrollList(widgets["audioTSL"], q=True, ai=True)
    for node in nodes:
        cmds.delete(node)
    cmds.textScrollList(widgets["audioTSL"], e=True, ra=True)

def offsetAudio(*args):
    """offsets selected audio by x frames"""

    offset = cmds.intFieldGrp(widgets["offsetIFG"], q=True, v=True)[0]
    sel = cmds.textScrollList(widgets["audioTSL"], q=True, si=True)
    print(sel)
    # sel = cmds.ls(sl=True, type="audio")
    if sel:
        for node in sel:
            cmds.setAttr("%s.offset"%node, offset)

def audioManager():
    """Use this to start the script!"""

    audioUI()