import os
import sys
from functools import partial

import maya.cmds as cmds


class ImportHair():
    def __init__(self, asset_namespace, proj_path):
        self.proj_path = proj_path

        # import hair
        hair_namespace = self.import_hair_file(asset_namespace)
        # connect
        if hair_namespace:
            result = self.connect_scalp_meshes(hair_namespace, asset_namespace)

    def import_hair_file(self, asset_namespace):
        """
        assumes a hair component is published. ..
        Args:
            char(string): the base character we're grabbing the hair from (the char folder name in openpipe)
            asset_namespace (string): the namespace for the character in the scene (eg anim_char_rig1. . . )
        """
        # hair master folder would be self.proj_path + "lib" + char, prop, env, etc + asset + "components/hair/version"
# TODO ---------- in the ui, separate into frames for each type of reference (based on pathing?)
        CHAR_BASE_FOLDER = os.path.join(self.proj_path, "lib", "char").replace('/', '\\')
        PROP_BASE_FOLDER = os.path.join(self.proj_path, "lib", "prop").replace("/", "\\")
        # need to derive character name from namespace - assumes compon_name_task format
        char = asset_namespace.split("_")[1]

# TODO ------------ look in the char folder first, then the prop folder? How can we get this sooner than here?
        charFolders = [x for x in os.listdir(CHAR_BASE_FOLDER) if os.path.isdir(os.path.join(CHAR_BASE_FOLDER, x))]

        charHairFolder = os.path.join(CHAR_BASE_FOLDER, char, "components", "hair")
        if not os.path.exists(charHairFolder):
            cmds.warning("Can't find the hair folder under: ", charHairFolder)
            return()

        # get latest master(vesion) if exists
        if not os.path.exists(os.path.join(charHairFolder, "version")):
            cmds.warning("Can't find a master (version) folder for the hair component:", charHairFolder)
            return()
        versionFolder = os.path.join(charHairFolder, "version")
        masterFiles = [x for x in os.listdir(versionFolder) if os.path.join(versionFolder, x) and x.endswith(".mb")]
        if not masterFiles:
            cmds.warning("Can't find a master (version) file for the hair:", versionFolder)
            return()

        # get version (currently just getting the lastest)
        masterFiles.sort()
        latest_master = masterFiles[-1]
        master_path = os.path.join(versionFolder, latest_master)

        # create the namespace we need (hair_char_000)
        namespace_init = "hair_{0}_0".format(asset_namespace)
        hair_namespace = self.make_valid_namespace(namespace_init)

        # import the file into the scene
        cmds.file(master_path, r=True, namespace=hair_namespace)

        print "---- Imported hair file: ", master_path
        return(hair_namespace)

    def connect_scalp_meshes(self, hair_namespace, asset_namespace):
        print "---- connecting meshes for hair: {0}".format(hair_namespace)
        char = asset_namespace.split("_")[1]
        # make sure that the groups exist: namespace:grp_scalps, namespace:char_grp_hairSystems
        if not cmds.namespace(exists=hair_namespace):
            cmds.warning("Can't find the hair namespace. Skipping!: ", hair_namespace)
            return()
        if not cmds.namespace(exists=asset_namespace):
            cmds.warning("Can't find the character namespace. Skipping!: ", asset_namespace)
            return()

        # in character namespace, make sure we have scalps grp
        char_scalp_grp = "{0}:{1}_grp_scalps".format(asset_namespace, char)
        if not cmds.objExists(char_scalp_grp):
            cmds.warning("Can't find scalp group in the character ref: ", char_scalp_grp)
            return()

        hair_scalp_grp = "{0}:grp_scalps".format(hair_namespace)
        if not cmds.objExists(hair_scalp_grp):
            cmds.warning("Can't find scalp group in the hair ref: ", hair_scalp_grp)
            return()

        # for hair_scalp in hair_scalps:
        hair_scalps = cmds.listRelatives(hair_scalp_grp, type="transform", c=True)
        char_scalps = cmds.listRelatives(char_scalp_grp, type="transform", c=True)

        # for scalp in hair_scalps:
        for hair_scalp in hair_scalps:
            # get vis of rig hair
            short_hair = hair_scalp.rpartition(":")[-1]
            char_scalp = "{0}:{1}_{2}".format(asset_namespace, char, short_hair)
            scalp_vis = cmds.getAttr(char_scalp + ".v")

            # get hair transform and set vis to char_scalp
            hair_transform = get_hair_xform(hair_scalp)
            if hair_transform:
                cmds.setAttr("{0}.v".format(hair_transform), scalp_vis)

            if not cmds.objExists(char_scalp):
                cmds.warning("Couldnt find a match for hair scalp: {0} in character scalps: {1}. Skipping!").format(hair_scalp, char_scalp)
                continue

            # get shapes for each
            hair_shape = cmds.listRelatives(hair_scalp, s=True, type="mesh")[0]
            char_shape = [x for x in cmds.listRelatives(char_scalp, s=True, type="mesh") if "Orig" not in x][0]
            print "CONNECTING: ", hair_shape, " --> ", char_shape
            # connect out mesh of char scalp to in mesh of hair scalp
            cmds.connectAttr("{0}.outMesh".format(char_shape), "{0}.inMesh".format(hair_shape))

        return(True)

    def make_valid_namespace(self, namespace):
        # return(namespace)

        # get last digit(s) and increment them. . .
        if not cmds.namespace(exists=namespace):
            return(namespace)
        incr = int(namespace.rpartition("_")[-1])
        new_namespace = "{0}_{1}".format(namespace.rpartition("_")[0], str(incr + 1))
        return(self.make_valid_namespace(new_namespace))
        # could try cmds.namespace(validateName=namespace). . .


class ImportHairUI(object):
    def __init__(self):
        # TODO ---------- add ability to version up/down hair imports
        self.proj_path = cmds.optionVar(q='op_currProjectPath')
        self.win_name = 'hairImportWin'

        self.width = 300
        self.height = 300

        self.create_win()
        self.populate_uis()

    def populate_uis(self, *args):
        self.collect_ref_info()
        self.clear_all()
        self.populate_nonhair_list()
        self.populate_hair_list()

    def collect_ref_info(self, *args):
        self.ref_dict = self.get_referenced_namespaces()
        self.hair_ref_dict = self.ref_dict["hair"]
        self.nonhair_ref_dict = self.ref_dict["nonhair"]

    def create_win(self):
        if cmds.window(self.win_name, ex=1):
            cmds.deleteUI(self.win_name)
        self.win = cmds.window(self.win_name, t='Xgen Hair Importer')
        self.tabLO = cmds.tabLayout(w=self.width)

        self.nonhair_clo = cmds.columnLayout("IMPORT HAIR")
# TODO ---- make this a inactive text field
        self.proj_tf = cmds.textFieldGrp(l="PROJECT: ", tx="PROJECT: {0}".format(self.proj_path), en=False, cal=[(1, "left"), (2, "left")], cw=[(1, 50), (2, 240)])
        cmds.text(l="Refs to potentially apply hair to:")
        self.nonhair_clo = cmds.columnLayout()
        self.refs_tsl = cmds.textScrollList(allowMultiSelection=True, h=200, w=self.width - 10, ann="Click to select references to apply hair to (assumes a published hair scene). Ctrl or shift click to select multiple\nHair visibility will be based on vis settings of character/rig scalps.")

        exec_but = cmds.button(l="Execute Hair Import/Connect for Selected", h=40, w=self.width - 10, bgc=(.5, .7, .5), c=self.execute_hair_import)
        cmds.separator(h=5)
        ref_refresh = cmds.button(l="REFRESH", h=20, w=self.width - 10, bgc=(.5, .5, 5), c=self.populate_uis)

        cmds.setParent(self.tabLO)
        hair_clo = cmds.columnLayout("DELETE HAIR")
        hair_txt = cmds.text(l="Hair references:")
        self.hair_clo = cmds.columnLayout()
        self.hair_tsl = cmds.textScrollList(allowMultiSelection=True, h=200, w=self.width - 10)
        delete_but = cmds.button(l="Execute Hair Deletion", h=40, w=self.width - 10, bgc=(.7, .5, .5), c=self.delete_hair_imports)
        cmds.separator(h=5)
        hair_refresh = cmds.button(l="REFRESH", h=20, w=self.width - 10, bgc=(.5, .5, 5), c=self.populate_uis)

        cmds.setParent(self.tabLO)
        vis_clo = cmds.columnLayout("HAIR VISIBILITY")
        vis_txt = cmds.text(l="Hair references:")
        self.vis_clo = cmds.columnLayout()
        self.vis_tsl = cmds.textScrollList(h=100, w=self.width - 10, sc=self.visibility_control)
        cmds.separator(h=5)
        self.vis_lo = cmds.columnLayout()

        cmds.showWindow(self.win)
        cmds.window(self.win, e=1, w=self.width, h=self.height)

    def clear_all(self, *args):
        cmds.textScrollList(self.refs_tsl, e=True, ra=True)
        cmds.textScrollList(self.hair_tsl, e=True, ra=True)

    def populate_nonhair_list(self, *args):
        cmds.textScrollList(self.refs_tsl, e=True, ra=True)
        namespaces = self.nonhair_ref_dict.keys()
        namespaces.sort()
        n = 1
        for ns in namespaces:
            # is hair for this rig already imported
            used = False
            related_hair = "hair_{0}_".format(ns)
            for hair in self.hair_ref_dict.keys():
                if hair.startswith(related_hair):
                    used = True
                    break
            if used:
                ns = ns + " +++"
                cmds.textScrollList(self.refs_tsl, e=True, a=ns, lineFont=[n, "boldLabelFont"])
            else:
                cmds.textScrollList(self.refs_tsl, e=True, a=ns, lineFont=[n, "plainLabelFont"])
            n += 1

    def populate_hair_list(self, *args):
        cmds.textScrollList(self.hair_tsl, e=True, ra=True)
        cmds.textScrollList(self.vis_tsl, e=True, ra=True)
        namespaces = self.hair_ref_dict.keys()
        namespaces.sort()
        for ns in namespaces:
            cmds.textScrollList(self.hair_tsl, e=True, a=ns)
            cmds.textScrollList(self.vis_tsl, e=True, a=ns)

    def execute_hair_import(self, *args):
        selected = cmds.textScrollList(self.refs_tsl, q=True, si=True)
        for namespace in selected:
            if namespace.endswith("+++"):
                result = confirm_window(title="Hair Exists", message="A hair import already exists onthis reference.\nCreate another hair on this reference?", confirm_name="Import Hair", parent=self.win)
                if result == "Cancel":
                    print "Additional hair import for {0} canceled!".format(namespace.strip(" +++"))
                    continue
                else:
                    namespace = namespace.strip(" +++")
            hair = ImportHair(namespace, self.proj_path)
        self.populate_uis()

    def delete_hair_imports(self, *args):
        selected = cmds.textScrollList(self.hair_tsl, q=True, si=True)
        for namespace in selected:
            refNode = namespace + "RN"
            filepath = cmds.referenceQuery(refNode, filename=True)  # get the ACTUAL maya file path (with braces if appropriate)
            cmds.file(filepath, removeReference=True, mergeNamespaceWithRoot=True)

            if cmds.namespace(exists=namespace):
                if not cmds.namespaceInfo(namespace, listNamespace=True):
                    cmds.namespace(removeNamespace=namespace)
        self.populate_uis()

    def get_referenced_namespaces(self):
        refs = cmds.file(q=True, r=True)
        hair_dict = {}
        nonhair_dict = {}
        ref_dict = {}
        for ref in refs:
            ref_node = cmds.referenceQuery(ref, rfn=True)
            namespace = cmds.referenceQuery(ref_node, namespace=True).lstrip(':')
            filename = cmds.referenceQuery(ref_node, filename=True)
            if namespace.startswith("hair_"):
                hair_dict[namespace] = filename
            else:
                nonhair_dict[namespace] = filename
        ref_dict["hair"] = hair_dict
        ref_dict["nonhair"] = nonhair_dict

        return(ref_dict)

    def visibility_control(self):
        namespace = cmds.textScrollList(self.vis_tsl, q=True, si=True)[0]
        parents = get_hair_description_from_namespace(namespace)

        # If layout exists, delete it
        if cmds.columnLayout(self.vis_lo, exists=True):
            cmds.deleteUI(self.vis_lo)
        # create the layout, parent to vis_clo
        self.vis_lo = cmds.columnLayout(parent=self.vis_clo)
        for p in parents:
            parent_xform = "{0}:{1}".format(namespace, p)
            init_vis = cmds.getAttr("{0}:{1}.v".format(namespace, p))
            cb = cmds.checkBox(l=p, v=init_vis)
            cmds.checkBox(cb, e=True, cc=partial(self.set_hair_vis, parent_xform, cb))

    def set_hair_vis(self, xform, ui, *args):
        value = cmds.checkBox(ui, q=True, v=True)
        cmds.setAttr(xform + ".v", value)


def get_hair_description_from_namespace(namespace, *args):
    descriptions = cmds.ls("{0}:*".format(namespace), type="xgmSplineDescription")
    parents = [cmds.listRelatives(x, p=True)[0].partition(":")[-1] for x in descriptions]
    return(parents)


def get_hair_xform(hair_scalp):
    """
    given a hair import scalp, return the xgmSplineDescription's transform to hide the vis
    """
    hair_scalp_shp = cmds.listRelatives(hair_scalp, s=True)[0]
    conns = cmds.listConnections(hair_scalp_shp, p=False, d=True)
    xg_base = [x for x in conns if cmds.objectType(x) == "xgmSplineBase"]
    if xg_base:
        base = xg_base[0]
    hair_descr_shp = return_description(base)
    if hair_descr_shp:
        hair_description = cmds.listRelatives(hair_descr_shp, p=True)
        if hair_description:
            return(hair_description[0])
    else:
        return(None)


def return_description(base):
    """
    given an xgmSplineBase object (from get_hair_xform), returns the hair description. This should be recursively walking down the pipes to the node from the base obj
    """
    base_conns = cmds.listConnections(base, c=False, s=False, d=True, shapes=True)
    if base_conns:
        for conn in base_conns:
            if cmds.objectType(conn) == "xgmSplineDescription":
                return(conn)
            result = return_descr(conn)
            if result:
                return(result)


def confirm_window(title="Confirm Dialog", message="Confirm?", confirm_name="Yes", parent=None, *args):
    result = cmds.confirmDialog(title=title, message=message, button=[confirm_name, "Cancel"], cancelButton="Cancel", defaultButton="Cancel", dismissString="Cancel", parent=parent)
    return(result)
