import maya.cmds as cmds
import random
import maya.OpenMaya as OpenMaya
from functools import partial

#TODO ---------- figure out how to get more line in the patches (separate tab)
#--------------- add button to average verts
#---------------  add control for bevel offset (0.01-0.1)

widgets = {}

def wrinklePolyUI(*args):
	if cmds.window("wrinkleWin", exists = True):
		cmds.deleteUI("wrinkleWin")

	widgets["win"] = cmds.window("wrinkleWin", t="zbw_wrinklePoly", w= 300, h=250)
	widgets["mainCLO"] = cmds.columnLayout(w=300)
	widgets["mainTLO"] = cmds.tabLayout()

	widgets["vertCLO"] = cmds.columnLayout("Object Random")
	widgets["text"] = cmds.text("Do randomization of verts on selected objects", al = "left")
	widgets["vertFLO"] = cmds.frameLayout(l = "Random Vert Move", cll=True, w=300)
	widgets["vpercISG"] = cmds.intSliderGrp(l="% of verts to move:", f=True, v = 50, min=0, max = 100, cw = [(1,100), (2, 50)], cal = [(1, "left"), (2, "left")])
	widgets["movexFFG"] = cmds.floatFieldGrp(l="distance X (min, max):", nf = 2, v1 = -.2, v2 = .2, cw = [(1,120), (2, 50), (3,50)], cal = [(1, "left"), (2, "left")])
	widgets["moveyFFG"] = cmds.floatFieldGrp(l="distance Y (min, max):", nf = 2, v1 = -.2, v2 = .2, cw = [(1,120), (2, 50), (3,50)], cal = [(1, "left"), (2, "left")])
	widgets["movezFFG"] = cmds.floatFieldGrp(l="distance Z (min, max):", nf = 2, v1 = -.2, v2 = .2, cw = [(1,120), (2, 50), (3,50)], cal = [(1, "left"), (2, "left")])
	widgets["iterIFG"] = cmds.intFieldGrp(l="number of iterations:", v1 = 9, cw = [(1,120), (2, 50)], cal = [(1, "left"), (2, "left")])
	widgets["moveBut"] = cmds.button(l = "Randomly Move Verts", w=300, h=30, bgc = (.8, .5, .3), c=moveVerts)
#### ---add a button to average verts

####----maybe a way to only select certain verts, edges, faces (converted to verts)

	cmds.setParent(widgets["vertCLO"])
	widgets["wrinkleFLO"] = cmds.frameLayout(l = "Random Bevel", cll=True, w=300)
	widgets["bpercISG"] = cmds.intSliderGrp(l="% of edges to bevel:", f=True, v = 50, min=0, max = 100, cw = [(1,100), (2, 50)], cal = [(1, "left"), (2, "left")])
####---------add some bevel controls fraction?, offset?	
	widgets["bevelBut"] = cmds.button(l = "Randomly Bevel Edges", w=300, h=30, bgc = (.2, .5, .8), c= bevelEdges)
#### - - - - add a way to preselect on certain edges? ? ? Only connected edges? 

	cmds.setParent(widgets["mainTLO"])
	widgets["selCLO"] = cmds.columnLayout("Selection Random")
	cmds.text("Do Radomization of vertex selection \nCan be soft selection!\n", al="left")
	widgets["selvpercISG"] = cmds.intSliderGrp(l="% of verts to move:", f=True, v = 50, min=0, max = 100, cw = [(1,100), (2, 50)], cal = [(1, "left"), (2, "left")])
	widgets["selmovexFFG"] = cmds.floatFieldGrp(l="distance X (min, max):", nf = 2, v1 = -.2, v2 = .2, cw = [(1,120), (2, 50), (3,50)], cal = [(1, "left"), (2, "left")])
	widgets["selmoveyFFG"] = cmds.floatFieldGrp(l="distance Y (min, max):", nf = 2, v1 = -.2, v2 = .2, cw = [(1,120), (2, 50), (3,50)], cal = [(1, "left"), (2, "left")])
	widgets["selmovezFFG"] = cmds.floatFieldGrp(l="distance Z (min, max):", nf = 2, v1 = -.2, v2 = .2, cw = [(1,120), (2, 50), (3,50)], cal = [(1, "left"), (2, "left")])
	widgets["seliterIFG"] = cmds.intFieldGrp(l="number of iterations:", v1 = 1, cw = [(1,120), (2, 50)], cal = [(1, "left"), (2, "left")])
	widgets["selmoveBut"] = cmds.button(l = "Randomly Move Verts", w=300, h=30, bgc = (.5, .8, .3), c=partial(getSoftSelection, "random"))

	cmds.setParent(widgets["mainTLO"])
	widgets["patchCLO"] = cmds.columnLayout("Patch Random")
	widgets["patchMoveFLO"] = cmds.frameLayout(l = "Move Patch", cll=True, w=300)
	cmds.text("Randomly move of a patch of verts \nCan be soft selection!\n", al="left")
	#widgets["patchvpercISG"] = cmds.intSliderGrp(l="% of verts to move:", f=True, v = 50, min=0, max = 100, cw = [(1,100), (2, 50)], cal = [(1, "left"), (2, "left")])
	widgets["patchmovexFFG"] = cmds.floatFieldGrp(l="distance X (min, max):", nf = 2, v1 = -1, v2 = 1, cw = [(1,120), (2, 50), (3,50)], cal = [(1, "left"), (2, "left")])
	widgets["patchmoveyFFG"] = cmds.floatFieldGrp(l="distance Y (min, max):", nf = 2, v1 = -1, v2 = 1, cw = [(1,120), (2, 50), (3,50)], cal = [(1, "left"), (2, "left")])
	widgets["patchmovezFFG"] = cmds.floatFieldGrp(l="distance Z (min, max):", nf = 2, v1 = -1, v2 = 1, cw = [(1,120), (2, 50), (3,50)], cal = [(1, "left"), (2, "left")])
	widgets["patchiterIFG"] = cmds.intFieldGrp(l="number of iterations:", v1 = 1, cw = [(1,120), (2, 50)], cal = [(1, "left"), (2, "left")])
	widgets["patchmoveBut"] = cmds.button(l = "Randomly Move Selected Patch of Verts", w=300, h=30, bgc = (.5, .8, .3), c=partial(getSoftSelection, "patch"))
	widgets["patchCreateFLO"] = cmds.frameLayout(l = "Create Patch", cll=True, w=300)
	widgets["patchCreateIFG"] = cmds.intFieldGrp(l="Iterations(size):", v1 = 5, cw = [(1,120), (2, 50)], cal = [(1, "left"), (2, "left")])
	widgets["patchRandISG"] = cmds.intSliderGrp(l="random culling:", f=True, v = 50, min=0, max = 100, cw = [(1,100), (2, 50)], cal = [(1, "left"), (2, "left")])
	widgets["patchVertsBut"] = cmds.button(l = "Create Patch from Selection of Verts", w=300, h=30, bgc = (.8, .8, .3), c=partial(patchChooser, "verts"))
	cmds.text("select poly object", al= "left")
	widgets["patchRandBut"] = cmds.button(l = "Create Patch from Randomly Chosen Vert", w=300, h=30, bgc = (.8, .4, .3), c=partial(patchChooser, "random"))
	
	widgets["patchMakeFLO"] = cmds.frameLayout(l = "Create/Move Multiple Random Patches", cll=True, w=300)
	widgets["patchMakeRandIFG"] = cmds.intFieldGrp(l="Number of Patches to create & move", v1 = 10, cw = [(1,220), (2, 50)], cal = [(1, "left"), (2, "left")])
	cmds.text("select poly object", al="left")
	widgets["patchRandMakeMoveBut"] = cmds.button(l = "Create and Move Random Patches", w=300, h=30, bgc = (.8, .1, .1), c=makeRandomPatches)

	cmds.setParent(widgets["mainTLO"])
	widgets["lineCLO"] = cmds.columnLayout("Random Lines")
	cmds.text("Do some stuff with lines here")

	cmds.showWindow(widgets["win"])

def getSoftSelection(type, *args):
	"""from brian ???, gets the list of softselection components and passes out the verts and the weights"""
	#Grab the soft selection
	selection = OpenMaya.MSelectionList()
	softSelection = OpenMaya.MRichSelection()
	OpenMaya.MGlobal.getRichSelection(softSelection)
	softSelection.getSelection(selection)

	dagPath = OpenMaya.MDagPath()
	component = OpenMaya.MObject()

	# Filter Defeats the purpose of the else statement
	iter = OpenMaya.MItSelectionList( selection,OpenMaya.MFn.kMeshVertComponent )
	elements, weights = [], []
	while not iter.isDone():
		iter.getDagPath( dagPath, component )
		dagPath.pop() #Grab the parent of the shape node
		node = dagPath.fullPathName()
		fnComp = OpenMaya.MFnSingleIndexedComponent(component)
		getWeight = lambda i: fnComp.weight(i).influence() if fnComp.hasWeights() else 1.0

		for i in range(fnComp.elementCount()):
			elements.append('%s.vtx[%i]' % (node, fnComp.element(i)))
			weights.append(getWeight(i))
		next(iter)

	if type == "random":
		selMoveVerts(elements, weights)
	elif type == "patch":
		selMovePatch(elements, weights)


def selMoveVerts(verts, weights, *args):
	"""take a selection of verts (could be soft) and randomly move them up"""
	cutoffRaw = cmds.intSliderGrp(widgets["selvpercISG"], q=True, v=True)
	cutoff = cutoffRaw/100.0
	cycles = cmds.intFieldGrp(widgets["seliterIFG"], q= True, v1 = True)
	xmin = cmds.floatFieldGrp(widgets["selmovexFFG"], q=True, v1= True)
	xmax = cmds.floatFieldGrp(widgets["selmovexFFG"], q=True, v2= True)
	ymin = cmds.floatFieldGrp(widgets["selmoveyFFG"], q=True, v1= True)
	ymax = cmds.floatFieldGrp(widgets["selmoveyFFG"], q=True, v2= True)
	zmin = cmds.floatFieldGrp(widgets["selmovezFFG"], q=True, v1= True)
	zmax = cmds.floatFieldGrp(widgets["selmovezFFG"], q=True, v2= True)

	sel = cmds.ls(sl=True)

	#####HERE GET VERTS TO SELECT (WITH MULT VALUES)
	for x in range(0,cycles):
		#print "doing pass %s"%x
		for y in range(0, len(verts)):
			rand = random.uniform(0, 1)
			if rand <= cutoff:
				randx = random.uniform(xmin, xmax)
				randy = random.uniform(ymin, ymax)
				randz = random.uniform(zmin, zmax)
			
				cmds.move(randx * weights[y],randy* weights[y], randz* weights[y], verts[y], r=True)

def selMovePatch(verts, weights, *args):
	"""take a selection of verts (could be soft) and randomly move them up"""
	#cutoffRaw = cmds.intSliderGrp(widgets["selvpercISG"], q=True, v=True)
	#cutoff = cutoffRaw/100.0
	cycles = cmds.intFieldGrp(widgets["patchiterIFG"], q= True, v1 = True)
	xmin = cmds.floatFieldGrp(widgets["patchmovexFFG"], q=True, v1= True)
	xmax = cmds.floatFieldGrp(widgets["patchmovexFFG"], q=True, v2= True)
	ymin = cmds.floatFieldGrp(widgets["patchmoveyFFG"], q=True, v1= True)
	ymax = cmds.floatFieldGrp(widgets["patchmoveyFFG"], q=True, v2= True)
	zmin = cmds.floatFieldGrp(widgets["patchmovezFFG"], q=True, v1= True)
	zmax = cmds.floatFieldGrp(widgets["patchmovezFFG"], q=True, v2= True)

	sel = cmds.ls(sl=True)

	#####HERE GET VERTS TO SELECT (WITH MULT VALUES)
	for x in range(0,cycles):
		#print "doing pass %s"%x
			#rand = random.uniform(0, 1)
			#if rand <= cutoff:
		randx = random.uniform(xmin, xmax)
		randy = random.uniform(ymin, ymax)
		randz = random.uniform(zmin, zmax)
		
		for y in range(0, len(verts)):
			cmds.move(randx * weights[y],randy* weights[y], randz* weights[y], verts[y], verts[y], r=True)

def moveVerts(*args):
	"""take a surface and wrinkle it up"""
	cutoffRaw = cmds.intSliderGrp(widgets["vpercISG"], q=True, v=True)
	cutoff = cutoffRaw/100.0
	#print cutoff
	cycles = cmds.intFieldGrp(widgets["iterIFG"], q= True, v1 = True)
	xmin = cmds.floatFieldGrp(widgets["movexFFG"], q=True, v1= True)
	xmax = cmds.floatFieldGrp(widgets["movexFFG"], q=True, v2= True)
	ymin = cmds.floatFieldGrp(widgets["moveyFFG"], q=True, v1= True)
	ymax = cmds.floatFieldGrp(widgets["moveyFFG"], q=True, v2= True)
	zmin = cmds.floatFieldGrp(widgets["movezFFG"], q=True, v1= True)
	zmax = cmds.floatFieldGrp(widgets["movezFFG"], q=True, v2= True)

	sel = cmds.ls(sl=True)

	for obj in sel:
		verts = cmds.ls("%s.vtx[*]"%obj, fl=True)
		
		for x in range(0,cycles):
			#print "doing pass %s"%x
			for vert in verts:
				rand = random.uniform(0, 1)
				if rand <= cutoff:
					randx = random.uniform(xmin, xmax)
					randy = random.uniform(ymin, ymax)
					randz = random.uniform(zmin, zmax)
				
					cmds.move(randx,randy, randz, vert, r=True)

def bevelEdges(*args):
	"""select obj, this will randomly bevel some edges"""

	cutoffRaw = cmds.intSliderGrp(widgets["bpercISG"], q=True, v=True)
	cutoff = cutoffRaw/100.0

	sel = cmds.ls(sl=True)

	for obj in sel:

		edges = cmds.ls("%s.e[*]"%obj, fl=True)

		bevelList = []

		for edge in edges:
			rand = random.uniform(0,1)
			if rand <= cutoff:
				bevelList.append(edge)

		cmds.select(cl=True)
		cmds.select(bevelList, r=True)

		cmds.polyBevel(fraction = .5, offset = .05)
		cmds.select(sel, r=True)

def patchChooser(thisType, *args):
	# can be "random" or "verts"
	iters = cmds.intFieldGrp(widgets["patchCreateIFG"], q= True, v1=True)
	cutoffRaw = cmds.intSliderGrp(widgets["patchRandISG"], q= True, v=True)
	cutoffInverse = cutoffRaw/100.0
	cutoff = 1.0 - cutoffInverse
	if thisType == "verts":
		growth(iters, cutoff)
	elif thisType == "random":
		selectRandomVert()
		growth(iters, cutoff)

def makeRandomPatches(*args):
	num = cmds.intFieldGrp(widgets["patchMakeRandIFG"], q= True, v1=True)
	obj = cmds.ls(sl=True)[0]
	#print obj
	for x in range(0, num):
		print("Doing patch number: %s"%x)
		cmds.select(obj, r=True)
		patchChooser("random")
		getSoftSelection("patch")

def growth(iters, cutoff, *args):
	#grow vertex selection
	for y in range(0, (iters-1)):
		origVerts = cmds.ls(sl=True, fl=True)

		cmds.GrowPolygonSelectionRegion()
		allVerts = cmds.ls(sl=True, fl=True)
		newVerts = [v for v in allVerts if v not in origVerts]
		
		for vert in newVerts:
			rand = random.uniform(0,1)
			if rand >= cutoff:
				cmds.select(vert, d=True)
		
def selectRandomVert(*args):
	sel = cmds.ls(sl=True)[0]
	
	fullList = cmds.ls("%s.vtx[*]"%sel, fl=True)
	vert = random.choice(fullList)
	
	cmds.select(vert, r=True)


def wrinklePoly(*args):
		wrinklePolyUI()

