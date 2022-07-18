#reload a selected module???
#get list of modules
import sys
import importlib

#list of modules . . . .
for mod in sys.modules:
    print(mod)

#to get a module. ..
print((sys.modules["moduleName"]))
#to reload? ? ?
importlib.reload(sys.modules["moduleName"])

#create text scroll list to list out all of the modules that are loaded . . .
#then button to reload the selected modules