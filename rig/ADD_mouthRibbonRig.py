# mouth ribbon Rig

import maya.cmds as cmds
import zTools3.rig.zbw_rig as rig

"""
grab the edge loops on top/bottom to create curve to create ribbons

basically need to rewrite ribbon setup? Do we though?

create ribbon for top mouth
create ribbon for bottom mouth

connect the controlers at the corners, etc. 
Is there some way to constrain these final inbetween joints to some mouth shape in the skull (like eyes around center of eye)

create mid ribbon. . . 
this is blend between both top adn bottom. 

This need to be blended somehow to top and bottom so close can go from top side or bottom side

create copy of top and bottom for the BIND joints. These copies get blended from top/bottom to mid

then connect all the cv's (by two's separated by 10) of the ribbons to the input weight attrs of the blend shapes (top/bottom to mid blend). COnnect these up with a ramp attribute so that we can go top/bottom from corner to mid left/right. . . lip zipper

"""

