# -*- coding: utf-8 -*-

###
#zbw_wireRig:
#to use: python window, call "import zbw_wireRig as zwire; zwire.wireRig()". Top pane will create a curve from selected poly edges, second button there
#will reverse a selected curve. Bottom pane select geo then curve then button and it will create a wire deformer with #of controls you've chosen. It
#will put the controls in a hierarchy depending on checkbox. Control scale just dictates the size of the created controls. Controls have a random color
#assigned to them. Wire def controls will be located on the group that contains the controls (select a control to find the master group it is in)
###

import maya.cmds as cmds
import zTools.rig.zbw_rig as rig
import maya.mel as mel
import random
#create UI
widgets = {}


def wireRigUI (*args):
    if cmds.window("wireRigWin", exists = True):
        cmds.deleteUI("wireRigWin")
    
    widgets["win"] = cmds.window("wireRigWin", t="zbw_wireRig", w=300, h=250)
    widgets["mainCLO"] = cmds.columnLayout()
    
    widgets["topFLO"] = cmds.frameLayout(l="Convert Poly Edges",cll=True, cl=True)
    widgets["topCLO"] = cmds.columnLayout()
    widgets["convertBut"] = cmds.button(l="convert selected poly edge to curve", w=300, bgc = (.8,.8,0), c=convertEdge)
    cmds.separator(h=20, style="single")
    widgets["reverseBut"] = cmds.button(l="reverse direction of selected curve", w=300, bgc = (.8,.5,0), c=reverseCrv)
    
    cmds.setParent(widgets["mainCLO"])
    widgets["botFLO"] = cmds.frameLayout(l="Create Wire Rig", cll=True)
    widgets["botCLO"] = cmds.columnLayout()
    widgets["numCtrlIFG"] = cmds.intFieldGrp(l="Number of Ctrls:", v1=5, cal=[(1, "left"), (2, "left")], cw=[(1, 150),(3, 75)])
    widgets["hierCBG"] = cmds.checkBoxGrp(ncb=1, l1 = "Put Ctrls in hierarchy?", v1=True, en=True)
    widgets["nameTFG"] = cmds.textFieldGrp(l="Wire Rig Name:", w=300, tx="wireCtrl1", cal=[(1, "left")])
    widgets["scaleFFG"] = cmds.floatFieldGrp(l="Control scale:", v1=1.0, cal=[(1, "left"), (2, "left")], cw=[(1, 150),(3, 75)])
    
    cmds.separator(h=30, style="single")
    widgets["textText"] = cmds.text("Select geo, then curve, then button below", al="center")
    widgets["rigBut"] = cmds.button(l="Create Wire Rig", w= 300, h=40, bgc= (0, .5, 0), c=createWireDef)
    
    cmds.showWindow(widgets["win"])
    
#option to pull curve from edges
def convertEdge(*args):
    """converts the selected poly edge to a nurbs curve"""
    sel = cmds.ls(sl=True, type="transform")
    try:
        mel.eval("polyToCurve -ch 0 -form 2 -degree 3;")
    except:
        cmds.warning("Couldn't complete this operation! Sorry buddy. Maybe you haven't selected a poly edge?")

def reverseCrv(*args):
  sel = cmds.ls(sl=True)[0]
  shp = cmds.listRelatives(sel, shapes=True)
  if cmds.objectType(shp) != "nurbsCurve":
    cmds.warning("not a nurbs curve to reverse")
  else: 
    revCrv = cmds.reverseCurve(sel, rpo=True, ch=False)[0]
    cmds.select(revCrv)
    print(("reversed curve: %s!"%revCrv))
  

def rebuildCrv(crv):
  #get curve and rebuild to number
  num = cmds.intFieldGrp(widgets["numCtrlIFG"], q=True, v1=True)
  name = cmds.textFieldGrp(widgets["nameTFG"],q=True, tx=True)
  crvName = name + "_CRV"
  newCrv = cmds.rebuildCurve(n=crvName, ch=0, rpo=True, d=3, s=(num-1))[0]
  # print "rebuilt curve name is :" + newCrv
  
  return newCrv
  
#create wire deformers on geo 
def createWireDef(*args):
  #clusterList = []
  #rebuiltCrv = ""
  #get geo and curve
  geo = cmds.ls(sl=True)[0]
  crv = cmds.ls(sl=True)[1]
  rebuiltCrv = rebuildCrv(crv)
  name = cmds.textFieldGrp(widgets["nameTFG"],q=True, tx=True)
  defName = "wire_"+ name
  wireDef = cmds.wire(geo, w = rebuiltCrv, n= defName, gw=True)
  wireGroup = wireDef[1] + "Group"
  cmds.setAttr(wireGroup + ".v", 0)

  clusterList = clstrOnCurve(rebuiltCrv)
  #print clusterList
  ctrlGrp = createControls(clusterList)
  
  masterGrp = cmds.group(n=name+"_GRP", em=True)
  cmds.parent(ctrlGrp, masterGrp)
  cmds.parent(wireGroup, masterGrp)

  cmds.addAttr(masterGrp, ln="xxWireDeformerCtrlsXX", at="bool", k=True)
  cmds.setAttr(masterGrp + ".xxWireDeformerCtrlsXX", l=True)
  cmds.addAttr(masterGrp, ln = 'envelope', at = "float", dv = 1, min=0, max=1, k=True)
  cmds.addAttr(masterGrp, ln = 'DropoffDistance', at = 'float', dv = 1, min = 0, max = 15, k = True)
  cmds.addAttr(masterGrp, ln = 'tension', at = 'float', dv = 1, min = -10, max = 10, k = True)
  cmds.addAttr(masterGrp, ln = 'rot', at = 'float', min = 0, max = 1, k =True)
  cmds.addAttr(masterGrp, ln = 'scl', at = 'float', dv = 1, min = 0, max = 3, k = True)

  cmds.connectAttr(masterGrp + ".envelope", wireDef[0] + ".envelope")
  cmds.connectAttr(masterGrp + ".DropoffDistance", wireDef[0] + ".dropoffDistance[0]")
  cmds.connectAttr(masterGrp + ".tension", wireDef[0] + ".tension")
  cmds.connectAttr(masterGrp + ".rot", wireDef[0] + ".rotation")
  cmds.connectAttr(masterGrp + ".scl", wireDef[0] + ".scale[0]")
  
  cmds.select(masterGrp, r = True)

  incrementName()

def incrementName(*args):
  name = cmds.textFieldGrp(widgets["nameTFG"],q=True, tx=True)
  if cmds.objExists(name + "_CLS"):
    cmds.warning("already used that name. Since I'm lazy, I'll let maya fix the clashing")
    #newText = name + ""
    #cmds.textFieldGrp(widgets["nameTFG"], tx=newText)
    
#create ctrls on curve (use clusters?) - option to create hierarchy? 
def clstrOnCurve(crv):
  """gets the cvs in the selected curve and calls create cluster on them. Note: first two and last two cvs are grouped together"""
  cvs = cmds.ls("%s.cv[*]"%crv, fl=True)
  thisCv = []
  size = len(cvs)
  clusterList = []
  clusterList.append(createCluster(cvs[0:1]))
  for cv in cvs[2:-2]:
    thisCV = [cv]
    clusterList.append(createCluster(thisCV))
  clusterList.append(createCluster([cvs[size-1], cvs[size-2]]))
  
  return(clusterList)
  
def createCluster(cvs):
  """create cluster on the list arg (needs to be cvs or verts)"""
  name = cmds.textFieldGrp(widgets["nameTFG"],q=True, tx=True)
  clsName = name + "_CLS"
  clstr = cmds.cluster(cvs, n = clsName, rel=False)[1]
  
  return(clstr)
    
def createControls(list):
  """for each thing in the list, creates a control. Requires zbw_rig.py module"""
  #for each cluster create a controlsOnCurve
  ctrlList = []
  grpList = []
  colorList = ["red","blue","green","darkRed","lightRed","medBlue","lightBlue","royalBlue","darkGreen","medGreen","yellowGreen","yellow","darkYellow","lightYellow","purple","darkPurple","black","brown","darkBrown","lightBrown","pink","orange"]
  randColor = colorList[random.randint(0, len(colorList)-1)]
  for clstr in list:
    #print list
    ctrlName = clstr.rpartition("Handle")[0] + "_CTRL"
    ctrl = rig.create_control(name = ctrlName, type="sphere", axis="x", color = randColor)
    #scale ctrl
    scl = cmds.floatFieldGrp(widgets["scaleFFG"], q=True, v1=True)/2
    pts = cmds.ls(ctrlName + ".cv[*]")
    cmds.select(pts)
    cmds.scale(scl, scl, scl)
    cmds.setAttr(clstr + ".v", 0)
    
    pos = cmds.xform(clstr, q=True, ws=True, rp=True)
    
    grp = cmds.group(em=True, name = ctrlName + "_GRP")
    cmds.parent(ctrl, grp)
    cmds.xform(grp, ws=True, t=pos)
    ctrlList.append(ctrlName)
    grpList.append(grp)
  
  for x in range(0, len(ctrlList)):
    cmds.parent(list[x], ctrlList[x])
  
  oldName = cmds.textFieldGrp(widgets["nameTFG"],q=True, tx=True)
  cntrlGrp = cmds.group(name = oldName + "_CTRL_GRP", em = True)
  
  for group in grpList:
    cmds.parent(group, cntrlGrp)
  
  hier = cmds.checkBoxGrp(widgets["hierCBG"], q=True, v1=True)
  if hier:
    for x in range(len(ctrlList)-1, 0, -1):
      cmds.parent(grpList[x], ctrlList[x-1])
    #cmds.parent(grpList[0], cntrlGrp)
  
  return(cntrlGrp)

#call the function
def wireRig():
  wireRigUI()