import maya.cmds as cmds
import zTools3.rig.zbw_rig as rig
import importlib
importlib.reload(rig)


class CreateProxyGeo(object):
    def __init__(self):
        self.bindJnts = []
        self.geo = []
        self.create_proxy_UI()

    def create_proxy_UI(self, *args):
        if cmds.window("proxyWin", exists=True):
            cmds.deleteUI("proxyWin")

        self.win = cmds.window("proxyWin", w=300, s=False)
        cmds.columnLayout()

        cmds.text(l="Select your bind joints and type of proxy geo, then create")
        cmds.separator(h=10)
        self.typeRBG = cmds.radioButtonGrp(l="Geo Type:", nrb=2, la2=["Cylinder", "Cube"], sl=1, cl3=["left", "left", "left"], cw3=[60, 75, 75])
        self.axisRBG = cmds.radioButtonGrp(l="Joint Axis:", nrb=3, la3=["x", "y", "z"], sl=1, cl4=["left", "left", "left", "left"], cw4=[65, 50, 50, 50])
        self.pivotRBG = cmds.radioButtonGrp(l="Pivot Place:", nrb=2, la2=["Center", "Base"], sl=1, cl3=["left", "left", "left"], cw3=[60, 75, 75])
        self.scaleFFG = cmds.floatFieldGrp(l="Scale: ", v1=1.0, cal=[[1, "left"], [2, "left"]], cw=[[1, 50], [2, 100]])
        cmds.separator(h=10)
        cmds.button(l="Create Proxy Geo", w=300, h=50, bgc=[.5, .7, .5], c=self.gather_proxy_info)
        cmds.separator(h=10)
        cmds.button(l="Bind and Combine Proxy Geo", w=300, h=50, bgc=[.7, .5, .5], c=self.gather_bind_info)

        cmds.showWindow(self.win)
        cmds.window(self.win, e=True, wh=[1, 1], rtf=True)

    def gather_proxy_info(self, *args):
        # get jnts
        self.bindJnts = cmds.ls(sl=True, type="joint")

        if not self.bindJnts:
            cmds.warning("you need select the joints to create geo for!")
            return()
        geoType = cmds.radioButtonGrp(self.typeRBG, q=True, sl=True)
        axis = cmds.radioButtonGrp(self.axisRBG, q=True, sl=True)
        pivot = cmds.radioButtonGrp(self.pivotRBG, q=True, sl=True)

        # convert to correct args
        if geoType == 1:
            geo = "cylinder"
        if geoType == 2:
            geo = "cube"

        if axis == 1:
            ax = [1, 0, 0]
        if axis == 2:
            ax = [0, 1, 0]
        if axis == 3:
            ax = [0, 0, 1]

        if pivot == 1:
            piv = "center"
        if pivot == 2:
            piv = "base"

        scale = cmds.floatFieldGrp(self.scaleFFG, q=True, v1=True)
        self.create_proxy_geo(self.bindJnts, geo, ax, piv, scale)

    def create_proxy_geo(self, jnts=[], geoType="cylinder", axis=[1, 0, 0], pivot="base", scale=1.0, *args):
        self.geo = rig.create_proxy_geo(jnts, geoType, axis, pivot, scale)

    def gather_bind_info(self, *args):
        rig.bind_combine_proxy_geo(self.bindJnts, self.geo)
