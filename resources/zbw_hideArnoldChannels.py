########################
#file: hideArnoldChannels.py
#Author: zeth willie
#Contact: zethwillie@gmail.com, www.williework.blogspot.com
#Date Modified: 
#To Use: type in python window  "import zTools.zbw_hideArnoldChannels as zhac; zhac.hideArnoldChannels()"
#Notes/Descriptions: based on stephen mann's script (MEL), http://smann3d.blogspot.com/2016/10/hiding-arnold-channels-on-shapes.html
########################

import maya.cmds as cmds

def toggle_arnold_attrs(*args):
    """
    will hide the arnold attributes from the channelbox
    """
    crvAttrs = None
    meshAttrs = ["aiOverrideLightLinking", "aiOverrideShaders", "aiUseFrameExtension", "aiFrameNumber", "aiUseSubFrame", "aiFrameOffset", "aiOverrideNodes", "aiOverrideReceiveShadows", "aiOverrideDoubleSided", "aiOverrideSelfShadows", "aiOverrideOpaque", "aiOverrideMatte"]
    # oldMesh = [".emitSpecular", ".emitDiffuse", ".intensity", ".scb", ".scg", ".scr", ".ai_color_temperature", ".ai_use_color_temperature", ".ai_volume", ".ai_indirect", ".ai_sss", ".ai_specular", ".ai_diffuse", ".ai_exposure", ".ai_shadow_density"]
    # oldCrv = [".ai_curve_shaderb", ".ai_curve_shaderg", ".ai_curve_shaderr", ".srate", ".cwdth", ".rcurve"]
    # octaneAttrs = [".octGeoType", ".octGenVis", ".octCamVis", ".octShVis", ".octLayerId", ".octBakGrId", ".octRandomSeed", ".octRPassColorR", ".octRPassColorG", ".octRPassColorB", ".octConstTopology", ".octMergeUnweldedVert", ".octSubdLevel", ".octSubdSharpness", ".octSubdBoundInterp", ".octSubdSceme"]
    # u'aiOverrideLightLinking', u'aiOverrideShaders', u'aiUseFrameExtension', u'aiFrameNumber', u'aiUseSubFrame', u'aiFrameOffset', u'aiOverrideNodes', u'aiNamespace', u'aiOverrideReceiveShadows', u'aiOverrideDoubleSided', u'aiOverrideSelfShadows', u'aiOverrideOpaque', u'aiOverrideMatte', u'aiFilters', u'aiTranslator'   
    meshes = cmds.ls(type="mesh")
    if meshes:
        for m in meshes:
            for attr in meshAttrs:
                cmds.setAttr("{0}.{1}".format(m, attr), keyable=True, channelBox=False)
    
# # use this to check attrs    
# sel = cmds.ls(sl=True)[0]
# shp = cmds.listRelatives(sel, s=True)[0]
# print cmds.attributeQuery("aiOverrideLightLinking", node=shp, k=True)


    # crvs = cmds.ls(type="nurbsCurve")
    # if crvs:
    #     for c in crvs:
    #         for attr in crvAttrs:
    #             cmds.setAttr("{0}.{1}".format(c, attr), keyable=False, channelBox=False)