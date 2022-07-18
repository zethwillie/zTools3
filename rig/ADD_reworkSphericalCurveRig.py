"""
UI:
collect info:
    get rig name
    get center obj
    get up obj
    get num of controls

    get curves (top and/or bottom?)
        get edge loops to create curve OR just get curves
        get label for each curve (top, low)
        create curve based on edge loops (ep curve?)

pass info to RIG

RIG:
    create base rig
        for each curve (hiCrv):
            get ep 
            base joint at center
            loc at each ep
            base joint at loc
            parent end joint to base joint
            connect ep pos to loc
            loc to loc group
            aim constrain base joint to loc

            duplicate curve - rebuild it to number of controls -1. This is ctrlCrv

            make a bindjoint for each ep in this dupe curve, position there
            group freeze these (these are the bind joint for the final curve)

            create wiredef from ctrlCrv to hiCrv
            bind ctrlCrv to bindJnts

            create controls for the bind joints

            setup xform connections between ctrls and joints (not scale)


    setup smart close for the two curves
        
        duplicate a control curve to get blink crv
        create blendshape between two ctrlCrvs on this to position in the middle (reverse setup)
        
        duplicate both hirez curves as targets (call them hirezBlink)
        set blink crv to the top and wire deform the tophirezBlink to the blinkCrv
        reverse and do to the lowhirezBlink
        set wire scale to 0 on both of these wire

        create blend from [tophirezBlink] to the  [tophiCrv], so tophiCrv is driven by the blink
        make sure the order is correct, blendshape is end of chain
        do same for bottom crvs


For mouth can we do this with ribbons instead of with curves? to get twist in there? 





def smart_close(*args):
    name = cmds.textFieldGrp(widgets["nameTFG"], q=True, tx=True)
    upSuf = cmds.textFieldGrp(widgets["upNameTFG"], q=True, tx=True)
    dwnSuf = cmds.textFieldGrp(widgets["downNameTFG"], q=True, tx=True)
    topMidCtrl = ctrlsUp[len(ctrlsUp)/2]
    downMidCtrl = ctrlsUp[len(ctrlsDwn)/2]
    
    if len(lowResCurves)==2 and len(highResCurves)==2:
        tmpCloseLow = cmds.duplicate(lowResCurves[0], n="{0}_closeLowTmpCrv".format(name))[0]
        cmds.parent(tmpCloseLow, w=True)

        tmpLowBS = cmds.blendShape(lowResCurves[0], lowResCurves[1], tmpCloseLow)[0]
        tmpLowUpAttr = "{0}.{1}".format(tmpLowBS, lowResCurves[0])
        tmpLowDwnAttr = "{0}.{1}".format(tmpLowBS, lowResCurves[1])
        cmds.setAttr(tmpLowUpAttr, 0.5)
        cmds.setAttr(tmpLowDwnAttr, 0.5)
        closeLow = cmds.duplicate(tmpCloseLow, n="{0}_CLOSE_LOW_CRV".format(name))[0]
        cmds.delete([tmpCloseLow, tmpLowBS])
        lowBS = cmds.blendShape(lowResCurves[0], lowResCurves[1], closeLow)[0]
        lowUpAttr = "{0}.{1}".format(lowBS, lowResCurves[0])
        lowDwnAttr = "{0}.{1}".format(lowBS, lowResCurves[1])

#---------------- connect up down into reverse setup that drives lowclosecrv to go up/down
        cmds.addAttr(topMidCtrl, ln="__xtraAttrs__", )

        cmds.setAttr(lowUpAttr, 1)
        cmds.setAttr(lowDwnAttr, 0)
        closeUpHigh = cmds.duplicate(highResCurves[0], n="{0}_HI_{1}_CLOSE_CRV".format(name, upSuf.upper() ))[0]
        cmds.parent(closeUpHigh, w=True)
        upHighWire = cmds.wire(closeUpHigh, en=1, gw=True, ce=0, li=0, w=closeLow, name = "{0}_CLS_UP_WIRE".format(name))[0]
        wireUpBaseCrv = "{0}BaseWire".format(closeLow)
        cmds.setAttr("{0}.scale[0]".format(upHighWire), 0)
#---------------- set up blend shape on high res curve (drive high res with wire driven curve)
#---------------- set up the center ctrl to drive this BS

        cmds.setAttr(lowUpAttr, 0)
        cmds.setAttr(lowDwnAttr, 1)
        closeDwnHigh = cmds.duplicate(highResCurves[1], n="{0}_HI_{1}_CLOSE_CRV".format(name, dwnSuf.upper() ))[0]
        cmds.parent(closeDwnHigh, w=True)
        dwnHighWire = cmds.wire(closeDwnHigh, en=1, gw=True, ce=0, li=0, w=closeLow, name = "{0}_CLS_DWN_WIRE".format(name))[0]
        wireDwnBase = "{0}BaseWire".format(closeLow)
        cmds.setAttr("{0}.scale[0]".format(dwnHighWire), 0)
#---------------- set up blend shape on high res curve (drive h





"""