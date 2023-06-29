# message attribute mapper - maya only

from PySide2 import QtCore, QtGui, QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui


def get_main_window():
    """
    get qt main from maya
    """
    main_win_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_win_ptr), QtWidgets.QWidget)


class MessageAttributesUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent=parent)
        if not parent:
            self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.setWindowTitle("Message Attribute Manager")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.show()

    def create_widgets(self):
        self.base_tx = QtWidgets.QLabel("Base Object: ")
        self.base_le = QtWidgets.QLineEdit()
        self.base_le.setMinimumWidth(250)
        self.base_but = QtWidgets.QPushButton("<-- SET  ")
        self.base_but.setStyleSheet("background-color:rgb(70, 100, 70)")
        self.base_but.setFixedWidth(50)
        self.base_sel_but = QtWidgets.QPushButton("SELECT")
        self.base_sel_but.setFixedWidth(60)

        self.message_list = QtWidgets.QListWidget()
        self.message_list.setMinimumWidth(590)
        self.message_list.setMinimumHeight(300)
        self.message_list.setStyleSheet("background-color:black")

        self.reset_but = QtWidgets.QPushButton("Reset")
        self.create_but = QtWidgets.QPushButton("Create New Attr")

    def create_layouts(self):
        top_groupbox = QtWidgets.QGroupBox()
        # top_groupbox.setStyleSheet("background-color:black; border:none")
        top_groupbox_layout = QtWidgets.QHBoxLayout()
        top_groupbox.setLayout(top_groupbox_layout)
        top_groupbox_layout.addWidget(self.base_tx)
        top_groupbox_layout.addWidget(self.base_le)
        top_groupbox_layout.addWidget(self.base_but)
        top_groupbox_layout.addWidget(self.base_sel_but)

        list_layout = QtWidgets.QVBoxLayout()
        list_layout.addWidget(self.message_list)

        low_horiz_layout = QtWidgets.QHBoxLayout()
        low_horiz_layout.addWidget(self.create_but)
        low_horiz_layout.addStretch()
        low_horiz_layout.addWidget(self.reset_but)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(top_groupbox)
        main_layout.addLayout(list_layout)
        main_layout.addLayout(low_horiz_layout)

    def create_connections(self):
        self.base_but.clicked.connect(self.set_base_obj)
        self.create_but.clicked.connect(self.create_new_attr_name)
        self.base_sel_but.clicked.connect(self.select_base)
        self.reset_but.clicked.connect(self.reset_ui)

    def set_base_obj(self):
        sel = mc.ls(sl=True, long=True)
        if len(sel) != 1:
            mc.warning("You need to select ONE object in scene as the base object to look at!")
            return()
        obj = sel[0]
        self.reset_ui()
        self.base_le.clear()
        self.base_le.setText(obj)
        self.process_base_object()

    def process_base_object(self):
        base_obj = self.base_le.text()
        attrs = self.list_message_attributes(base_obj)
        for attr in attrs:
            value = ""
            conns = mc.listConnections("{0}.{1}".format(base_obj, attr), d=False, s=True)
            if conns:
                value = conns[0]
            self.create_attr_widget(attr, attr_value=value)

    def select_base(self):
        if self.base_le.text() and mc.objExists(self.base_le.text()):
            mc.select(self.base_le.text(), replace=True, noExpand=True)

    def list_message_attributes(self, obj):
        exclude = ["message", "hyperLayout", "borderConnections", "ghostDriver", "partition", "groupNodes", "usedBy"]
        attrs = [x for x in mc.listAttr(obj) if "." not in x and x not in exclude]
        msg_attrs = [x for x in attrs if mc.attributeQuery(x, node=obj, message=True)]
        return(msg_attrs)

    def create_new_attr_name(self):
        """popup to create new name, then sends to create_widget"""
        if not self.base_le.text():
            mc.warning("You need have a base object chosen!")
            return()
        attr_name, done = QtWidgets.QInputDialog.getText(self, "New Message Attr Name", "Enter New Message Attr Name:")
        # validate attr name?
        if done:
            self.create_message_attribute(attr_name)
            self.create_attr_widget(attr_name)

    def create_message_attribute(self, attr_name):
        """makes a new message attr named attr_name on self.base_obj"""
        if not self.base_le.text():
            mc.warning("You need to have a base object in the ui!")
            return()
        try:
            mc.addAttr(self.base_le.text(), ln=attr_name, at="message")
        except:
            mc.warning("Couldn't add the attr: ", attr_name)

    def create_attr_widget(self, attr_name, attr_value=""):
        base_obj = self.base_le.text()
        if not mc.objExists(base_obj):
            return()
        message_widget = MessageAttributeWidget(self, base_obj, attr_name, attr_value)
        item = QtWidgets.QListWidgetItem(self.message_list)
        item.setSizeHint(message_widget.sizeHint())
        self.message_list.addItem(item)
        self.message_list.setItemWidget(item, message_widget)

        num = self.message_list.count()
        if num > 0:
            num = num - 1
        self.message_list.setCurrentRow(num)

    def get_all_widgets(self):
        widgets = []
        for x in range(self.message_list.count()):
            item = self.message_list.item(x)
            widget = self.message_list.itemWidget(item)
            widgets.append(widget)
        return(widgets)

    def delete_widget(self, widget):
        """deletes item, widget and attribute"""
        self.select_item_from_widget(widget)
        item = self.message_list.currentItem()
        self.message_list.takeItem(self.message_list.row(item))
        widget.deleteLater()

        try:
            mc.deleteAttr(f"{self.base_le.text()}.{widget.attr_name}")
        except:
            pass

    def select_item_from_widget(self, my_widget):
        """selects the list item that contains the given widget"""
        for x in range(self.message_list.count()):
            item = self.message_list.item(x)
            widget = self.message_list.itemWidget(item)
            if widget == my_widget:
                self.message_list.setCurrentItem(item)
                return()

    def reset_ui(self):
        self.base_le.clear()
        widgets = self.get_all_widgets()
        if widgets == [None]:
            widgets = []
        for widget in widgets:
            widget.deleteLater()
        self.message_list.clear()


class MessageAttributeWidget(QtWidgets.QWidget):
    def __init__(self, parent, base_obj, attr_name, attr_value=None):
        """widget for each message attr"""
        super(MessageAttributeWidget, self).__init__(parent=None)
        self.main_ui = parent
        self.attr_name = attr_name
        self.attr_value = attr_value
        self.base_obj = base_obj
        self.full_attr = self.base_obj + "." + self.attr_name

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.fill_value(value=self.attr_value)

    def create_widgets(self):
        self.base_widget = QtWidgets.QWidget()
        self.base_widget.setMinimumWidth(580)
        self.base_widget.setFixedHeight(40)
        self.base_widget.setStyleSheet("background-color:rgb(30, 30, 30); border:none")

        self.attr_tx = QtWidgets.QLabel(f".{self.attr_name} ")
        self.attr_tx.setFixedWidth(135)
        self.attr_le = QtWidgets.QLineEdit()
        self.attr_le.setReadOnly(True)
        self.attr_le.setMinimumWidth(200)
        self.attr_le.setStyleSheet("background-color:rgb(10, 10, 10)")

        self.set_but = QtWidgets.QPushButton("<-- SET  ")
        self.set_but.setStyleSheet("background-color:rgb(70, 100, 70)")
        self.set_but.setFixedWidth(60)
        self.clr_but = QtWidgets.QPushButton("DISCONN.")
        self.clr_but.setStyleSheet("background-color:rgb(70, 70, 70)")
        self.clr_but.setFixedWidth(70)
        self.del_but = QtWidgets.QPushButton("DELETE")
        self.del_but.setStyleSheet("background-color:rgb(175, 70, 70)")
        self.del_but.setFixedWidth(50)

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.base_widget)
        main_layout.setContentsMargins(2, 2, 2, 2)

        base_layout = QtWidgets.QHBoxLayout()
        self.base_widget.setLayout(base_layout)
        base_layout.addWidget(self.attr_tx)
        base_layout.addWidget(self.attr_le)
        base_layout.addWidget(self.set_but)
        base_layout.addWidget(self.clr_but)
        base_layout.addWidget(self.del_but)

        self.setLayout(main_layout)

    def create_connections(self):
        self.set_but.clicked.connect(self.get_and_set_attr)
        self.clr_but.clicked.connect(self.clear_attr)
        self.del_but.clicked.connect(self.delete_me)

    def clear_attr(self):
        self.main_ui.select_item_from_widget(self)
        if not self.attr_le.text():
            return()
        mc.disconnectAttr(f"{self.attr_le.text()}.message", f"{self.base_obj}.{self.attr_name}")
        self.attr_le.clear()

    def get_and_set_attr(self):
        self.main_ui.select_item_from_widget(self)
        sel = mc.ls(sl=True, long=True)
        if len(sel) != 1:
            mc.warning("You need to select only ONE object to go into the message attr!")
            return()
        obj = sel[0]

        self.fill_value(obj)
        try:
            mc.connectAttr(f"{obj}.message", f"{self.base_obj}.{self.attr_name}", force=True)
        except:
            mc.warning("Had a problem trying to connect ")
            pass

    def fill_value(self, value=""):
        self.attr_le.clear()
        if value:
            self.attr_le.setText(value)
            self.attr_value = value

    def delete_me(self):
        self.main_ui.delete_widget(self)


def launch_ui():
    global messageWin
    try:
        messageWin.close()
        messageWin.deleteLater()
    except:
        pass

    main = get_main_window()
    messageWin = MessageAttributesUI(main)
