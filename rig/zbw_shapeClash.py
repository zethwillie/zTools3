"""zbw_shapeClash"""

import maya.cmds as cmds
import zTools.resources.zbw_clash as clash
import importlib
importlib.reload(clash)

# get all shape node clashes
def shapeClash():
    clashes = clash.detectShapeClashes(fixClashes = False)
    print(("in Shape Clashes:", clashes))
# put them all into a list

# button to fix the shape nodes for each clash incident