import maya.cmds as cmds
import zTools3.rig.zbw_rig as rig
from functools import partial


#---------------- clear fields button
#---------------- check and delete follow attrs if they exists (warn first)

widgets = {}
def follow_constraints_UI():
    if cmds.window("followCreatorWin", exists = True):
        cmds.deleteUI("followCreatorWin")

    w = 500
    h = 275
    widgets["win"] = cmds.window("followCreatorWin", w=w, h=h)
    widgets["mainCLO"] = cmds.columnLayout(w=w, h=h)
    widgets["mainForm"] = cmds.formLayout(w=w, h=h)

    widgets["tgtTFBG"] = cmds.textFieldButtonGrp(l="Base Cnstr Obj: ", w=300, bl="<<<", cal=[(1, "left"), (2,"left"), (3,"left")], cw=[(1, 80), (2, 180), (3, 20)])

    widgets["tgtCTRLTFBG"] = cmds.textFieldButtonGrp(l="Base Ctrl: ", w=300, bl="<<<", cal=[(1, "left"), (2,"left"), (3,"left")], cw=[(1, 80), (2, 180), (3, 20)])

    cmds.textFieldButtonGrp(widgets["tgtTFBG"], e=True, bc=partial(add_object_to_field, widgets["tgtTFBG"]))

    cmds.textFieldButtonGrp(widgets["tgtCTRLTFBG"], e=True, bc=partial(add_object_to_field, widgets["tgtCTRLTFBG"]))


    widgets["name1TFG"] = cmds.textFieldGrp(l="Attr 1 Name: ", w=200, cal=[(1, "left"), (2,"left")], cw=[(1, 70), (2, 110)])
    widgets["obj1TFBG"] = cmds.textFieldButtonGrp(l="Obj 1 Name: ", w=300,  bl="<<<", cal=[(1, "left"), (2,"left"), (3,"left")], cw=[(1, 70), (2, 180), (3, 20)])
    cmds.textFieldButtonGrp(widgets["obj1TFBG"], e=True, bc=partial(add_object_to_field, widgets["obj1TFBG"]))
    widgets["name2TFG"] = cmds.textFieldGrp(l="Attr 2 Name: ", w=200, cal=[(1, "left"), (2,"left")], cw=[(1, 70), (2, 110)])
    widgets["obj2TFBG"] = cmds.textFieldButtonGrp(l="Obj 1 Name: ", w=300, bl="<<<", cal=[(1, "left"), (2,"left"), (3,"left")], cw=[(1, 70), (2, 180), (3, 20)])
    cmds.textFieldButtonGrp(widgets["obj2TFBG"], e=True, bc=partial(add_object_to_field, widgets["obj2TFBG"]))    
    widgets["name3TFG"] = cmds.textFieldGrp(l="Attr 3 Name: ", w=200, cal=[(1, "left"), (2,"left")], cw=[(1, 70), (2, 110)])
    widgets["obj3TFBG"] = cmds.textFieldButtonGrp(l="Obj 1 Name: ", w=300, bl="<<<", cal=[(1, "left"), (2,"left"), (3,"left")], cw=[(1, 70), (2, 180), (3, 20)])
    cmds.textFieldButtonGrp(widgets["obj3TFBG"], e=True, bc=partial(add_object_to_field, widgets["obj3TFBG"]))          
    widgets["name4TFG"] = cmds.textFieldGrp(l="Attr 4 Name: ", w=200, cal=[(1, "left"), (2,"left")], cw=[(1, 70), (2, 110)])
    widgets["obj4TFBG"] = cmds.textFieldButtonGrp(l="Obj 1 Name: ", w=300, bl="<<<", cal=[(1, "left"), (2,"left"), (3,"left")], cw=[(1, 70), (2, 180), (3, 20)])
    cmds.textFieldButtonGrp(widgets["obj4TFBG"], e=True, bc=partial(add_object_to_field, widgets["obj4TFBG"]))        
    widgets["name5TFG"] = cmds.textFieldGrp(l="Attr 5 Name: ", w=200, cal=[(1, "left"), (2,"left")], cw=[(1, 70), (2, 110)])
    widgets["obj5TFBG"] = cmds.textFieldButtonGrp(l="Obj 1 Name: ", w=300, bl="<<<", cal=[(1, "left"), (2,"left"), (3,"left")], cw=[(1, 70), (2, 180), (3, 20)])
    cmds.textFieldButtonGrp(widgets["obj5TFBG"], e=True, bc=partial(add_object_to_field, widgets["obj5TFBG"]))

    widgets["buttonPar"] = cmds.button(l="Create Parent Constrs", w=200, h=40, bgc=(.5, .8, .5), c=partial(gather_info, "parent"))
    widgets["buttonOri"] = cmds.button(l="Create Orient Constrs", w=200, h=40, bgc=(.5, .8, .5), c=partial(gather_info, "orient"))

    cmds.formLayout(widgets["mainForm"], e=True, af=[
        (widgets["tgtTFBG"], "left", 100),
        (widgets["tgtTFBG"], "top", 10),
        (widgets["tgtCTRLTFBG"], "left", 100),
        (widgets["tgtCTRLTFBG"], "top", 35),
        (widgets["name1TFG"], "left", 5),
        (widgets["name1TFG"], "top", 75),
        (widgets["obj1TFBG"], "left", 205),
        (widgets["obj1TFBG"], "top", 75),
        (widgets["name2TFG"], "left", 5),
        (widgets["name2TFG"], "top", 100),
        (widgets["obj2TFBG"], "left", 205),
        (widgets["obj2TFBG"], "top", 100),
        (widgets["name3TFG"], "left", 5),
        (widgets["name3TFG"], "top", 125),
        (widgets["obj3TFBG"], "left", 205),
        (widgets["obj3TFBG"], "top", 125),
        (widgets["name4TFG"], "left", 5),
        (widgets["name4TFG"], "top", 150),
        (widgets["obj4TFBG"], "left", 205),
        (widgets["obj4TFBG"], "top", 150),
        (widgets["name5TFG"], "left", 5),
        (widgets["name5TFG"], "top", 175),
        (widgets["obj5TFBG"], "left", 205),
        (widgets["obj5TFBG"], "top", 175),
        (widgets["buttonPar"], "left", 25),
        (widgets["buttonPar"], "top", 225),
        (widgets["buttonOri"], "left", 275),
        (widgets["buttonOri"], "top", 225)
        ])
        

    cmds.window(widgets["win"], e=True, w=5, h=5, rtf=True)
    cmds.showWindow(widgets["win"])


def add_object_to_field(field):
    sel = cmds.ls(sl=True, type="transform", l=True)
    if sel:
        obj = sel[0]
    obj = rig.remove_front_pipe(obj)
    cmds.textFieldGrp(field, e=True, tx=obj.rpartition("|")[2])


def gather_info(constType, *args):
    objs = []
    names = []
    tgt = cmds.textFieldButtonGrp(widgets["tgtTFBG"], q=True, tx=True)
    if not tgt:
        cmds.warning("You need to select a target object in the field!")
        return()
    tgtCtrl = cmds.textFieldButtonGrp(widgets["tgtCTRLTFBG"], q=True, tx=True)
    nameFields = ["name1TFG", "name2TFG", "name3TFG", "name4TFG", "name5TFG"]
    objFields = ["obj1TFBG", "obj2TFBG", "obj3TFBG", "obj4TFBG", "obj5TFBG"]
    for x in range(5):
        o = cmds.textFieldButtonGrp(widgets[objFields[x]], q=True, tx=True)
        if o:
            objs.append(o)
            n = cmds.textFieldGrp(widgets[nameFields[x]], q=True, tx=True)
            if n:
                names.append(n)
            else:
                names.append(o.split("|")[-1])

    if not objs or not names:
        cmds.warning("You need to select some objects to constrain to!")
        return()

    create_follow_constraints(constType=constType, tgt=tgt, tgtCtrl=tgtCtrl, spaceNames=names, spaceObjs=objs)


def create_follow_constraints(tgt=None, tgtCtrl=None, spaceNames=None, spaceObjs=None, constType="parent"):
    # refactor this part
    if not tgt:
        tgt = cmds.ls(sl=True)[0]

    spaceGrps = []

    for i in range(len(spaceObjs)):
        name = "{0}_{1}_space".format(tgt, spaceObjs[i])
        space = name
        if not cmds.objExists(name):  
            space = cmds.group(em=True, name=name)

            rig.snap_to(tgt, space)
            cmds.parentConstraint(spaceObjs[i], space, mo=True)
        spaceGrps.append(space)

    # check if grp for spaces exists
    spaceGrpTest = cmds.attributeQuery("follow", node=tgt, exists=True)
    if not spaceGrpTest:
        cmds.addAttr(tgtCtrl, ln="follow", at="enum", en="{0}".format(":".join(spaceNames)), dv=1, k=True)
    if constType == "parent":
        cnstr = cmds.parentConstraint(spaceGrps, tgt, mo=True)[0]
    if constType == "orient":
        cnstr = cmds.orientConstraint(spaceGrps, tgt, mo=True)[0]    
    

    # create setDrivenKey
    for i in range(len(spaceGrps)):
        spaceGrp = rig.remove_front_pipe(spaceGrps[i])
        tmpList = spaceNames[:]
        attr = tmpList.pop(i)
        index = get_enum_index_from_string(tgtCtrl, "follow", attr)
        cmds.setAttr("{0}.follow".format(tgtCtrl), i)
        cmds.setDrivenKeyframe("{0}.{1}W{2}".format(cnstr, spaceGrp, i), cd="{0}.follow".format(tgtCtrl), value=1)
        for a in range(len(spaceGrps)):
            if a != index:
                cmds.setDrivenKeyframe("{0}.{1}W{2}".format(cnstr, spaceGrps[a], a), cd="{0}.follow".format(tgtCtrl), value=0)
    cmds.setAttr("{0}.follow".format(tgtCtrl), 0)

    cmds.group(spaceGrps, name="{0}_spaces_GRP".format(tgt))

    return(cnstr)


def get_enum_index_from_string(node, attr, value):
    enumList = cmds.attributeQuery(attr, node=node, listEnum=True)[0].split(":")
    index = enumList.index(value)
    return(index)


def followConstraints(*args):
    follow_constraints_UI()