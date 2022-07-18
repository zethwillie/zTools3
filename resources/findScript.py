import sys
import maya.cmds as cmds
import os


def activeScript(scriptName):
    
    pathList = []
    nameList = []
    
    trimmed = scriptName.partition(".")[0]
    print(trimmed)
    
    for pth in sys.path:
        try: 
            #print "searching-----PATH: %s-----"%pth
            files = os.listdir(pth)
            for fl in files:
                if (fl.startswith(trimmed)):
                    pathList.append(pth)
                    nameList.append(fl)
            #for fl in files:
            #    print("     %s"%fl)
        except: 
            pass
            #cmds.warning("couldn't get into %s"%pth)
            
    print(("found %s in the following directories:"%trimmed))
    for x in range(0, len(pathList)):
         print(("%s---%s"%(nameList[x],pathList[x])))
         
         
activeScript("zbw_appendPath.py")