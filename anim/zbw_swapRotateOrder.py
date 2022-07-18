import maya.cmds as cmds
objA = ""
objB = ""
rotBuffer = {} #empty dictionary for frame:tuple of rotates
transBuffer = {}

def getRot():
    rotateT = cmds.getAttr(objB + ".rotate") #gets rotation from objB
    currentFrame = cmds.currentTime(query=True) #gets current frame.
    rotBuffer[currentFrame] = rotateT[0] #adds the key:value for the frame:rotation

def getTrans():
    transT = cmds.getAttr(objB + ".translate") #gets translation from objB
    currentFrame = cmds.currentTime(query=True) #gets current frame.
    transBuffer[currentFrame] = transT[0] #adds the key:value for the frame:rotation

def zbw_swapRotateOrder():

    #find frame range from slider
    startF = cmds.playbackOptions (query=True, minTime=True)
    endF = cmds.playbackOptions (query=True, maxTime=True)
    
    objs = cmds.ls (selection=True)
    #dummy check for two objects!    
    objA = objs[0]
    objB = objs[1]
    
    #get list of keys to use
    keysAtFull = cmds.keyframe (objA, query=True, time=(startF,endF), attribute=('tx','ty','tz','rx','ry','rz'))
    keysSet = set(keysAtFull)    
    keyList=[]
    for key in keysSet:
        keyList.append(key)
    keyList.sort()
    #print keyList
    
    for thisKey in keyList: #populate the dictionary with the key values
        cmds.currentTime(thisKey) #set currentTime to the value
        cmds.pointConstraint(objA, objB, name="pointConst")#pointConstriain B to A
        cmds.orientConstraint(objA, objB, name="orientConst")#orientConstan B to A
        getRot() #getData() for B and puts it in keyBuffer
        getTrans() #gets tranlslation data for same
        cmds.delete('pointConst','orientConst') # delete the constaints on B
    
    #since I can't add the keys while I"m constraining, do it now from dictionary	
    for newKey in keyList:
        objRot = rotBuffer[newKey]
        objTrans = transBuffer[newKey]
        cmds.setKeyframe( objB, t=newKey,at='tx', v=objTrans[0]) #set keys for B on all the frames in keyBuffer to values in keyBuffer
        cmds.setKeyframe( objB,t=newKey,at='ty', v=objTrans[1])
        cmds.setKeyframe( objB,t=newKey,at='tz', v=objTrans[2])
        cmds.setKeyframe( objB,t=newKey,at='rx', v=objRot[0])
        cmds.setKeyframe( objB,t=newKey,at='ry', v=objRot[1])
        cmds.setKeyframe( objB,t=newKey,at='rz', v=objRot[2])
    
    cmds.filterCurve((objB+'_rotateX'), (objB+'_rotateY'), (objB+'_rotateZ' ))	#run Euler filter on curves for rotation? 

