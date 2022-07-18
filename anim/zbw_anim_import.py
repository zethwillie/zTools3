import maya.cmds as cmds
import os
import random
from functools import partial

# to run: (in python window in maya) import zbw_anim_import as zai; zai.anim_import()

widgets = {}
def import_anim_UI():
	width = 400

	if cmds.window("impAnimWin", exists=True):
		cmds.deleteUI("impAnimWin")

	widgets["win"] = cmds.window("impAnimWin", t="Import anim files", w=width, h=400, rtf=True)
	# widgets["clo"] = cmds.columnLayout()
	widgets["mainTLO"] = cmds.tabLayout()
	widgets["impCLO"] = cmds.columnLayout("Import Anim")
	cmds.text("1. choose the folder where your anim clips live,\n2. select the objs in scene to apply to\n3. 'random' will start anim in frame range\n4. select anim clips from list to randomly apply to objs\n5. press button to apply",al="left")
	cmds.separator(h=10)	
	widgets["impPathTFG"] = cmds.textFieldButtonGrp(l="Anim Path:", bl="<<<", cal = ([1, "left"], [2, "left"], [3, "right"]), cw=([1, 75], [2, 275], [3, 40]), bc=partial(get_path, "import", "impPathTFG"), cc=populate_tsl)
	widgets["randRBG"] = cmds.radioButtonGrp(l="Insert Placement:", nrb=2, l1="Random Start", l2="At current Frame", sl=1, cal=([1, "left"], [2,"left"], [3,"left"]), cw=([1,100], [2, 100], [3, 100]), cc=partial(toggle_enable, "randRBG", "rangeIFG"))
	widgets["rangeIFG"] = cmds.intFieldGrp(l="Random Start Range:", nf=2, v1=0, v2=100, cw=([1, 120], [2, 50], [3, 50]), cal=([1, "left"], [2, "left"], [3, "left"]))
	widgets["delCBG"] = cmds.checkBoxGrp(l="Delete subsequent keys?", v1=True, cal=([1, "left"], [2, "left"]), cw=([1, 130], [2, 20]))
	cmds.separator(h=10)	
	widgets["animTSL"] = cmds.textScrollList(w=400, h=150, allowMultiSelection=True)
	cmds.separator(h=10)	
	widgets["importBut"] = cmds.button(l="Import random anim from selection", h=40, w=width, bgc=(.5, .8, .5), c=import_animation)

	cmds.setParent(widgets["mainTLO"])
	widgets["expCLO"] = cmds.columnLayout("Export Anim")
	cmds.text("1. Select the obj 2. choose a path and name the anim\n3. choose range and hierarchy 4. press button!", al="left")
	cmds.separator(h=10)
	widgets["expPathTFG"] = cmds.textFieldButtonGrp(l="Export Path:", bl="<<<", cal = ([1, "left"], [2, "left"], [3, "right"]), cw=([1, 75], [2, 275], [3, 40]), bc=partial(get_path, "export", "expPathTFG"))
	widgets["nameTFG"] = cmds.textFieldGrp(l="Animation Name:", cw=([1, 100], [2, 250]), cal=([1, "left"], [2, "left"]))	
	widgets["selRBG"] = cmds.radioButtonGrp(l="Hierarchy:", nrb=2, l1="Selection Only", l2="Below", sl=2, cal=([1, "left"], [2,"left"], [3,"left"]), cw=([1,75], [2, 100], [3, 100]))
	widgets["expRngRBG"] = cmds.radioButtonGrp(l="Time Range:", nrb=2, l1="Start_End", l2="All", sl=2, cal=([1, "left"], [2,"left"], [3,"left"]), cw=([1,75], [2, 100], [3, 100]), cc=partial(toggle_enable, "expRngRBG", "expRngIFG"))
	widgets["expRngIFG"] = cmds.intFieldGrp(nf=2, en=False, l="Start_End", v1=1, v2=10, cal=([1, "left"], [2,"left"], [3,"left"]), cw=([1,75], [2, 100], [3, 100]))
	cmds.separator(h=10)	
	widgets["exportBut"] = cmds.button(l="Export anim from selection", h=40, w=width, bgc=(.5, .8, .5), c=export_animation)

	cmds.window(widgets["win"], e=True, w=5, h=5, rtf=True)
	cmds.showWindow(widgets["win"])


def load_check(*args):
	"""checks whether anim imp/exp plugin is loaded. Loads it if not"""
	loaded = cmds.pluginInfo("animImportExport", q=True, loaded=True)
	if not loaded:
		cmds.loadPlugin("animImportExport")

def fix_path(pathIn):
	"""cleans up path separators, just to be safe"""
	return(pathIn.replace("\\", "/"))


def toggle_enable(currWidget, toggleWidget, *args):
	"""toggles on/off the enabled attr of int field toggleWidget. Currwidget is the radio button grp we look at to get state"""
	onOff = cmds.radioButtonGrp(widgets[currWidget], q=True, sl=True)
	if onOff == 1:
		cmds.intFieldGrp(widgets[toggleWidget], e=True, en=1)
	else:
		cmds.intFieldGrp(widgets[toggleWidget], e=True, en=0)


def get_path(pType, widgetPath, *args):
	"""get the path from dialog, and puts it in approp textFieldGrp (based on pType == 'import')"""
	path = cmds.fileDialog2(dialogStyle=1, fileMode=3)
	cmds.textFieldButtonGrp(widgets[widgetPath], e=True, tx=fix_path(path[0]))
	if pType == "import":
		clear_tsl()
		populate_tsl()


def clear_tsl(*args):
	"""clears to textscroll list"""
	cmds.textScrollList(widgets["animTSL"], e=True, ra=True)


def populate_tsl(*args):
	"""populates the list from the imp text field grp path"""
	path = cmds.textFieldButtonGrp(widgets["impPathTFG"], q=True, tx=True)
	if not path or not os.path.isdir(path):
		cmds.warning("Couldn't find that path ({0})!".format(path))
		return()

	animFiles = [x for x in os.listdir(path) if x.rpartition(".")[2] == "anim"]
	if not animFiles:
		return()

	animFiles.sort()
	for af in animFiles:
		cmds.textScrollList(widgets["animTSL"], e=True, a=af)


def delete_later_keys(obj, frame, *args):
	"""sets a key at 'frame' and then deletes all subsequent keys in the timeline (time based only)"""
	animTypes = ["animCurveTL","animCurveTA", "animCurveTT", "animCurveTU"]
	animNodes = cmds.listConnections(obj, type="animCurve")
	if not animNodes:
		return()
	for a in animNodes:
		if (cmds.objectType(a)in animTypes):
			cmds.setKeyframe(a, time=frame)
			cmds.cutKey(a,clear=1, time=(frame + 1, 100000))

def import_animation(*args):
	"""imports the anim (from rand selection of list items) onto selected objs"""
	lo, hi = cmds.intFieldGrp(widgets["rangeIFG"], q=True, v=True)
	rand = cmds.radioButtonGrp(widgets["randRBG"], q=True, sl=True)
	clips = cmds.textScrollList(widgets["animTSL"], q=True, si=True)
	path = cmds.textFieldButtonGrp(widgets["impPathTFG"], q=True, tx=True)
	options = {"targetTime":3, "time": 1, "option":"insert", "connect":1}

	delKeys = cmds.checkBoxGrp(widgets["delCBG"], q=True, v1=True)
	sel = cmds.ls(sl=True)
	for obj in sel:
		startF = cmds.currentTime(q=True)
		if rand == 1:	
			startF = random.randint(lo, hi)
			cmds.currentTime(startF)
		if delKeys:
			delete_later_keys(obj, startF)
		cmds.select(obj, r=True)
		myClip = random.choice(clips)
		animPath = "{0}/{1}".format(path, myClip)
		cmds.file(animPath, i = True, type = "animImport", ignoreVersion = True, options = "targetTime={0};time={1};copies=1;option={2};pictures=0;connect={3};".format(options["targetTime"], startF, options["option"], options["connect"]), preserveReferences=True)
		
	cmds.select(sel, r=True)


def export_animation(*args):
	"""exports the animation on current selected object"""
	sel = cmds.ls(sl=True)
	if len(sel)>1:
		cmds.warning("You should only select one object to export anim from!")
		return()

	rng = 1
	rngOption = cmds.radioButtonGrp(widgets["expRngRBG"], q=True, sl=True)
	if rngOption==1:
		rng = 2
	lo, hi = cmds.intFieldGrp(widgets["expRngIFG"], q=True, v=True)
	hier = "below"
	hierRBG = cmds.radioButtonGrp(widgets["selRBG"], q=True, sl=True)
	if hierRBG==1:
		hier = "none"
	animName = cmds.textFieldGrp(widgets["nameTFG"], q=True, tx=True)
	if not animName:
		cmds.warning("You need to name the anim!")
		return()

	path = cmds.textFieldButtonGrp(widgets["expPathTFG"], q=True, tx=True)
	if not path or not os.path.isdir(path):
		cmds.warning("Not a valid path in the path field!")
		return()
	
	animPath = "{0}/{1}.anim".format(path, animName)
	# if os.path.isfile(animPath):
	# 	cmds.warning("There already is an animation by that name.")
	# 	return()

	options = {"whichRange":rng, "range":"{0}:{1}".format(lo, hi), "hierarchy":hier}

	cmds.file(animPath, type="animExport", exportSelected=True, force=True, options="precision=8;intValue=17;nodeNames=1;verboseUnits=0;whichRange={0};range={1};options=keys;hierarchy={2};controlPoints=0;shapes=1;helpPictures=0;useChannelBox=0;copyKeyCmd=-animation objects -option keys -hierarchy below -controlPoints 0 -shape 1".format(options["whichRange"], options["range"], options["hierarchy"]))


def anim_import():
	load_check()
	import_anim_UI()