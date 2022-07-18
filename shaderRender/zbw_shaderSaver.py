import maya.cmds as cmds
import zTools.resources.zbw_window as win
import pickle

# sg = cmds.ls(type="shadingEngine")
# print sg

# cs = cmds.listConnections("lambert2SG.dagSetMembers")
# print cs

class Shader_Saver_UI(win.Window):
    def __init__(self):
        self.windowName = "zbw_shaderSaver"
        self.windowSize = [420, 280]
        self.sizeable = 1

        self.create_UI()

    def common_UI(self):
        pass

    def custom_UI(self):
        cmds.text("put UI stuff here for options")
        path = cmds.internalVar(upd=True) + "default.txt"
        self.widgets["destinationTFBG"] = cmds.textFieldButtonGrp(l="destination", bl="<<<", cal=([1,"left"], [2,"left"], [3,"left"]), cw3=(65,275, 50), tx=path, bc=self.get_location)

    def action(self, close, *args):
        #do the action here
        self.save_shader_list()

        #close window
        if close:
            self.close_window()
        pass

    def print_help(self, *args):
        #########  modify for inheritence ###########
        print("this is your help, yo")

    def reset_values(self, *args):
        #########  modify for inheritence ###########
        print("test values reset")

    def save_values(self, *args):
        #########  modify for inheritence ###########
        print("test save values")

    def load_values(self, *args):
        #########  modify for inheritence ###########
        print("test load values")

    def get_location(*args):
        print("this gets location")
        pass

    def save_shader_list(self, *args):
        """
        """
        sgs = []
        objs = []
        connections = {}

        #get the shaders
        sgs = cmds.ls(type="shadingEngine")

        #get the objects assigned to those shaders
        for sg in sgs:
            objs = cmds.listConnections("%s.dagSetMembers"%sg)
            if objs:
                connections[sg] = objs
            else:
                pass

        #write these lists out to file
        #check if that file exists already . . .
        self.path = cmds.textFieldButtonGrp(self.widgets["destinationTFBG"], q=True, tx=True)
        #print self.path
        file = open(self.path, "w")

        #can't write a dictionary
        #file.write(connections)
        #so. . .
        for key in list(connections.keys()):
            file.write("%s,%s\n"%(key, connections[key]))
        file.close()


    def get_shader_list(self, *args):
        #retrieve the dict of shaders from file
        self.path = cmds.textFieldButtonGrp(self.widgets["destinationTFBG"], q=True, tx=True)
        getFile = open(self.path, "r")
        #getFile.read(self.path)
        for line in getFile:
            print(line)
        getFile.close()
        print(("connections = %s"%connections))


    def assign_shader_list(self, *args):
        #assign the list of shaders to the geo in the new scene
        #check about namespaces, etc. How to deal with that? type in a namespace?
        #select the top node then use the | to split split the names of the objects
        #check-top node replaces top node, then replace on each object the first bit with selection, then other bits with SEL|thenRest . . .

        # #use this code to assign shadingGrp "sg" to object "obj"
        # cmds.sets(obj, fe=sg)

        pass

def shaderSaver():
    shaderWin = Shader_Saver_UI()