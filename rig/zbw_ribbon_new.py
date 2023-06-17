import maya.cmds as cmds
import maya.OpenMaya as om

import zTools3.rig.zbw_rig as rig
import importlib
import zTools3.resources.zbw_window as win


class RibbonUI(win.Window):
    def __init__(self):
        self.common_UI()

    def common_UI(self):
        #---------------- make ribbon tools (reverse, rebuild, etc)
        #---------------- option to have middle follow?
        #---------------- options for FK
        #---------------- volume for scaling
        #----------------easier to use with height width instead of ratio
        #----------------add a copy to do blends on? option

        w = 420
        h = 350
        if cmds.window("ribbonWin", exists=True):
            cmds.deleteUI("ribbonWin")
        self.ribWin = cmds.window("ribbonWin", w=w, h=h, s=False)

        tab = cmds.tabLayout()
        cmds.columnLayout("Create Geo", w=w, h=h)
        self.ribbonNameTFG = cmds.textFieldGrp(l="Ribbon Rig Name", cal=[(1, "left"), (2, "left")], cw=[(1, 100), (2, 200)], tx="ribbon", sbm="Name your ribbon")
        cmds.separator(h=10, style="single")
        self.simpleCB = cmds.checkBox(l="Create Simple Control Ribbons", v=0)
        cmds.separator(h=10)

        self.bindJointsIFG = cmds.intFieldGrp(l="Num Bind Joints", cal=([1, "left"]), cw=([1, 125], [2, 100]), v1=11)
        self.ctrlsIFG = cmds.intFieldGrp(l="Num Ctrls", cal=([1, "left"]), cw=([1, 125], [2, 100]), v1=3)

        cmds.separator(h=10)
        self.heightFFG = cmds.floatFieldGrp(l="Ribbon Height", cal=[(1, "left"), (2, "left")], cw=[(1, 125), (2, 100)], v1=10.0)
        self.widthFFG = cmds.floatFieldGrp(l="Width", cal=[(1, "left"), (2, "left")], cw=[(1, 125), (2, 100)], v1=2.0)

        cmds.separator(h=10)
        self.mainCtrlTypeOM = cmds.optionMenu(l="Main Ctrl Type: ")
        cmds.menuItem(l="cube")
        cmds.menuItem(l="circle")
        cmds.menuItem(l="square")
        cmds.menuItem(l="hexagon")
        self.fineCtrlTypeOM = cmds.optionMenu(l="Fine Ctrl Type: ")
        cmds.menuItem(l="cube")
        cmds.menuItem(l="circle")
        cmds.menuItem(l="star")
        cmds.menuItem(l="sphere")
        cmds.optionMenu(self.fineCtrlTypeOM, e=True, v="star")

        cmds.separator(h=10)
        self.axisRBG = cmds.radioButtonGrp(l="Ctrl Main Axis: ", nrb=3, cw4=[100, 40, 40, 40], cl4=["left", "left", "left", "left"], la3=["x", "y", "z"], sl=1)
        cmds.separator(h=10)
        self.rotOrderOM = cmds.optionMenu(l="RotateOrder")
        cmds.menuItem(l="xyz")
        cmds.menuItem(l="yzx")
        cmds.menuItem(l="zxy")
        cmds.menuItem(l="xzy")
        cmds.menuItem(l="yxz")
        cmds.menuItem(l="zyx")

        cmds.separator(h=10)
        cmds.button(l="Create Ribbon and Geo", w=w, h=40, bgc=(.5, .7, .5), c=self.collect_info_for_ribbon)

        ##########################
        #---------------- add simple option? Would we need this?
        cmds.setParent(tab)
        cmds.columnLayout("Use Existing", w=420, h=350)
        self.geoRibbonNameTFG = cmds.textFieldGrp(l="Ribbon Rig Name", cal=[(1, "left"), (2, "left")], cw=[(1, 100), (2, 200)], tx="ribbon", sbm="Name your ribbon")
        self.geoRibbonGeoTFBG = cmds.textFieldButtonGrp(l="Ribbon Geo", cal=[(1, "left"), (2, "left")], cw=[(1, 100), (2, 200)], tx="", sbm="Select the geometry and press <<< to add to field", bl="<<<", bc=self.get_geometry_for_field)
        cmds.separator(h=10)
        self.geoSimple = cmds.checkBox(l="Create Simple Control Ribbon", v=0)

        cmds.separator(h=10)
        self.geoBindJointsIFG = cmds.intFieldGrp(l="Num Bind Joints", cal=([1, "left"]), cw=([1, 125], [2, 100]), v1=11)
        self.geoCtrlsIFG = cmds.intFieldGrp(l="Num Ctrls", cal=([1, "left"]), cw=([1, 125], [2, 100]), v1=3)

        cmds.separator(h=10)
        self.geoMainCtrlTypeOM = cmds.optionMenu(l="Main Ctrl Type: ")
        cmds.menuItem(l="cube")
        cmds.menuItem(l="circle")
        cmds.menuItem(l="square")
        cmds.menuItem(l="hexagon")
        self.geoFineCtrlTypeOM = cmds.optionMenu(l="Fine Ctrl Type: ")
        cmds.menuItem(l="cube")
        cmds.menuItem(l="circle")
        cmds.menuItem(l="star")
        cmds.menuItem(l="sphere")
        cmds.optionMenu(self.geoFineCtrlTypeOM, e=True, v="star")

        cmds.separator(h=10)
        self.geoAxisRBG = cmds.radioButtonGrp(l="Ctrl Main Axis: ", nrb=3, cw4=[100, 40, 40, 40], cl4=["left", "left", "left", "left"], la3=["x", "y", "z"], sl=1)

        cmds.separator(h=10)
        self.geoRotOrderOM = cmds.optionMenu(l="RotateOrder")
        cmds.menuItem(l="xyz")
        cmds.menuItem(l="yzx")
        cmds.menuItem(l="zxy")
        cmds.menuItem(l="xzy")
        cmds.menuItem(l="yxz")
        cmds.menuItem(l="zyx")

        cmds.separator(h=10)
        cmds.button(l="Create Ribbon Rig on Geo", w=w, h=40, bgc=(.7, .5, .5), c=self.collect_info_for_geoRibbon)

        cmds.window(self.ribWin, e=True, wh=(5, 5))
        cmds.window(self.ribWin, e=True, rtf=True)
        cmds.showWindow(self.ribWin)

    def get_geometry_for_field(self, *args):
        sel = cmds.ls(sl=True)
        if not sel:
            return()
        cmds.textFieldButtonGrp(self.geoRibbonGeoTFBG, e=True, tx=sel[0])

    def collect_info_for_ribbon(self, *args):
        name = cmds.textFieldGrp(self.ribbonNameTFG, q=True, tx=True)
        simple = cmds.checkBox(self.simpleCB, q=True, v=True)
        numBindJnt = cmds.intFieldGrp(self.bindJointsIFG, q=True, v1=True)
        numCtrls = cmds.intFieldGrp(self.ctrlsIFG, q=True, v1=True)
        height = cmds.floatFieldGrp(self.heightFFG, q=True, v1=True)
        width = cmds.floatFieldGrp(self.widthFFG, q=True, v1=True)
        mainType = cmds.optionMenu(self.mainCtrlTypeOM, q=True, v=True)
        fineType = cmds.optionMenu(self.fineCtrlTypeOM, q=True, v=True)
        axis = cmds.radioButtonGrp(self.axisRBG, q=True, sl=True)
        rotOrder = cmds.optionMenu(self.rotOrderOM, q=True, sl=True) - 1
        makeGeo = 1

        if axis == 1:
            axis = "x"
        if axis == 2:
            axis = "y"
        if axis == 3:
            axis = "z"

        rib = RibbonMaker(name=name, makeGeo=makeGeo, simple=simple, numBindJnt=numBindJnt, numCtrls=numCtrls, height=height, width=width, mainType=mainType, fineType=fineType, axis=axis, rotOrder=rotOrder)

    def collect_info_for_geoRibbon(self, *args):
        name = cmds.textFieldGrp(self.geoRibbonNameTFG, q=True, tx=True)
        numBindJnt = cmds.intFieldGrp(self.geoBindJointsIFG, q=True, v1=True)
        numCtrls = cmds.intFieldGrp(self.ctrlsIFG, q=True, v1=True)
        mainType = cmds.optionMenu(self.geoMainCtrlTypeOM, q=True, v=True)
        fineType = cmds.optionMenu(self.geoFineCtrlTypeOM, q=True, v=True)
        axis = cmds.radioButtonGrp(self.geoAxisRBG, q=True, sl=True)
        rotOrder = cmds.optionMenu(self.geoRotOrderOM, q=True, sl=True) - 1
        makeGeo = 0
        geo = cmds.textFieldButtonGrp(self.geoRibbonGeoTFBG, q=True, tx=True)
        if not geo:
            cmds.warning("you need to have a nurbs surface to ribbonize!")
            return()

        if axis == 1:
            axis = "x"
        if axis == 2:
            axis = "y"
        if axis == 3:
            axis = "z"

        rib = RibbonMaker(name=name, numBindJnt=numBindJnt, numCtrls=numCtrls, mainType=mainType, fineType=fineType, axis=axis, rotOrder=rotOrder, geo=geo)


class RibbonMaker(object):
    def __init__(self, name="ribbon", makeGeo=0, simple=0, numBindJnt=15, numCtrls=3, height=10, width=2, mainType="cube", fineType="star", axis="x", rotOrder=0, geo=None):

        self.name = name
        self.simple = simple
        self.numBindJnt = numBindJnt
        self.numCtrls = numCtrls
        self.height = height
        self.width = width
        self.mainType = mainType
        self.fineType = fineType
        self.axis = axis  # is a string, x y or z
        self.rotOrder = rotOrder  # is an int
        self.geo = geo
        self.makeGeo = makeGeo

        if self.makeGeo == 1:
            self.create_new_geo_ribbon()
        # parse data here to figure out where to go
        # make geo
        # if simple - create the ribbon, rig, controls then the simple geo, then the simple control structure
        # if not create the ribbon, rig, then the control structure

        # use existing geo
        # if using other geo then dupe geo (hide orig) check geo for direction, fix if wrong, rig, place and create controls
        pass

    def create_new_geo_ribbon(self):
        # create geo
        self.geo = self.create_geometry()
        self.divList = self.calculate_u_values()
        self.folList = self.create_follicles(self.name, self.geo, self.divList)
        self.bindJnts, self.fineCtrls = self.create_bind_rig(self.name, self.folList, self.fineType, self.axis)
        #---------------- setup volume stuff
        self.mainCtrls, self.ctrlJnts = self.create_control_rig(self.name, self.geo, self.numCtrls, self.mainType, self.axis)
        #---------------- setup follow options
        self.bind_ribbon(self.ctrlJnts, self.geo)
        if self.simple:
            self.create_simple_rig()

        # clean up (grouping, volume)
        self.clean_up(self.name)

    def create_existing_geo_ribbon(self):
        # check geo
        # fix geo, if necessary
        # calc u vals
        # create follicles
        # create bind rig
        # create control rig
        # if simple:
        #     create simple ribbon
        #     create simple follicles
        #     create simple bind joints
        #     create simple control rig
        #     connect controls to simple follicles
        # clean up (grouping, volume)

        pass

    def create_geometry(self):

        name = "{0}_bind_ribbon_GEO".format(self.name)
        ratio = self.height / self.width
        uDiv = self.numBindJnt
        vDiv = 0
        # create the nurbsPlane
        thisRib = cmds.nurbsPlane(name=name, axis=[0, 0, 1], width=self.width, d=3, constructionHistory=0, lengthRatio=ratio)[0]
        # cmds.xform(thisRib, ws=True, s=(1, self.height, self.width))
        cmds.makeIdentity(thisRib, apply=True, scale=True)
        cmds.reverseSurface(thisRib, d=3, ch=0, rpo=1)  # flips uv
        cmds.reverseSurface(thisRib, d=1, ch=0, rpo=1)  # flips u
        outRib = cmds.rebuildSurface(thisRib, constructionHistory=0, replaceOriginal=True, rebuildType=0, end=1, keepRange=0, keepControlPoints=0, keepCorners=0, degreeU=3, degreeV=1, spansV=vDiv, spansU=uDiv, tolerance=0.01, fitRebuild=0, direction=2)[0]
        return(outRib)

    def geo_check(self):
        # check whether given geo is in u
        # sel = cmds.ls(sl=True)[0]
        # shp = cmds.listRelatives(sel, s=True)[0]

        # crvU = cmds.duplicateCurve(shp + ".u[0.5]", local=True, ch=0)
        # crvV = cmds.duplicateCurve(shp + ".v[0.5]", local=True, ch=0)

        # if cmds.arclen(crvU) > cmds.arclen(crvV):
        # check spans? Does this matter that much?

        # selected surface is periodic or open? (cylinder or a plane)
        # if mc.getAttr(surf + ".formU") == 2 or mc.getAttr(surf + ".formV") == 2:
        #     curve_type = "periodic"
        #     divider_for_ctrls = num_of_ctrls
        # elif mc.getAttr(surf + ".formU") == 0 or mc.getAttr(surf + ".formV") == 0:
        #     curve_type = "open"
        #     divider_for_ctrls = num_of_ctrls - 1
        pass

    def geo_fix(self):
        # reverse geo direction if it's bad
        pass

    def calculate_u_values(self):
        if self.makeGeo:
            div = 1.0 / (self.numBindJnt - 1)
            divList = []
            for x in range(self.numBindJnt):
                divList.append(x * div)
        else:
            pass
            # figure out whether its open or closed geo

        return(divList)

    def create_follicles(self, name, geo, divList):
        """divList = list of increments ie. [0, .25, .5, .75, 1]"""
        folList = []
        for u in divList:
            fol = rig.follicle(surface=geo, name="{0}_follicle_{1}".format(name, divList.index(u)), u=u, v=0.5)
            folList.append(fol)

        return(folList)

    def create_bind_rig(self, name, folList, ctrlType, axis):
        jntList = []
        ctrlList = []
        for x in range(len(folList)):
            cmds.select(cl=True)
            jnt = cmds.joint(name="{0}_bind_{1}_JNT".format(name, x))
            rig.snap_to(folList[x], jnt)
            ctrl = rig.create_control(name="{0}_fine_{1}_CTRL".format(name, x), type=ctrlType, color="yellow", axis=axis)
            grp = rig.group_freeze(ctrl)
            rig.snap_to(jnt, grp)
            cmds.parentConstraint(ctrl, jnt)
            cmds.scaleConstraint(ctrl, jnt)
            cmds.parent(grp, folList[x][0])
            u = cmds.getAttr("{0}.parameterU".format(folList[x][0]))
            cmds.addAttr(ctrl, ln="uPos", at="float", dv=u, min=0.0, max=1.0, k=True)
            cmds.connectAttr("{0}.uPos".format(ctrl), "{0}.parameterU".format(folList[x][0]))
            cmds.setAttr("{0}.uPos".format(ctrl), l=True)
            jntList.append(jnt)
            ctrlList.append(ctrl)

        return(jntList, ctrlList)

    def create_control_rig(self, name, geo, numCtrls, ctrlType, axis):
        ctrlList = []
        jntList = []
        ctrlDiv = 1.0 / (numCtrls - 1)
        fol = rig.follicle(surface=self.geo, name="{0}_delete_tmp_follicle".format(name), u=0.5, v=0.5)
        for x in range(numCtrls):
            print(ctrlDiv * x)
            cmds.setAttr("{0}.parameterU".format(fol[0]), ctrlDiv * x)
            ctrl = rig.create_control(name="{0}_{1}_Ctrl".format(self.name, x), type=ctrlType, color="red", axis=axis)
            grp = rig.group_freeze(ctrl)
            rig.snap_to(fol[0], grp)
            cmds.select(cl=True)
            jnt = cmds.joint(name="{0}_ctrl_{1}_JNT".format(name, x))
            rig.snap_to(ctrl, jnt)
            cmds.parentConstraint(ctrl, jnt, mo=True)
            cmds.scaleConstraint(ctrl, jnt, mo=True)
            ctrlList.append(ctrl)
            jntList.append(jnt)
        cmds.delete(fol)

        return(ctrlList, jntList)

    def bind_ribbon(self, ctrlJnts, geo):
        #---------------- what to do if simple/?
        bindSkinCluster = cmds.skinCluster(ctrlJnts, geo, maximumInfluences=5, smoothWeights=0.5, obeyMaxInfluences=True, toSelectedBones=True, normalizeWeights=1, dropoffRate=5)

    def creat_simple_rig(self):
        # duplicate geo
        # rebuild that
        # put simple controls at either end
        # make joints for those, bind to simple ribbon
        # make num of follicles matchign num of main ctrls
        # connect main ctrls to those follicles (constraint)
        pass

    def clean_up(self, name):
        # add a master control
        topGrp = cmds.group(em=True, name="{0}_ribbon_GRP".format(name))
        xformGrp = cmds.group(em=True, name="{0}_ribbon_transform_GRP".format(name))
        noXformGrp = cmds.group(em=True, name="{0}_ribbon_noTransform_GRP".format(name))
        cmds.setAttr("{0}.inheritsTransform".format(noXformGrp), 0)

        geoGrp = cmds.group(em=True, name="{0}_ribbonGeo_GRP".format(name))
        bindJntGrp = cmds.group(em=True, name="{0}_ribbonBindJnt_GRP".format(name))
        ctrlJntGrp = cmds.group(em=True, name="{0}_ribbonCtrlJnt_GRP".format(name))
        ctrlGrp = cmds.group(em=True, name="{0}_ribbonCtrl_GRP".format(name))
        mainCtrlGrp = cmds.group(em=True, name="{0}_ribbonMainCtrl_GRP".format(name))
        follicleGrp = cmds.group(em=True, name="{0}_ribbonFollicle_GRP".format(name))
        cmds.parent(follicleGrp, noXformGrp)
        cmds.parent(mainCtrlGrp, ctrlGrp)
        cmds.parent(bindJntGrp, xformGrp)
        cmds.parent(ctrlJntGrp, xformGrp)
        cmds.parent(ctrlGrp, xformGrp)
        cmds.parent(geoGrp, noXformGrp)
        cmds.parent(xformGrp, topGrp)
        cmds.parent(noXformGrp, topGrp)

        for fol in self.folList:
            cmds.parent(fol[0], follicleGrp)
            cmds.scaleConstraint(xformGrp, fol[0], mo=True)
        cmds.parent(self.bindJnts, bindJntGrp)
        cmds.parent(self.ctrlJnts, ctrlJntGrp)
        for ctrl in self.mainCtrls:
            grp = cmds.listRelatives(ctrl, p=True)[0]
            cmds.parent(grp, ctrlGrp)
        cmds.parent(self.geo, geoGrp)

    # do shit here
    #---------------- only in U
    #---------------- use a premade surface option, check that it's in U, swap if not (reverseSurface -d 3 -ch 1 -rpo 1 "nurbsPlane1"; )
    #---------------- option for simple added in (for arms, etc)

    # surf_tr = mc.rename(surf_tr, prefix + "ribbon_surface")
    # surf = mc.listRelatives(surf_tr, shapes=True)[0]

    # # freeze transformations and delete the surface history
    # mc.makeIdentity(surf_tr, t=True, r=True, s=True, apply=True)
    # mc.delete(surf_tr, ch=True)

    # # duplicate surface curves to determine the direction
    # u_curve = mc.duplicateCurve(surf_tr + ".v[.5]", local=True, ch=0)
    # v_curve = mc.duplicateCurve(surf_tr + ".u[.5]", local=True, ch=0)

    # # delete the history just in case
    # mc.delete(surf_tr, ch=True)

    # u_length = mc.arclen(u_curve)
    # v_length = mc.arclen(v_curve)

    # if u_length < v_length:
    #     mc.reverseSurface(surf_tr, d=3, ch=False, rpo=True)
    #     mc.reverseSurface(surf_tr, d=0, ch=False, rpo=True)

    # parameter = ".parameterU"
    # other_param = ".parameterV"

    # # correct u_curve after reversing to calculate the length
    # u_curve_corr = mc.duplicateCurve(surf_tr + ".v[.5]", local=True, ch=0)[0]

    # #############################################################################

    # # selected surface is periodic or open? (cylinder or a plane)
    # if mc.getAttr(surf + ".formU") == 2 or mc.getAttr(surf + ".formV") == 2:
    #     curve_type = "periodic"
    #     divider_for_ctrls = num_of_ctrls
    # elif mc.getAttr(surf + ".formU") == 0 or mc.getAttr(surf + ".formV") == 0:
    #     curve_type = "open"
    #     divider_for_ctrls = num_of_ctrls - 1
