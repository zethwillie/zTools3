import maya.cmds as cmds
"""
looks in the current scene and removes namespaces
Return:
    list: namespaces that have been cleaned up
"""
def remove_namespaces(*args):

    defaults = ['UI', 'shared']

    def num_children(ns): #function to used as a sort key
        return ns.count(':')

    namespaces = [ns for ns in cmds.namespaceInfo(lon=True, r=True) if ns not in defaults]
    namespaces.sort(key=num_children, reverse=True) # reverse the list
    print(("Namespaces: ", namespaces))

    cleaned = []
    for ns in namespaces:
        try:
            #get contents of namespace and move to root namespace
            cmds.namespace(mv=[ns, ":"], force=True)
            cmds.namespace(rm=ns)
            cleaned.append(ns)
        except RuntimeError as e:
            # namespace isn't empty, so you might not want to kill it?
            cmds.warning("Had an issue deleting namespace: {0}. Skipping!".format(ns))
            print(e)
    
    return(cleaned)