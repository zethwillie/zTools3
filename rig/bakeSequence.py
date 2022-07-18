import maya.cmds as cmds

"""bake sequence of objects"""

step = 1
frameStart = 1
frameEnd = 10
shortName = sel

#this or timeSlider
frameRange = [frameStart,frameEnd]

sel = cmds.ls(sl=True)[0]

##catch this
shortName = sel

for frame in range(frameRange[0], frameRange[1], step):
    cmds.currentTime(frame, edit=True)
    cmds.duplicate(sel, n="%s%d"%(shortName, frame))