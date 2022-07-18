import maya.cmds as cmds
from functools import partial
import re

widgets = {}
typeList = cmds.allNodeTypes() # get all current node types in the scene

def typeFinderUI(*args):
	if cmds.window("typeFinderWin", exists=True):
		cmds.deleteUI("typeFinderWin")

	widgets["win"] = cmds.window("typeFinderWin", w=400, h=400, t="zbw_typeFinder")
	widgets["mainCLO"] = cmds.columnLayout(w=400, h=400, bgc=(.2, .2,.2))

#---------------- right click on an item and get option to replace with parent or go down to shape

	cmds.text(l="Note: Rt-click on the below field to get suggestions from your sub-string")
	cmds.separator(h=10)

	widgets["typeTFBG"] = cmds.textFieldButtonGrp(l="Node Type", bl="Find", cal=[(1,"left"),(2,"left"),(3,"left")], cw=[(1, 75), (2,250), (3, 50)], bc=getObjectList)
	widgets["searchPUM"] = cmds.popupMenu(postMenuCommand=populateMenuItems)

	widgets["searchSelCB"] = cmds.checkBox(l="Only search current selection?", v=0)
	widgets["shpsToXformCB"] = cmds.checkBox(l="List transforms of found shapes (mesh, etc)?", v=1)

	widgets["stringMatchCB"] = cmds.checkBox(l="Additional name/string search?", v=0, changeCommand=toggleStringSearchEnable)
	widgets["stringSearchTFG"] = cmds.textFieldGrp(l="String:", en=False, cal=[(1,"left"),(2,"left")], cw=[(1, 75), (2,250)], changeCommand=getObjectList)


	cmds.separator(h=10)

	widgets["resultsTSL"] = cmds.textScrollList(w=400, h=200, bgc=(0,0,0), allowMultiSelection=True)
#---------------- checkbox here to expand selection? for sets (true-select objects in set, false - just seletc the set)

	widgets["selectAllBut"] = cmds.button(l="Select All in List", h= 30)
	widgets["selectSelBut"] = cmds.button(l="Select Selected in List", h= 30)
	widgets["selectParOfSelBut"] = cmds.button(l="Select Parent/Transform of Selected in List", h= 30)
	widgets["deleteAllBut"] = cmds.button(l="Delete All in List", h= 30)
	widgets["deleteSelBut"] = cmds.button(l="Delete Selected in List", h= 30)
	widgets["clearListBut"] = cmds.button(l="Clear List", h= 30, c=clearScrollList)
	#widgets["connectDecompBut"] = cmds.button(l="Clear List", h= 30, c=clearList)
#---------------- button to promote all shape to transforms?
#---------------- button to select shapes of all in list

	cmds.showWindow(widgets["win"])

#---------------- FUNCTIONS:
#---------------- get current selection (to filter our list)
#---------------- filter our list based on another list
#---------------- promote shapes: given an obj, is it a shape node? if it is, return it's parent
#---------------- stop the process if the list count is more than 100? or 1000?
#---------------- create a confirm dialog func (in zbw_rig?), args = message, buttons? 
#---------------- populate the buttons and related functions


def getTypeText(*args):
	"""
	gets text
	"""
	txt = cmds.textFieldButtonGrp(widgets["typeTFBG"], q=True, tx=True)
	if not txt: # if no entry
		cmds.warning("node type: Nothing entered!")
		return(None)
	if re.match('^[a-zA-Z0-9_]+$',txt): # if we have valid text
		return(txt)
	else: # if we have bad text
		cmds.warning("Some bad characters in there. Please use numbers, letters, or underscores!")
		return(None)


def getSearchText(*args):
	"""
	gets text
	"""
	txt = cmds.textFieldGrp(widgets["stringSearchTFG"], q=True, tx=True)
	if not txt: # if no entry
		cmds.warning("string search: Nothing entered!")
		return(None)
	if re.match('^[a-zA-Z0-9_]+$',txt): # if we have valid text
		return(txt)
	else: # if we have bad text
		cmds.warning("Some bad characters in there. Please use numbers, letters, or underscores!")
		return(None)


def getObjectList(*args):
	"""gets the list of object of type txt"""

	objs = []
	objText = getTypeText()

	if objText in typeList:
		objs = cmds.ls(type=objText)
	else:
		cmds.warning("This instance of Maya doesn't recognize that type of object: {0}!".format(objText))
		return()

	if objs:
#---------------- check if we're promoting shapes		
#---------------- if yes, send out list to see which elements are shapes and promote them, return a new list into obj ie. objs = promoteList(objs), this will return either the same list or an ammended list
		addObjectsToScrollList(objs)
	else:
		cmds.warning("No objects found of type: {0}".format(objText))


def toggleStringSearchEnable(*args):
	enabled = cmds.textFieldGrp(widgets["stringSearchTFG"], q=True, en=True)
	toggle = 1

	if enabled==1:
		toggle = 0

	cmds.textFieldGrp(widgets["stringSearchTFG"], e=True, en=toggle)
	return(toggle)


def addObjectsToScrollList(objs):
	"""puts the list of things in the textScrollList"""

	clearScrollList()
	stringSearch = cmds.checkBox(widgets["stringMatchCB"], q=True, v=True)
	searchText = ""
	checkedObjs = []
	
	if stringSearch:
		searchText = getSearchText()

	if stringSearch and searchText:
		for obj in objs:
			# check if the string is in the name of obj
			if searchText.lower() in obj.lower():
				checkedObjs.append(obj)

	else:
		checkedObjs = objs

	for x in checkedObjs:
#---------------- here add rt click functions to select all shapes or select transform (if shape)
		cmds.textScrollList(widgets["resultsTSL"], e=True, a=x, doubleClickCommand=selectItemInList)


def clearScrollList(*args):
	"""just empties the scroll list"""

	cmds.textScrollList(widgets["resultsTSL"], e=True, removeAll=True)


def queryListSelection(*args):
	"""gets a list of selected items from the textScrollList"""

	sel = cmds.textScrollList(widgets["resultsTSL"], q=True, si=True)
	return(sel)


def selectItemInList(*args):
	"""selects (in your scene) given list of items"""

	sel = queryListSelection()

	if sel:
		print(("selecting: {0}".format(sel)))
		# check whether the noExpand should be there (for sets: do we want to select the set or expand to select it's elements?)
		cmds.select(sel, r=True, noExpand=False)
	else:
		cmds.warning("Nothing selected!")


def returnMatches(currText, theList, *args):
	myMatches = []
	if currText and len(currText)>2:
		myMatches = [x for x in theList if currText.lower() in x.lower()]

	return(myMatches)


def populateMenuItems(*args):
	cmds.popupMenu(widgets["searchPUM"], e=True, deleteAllItems=True) # clear popup menu
	t = getTypeText()
	
	matches = []

	if t:
		matches = returnMatches(t, typeList)

	if matches:
		for item in matches:
			cmds.menuItem(p=widgets["searchPUM"], l=item, c=partial(fillMenuText, item))


def fillMenuText(text, *args):
	cmds.textFieldButtonGrp(widgets["typeTFBG"], e=True, tx=text)


def typeFinder(*args):
	typeFinderUI()