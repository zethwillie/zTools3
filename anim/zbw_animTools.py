###########
#import zbw_anim tools, call with zbw_animTools.animTools()
###########

import maya.cmds as cmds
import random

#get frame range
def zbw_getFrameRange():
    """gets framerange in current scene and returns start and end frames"""
    #get timeslider range start
    startF = cmds.playbackOptions(query=True, min=True)
    endF = cmds.playbackOptions(query=True, max=True)
    return(startF, endF)

#step key all
def zbw_stepAll():
    sel = cmds.ls(sl=True)
    keyList = []
    keySet = set()
    allKeys = []
    #get timeslider range start
    startF = cmds.playbackOptions(query=True, min=True)
    #get end frame
    endF = cmds.playbackOptions(query=True, max=True)
    #get all the keyed frames
    for this in sel:
        keyList = cmds.keyframe(this, query=True, time=(startF,endF))
        for key in keyList:
            key = int(key)
            keySet.add(key)
    #print keyList
    keySet = set(keyList)
    for frame in keySet:
        allKeys.append(frame)

    allKeys.sort()
    allKeys.reverse()
    #print allKeys

    for object in sel:
        for thisKey in allKeys:
            cmds.currentTime(thisKey)
            cmds.setKeyframe(object, t=thisKey, ott="step")

#pull down anim from master
def zbw_pullDownAnim():
    #eventually pull these out to be two separate operations, grab controls, grab master
    #select controls to pull down (create a visible list to see these controls)
    controls =  cmds.ls(sl=True)
    controlSize = len(controls)

    #select master control
    master = controls[0]

    def zbw_getWSTranslate(obj):
        transT = cmds.xform(obj, query=True, t=True, ws=True) #gets translation from obj
        #currentFrame = cmds.currentTime(query=True) #gets current frame.
        return transT

    def zbw_getWSRotation(obj): #do I need to decompose matrix here? or create and discard locator with rot orders
        rotateT = cmds.xform(obj, query=True, ro=True, ws=True) #gets WS rotation from obj
        #rotateNew = [rotateT[0][0], rotateT[0][1], rotateT[0][2]]
        #currentFrame = int(cmds.currentTime(query=True)) #gets current frame.
        return rotateT

    #for each control selected grab the ws pos and rotation for each key, store these in a dictionary
    for i in range(1,controlSize):
        transKeys = {} #initialize dictionary for this control
        rotKeys = {}  #initialize dictionary for this control
        thisControl = controls[i]
        #create list of master control keys too (create set to contain keys
        #from master, translate,rotate)

        ###### loop here for each keyframe
        for nowKey in keyList:
            cmds.currentTime(nowKey)
            #at each key location, grab ws translation
            thisTrans = zbw_getWSTranslate(thisControl)
            transKeys[nowKey] = thisTrans
            #at each key location, grab ws rotation/orientation
            thisRot = zbw_getWSRotation(thisControl)
            rotKeys[nowKey] = thisRot
            ###### end loop

        #at each key location, apply the pos and rot
        for thisKey in keyList:
            cmds.setKey(thisControl, at='tx', t=thisKey, value=transKeys[thisKey[0]])

    #zero out master control

#change frame rate
def zbw_changeFrameRate():
    pass

#playblast tool
def zbw_playblast():
    pass
#hide all but geo, bckgrnd color, where to save, size, camera, etc
#more of a view/visibility thing with some playblast options added (revert back to previous view?) could have toggle now button AND "when PB" check box to set/reset view when PBing
 

#random anim shifting
def zbw_randomizeKeys():
    pass
#shift existing keys around in the timeline, either as all, or each key individually
#cmds.keyframe(edit=True,relative=True,timeChange=1,time=(10,20))

#add random values to your anim
def zbw_animNoise(*args):
    """
    based on obj selected and channels highlighted in the channel box, will create random noise based on the entered value. The noise will be keyed at the freq entered, with the possibility for THAT value to have some randomization also.
    """
    def zbw_animNoiseRange(*args):
        onOff=cmds.checkBoxGrp('zbw_animNoiseTimeOn', q=True, value1=True)
        if not onOff:
            cmds.floatFieldGrp('zbw_animNoiseFrameRange', e=True, en=1)
        else:
            cmds.floatFieldGrp('zbw_animNoiseFrameRange', e=True, en=0)

    def zbw_animNoiseRandom(*args):
        onOff=cmds.checkBoxGrp('zbw_animNoiseRandom', q=True, value1=True)
        if not onOff:
            cmds.intFieldGrp('zbw_animNoiseRandFreq', e=True, en=0)
        else:
            cmds.intFieldGrp('zbw_animNoiseRandFreq', e=True, en=1)

    def zbw_runAnimNoise(*args):
        channels = cmds.channelBox ('mainChannelBox', query=True,selectedMainAttributes=True)
        obj = []
        obj = cmds.ls(selection=True)
        #get frequency value
        freqRaw= cmds.intFieldGrp('zbw_animNoiseFreq', q=True, value=True)
        freq = freqRaw[0]
        #should freq value have randomness?
        randDo = cmds.checkBoxGrp('zbw_animNoiseRandom', q=True, value1=True)
        randFreq = cmds.intFieldGrp('zbw_animNoiseRandFreq', q=True, value1=True)
        addLow = cmds.floatFieldGrp('zbw_animNoiseAmp', q=True, value1=True )
        addHigh = cmds.floatFieldGrp('zbw_animNoiseAmp', q=True, value2=True )
        buffer = cmds.checkBoxGrp('zbw_animNoiseAvoid', q=True, value1=True)
        origVal = {}
        randVal = {}
        newVal = {}
        keyList = []

        #deal with range
        startF=0
        endF=0
        if (cmds.checkBoxGrp('zbw_animNoiseTimeOn', q=True, value1=True)):
            startF, endF = zbw_getFrameRange()
        else:
            startF = cmds.floatFieldGrp('zbw_animNoiseFrameRange', q=True, value1=True)
            endF = cmds.floatFieldGrp('zbw_animNoiseFrameRange', q=True, value2=True)

        #MAKE SURE TO SET AUTOKEY FOR ATTRS SELECTED?
        if (obj):
            for me in obj:
                #check that there are channels selected
                if (channels):
                    for this in channels:
        
                        #for each channel
                        channel = me + "." + this
                        print(me)
                        print(this)
                        print(freqRaw)
                        #clear the dictionary
                        
                        #CLEAR ALL LISTS, ETC? randval, existKey, temprandval, etc
                        
                        randVal.clear()
                        #this will create the dictionary of frames to key for rand values
                        x = startF
                        while (x < endF):
                            #if random freq box is checked, then create rand value. Add this, curr frm and freq from UI to get the next frame
                            if (randDo):
                                randFrame = random.randint((-randFreq),randFreq)
                                x = x + randFrame + freq
                            #if not random then add the curr frm to frequency from UI
                            else:
                                x = x + freq
                            print(x)
                            #FOR VALUE GIVE THE OPTION FOR WHAT TYPE OF RAND YOU WANT
                            #here create the random value for each frame defined above
                            addVal = float(random.uniform(addLow,addHigh))
                            #create the dictionary of random values for adding to the orig values
                            randVal[x] = addVal
                            keyList.append(x)
                        
                        sortKeyList = []
                        keySet = set(keyList)
                        for g in keySet:
                            sortKeyList.append(g)
                        
                        if (buffer):
                            #create existkey list from object
                            existKey = []
                            existKey = cmds.keyframe(me,at=this,q=True,time=(startF,endF))
                            ekLength = len(existKey)
                            for f in range(0, ekLength):
                                existKey[f] = int(existKey[f])
                            print(("existingKey: " + str(existKey)))
                            
                            #do a comparison. for each in existkey compare with all sortkeys
                            tempRandVal = randVal.copy()
        
                            for thisExistKey in existKey:
                                for thisRandKey in tempRandVal:
                                    distance = abs(thisRandKey-thisExistKey)
                                    if distance< freq:  
                                        #if randkey is close to existing key, pop that rand key
                                        del randVal[thisRandKey]                                
        
                        #for each value in the rand dict, evaluate the curve in question to get the current value and put that into a current value dictionary
                        for m in randVal:
                            origThis = cmds.keyframe(channel, at=this, query=True, time=(m,m), eval=True)
                            origVal[m] = origThis[0]
                        #for each value in the rand dict, add the current value to the rand value
                        print(("randVal = : " + str(randVal)))
                        print(("origVal = : " + str(origVal))) 
                        for j in randVal:
                            newVal[j] = randVal[j] + origVal[j]
                        #for each value in the rand dict, setKey to the current attr with the new value
                        print(("newVal = : " + str(newVal)))
                        for k in newVal:
                            cmds.setKeyframe(me, at=this, time=k, value=newVal[k])
                        #create options for random values to be calculated based on gauss, random, perlin, etc.
                else:
                    print("please select some channels from the channel box")
    def zbw_animNoiseUI():
        if (cmds.window('zbw_animNoiseUI', exists=True)):
            cmds.deleteUI('zbw_animNoiseUI', window=True)
            cmds.windowPref('zbw_animNoiseUI', remove=True)
        window=cmds.window('zbw_animNoiseUI', widthHeight=(350,200), title='zbw_animNoise')
        cmds.columnLayout(cal='center')
        cmds.floatFieldGrp('zbw_animNoiseAmp', cal=(1, 'left'), nf=2, label="set Min/Max Amp", value1=-1.0, value2=1.0)
        #add gradient?
        cmds.intFieldGrp('zbw_animNoiseFreq', cal=(1,'left'), label='frequency(frames)', value1=5)
        #checkbox for random freq
        cmds.checkBoxGrp('zbw_animNoiseRandom', cal=(1,'left'), cw=(1, 175),label='random frequency on', value1=0, cc=zbw_animNoiseRandom)
        cmds.intFieldGrp('zbw_animNoiseRandFreq', label='random freq (frames)', value1=1, en=0)
        #checkbox for avoid keys
        cmds.checkBoxGrp('zbw_animNoiseAvoid', cal=(1,'left'), cw=(1, 175),label='buffer existing keys (by freq)', value1=0)
        #radiobutton group for tangents
        #checkbox for timeline range
        cmds.checkBoxGrp('zbw_animNoiseTimeOn', cal=(1,'left'), cw=(1, 175),label='use timeline start/end', value1=1, cc=zbw_animNoiseRange)
        #floatFieldGrp for range
        cmds.floatFieldGrp('zbw_animNoiseFrameRange', nf=2, label='start/end frames', value1=1, value2=10, en=0)
        cmds.text("")
        cmds.button('zbw_animNoiseGo', label='add Random', width=75, command=zbw_runAnimNoise)
    
        cmds.showWindow(window)
    
    zbw_animNoiseUI()

#copy chunk of animation and plug it back into timeline

#offset anim based on selection order
def zbw_offsetAnim(*args):
    """creates offset from first obj sel to last based on the entered offset value"""
    def zbw_runOffsetAnim(*args):
        #get frame range!!!!!!
        #get selection, check that they are tranforms
        sel = cmds.ls(sl=True,type="transform")
        selSize = int(len(sel))
        #for each selection mult the index by the offset value
        for i in range(0,selSize):
            obj = sel[i]
            offsetRaw = cmds.intFieldGrp('zbw_offsetValue', q=True, v=True)
            offset = offsetRaw[0]
            multFactor = i * offset
            #shift the entire anim curve by the offset mult value
            cmds.keyframe(obj, edit=True,relative=True,timeChange=multFactor,time=(1,24))

    #create UI, get offset value, frame range or all anim
    if (cmds.window('zbw_offsetAnimUI', exists=True)):
        cmds.deleteUI('zbw_offsetAnimUI', window=True)
        cmds.windowPref('zbw_offsetAnimUI', remove=True)
    window=cmds.window('zbw_offsetAnimUI', widthHeight=(350,200), title='zbw_offsetAnim')
    cmds.columnLayout(cal='center')
    cmds.intFieldGrp('zbw_offsetValue', cal=(1,'left'), label='frequency(frames)', value1=5)
    #CREATE FRAME RANGE AREA (WHICH FRAMES ARE WE DOING?)
    #WHEN THAT HAPPENS, WHAT DO WE DO WITH THE FRAMES AFTER THAT? (PROBABLY NOTHING. . . LET USER WORRY ABOUT IT)
    #checkbox for random freq (to give a random amount to offset each object)
    #cmds.checkBoxGrp('zbw_animNoiseRandom', cal=(1,'left'), cw=(1, 175),label='random frequency on', value1=0, cc=zbw_animNoiseRandom)
    cmds.button('zbw_offsetAnimGo', label='offset!', width=75, command=zbw_runOffsetAnim)

    cmds.showWindow(window)

#clean up keys
def zbw_cleanKeys(*args):
    #try to find dead keyframes
    sel = cmds.ls(sl=True)

    #get timeslider range start
    frameRange=zbw_getFrameRange()
    startF = frameRange[0]
    endF = frameRange[1]

    # loop through objects
    for object in sel:
        keyedAttr = []
        # find which attr have keys on them
        keyedAttrRaw = cmds.keyframe(object, query=True, name=True)
        #now fix the "object_" part to "object."
        for oldAttr in keyedAttrRaw:
            newAttr = oldAttr.lstrip((object + "_"))
            keyedAttr.append(newAttr)
            # loop through attrs with keys
        for attr in keyedAttr:
            #loopNum = 0
            for a in range(0,1):
                keyList = []
                keyList = cmds.keyframe(object, query=True, at=attr,time=(startF, endF))
                if (keyList):
                    keySize = len(keyList)
                    if keySize < 3:
                        if keySize < 2:
                            #pass
                            print(("only one key for " + object + "." + attr))
                            print("cutting " + object + "." + attr)
                            currentVal = cmds.getAttr((object+"."+attr), time=keyList[0])
                            cmds.cutKey(object, at=attr, time=(keyList[0],keyList[0]), cl=True)
                            #cmds.setAttr(object, at=attr, time=(keyList[0]), cl=True)
                        else:
                            print("compare two keys for " + attr)
                            #check for keep start end options
                            firstKey = keyList[0]
                            secondKey = keyList[1]
                            firstVal = cmds.keyframe(object, at=attr, query=True, time=(firstKey,firstKey), eval=True)
                            secondVal = cmds.keyframe(object, at=attr, query=True, time=(secondKey,secondKey), eval=True)
                            #add a check in here for keep first keep last
                            if firstVal == secondVal:
                                print("cutting two keys for " + attr)
                                cmds.cutKey(object, at=attr, time=(firstKey,secondKey), cl=True)

                    else:
                        print("here we cycle through the comparisons for " + attr)

                        for i in range(1,keySize-1):
                            thisKey = keyList[i]
                            prevKey = keyList[i-1]
                            nextKey = keyList[i+1]
                            thisVal = cmds.keyframe(object, at=attr, query=True, time=(thisKey,thisKey), eval=True)
                            prevVal = cmds.keyframe(object, at=attr, query=True, time=(prevKey,prevKey), eval=True)
                            nextVal = cmds.keyframe(object, at=attr, query=True, time=(nextKey,nextKey), eval=True)
                            if (thisVal==prevVal) and (thisVal==nextVal):
                                cmds.cutKey(object, at=attr, time=(thisKey,thisKey), cl=True)
                else:
                    pass

#list of characters/subset of chars for selection
#create a list, button to select all, select some to create a subset list
#button will pull down list to select which list to look at, etc

#pull up animation from objs underneath
def zbw_pullUpAnim(*args):
    #dummy check for rotate orders. Is there a way to fix that easily if they have different rot orders?
    #check to make sure autokey is on? or use setKey for setting keys

    rotBuffer = {}
    transBuffer = {}

    def zbw_getFrameRange():
        startF = cmds.playbackOptions(query=True, min=True)
        endF = cmds.playbackOptions(query=True, max=True)
        return (startF, endF)

    def getRot(obj):
            rotateT = cmds.getAttr((obj+ ".rotate")) #gets WS rotation from bottom object
            rotateNew = [rotateT[0][0], rotateT[0][1], rotateT[0][2]]
            currentFrame = int(cmds.currentTime(query=True)) #gets current frame.
            rotBuffer[currentFrame] = rotateNew #adds the key:value for the frame:rotation

    def getTrans(obj):
            transT = cmds.xform(obj, query=True, t=True, ws=True) #gets translation from bottom obj
            currentFrame = cmds.currentTime(query=True) #gets current frame.
            transBuffer[currentFrame] = transT #adds the key:value for the frame:rotation

    sel = cmds.ls(sl=True)

    frames = zbw_getFrameRange()
    startF = frames[0]
    endF = frames[1]
    objSize = len(sel)
    topObj = sel[objSize-1]
    bottomObj = sel[0]
    #get key times for each object add those lists together, convert to set to get rid of dupes
    #for each object use clean list to eval to get value, put key, value combo into dictionary

    #initialize all keys list
    allKeys = []

    #create redundant list of frames for all objects (allKeys)
    for i in range(0, objSize):
        thisKeys = cmds.keyframe(sel[i], query=True, time=(startF,endF), attribute=('tx','ty','tz','rx','ry','rz'))
        allKeys = allKeys + thisKeys

    #turn allKeys into set to clean redundancies (keysSet)
    keysSet = set(allKeys)
    #turn set back into clean list (keyList)
    keyList=[]
    for key in keysSet:
        keyList.append(key)
    keyList.sort()

    #populate the dictionary with the key values
    #!!!!!!do this for EACH OBJECT in the chain? then the getRot bit would have to be getAttr for rotations, not xform, then rot order is issue!!!!!
    for thisKey in keyList:
        cmds.currentTime(thisKey)
        #get rot and translate data and put into rotBuffer and transBuffer, key:value
        getRot(sel[0])
        getTrans(sel[0])

    #go through keys of dictionary
    for key in keyList:
        objRot = rotBuffer[key]
        objTrans = transBuffer[key]
        cmds.currentTime(key)
        cmds.xform(topObj, ws=True, t=(objTrans[0], objTrans[1], objTrans[2])) #set keys for B on all the frames in keyBuffer to values in keyBuffer
        cmds.xform(topObj, r=True, ws=True, ro=(objRot[0], objRot[1], objRot[2]))

    #zero out the two other controls
    for j in range(0,(objSize-1)):
        #do this with keyframe command? so no need for loop
        cmds.keyframe(sel[j], edit=True, valueChange=0, at=('tx','ty','tz','rx','ry','rz'))
        #add the value to the master control (plus initial offset)

#retime animation based on scrubbing

#camAnim bake
def zbw_bakeCleanCam():
    #copies camera with connections and bakes that camera and breaks connections
    pass

#IKFK switcher generic
def zbw_ikfkMatching():
    pass
    #select FKjoints, then IK joints, then create two scripts and make shelf buttons

#copyAnim from a to b
def zbw_copyAnimRange():
    pass
    #copy anim from object a to b, either current frame values or frame range (get highlighted area from timeline?)
#     att = [ '.tx','.ty','.tz','.rx','.ry','.rz','.sx','.sy','.sz']
#     s = cmds.ls(sl=True) 
#     for v in range(len(att)):
#         cmds.setAttr((s[1] + att[v]),cmds.getAttr(s[0]+ att[v]))
    
#create GUI for all of these, one panel, then pull out panel for characters. . .
def animTools():
    #create simple button based GUI for now
    if (cmds.window('zbw_animToolsUI', exists=True)):
        cmds.deleteUI('zbw_animToolsUI', window=True)
        cmds.windowPref('zbw_animToolsUI', remove=True)
    window=cmds.window('zbw_animToolsUI', widthHeight=(350,200), title='zbw_animTools')
    cmds.columnLayout(cal='center')
    #cmds.intFieldGrp('zbw_offsetValue', cal=(1,'left'), label='frequency(frames)', value1=5)
    #CREATE FRAME RANGE AREA (WHICH FRAMES ARE WE DOING?)
    #WHEN THAT HAPPENS, WHAT DO WE DO WITH THE FRAMES AFTER THAT? (PROBABLY NOTHING. . . LET USER WORRY ABOUT IT)
    #checkbox for random freq
    #cmds.checkBoxGrp('zbw_animNoiseRandom', cal=(1,'left'), cw=(1, 175),label='random frequency on', value1=0, cc=zbw_animNoiseRandom)
    cmds.text('zbw_offsetAnim')
    cmds.button('zbw_offsetAnimButton', label='offsetAnim', width=75, command=zbw_offsetAnim)
    cmds.text('zbw_pullDownAnimButton')
    cmds.button('zbw_pullDownAnim', label='pullDownAnim', width=75, command=zbw_pullDownAnim)
    cmds.text('zbw_pullUpAnimButton')
    cmds.button('zbw_pullUpAnimButton', label='pullUpAnim', width=75, command=zbw_pullUpAnim)
    cmds.text('zbw_randomizeKeys')
    cmds.button('zbw_randomizeKeysButton', label='randomizeKeys', width=75, command=zbw_randomizeKeys)
    cmds.text('zbw_animNoise')
    cmds.button('zbw_animNoiseButton', label='animNoise', width=75, command=zbw_animNoise)
    cmds.text('zbw_playblast')
    cmds.button('zbw_playblastButton', label='playblast', width=75, command=zbw_playblast)
    cmds.text('zbw_stepAll')
    cmds.button('zbw_stepAllButton', label='stepAll', width=75, command=zbw_stepAll)
    cmds.text('zbw_cleanKeys')
    cmds.button('zbw_cleanKeysButton', label='cleanKeys', width=75, command=zbw_stepAll)
    cmds.text('zbw_changeFrameRate')
    cmds.button('zbw_changeFrameRate', label='frameRate', width=75, command=zbw_changeFrameRate)

    cmds.showWindow(window)
    #XXX_selection_XXX
    #character selection list?
    #select nodes with animation?

    #XXX_workflow_XXX
    #pull down anim from Master
    #randomize keys
    #random noise
    #anim offsetting
    #zbw_playblast
    #zbw_copyAnimRange
    #animRetiming

    #XXX_3rdParty_XXX
    #tween machine
    #abx picker?
    #abx smartkeys?
    #poselibrary
    
    #XXX_blocking/polishing tools_XXX
    #blocking step keys
    #clean up dead keys
    
    #XXX_miscellaneous_XXX
    #pull up anim from obj under
    #fkIK matching script
    #zbw_changeFrameRate
    #zbw_bakeCleanCam
