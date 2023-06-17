########################
#file: zbw_messageMapper.py
#author: zeth willie
#contact: zeth@catbuks.com, www.williework.blogspot.com, https://github.com/zethwillie
#date modified: 09/23/12
#
#notes: for checking and creating message attributes for objs in the scene (through UI).
#to run: import zbw_messageMapper; zbw_messageMapper.messageMapper()
########################

import maya.cmds as cmds
from functools import partial

#create a window
def zbw_mmUI():
    """the UI for the script"""

    if (cmds.window('zbw_messageMapperUI', exists=True)):
        cmds.deleteUI('zbw_messageMapperUI', window=True)
        cmds.windowPref('zbw_messageMapperUI', remove=True)
    window=cmds.window('zbw_messageMapperUI', widthHeight=(600,400), title='zbw_messageMapper')

    cmds.tabLayout(h=400)
    cmds.columnLayout("mmAddNewConnections", h=400)
    #2nd small column for the persistant UI
    cmds.columnLayout(w=400, h=100)
    cmds.textFieldButtonGrp('zbw_tfbg_baseObj', cal=(1, "left"), cw3=(75, 200, 75), label="base object", w=400, bl="choose object", bc=partial(zbw_mmAddBase, "zbw_tfbg_baseObj", "clear"))

    #button to create new message/obj field groups
    cmds.separator(h=20, st="single")
    cmds.button(w=150, l="add new message attr/obj", c=zbw_mmAddMObjs)
    cmds.separator(h=20, st="single")

    cmds.setParent(u=True)
    cmds.rowColumnLayout("mmRCLayout", nc=2, co=(2, "left", 30))

    #back up to the 2nd columnLayout
    cmds.setParent(u=True)

    cmds.separator(h=20, st="single")
    #create button to delete last pair of text fields
    cmds.button("deleteLastButton", w=150, bgc=(.5,0,0), l="delete last attr/obj pair", c=zbw_mmDeleteLast)
    cmds.separator(h=20, st="double")

    #button to do connect all the attr/messages
    cmds.button("createMessageButton", w=150, bgc=(0,.5,0), l="create messages", c=zbw_mmConnectM)

    #back up to the main column
    cmds.setParent(u=True)
    #back up to the tab
    cmds.setParent(u=True)
    #new tab
    cmds.columnLayout("existingMessages", w=600, h=400)

    #Here we add stuff to the second tab
    cmds.textFieldButtonGrp("mmListMessages", cal=(1, "left"), cw3=(75,200,75), label="baseObject", w=400, bl="choose object", bc=partial(zbw_mmAddBase,"mmListMessages", "noClear"))
    cmds.separator(h=20, st="double")
    #button to create list of message attrs
    cmds.button(w=200, l="list all message attr for base", bgc = (0,.5,0), c=partial(zbw_mmListCurrentMessages, "mmListMessages"))
    cmds.separator(h=20, st="double")
    cmds.text("rt-click on the attr or object to change the connection")
    cmds.separator(h=20, st="double")

    cmds.rowColumnLayout("mmRCTextLayout", w=600, nc=3, cw=[(1, 200),(2,290),(3,100)])
    cmds.text("ATTR")
    cmds.text("OBJECT")
    cmds.text("DELETE")

    cmds.showWindow(window)

def zbw_mmAddMObjs(*args):
    """
    adds textFields to the UI for adding target objects for the message attrs
    """
    #delete text confirm dialogue if it exists
    zbw_mmDeleteConfirm()
    #figure out what objects are already parented
    children = cmds.rowColumnLayout("mmRCLayout" , q=True, ca=True)
    #figure out where stuff goes (2 column layout, so divide by 2), 1 based
    if children:
        currentNum = len(children)/2 + 1
        currentTFG = "attr" + str(currentNum)
        currentTFBG = "obj" + str(currentNum)
    #if no objects exist . . .
    else:
        currentTFG = "attr1"
        currentTFBG = "obj1"

    cmds.textFieldGrp(currentTFG, l="addedAttr (ln)", cal=(1, "left"), cw2=(100, 150), p="mmRCLayout")
    cmds.textFieldButtonGrp(currentTFBG, l="messageObj", cal=(1, "left"), cw3=(75,150,50), p="mmRCLayout", bl="get", bc=partial(zbw_mmAddTarget, currentTFBG))


#proc to grab the attrs and create connections
def zbw_mmConnectM(*args):
    """
    uses the items from the textFields to create message attrs in the base obj, and connects to those the objs from the rightmost fields of the UI
    """
    #check there's a base obj
    if (cmds.textFieldButtonGrp("zbw_tfbg_baseObj", q=True, tx=True)):
        #check there are any fields created
        if (cmds.rowColumnLayout("mmRCLayout", q=True, ca=True)):

            children = cmds.rowColumnLayout("mmRCLayout", q=True, ca=True)
            numObj = (len(children)/2)

            if numObj:
                for num in range(1, numObj+1):
                    attrTFG =  "attr" + str(num)
                    objTFBG = "obj" + str(num)
                    baseObj = cmds.textFieldButtonGrp("zbw_tfbg_baseObj", q=True, tx=True)
                    targetObj = cmds.textFieldButtonGrp(objTFBG, q=True, tx=True)
                    baseAttr = cmds.textFieldGrp(attrTFG, q=True, tx=True)
                    baseMAttr = baseObj + "." + baseAttr
                    objMAttr = targetObj + ".message"
                    #check to make sure there's something in each field, otherwise skip
                    if baseAttr and targetObj:
                        #check that attr doesnt' already exist with connection
                        if (cmds.attributeQuery(baseAttr, n=baseObj, ex=True)):
                            #delete the attr that exists, print note about it
                            cmds.deleteAttr(baseMAttr)
                            cmds.warning(baseMAttr + " already exists! Deleting for overwrite and reconnection")
                        cmds.addAttr(baseObj, at="message", ln=baseAttr)
                        cmds.connectAttr(objMAttr, baseMAttr, f=True)
                        #print confirmation of connection
                        print(("Connected: "+ objMAttr +"--->"+ baseMAttr))

                    else:
                        cmds.warning("Line # " + str(num) + " was empty! Skipped that attr")
                #leave a text field saying that it's done
                zbw_mmDeleteConfirm()
                cmds.separator("mmConfirmSep", h=20, st="single", p="mmAddNewConnections")
                cmds.text("mmTextConfirm", l="MESSAGES MAPPED!", p="mmAddNewConnections")
        else:
            cmds.warning("Please create some attrs and objs to connect to base obj!")
    else:
        cmds.warning("Please choose a base object to add attrs to!")

def zbw_mmDeleteConfirm():
    if (cmds.text("mmTextConfirm", q=True, ex=True)):
        cmds.deleteUI("mmTextConfirm")
        cmds.deleteUI("mmConfirmSep")

def zbw_mmAddBase(tfbg,*args):
    """
    uses the selected item to add the full path in to the textField of the UI base obj
    """
    #check that selection is only one object
    sel = cmds.ls(sl=True, l=True, tr=True)
    if len(sel) == 1:
        baseObj = sel[0]
        cmds.textFieldButtonGrp(tfbg, e=True, tx=baseObj)
        #delete the text about "Messages mapped" if it exists (and you're coming from the first tab)
        if (args[0]=="clear"):
            zbw_mmDeleteConfirm()
    else:
        cmds.error("please select one tranform object to be the base to add message attrs to")

def zbw_mmAddTarget(currentTFBG, *args):
    """
    uses the selected item to add full path into the textField of the UI target obj
    """
    #check selection is one object
    sel = cmds.ls(sl=True, l=True)
    if len(sel) == 1:
        targetObj = sel[0]
        #add selected to textField
        cmds.textFieldButtonGrp(currentTFBG, e=True, tx=targetObj)
    else:
        cmds.error("please select one object to send out message attr")

def zbw_mmDeleteLast(*args):
    """
    deletes the last pair of attr, obj text fields in the UI
    """
    children = cmds.rowColumnLayout("mmRCLayout" , q=True, ca=True)

    if children:
        numChildren = len(children)
        lastTFG = "attr" + str(numChildren/2)
        lastTFBG = "obj" + str(numChildren/2)
        cmds.deleteUI(lastTFG)
        cmds.deleteUI(lastTFBG)

    else:
        pass

def zbw_mmListCurrentMessages(tfbg, *args):
    """
    lists the message attrs in the base obj and sets up rt-click menus to change them and a button to delete them
    """
    if (cmds.rowColumnLayout("mmRCListLayout", q=True, ex=True)):
        cmds.deleteUI("mmRCListLayout")
    cmds.rowColumnLayout("mmRCListLayout", w=600, nc=3, cw=[(1, 250),(2,250),(3,100)],p="existingMessages")
    #get the base object
    baseObj = cmds.textFieldButtonGrp(tfbg, q=True, tx=True)
    #find all attr of type message for base obj
    userAttrs = cmds.listAttr(baseObj, ud=True)
    #print(udAttrs)
    messageAttrs = []
    messageObjs = []
    if userAttrs:
        for attr in userAttrs:
            isMsg = cmds.attributeQuery(attr, n=baseObj, msg=True)
            if isMsg:
                fullMsgAttr = baseObj + "." + attr
                messageAttrs.append(fullMsgAttr)
                targetObj = cmds.listConnections(fullMsgAttr)
                if not targetObj:
                    targetObj = ["no Connection"]
                messageObjs.append(targetObj[0])

        sizeMsgs = len(messageObjs)
        for i in range(0, sizeMsgs):
            thisObj = messageObjs[i]
            thisAttr = messageAttrs[i]

            #create textField based on num already there, non-editable
            attrId = "listAttrTFG" + str(i)
            objId = "listObjTFG" + str(i)
            buttonId = "listButton" + str(i)

            cmds.separator(h=15, style="single")
            cmds.separator(h=15, style="single")
            cmds.separator(h=15, style="single")

            #create text field for attr
            cmds.textFieldGrp(attrId, p="mmRCListLayout", l=i, cw=[(1,10), (2,190)], ed=False, tx=thisAttr)
            #create popup for text field
            cmds.popupMenu(("attrPUM"+str(i)), b=3)
            cmds.menuItem(l="change attr name", p=("attrPUM"+str(i)), c=partial(zbw_mmChangeConnectAttrUI, baseObj, thisAttr, thisObj))

            #create textField obj based on num, non-editable
            cmds.textFieldGrp(objId, p="mmRCListLayout", w=200, ed=False, tx=thisObj)
            #create pop up
            cmds.popupMenu(("objPUM"+str(i)), b=3)
            cmds.menuItem(l="change obj", p=("objPUM"+str(i)), c=partial(zbw_mmChangeConnectObjUI, baseObj, thisAttr, thisObj))

            #create button to delete attr
            cmds.button(buttonId, l="delete", w=50, c=partial(zbw_mmDeleteMsgAttr, thisAttr))
    else:
        cmds.text("no message attributes on this object", p="mmRCListLayout")

def zbw_mmDeleteMsgAttr(attr, *args):
    #delete the attr from the base obj
    cmds.deleteAttr(attr)
    #when you delete, then run the whole proc again afterwards (to clean up the nums)
    cmds.deleteUI("mmRCListLayout")
    zbw_mmListCurrentMessages("mmListMessages")

def zbw_mmChangeConnectAttrUI(base, attr, obj, *args):
    if (cmds.window('zbw_mmChangeAttrUI', exists=True)):
        cmds.deleteUI('zbw_mmChangeAttrUI', window=True)
        cmds.windowPref('zbw_mmChangeAttrUI', remove=True)
    window=cmds.window('zbw_mmChangeAttrUI', widthHeight=(400,80), title='zbw_messageMapper_changeAttrName')
    cmds.columnLayout()
    #show old attr name
    cmds.text("old attribute name: " + attr)
    #asks for the new attr name
    cmds.textFieldGrp("zbw_mmChangeAttrTFG", l="new attr name (just attr name)")
    #button to do it (pass along attr, obj)
    cmds.button("zbw_mmChangeAttrB", l="change attr!", c=partial(zbw_mmChangeConnectAttr, base, attr, obj))
    cmds.showWindow(window)
    #force window to size
    cmds.window('zbw_mmChangeAttrUI', e=True, widthHeight = (400,80))
    pass

def zbw_mmChangeConnectAttr(base, attr, obj, *args):
    #get that from the text field
    newAttr = cmds.textFieldGrp("zbw_mmChangeAttrTFG", q=True, tx=True)
    #delete old attr
    cmds.deleteAttr(attr)
    #create new attr
    cmds.addAttr(base, at="message", ln=newAttr)
    #create connection to obj in new attr
    cmds.connectAttr((obj+".message"), (base+"."+newAttr), f=True)

    #when you delete, then run the whole proc again afterwards (to clean up the nums)
    cmds.deleteUI('zbw_mmChangeAttrUI', window=True)
    cmds.windowPref('zbw_mmChangeAttrUI', remove=True)
    cmds.deleteUI("mmRCListLayout")
    zbw_mmListCurrentMessages("mmListMessages")

def zbw_mmChangeConnectObjUI(base, attr, obj, *args):
    if (cmds.window('zbw_mmChangeObjUI', exists=True)):
        cmds.deleteUI('zbw_mmChangeObjUI', window=True)
        cmds.windowPref('zbw_mmChangeObjUI', remove=True)
    window=cmds.window('zbw_mmChangeObjUI', widthHeight=(400,85), title='zbw_messageMapper_changeObjName')
    cmds.columnLayout()
    #show old attr name
    cmds.text("base attribute name: " + attr)
    cmds.text("old connected obj name: " + obj)
    #asks for the new attr name
    cmds.textFieldButtonGrp("zbw_mmChangeObjTFBG", l="select new obj: ", bl="get", bc=partial(zbw_mmAddTarget, "zbw_mmChangeObjTFBG"))
    #button to do it (pass along attr, obj)
    cmds.button("zbw_mmChangeObjB", l="change obj!", c=partial(zbw_mmChangeConnectObj, base, attr, obj))
    cmds.showWindow(window)
    #force window to size
    cmds.window('zbw_mmChangeObjUI', e=True, widthHeight = (420,85))

def zbw_mmChangeConnectObj(base, attr, obj, *args):
    #get that from the text field
    newObj = cmds.textFieldGrp("zbw_mmChangeObjTFBG", q=True, tx=True)
    #create connection to obj in new attr
    cmds.connectAttr((newObj+".message"), attr, f=True)

    #delete this window, delete mmRCListLayout and call the list again
    cmds.deleteUI('zbw_mmChangeObjUI', window=True)
    cmds.windowPref('zbw_mmChangeObjUI', remove=True)
    cmds.deleteUI("mmRCListLayout")
    zbw_mmListCurrentMessages("mmListMessages")

def messageMapper():
    """use this to start the script!"""

    zbw_mmUI()
