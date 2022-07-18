import maya.cmds as cmds

# select blend shape node(s) then select new (wrapped?) geo to be duped
# blend shapes should be all be for the selected geo

# to run (in a python window):
# import zbw_dupeBlends
# zbw_dupeBlends.dupe_blend_setup()

def dupe_blends(bss, geo, *args):
    """
    bss: blendshape nodes
    geo: geo to duplicate    
    """
    for bs in bss:
        tgts = cmds.listAttr(bs + ".w", m=True)
        print("duplicating blendshapes: " + str(tgts))
        for x in range(len(tgts)):
            for t in tgts:
                cmds.setAttr(bs+"."+t, 0)
            cmds.setAttr("{0}.{1}".format(bs, tgts[x]), 1)
            name = geo+"_"+tgts[x]
            cmds.duplicate(geo, name=tgts[x])
            cmds.setAttr("{0}.{1}".format(bs, tgts[x]), 0)   


def dupeBlends(*args):
    sel = cmds.ls(sl=True)
    geo = sel[-1]
    bss = sel[:-1]    
    dupe_blends(bss, geo)