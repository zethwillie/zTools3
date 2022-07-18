"""
connecting multiple things to a message attr
"""
sel = cmds.ls(sl=True)[0]

cmds.addAttr("null1", at="message", sn = "myAttr", multi=True)

cmds.connectAttr("locator1.message", 'null1.myAttr[0]')
cmds.connectAttr("locator2.message", 'null1.myAttr[1]')


print((cmds.listConnections("null1.myAttr")))