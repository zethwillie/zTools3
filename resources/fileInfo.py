import maya.cmds as cmds
import os

###########
# getInfoDict(path) will return a dictionary of the scene's info 
# fileInfo(path) will call the funcs to show the window with all scene fileInfo
############

#info window on selected scene
widgets = {}

def fileInfoUI(filePath, *args):
	if cmds.window("fileInfoWin", exists=True):
		cmds.deleteUI("fileInfoWin")

	widgets["win"] = cmds.window("fileInfoWin", w=270, h=300, t="Charlex File Info", s=False)
	widgets["mainSLO"] = cmds.scrollLayout(w=450, h=300)
	widgets["mainCLO"] = cmds.columnLayout()

	cmds.window(widgets["win"], e=True, w=270, h=300)
	cmds.showWindow(widgets["win"])
	
	#populate the window here
	populateInfoWin(filePath, widgets["mainCLO"])

def populateInfoWin(filePath, parent, *args):
	"""grabs only the relevant info from the file and creates text for the window"""

	cmds.text(l=os.path.basename(filePath), font = "boldLabelFont", align = "left")
	cmds.text(l="================================", align = "left", h=20)

	goodInfo = ['"FILETYPE"', '"DATE"', '"WORKSHOP"', '"USER"', '"CHRLX_NOTE"', '"version"']
	infoDict = getInfoDict(filePath)
	if infoDict:
		for key in list(infoDict.keys()):
			if key in goodInfo:
				cmds.text(l=key.replace("\"",""), parent= parent, align="left", ww=True, font="boldLabelFont")
				cmds.text(l= infoDict[key], parent = parent, align = "left", ww=True)


def getInfoDict(filePath):
	"""given a full path, will get the file info for a maya file and return the info as a dictionary"""

	infoDict = {}
	
	with open(filePath) as x:
		for line in x:
			found = False
			if "fileInfo" in line:
				lineList = []
				lineList = line.split(" ") 
				info = " ".join(lineList[2:])
				infoDict[lineList[1]] = info
				found = True
			else:
				if found:
					break
		if infoDict:
			return infoDict
		else:
			return None

def fileInfo(filePath):
	"""calls the window, then populates it"""
	
	fileInfoUI(filePath)


# fileinfo keys in current scene:
# "FILETYPE" : "geo";
# "cutIdentifier" : "201511301000-979500";
# "product" : "Maya 2016";
# "NOTE" : "dinoBodyB and eyeblink shapes added";
# "USER" : "ekim";
# "osv" : "Microsoft Windows 7 Business Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
# "CHRLX_NOTE" : "dinoBodyB and eyeblink shapes added";
# "version" : "2016";
# "application" : "maya";
# "DATE" : "11:59:22 2016/05/10";
# "WORKSHOP" : "66";