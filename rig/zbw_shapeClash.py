"""zbw_shapeClash"""

import maya.cmds as cmds
import zTools3.resources.zbw_clash as clash


# get all shape node clashes
def shapeClash():
    clashes = clash.detectShapeClashes(fixClashes = False)
    print(("in Shape Clashes:", clashes))
# put them all into a list

# button to fix the shape nodes for each clash incident