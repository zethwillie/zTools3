import maya.cmds as cmds

#get selections
#first object is main object
obj = cmds.ls(sl=True)[0]
#print obj

#all rest are the cubes
stencils = cmds.ls(sl=True)[1:]
#print cubes

newObjs = []
count = 0

for stencil in stencils:
    #dupe obj as objDupe
    newObj = cmds.duplicate(obj)
    #put obj dupe in list
    newObjs.append(newObj)
    #bool with the object selections (stencil then obj)
    #polyBoolOp -op 3 -ch 1 -useThresholds 1 -preserveColor 0 pstencil2 pSphere1;
    cmds.polyBoolOp(stencil, newObj, op=3, n="BooledObj_%s"%count)
    #hide stencil
    cmds.setAttr("%s.v"%stencil, 0)
    
    count += 1

    #delete history on the newObjs
	# Deal with transferring the pivot point of cubes to new pieces of geo

    #create an empty group, name it "newObj_Grp"
    #parent the newObjs into the group
    #hide the orig object


# Deal with UV mapping from original to new


##############
#finding cubes based on bounding box
import maya.cmds as cmds
import math

#get obj scale
sel = cmds.ls(sl = True)[0]
shape = cmds.listRelatives(sel, shapes=True)[0]

bbInfo = cmds.xform(sel, q=True, bb=True) #xmin, ymin, zmin, xmax, ymax, zmax

#print(bbInfo)

bbWidth = bbInfo[3]-bbInfo[0]
bbHeight = bbInfo[4]-bbInfo[1]
bbDepth = bbInfo[5]-bbInfo[2]

bbCenter = (bbWidth/2, bbHeight/2, bbDepth/2)

#select number of cubes (for now we'll go with x_width)
cubesX = 3 #this is weird, what dimension are we talking about if bb is not a cube? 
cubeWidth = bbWidth/cubesX

cubesY = int(math.ceil(bbHeight/cubeWidth))
cubesZ = int(math.ceil(bbDepth/cubeWidth))

#find num of cubes
numCubes = cubesX * cubesY * cubesZ

#come up with a list of cube locations? How to do this with Math? Not necessarily starting in center (if not odd num)

#get num of cubes in direction, including remainder. Then div remainder in half and place cubes starting with this offset? ?


######################
#moving objects randomly around the origin (front left moves front left, etc)
import maya.cmds as cmds
import random

objs = cmds.ls(sl=True)

for obj in objs:
    
# here we should find the point of reference, either an object or choose a point or choose origin

    #find which coordinate frame 
    objX = cmds.xform(obj, ws=True, q=True, rp=True)[0]
    objY = cmds.xform(obj, ws=True, q=True, rp=True)[1]
    objZ = cmds.xform(obj, ws=True, q=True, rp=True)[2]
    #print [objX, objY, objZ]

# here we should compare the pivots from last section to the reference point we chose to get the quadrants
    
#here we generate random numbers. The multiplier should be user selectable
    randX = random.random() * 10
    randY = random.random() * 10
    randZ = random.random() * 10
    
    #here we make these random values positive or negative values depending on the quadrant    
    if objX <= 0:
        randX = randX * -1
    if objY <= 0:
        randY = randY * -1
    if objZ <= 0:
        randZ = randZ * -1                
        
    #print [randX, randY, randZ]
    cmds.xform(obj, relative=True, t=(randX, randY, randZ)) 
        
        
#More cool shit - make a grid of cubes and drive their y position by the color of the image (U,V) on some texture
import maya.cmds as cmds

#cubes
cubes=[]
grp = cmds.group(empty=True, n="cube_GRP")

for x in range(1,11):
    for z in range(1,11):
        U = 1-(x*0.009)
        V = 1-(z*0.009)
        yVal = cmds.colorAtPoint("checker1", u=U, v=V)[0]
        
        thisCube = cmds.polyCube(n="cube_%d"%(x*z))[0]
        cmds.move(x-5.5,yVal,z-5.5, thisCube, a=True)
        cmds.addAttr(at="float", sn="U", k=True)
        cmds.addAttr(at="float", sn="V", k=True)
        cubes.append(thisCube)
        
        print(yVal)
        
for cube in cubes:
    cmds.parent(cube, grp)

#Plane
#create a checker pattern on this
#myPlane = cmds.polyPlane(n="imageBase_plane", axis=(0,1,0), w=10, h=10, sx=20, sy=20)  

#####################
#really should write a plugin that catches RGBA values of a specified surface at a specified UV value. Then hook those values into whatever
# http://forums.cgsociety.org/archive/index.php?t-866713.html


    
    
    