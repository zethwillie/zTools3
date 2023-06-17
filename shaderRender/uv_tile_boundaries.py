import maya.OpenMaya as om
import maya.cmds as cmds

from functools import reduce
import math

def check_uv_borders(geo, buffer=0.000):
    geo_dict = process_geo(geo, buffer)
    output_dict = {}
    for geo in geo_dict.keys():
        for uvset in geo_dict[geo].keys():
            for shell in geo_dict[geo][uvset]:
                if geo_dict[geo][uvset][shell]:
                    output_dict[geo] = {uvset:{shell:{}}}
                    for border in geo_dict[geo][uvset][shell].keys():
                        output_dict[geo][uvset][shell][border] = geo_dict[geo][uvset][shell][border]
    return(output_dict)


def process_geo(geo, buffer):
    all_geo_dict = {}
    all_geo_dict[geo] = {}
    all_uv_sets = get_uv_shell_lists(geo)[0]
    for sets_dict in all_uv_sets.keys():
        all_geo_dict[geo][sets_dict] = {}
        for shell in all_uv_sets[sets_dict].keys():
            all_geo_dict[geo][sets_dict][shell] = {}
            minu = reduce(lambda a,b: a if a[0] < b[0] else b, all_uv_sets[sets_dict][shell])[0]
            minv = reduce(lambda a,b: a if a[1] < b[1] else b, all_uv_sets[sets_dict][shell])[1]
            maxu = reduce(lambda a,b: a if a[1] > b[1] else b, all_uv_sets[sets_dict][shell])[0]
            maxv = reduce(lambda a,b: a if a[1] > b[1] else b, all_uv_sets[sets_dict][shell])[1]

            tile_min_u = math.floor(minu - buffer)
            tile_max_u = math.ceil(maxu + buffer)
            tile_min_v = math.floor(minv - buffer)
            tile_max_v = math.ceil(maxv + buffer)

            if ((tile_max_u - tile_min_u) > 1) or (minu < 0):
                all_geo_dict[geo][sets_dict][shell]["MIN-U"] = minu
                all_geo_dict[geo][sets_dict][shell]["MAX-U"] = maxu
                all_geo_dict[geo][sets_dict][shell]["TILE"] = [tile_max_u, tile_max_v]

            if ((tile_max_v - tile_min_v) > 1) or (minv < 0):
                all_geo_dict[geo][sets_dict][shell]["MIN-V"] = minv
                all_geo_dict[geo][sets_dict][shell]["MAX-V"] = maxv
                all_geo_dict[geo][sets_dict][shell]["TILE"] = [tile_max_u, tile_max_v]

    return(all_geo_dict)


def get_uv_shell_lists(name):
    selList = om.MSelectionList()
    selList.add(name)
    selListIter = om.MItSelectionList(selList, om.MFn.kMesh)
    pathToShape = om.MDagPath()
    selListIter.getDagPath(pathToShape)
    meshNode = pathToShape.fullPathName()
    uvSets = cmds.polyUVSet(meshNode, query=True, allUVSets =True)
    allSets = []
    for uvset in uvSets:
        shapeFn = om.MFnMesh(pathToShape)
        shells = om.MScriptUtil()
        shells.createFromInt(0)
        # shellsPtr = shells.asUintPtr()
        nbUvShells = shells.asUintPtr()

        uArray = om.MFloatArray()   #array for U coords
        vArray = om.MFloatArray()   #array for V coords
        uvShellIds = om.MIntArray() #The container for the uv shell Ids

        shapeFn.getUVs(uArray, vArray)
        shapeFn.getUvShellsIds(uvShellIds, nbUvShells, uvset)

        # shellCount = shells.getUint(shellsPtr)
        shells = {}
        for i, n in enumerate(uvShellIds):
            if n in shells:
                shells[n].append([uArray[i],vArray[i]])
            else:
                shells[n] = [[uArray[i],vArray[i]]]
        allSets.append({uvset: shells})
    return allSets

