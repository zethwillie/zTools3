######## clean up shaders and textures, both for UI AND headless maya sessions
import maya.cmds as cmds

#delete unused shaders
materials = cmds.ls(materials=True)
materials.remove("lambert1")
materials.remove("particleCloud1")
# print materials
for m in materials:
    sg = []
    outs = list(set(cmds.listConnections(m, destination =True)))
    for out in outs:
        type = cmds.nodeType(out)
        if type == "shadingEngine":
            sg.append(out)

    if sg:
        if not cmds.listConnections("{}.dagSetMembers".format(sg[-1])):
            cmds.delete(m)

#delete unused textures
textures = cmds.ls(textures=True)
tTypeList = ["blinn", "lambert", "phong", "aiStandard", "phongE", "surfaceShader"]
for t in textures:
    x = cmds.listConnections(t, destination=True)
    if cmds.nodeType(x[-1]) not in tTypeList:
        cmds.delete(t)

#delete unused utility nodes