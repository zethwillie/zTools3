import maya.cmds as cmds

cards = cmds.ls(sl=True)

mainSkinGrp = cmds.group(em=True, name="skinned_cards")
mainTweakGrp = cmds.group(em=True, name="tweak_cards")

# skin
for card in cards:
    print(("++++++\n" + card))
    skinGrp = None
    tweakGrp = None
    # get parent, if grp version doesn't exist make it nad parent to correct grp
    par = cmds.listRelatives(card, p=True)[0]
    if par:
        skinPar = "skin_{0}".format(par)
        tweakPar = "tweak_{0}".format(par)
        if not cmds.objExists(skinPar):
            skinGrp = cmds.group(em=True, name=skinPar)
            cmds.parent(skinGrp, mainSkinGrp)
        else:
            skinGrp = skinPar
        if not cmds.objExists(tweakPar):
            tweakGrp = cmds.group(em=True, name=tweakPar)
            cmds.parent(tweakGrp, mainTweakGrp)
        else:
            tweakGrp = tweakPar
            
    skin = cmds.duplicate(card, name="{0}_skinTGT".format(card))[0]
    cmds.parent(skin, skinGrp)
    cmds.select(cl=True)
    
    tweak = cmds.duplicate(card, name="{0}_tweakTGT".format(card))[0]
    cmds.parent(tweak, tweakGrp)
    
    bsName = "{0}_BS".format(card)

    # blend shape both that into orig card
    bs = cmds.blendShape([tweak, skin, card], name=bsName)
    # turn on both bs's
    cmds.blendShape(bs, e=True, w=[(0, 1),(1, 1)])
   
