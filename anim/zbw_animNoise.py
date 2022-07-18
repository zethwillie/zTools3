import maya.cmds as cmds
import random
from functools import partial

# TODO----------------make sure that it only evaluates on the attrs we want (store the values and add them without having to go the frames for each)
# TODO ----------- option to do each channel independently

widgets = {}

def animNoiseUI():
    if cmds.window('animNoiseWin', exists=True):
        cmds.deleteUI('animNoiseWin', window=True)
        cmds.windowPref('animNoiseWin', remove=True)

    widgets["win"] = cmds.window('animNoiseWin', widthHeight=(300,200), title='zbw_animNoise')
    widgets["CLO"] = cmds.columnLayout(cal='center')
    widgets["ampFFG"] = cmds.floatFieldGrp(cal=(1, 'left'), nf=2, l="set Min/Max Amp", v1=-1.0, v2=1.0)
    #add gradient?
    widgets["freqIFG"] = cmds.intFieldGrp(cal=(1,'left'), l='frequency(frames)', v1=5)
    widgets["randFreqOnCBG"] = cmds.checkBoxGrp(cal=(1,'left'), cw=(1, 175),l='random frequency on', v1=0, cc=animNoiseRandom)
    widgets["randFreqFFG"] = cmds.floatFieldGrp(l='random freq (frames)', v1=1, en=0)
    widgets["avoidCBG"] = cmds.checkBoxGrp(cal=(1,'left'), cw=(1, 175),l='buffer existing keys (by freq)', v1=0)
    widgets["rangeRBG"] = cmds.radioButtonGrp(nrb=2,l="Frame Range:", l1="Timeslider", l2="Frame Range", sl=1, cw=[(1,100),(2,75),(3,75)],cc=enableFrameRange)
    widgets["frameRangeIFG"] = cmds.intFieldGrp(nf=2, l='start/end frames', v1=1, v2=10, en=0)

    widgets["goBut"] = cmds.button(l='Add Noise', width=300, h=30, bgc=(.6,.8,.6), command=addNoise)

    cmds.showWindow(widgets["win"])


def enableFrameRange(*args):
    onOff=cmds.checkBoxGrp(widgets["rangeRBG"], q=True, v1=True)
    if not onOff:
        cmds.floatFieldGrp(widgets["frameRangeFFG"], e=True, en=1)
    else:
        cmds.floatFieldGrp(widgets["frameRangeFFG"], e=True, en=0)

def animNoiseRandom(*args):
    onOff=cmds.checkBoxGrp(widgets["randFreqOnCBG"], q=True, v1=True)
    if not onOff:
        cmds.floatFieldGrp(widgets["randFreqFFG"], e=True, en=0)
    else:
        cmds.floatFieldGrp(widgets["randFreqFFG"], e=True, en=1)
###MAKE ALL THIS A FUNCTION!!!!
#figure out GUI
#DONE,BUT COULD BE MORE GENERAL -figure out how to grab attrs from channel box (in Mel use "global string $gchannelBox")
def getRange(*args):
    sl = cmds.radioButtonGrp(widgets["rangeRBG"], q=True, sl=True)
    if sl==1:
        startF = cmds.playbackOptions (query=True, minTime=True)
        endF = cmds.playbackOptions (query=True, maxTime=True)
    else:
        startF = cmds.intFieldGrp(widgets["frameRangeIFG"], q=True, v1=True)
        endF = cmds.intFieldGrp(widgets["frameRangeIFG"], q=True, v2=True)
    return(int(startF), int(endF))

def addNoise(*args):
    objects = cmds.ls(sl=True)
    if objects:
        channels = cmds.channelBox("mainChannelBox", q=True, sma=True)
        #hist = cmds.channelBox("mainChannelBox", q=True, sha=True)
        if channels:
            #get frequency value
            freq = cmds.intFieldGrp(widgets["freqIFG"], q=True, v=True)[0]
            #should freq value have randomness?
            randFreq = cmds.checkBoxGrp(widgets["randFreqOnCBG"], q=True, v1=True )
            addLow = cmds.floatFieldGrp(widgets["ampFFG"], q=True, v1=True )
            addHigh = cmds.floatFieldGrp(widgets["ampFFG"], q=True, v2=True )
            origVal = {}
            keyList = []

            #deal with range
            startF, endF = getRange()

            #MAKE SURE TO SET AUTOKEY FOR ATTRS SELECTED
#TO-DO----------------make sure the attr exists on th obj (in case of multiselection)

# create a list of currentkeys on attr (what to do if there is no anim curve on that object)
# create a list of keys that are the random values (use freq stuff to figure out that list)
#create dict for each rand key with the orig value of the attr
# for each randKey: is it a key already?(don't change), is it too close to an existing key?(don't add)
#else. . . if we are creating a key. . . take teh orig value and add the rand value to it, then set a key for the attr at that frame with that newValue
#could make a graph control to multiply. . . have to figure out what value to mult each rand frame by based on the graph
#channelbox . . . can I get inputs and other shit to work here or will the obj name be a problem?



            #CHANGE BELOW TO STEP THROUGH BY FRAME/RAND AND KEY VALUES BY (RAND FUNC)
            for obj in objects:
                for this in channels:
                    channel = "%s.%s"%(obj, this)

#TO-DO----------------check if there are keys in keylist
                    #create keyList of frames for keys on this attr
                    keyList = cmds.keyframe(obj, query=True, time=(startF,endF),attribute=this)
                    if not keyList:
                        keyList = [startF, endF]
                    #to create dictionary of orig values to access in a sec
#TO-DO----------------here I can just eval at time to get the value?
                    for i in range(startF,endF,freq):
                        cmds.currentTime(i,edit=True)
                        origVal[i] = cmds.getAttr(channel)

                    #to create rand number and add that to orig value and setKey
                    for i in range(startF,endF,freq):
                        cmds.currentTime(i, edit=True)
                        addVal = float(random.uniform(addLow,addHigh))
                        oldVal = origVal[i]
                        newVal = (oldVal + addVal)
                        disCheck = []
                        #check that the new keys aren't going to be within freq of existing keys
#TO-DO----------------make the "protect" function an option, not mandatory
                        for key in keyList:
                            nowF = cmds.currentTime(query=True)
                            distance = abs(key-i)
                            if distance<=freq:
                                disCheck.append(distance)
                        if disCheck:
                            pass
                        else:
                            cmds.setAttr(channel, newVal)
        else:
            cmds.warning("You need to select some channels in the channel box!")
    else:
        cmds.warning("You haven't selected any objects!")

def animNoise():
    animNoiseUI()
