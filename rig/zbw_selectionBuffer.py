########################
# File: zbw_selectionBuffer.py
# Date Modified: 04 Aug 2017
# creator: Zeth Willie
# Contact: zethwillie@gmail.com, catbuks.com, williework.blogspot.com
# Description: stores your selection and then restores it in add mode (meaning you can select xyz, store it,
# select a, restore it, and have selection be axyz
# To Run: type "import zTools.zbw_selectionBuffer as zbw_selectionBuffer; reload(zbw_selectionBuffer);zbw_selectionBuffer.zbw_selectionBuffer()"
########################

import maya.cmds as cmds

widgets = {}
selection = []

def selectionUI(*args):
	#window stuff, two buttons
	if cmds.window("selWin", exists=True):
		cmds.deleteUI("selWin")
		
	widgets["win"] = cmds.window("selWin", t="zbw_selectionBuffer", s=False)
	widgets["mainCLO"] = cmds.columnLayout(bgc = (.8, .8, .8))
	
	widgets["getBut"] = cmds.button(l="Grab Selection", bgc = (.5, .5, .9), w=200, h=50, c=grabSel)
	cmds.separator(h=5)
	widgets["checkBut"] = cmds.button(l="Check Stored (in scipt ed.)", bgc = (.5, .5, .5), w=200, h=20, en=False, c=checkSel)
	cmds.separator(h=10)
	widgets["restoreBut"] = cmds.button(l="Restore Selection", bgc = (.5, .8, .5), w=200, h=50, c=restoreSel)
	
	cmds.window(widgets["win"], e=True, w=200, h=135)
	cmds.showWindow(widgets["win"])


def grabSel(*args):
	
	del selection[:]   # empty the variable
	sel = cmds.ls(sl=True, fl=True)
	for obj in sel:
		selection.append(obj)
	
	if selection:
		cmds.button(widgets["checkBut"], e=True, bgc = (.8, .7, .5),  en = True)
	else:
		cmds.button(widgets["checkBut"], e=True, bgc = (.5, .5, .5), en=False)


def checkSel(*args):
	print("\n IN THE SELECTION BUFFER:")
	for obj in selection:
		print(obj)


def restoreSel(*args):
	sel = cmds.ls(sl=True)

	if selection:
		for obj in selection:
			sel.append(obj)
	cmds.select(sel, r=True)


def selectionBuffer(*args):
	selectionUI()
	
selectionBuffer()