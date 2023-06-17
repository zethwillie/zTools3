import maya.cmds as mc

def replace_maya_nodes_with_arnold(replace_files=True, replace_mults=True, delete=False):
    """
    search for maya native nodes and replace with arnold nodes and swap connections
    currently does file nodes (to aiImage), multiplyDivide nodes (to aimult, etc)
    ARGS:
        replace_files(bool): should we replace file nodes
        replace_mults(bool): should we replace multiply divide nodes
        delete(bool): should we delete nodes once we've replaced them
    """
    old_nodes = [] # list of any nodes we've replaced
    new_nodes = [] # list of any new nodes we've made
    if replace_files:
        # files
        files = mc.ls(type="file")
        for f in files:
            ai_image = replace_file_with_aiImage(f, delete)
            if ai_image:
                old_nodes.append(f)
                new_nodes.append(ai_image)

    if replace_mults:
        mults = mc.ls(type="multiplyDivide")
        for m in mults:
            ai_math = replace_multdiv_with_ai_nodes(m, delete)
            if ai_math:
                old_nodes.append(m)
                new_nodes.append(ai_math)


def replace_file_with_aiImage(node, delete=False):
    """
    replace given maya file node (texture) with an aiImage node. Will get outputs and reconnect them
    ARGS:
        node (str): name of maya file node
        delete(bool): should we delete orig node after connecting new one
    """
    if not mc.objectType(node) == "file":
        return()
    tx = mc.getAttr(f"{node}.fileTextureName")
    colorSpace = mc.getAttr(f"{node}.colorSpace") # if fail on setting, set up a default
    alphaIsLum = mc.getAttr(f"{node}.alphaIsLuminance")
    # get conns
    outColorConns = mc.listConnections(f"{node}.outColor", d=True, s=False, plugs=True)
    outAlphaConns = mc.listConnections(f"{node}.outAlpha", d=True, s=False, plugs=True)

    # create aiFile
    aiFile = mc.shadingNode("aiImage", asTexture=True, name=f"ai_{node}")
    # set values
    mc.setAttr(f"{aiFile}.filename", tx, type="string")
    mc.setAttr(f"{aiFile}.colorSpace", colorSpace, type="string")
    # set connections
    if outColorConns:
        for colorConn in outColorConns:
            mc.connectAttr(f"{aiFile}.outColor", colorConn, force=True)
    if outAlphaConns:
        for alphaConn in outAlphaConns:
            mc.connectAttr(f"{aiFile}.outAlpha", alphaConn, force=True)
    if delete:
        mc.delete(node)
    return(aiFile)


def replace_multdiv_with_ai_nodes(node, delete=False):
    """
    replace given maya multiplyDivide node with an aiMultiply or aiDivide node. Will get outputs and reconnect them
    ARGS:
        node (str): name of maya native node
        delete(bool): should we delete orig node after connecting new one
    """
    if not mc.objectType(node) == "multiplyDivide":
        return()

    # get values
    input1Val = mc.getAttr(f"{node}.input1")[0]
    input2Val = mc.getAttr(f"{node}.input2")[0]
    operation = mc.getAttr(f"{node}.operation")

    # get connections
    in1Conns = mc.listConnections(f"{node}.input1", d=False, s=True, plugs=True)
    in2Conns = mc.listConnections(f"{node}.input2", d=False, s=True, plugs=True)
    outConns = mc.listConnections(f"{node}.output", d=True, s=False, plugs=True)

    #create node
    if operation == 1:
        mathNode = mc.shadingNode("aiMultiply", asUtility=True, name=f"ai_{node}")
    elif operation == 2:
        mathNode = mc.shadingNode("aiDivide", asUtility=True, name=f"ai_{node}")
    else:
        return()
    # set values

    mc.setAttr(f"{mathNode}.input1", input1Val[0], input1Val[1], input1Val[2])
    mc.setAttr(f"{mathNode}.input2", input2Val[0], input2Val[1], input2Val[2])
    # set connections
    if in1Conns:
        for in1Conn in in1Conns:
            mc.connectAttr(in1Conn, f"{mathNode}.input1", force=True)
    if in2Conns:
        for in2Conn in in2Conns:
            mc.connectAttr(in2Conn, f"{mathNode}.input2", force=True)
    if outConns:
        for outConn in outConns:
            mc.connectAttr(f"{mathNode}.outColor", outConn, force=True)
    if delete:
        mc.delete(node)
    return(mathNode)
