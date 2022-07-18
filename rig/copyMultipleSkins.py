    # get source skin(s)
if True: # delete this

    meshes = []
    for skin in cmds.listConnections(joints, type='skinCluster'):
        if skin:
            shape = cmds.skinCluster(skin, query=True, geometry=True)
            meshTransform = cmds.listRelatives(shape, parent=True)[0]
            if meshTransform not in meshes:
                meshes.append(meshTransform)

    oldSkin = cmds.polyUniteSkinned(meshes,ch=0)
    newSkin = False
    #add skin to imported object
    if skinObj != False:
        newSkin = cmds.skinCluster(joints, skinObj)

    if newSkin != False:
        # run copy skin weights
        cmds.copySkinWeights(ss=oldSkin[1], ds=newSkin[0])