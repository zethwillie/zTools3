import maya.cmds as cmds

########this works but need to make it generic for s, t, or u being the direction along the path
#todo: autoguess option to get highest val and make it the main axis?

def latticeFixDo(*args):
    """grab lattice and need a ctrl named 'ctrl'"""
    lat  = cmds.ls(sl=True)[0]
    latShp = cmds.listRelatives(lat, s=True)[0]
    sDivs = cmds.getAttr("%s.sDivisions"%latShp) 
    tDivs =  cmds.getAttr("%s.tDivisions"%latShp)
    uDivs = cmds.getAttr("%s.uDivisions"%latShp)

    numPerSpan = sDivs * uDivs

    #set Direction
    main = "s"
    secondary = "t"
    tertiary = "u"

    if main=="s":
        mainDir = sDivs
    elif main=="u":
        mainDir = uDivs
    elif main=="t":
        mainDir = tDivs

    if secondary == "t":
        secDir = tDivs
    elif secondary == "s":
        secDir = sDivs
    elif secondary == "u":
        secDir = uDivs

    if tertiary == "t":
        terDir = tDivs
    elif tertiary == "s":
        terDir = sDivs
    elif tertiary == "u":
        terDir = uDivs

    clsList = []
    grpList = []
    grp2List = []
    upClsList = []
    ctrlList = []
    addList = []

    for x in range(mainDir):
        pts = []
        for y in range(secDir):
            for z in range(terDir):
                if main == "s" and secondary == "t": 
                    pt = "%s.pt[%s][%s][%s]"%(lat, x, y, z)
                if main == "s" and secondary == "u": 
                    pt = "%s.pt[%s][%s][%s]"%(lat, x, z, y)
                if main == "t" and secondary == "s": 
                    pt = "%s.pt[%s][%s][%s]"%(lat, y, x, z)                                
                if main == "t" and secondary == "u": 
                    pt = "%s.pt[%s][%s][%s]"%(lat, y, z, x)
                if main == "u" and secondary == "s": 
                    pt = "%s.pt[%s][%s][%s]"%(lat, z, x, y)
                if main == "u" and secondary == "t": 
                    pt = "%s.pt[%s][%s][%s]"%(lat, z, y, x)                                                
                pts.append(pt)
        clstr = cmds.cluster(pts, n="Clstr%s"%x)
        clsList.append(clstr[1])
        pos = cmds.xform(clstr[1], ws=True, q=True, rp=True)
       
        ctrl = cmds.duplicate("ctrl", n="ctrl%s"%x)[0]
        ctrlList.append(ctrl)
        cmds.addAttr(ctrl, ln="fix",k=True, at="float" )
        
        grp = cmds.group(em=True, n="%sGRP"%clstr[0])
        grpList.append(grp)
            
        add = cmds.shadingNode("addDoubleLinear", asUtility=True, n="%sAdd"%clstr[0])
        addList.append(add)
        cmds.connectAttr("%s.fix"%ctrl, "%s.input1"%add)
        cmds.connectAttr("%s.output"%add, "%s.ry"%grp)
        
        grp2 = cmds.group(em=True, n="%sHierGRP"%clstr[0])
        grp2List.append(grp2)
        cmds.parent(ctrl, grp)
        cmds.parent(grp, grp2)
        #transform grp here
        cmds.xform(grp2, ws=True, t=pos)
        upPts = []
        for a in range(secDir):
            upPts.append("%s.pt[0][%s][%s]"%(lat, a, x))
        upClstr = cmds.cluster(upPts, n="upClster%s"%x)
        upClsList.append(upClstr[1])
        ###########  here need to get the cross product and orient the cluster (group) to the pts . . .


    for x in range(len(clsList)-1, 0, -1):
        aim = cmds.aimConstraint(clsList[x], grp2List[x-1],aim=(0,1,0), u=(1,0,0), wut="object", wuo=upClsList[x])
        cmds.delete(aim)
        cmds.delete(upClsList[x])
        cmds.parent(clsList[x], ctrlList[x])
        cmds.parent(grp2List[x], grp2List[x-1])
        cmds.connectAttr("%s.ry"%grpList[x-1],"%s.input2"%addList[x])
        cmds.setAttr("%s.v"%clsList[x], 0)

def latticeFix(*args):
    latticeFixDo()