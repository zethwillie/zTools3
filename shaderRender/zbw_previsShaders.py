import maya.cmds as cmds
from functools import partial

widgets = {}

ann = {"hier":"gets all geo objs under the selected obj(s) or ctrl(s)\nand adds that geo to the list.\nIgnores non-geo objs.", 
"sel":"gets only the selected geo. Ignores groups and curves",
"all":"will get all the geo in your scene and add to list.\nNote: For your scene's safety, the max num of objs in the list is 100", 
"refresh":"if you've made shader changes outside of this script,\nthis will update the current list to reflect those",
"toAll":"This will take the shader from the selected obj (doesn't have to be in this win)\n and copy to ALL objs in the current list"}


def pvShaderUI(*args):
    if cmds.window("shdWin", exists = True):
        cmds.deleteUI("shdWin")

    widgets["mainWin"] = cmds.window("shdWin", t="Previs Shader Setup", w=600, h=600, s=False)
    widgets["mainCLO"] = cmds.columnLayout(w=600,  bgc = (.3,.3,.3), h=600)
    cmds.separator(h=10)
    widgets["topRCLO"] = cmds.rowColumnLayout(w=600, nc=3, cw=[(1, 300),(2, 135), (3,135)], cs=[(2,15), (3,15)])
    widgets["HierBut"] = cmds.button(l="List Geo Hierarchy Under Selected", w=300, h=30, bgc = (.4,.6, .7), ann = ann["hier"], c=getHierGeo)
    widgets["getSelBut"] = cmds.button(l="List Selected", w=135, h=30, bgc = (.7,.7,.4), ann=ann["sel"], c=getSelectedGeo)
    widgets["getAllBut"] = cmds.button(l="List All Geo", w=135, h=30, bgc = (.7,.4,.4), ann= ann["all"], c=getAllGeo)

    widgets["refrRCLO"] = cmds.rowColumnLayout(p=widgets["mainCLO"], nc =2, cw = [(1,300), (2,290)], cs = [(2,10)], w=600)
    cmds.separator(h=10, style = "none")
    cmds.separator(h=10, style = "none")
    widgets["refrBut"] = cmds.button(l="Refresh Current", w=300, h=30, bgc = (.5,.5,.5),en=False, ann=ann["refresh"], c=refreshList)
    widgets["toAllBut"] = cmds.button(l="Selected Obj's Shader to All Listed", w=290, h=30, bgc = (.5,.5,.5), ann=ann["toAll"],en=False, c=shaderToAll)

    cmds.separator(style="none", h=10)
    cmds.separator(style="none", h=10)
    widgets["mainSLO"] = cmds.scrollLayout(w=600, h=600)
    widgets["objectRCLO"] = cmds.rowColumnLayout(w=600, nc=1, cal = [(1, "left")])
    cmds.text("1. Select geo to address shaders on from the top buttons. . . ")
    cmds.text("2. Clickin the name of obj will select that obj. Middle mouse 'Drag/Drop' button onto other D/D buttons to pass shaders.")
    cmds.text("3. 'Create' will create a new lambert shdr on that obj. Red means obj has a shdr other than the default lambert")

    cmds.window(widgets["mainWin"], e=True, w=600, h=600)
    cmds.showWindow(widgets["mainWin"])

class GeoObject(object):
    #static variables for passing info
    passingSG = ""
    passingAttr = ""

    currentGeoList = []

    def __init__(self, geo):
        self.geo = geo
        self.shader = ""
        self.shaderName = ""
        self.shadingGroup = ""
        self.shaderMade = False
        self.colorAttr = ""	
        self.color = ""
        self.createUI()
        GeoObject.currentGeoList.append(geo)

    def createUI(self):
        self.selButton = cmds.iconTextButton(style="textOnly", label=self.geo, w=120, p=widgets["objectRCLO"], c=self.select)
        self.createButton = cmds.button(l="create", w=50, p=widgets["objectRCLO"], c=self.createShader)
        self.color = cmds.attrColorSliderGrp(l="", cw=[(1,10), (2,40),(3,50)], rgb=(.5,.5,.5), p = widgets["objectRCLO"])
        self.dragBut = cmds.iconTextButton(l="Drag/Drop", style = "textOnly", w=50, fla = False, p = widgets["objectRCLO"], dpc = partial(self.dropCommand, self.geo, self.color))
        self.shadText = cmds.textField(w=110, ed=False, tx= self.shaderName)
        cmds.separator(style="none", h=5)
        cmds.separator(style="none", h=5)
        cmds.separator(style="none", h=5)
        cmds.separator(style="none", h=5)
        cmds.separator(style="none", h=5)

        self.shaderCheck()
            
        if self.shaderName and self.shadingGroup:
            if self.shadingGroup != "initialShadingGroup":
                self.colorAttr = getColorAttr(self.shaderName)
                if self.colorAttr:
                    cmds.button(self.createButton, e=True, bgc = (.5,.2,.2))
                    cmds.attrColorSliderGrp(self.color, e=True, en=True, at="%s.%s"%(self.shaderName, self.colorAttr))
                    cmds.iconTextButton(self.dragBut, e=True, dgc = partial(self.dragCommand, self.shadingGroup, ("%s.%s"%(self.shaderName,self.colorAttr))))
            else:
                cmds.attrColorSliderGrp(self.color, e=True, en=False)
                pass

    def createShader(self, *args):
        self.shaderName = cmds.shadingNode("lambert", asShader=True, n=("%sPVSHD")%self.geo)
        self.shadingGroup = cmds.sets(n=("%sSG"%self.shaderName), renderable=True, noSurfaceShader=True, empty=True)
        cmds.connectAttr("%s.outColor"%self.shaderName, "%s.surfaceShader"%self.shadingGroup)
        cmds.sets(self.geo, e=True, forceElement=self.shadingGroup)
        self.colorAttr = "color"
        cmds.setAttr("%s.%s"%(self.shaderName, self.colorAttr), 1, .7, .4)

        cmds.attrColorSliderGrp(self.color, e=True, en=True, at = "%s.%s"%(self.shaderName,self.colorAttr) )
        cmds.iconTextButton(self.dragBut, e=True, dgc = partial(self.dragCommand, self.shadingGroup, ("%s.%s"%(self.shaderName,self.colorAttr))))
        cmds.button(self.createButton, e=True, bgc=(.5,.2,.2))
        cmds.textField(self.shadText, e=True, tx=self.shaderName)
    
    def shaderCheck(self):
        # do we have a shader assigned?
        shapeA = cmds.listRelatives(self.geo, s=True)
        if shapeA:
            shape = shapeA[0]
            sg = cmds.listConnections(shape, t="shadingEngine")
            if sg:
                self.shadingGroup = sg[0]
                mat = cmds.listConnections("%s.surfaceShader"%self.shadingGroup)
                if mat:
                    self.shaderName = mat[0]
                    cmds.textField(self.shadText, e=True, tx=self.shaderName)

    def dropCommand(self, targetGeo, sldrGrp, *args):
        print(("dropCommand passingAttr = %s\ndrop passingSG = %s"%(GeoObject.passingAttr, GeoObject.passingSG)))
        #connect geo to passed sg
        cmds.sets(targetGeo, e=True, forceElement=GeoObject.passingSG)
        #connect slider to passed attr
        shd = cmds.listConnections("%s.surfaceShader"%GeoObject.passingSG)[0]
        cmds.attrColorSliderGrp(sldrGrp, e=True, at = "%s.%s"%(shd,GeoObject.passingAttr))
        #deactivate createButton
        cmds.button(self.createButton, e=True, bgc = (.5,.2,.2))
        #activate drag functionality
        shd = cmds.listConnections("%s.surfaceShader"%GeoObject.passingSG)[0]
        self.shadingGroup = GeoObject.passingSG
        self.colorAttr = GeoObject.passingAttr
        self.shaderName = cmds.listConnections("%s.surfaceShader"%self.shadingGroup)[0]
        cmds.iconTextButton(self.dragBut,  e=True, dgc = partial(self.dragCommand, self.shadingGroup, GeoObject.passingAttr))
        cmds.textField(self.shadText, e=True, tx = self.shaderName)
        #################----- self here is the DROPPED on object

    def dragCommand(self, sg, attr, *args):
        GeoObject.passingSG = self.shadingGroup
        GeoObject.passingAttr = self.colorAttr
        print(("drag just set sg: %s\nand attr: %s"%(GeoObject.passingSG, GeoObject.passingAttr)))
        ###################-----------self here is the dragged object

    def select(self):
        cmds.select(self.geo, r=True)

def createList(glist, *args):
    if glist:
        if len(glist) <100:
            cmds.deleteUI(widgets["objectRCLO"])
            widgets["objectRCLO"] = cmds.rowColumnLayout(nc=5, w=600, p=widgets["mainSLO"], cw = [(1, 120), (2,60), (3,165), (4,100), (5,110)], cs=(5,5))
            GeoObject.currentGeoList = []
            #doubleCheck that all are only poly or nurbs
            clist = []
            for geo in glist:
                if cmds.objectType(cmds.listRelatives(geo, s=True)[0])=="mesh" or cmds.objectType(cmds.listRelatives(geo, s=True)[0])=="nurbsSurface":
                    clist.append(geo)
            #create an instance for each that will populate the list
            for obj in clist:
                GeoObject(obj)

            cmds.button(widgets["refrBut"], e=True, en=True, bgc = (.4,.7, .4))	
            cmds.button(widgets["toAllBut"], e=True, en=True, bgc = (.8,.6, .3))
        else:
            cmds.confirmDialog(m="Sorry, for performance reasons, I don't want to access more than 100 objects. . . \nTry use smaller chunks with other options (hierarchy or selected)")

def getHierGeo(*args):
    geoList = []
    sel = cmds.ls(sl=True)

    if sel:
        for mstr in sel:
             relsSh = cmds.listRelatives(mstr, ad=True, f=True, type=["nurbsSurface", "mesh"])
             if relsSh:
                for shp in relsSh:
                    geoList.append(cmds.listRelatives(shp, p=True)[0])
             else:
                cmds.warning("No shapes gotten!")
    else:
        cmds.warning("Nothing selected!")
    geoSet = set(geoList)

    createList(geoSet)

def getSelectedGeo(*args):
    geo = []
    sel = cmds.ls(sl=True)
    if sel:
        for obj in sel:
            shp = cmds.listRelatives(obj, s=True)
            if shp:
                if cmds.objectType(shp[0])=="mesh" or cmds.objectType(shp[0])=="nurbsSurface":
                    geo.append(obj)
                else:
                    cmds.warning("%s is not a mesh or nurbs. Skipping!"%obj)
            else:
                cmds.warning("%s is not tranform node with a shape! Skipping!"%obj)
    else:
        cmds.warning("Nothing selected!")
    createList(geo) 

def getAllGeo(*args):
    geo = []
    shps = cmds.ls(g=True)
    for shp in shps:
        if cmds.objectType(shp)=="mesh" or cmds.objectType(shp)=="nurbsSurface":
            geo.append(cmds.listRelatives(shp, parent=True)[0])
    
    createList(geo)

def getColorAttr(shd, *args):
    color = ""
    shType = cmds.objectType(shd)

    shList = ["lambert","blinn", "phong", "phongE", "aiStandard", "mia_material_x_passes", "mia_material", "mia_material_x"]
    if shType in shList:
        color = "color"
        return color
    elif shType == "surfaceShader":
        color = "outColor"
        return mat, color
    else:
        return None

def refreshList(*args):
    createList(GeoObject.currentGeoList)

def shaderToAll(*args):
    sel = cmds.ls(sl=True)
    if len(sel) != 1:
        cmds.warning("You must only select one object to pass it's shader")
    else:
        shp = cmds.listRelatives(sel[0], s=True)
        if shp:
            if cmds.objectType(shp[0]) == "mesh" or cmds.objectType(shp) == "nurbsSurface":
                sg = cmds.listConnections(shp[0], t="shadingEngine")[0]
                if sg:
                    sdr = cmds.listConnections("%s.surfaceShader"%sg)[0]
                    if sdr:
                        #for each in geoList, connect obj to sg
                        for geo in GeoObject.currentGeoList:
                            cmds.sets(geo, e=True, forceElement=sg)
                        refreshList()	
                    else: 
                        cmds.warning("No shader on this shading group.Sorry!")
                else:
                    cmds.warning("No shading group on this object! Sorry!")
            else:
                cmds.warning("The object must be geo (nurbs or polys)")
        else:
            cmds.warning("You must select an obj w/ a shape(like geo, not grps or shdrs). %s doesn't have one"%sel[0])

def previsShaders(*args):
    pvShaderUI()