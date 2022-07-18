from functools import wraps
from maya import cmds
import sys


def undo(function):
    '''A decorator that will make commands undoable in maya'''

    def decoratorCode(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        functionReturn = None
        try:
            functionReturn = function(*args, **kwargs)
        except:
            print((sys.exc_info()[1]))
        finally:
            cmds.undoInfo(closeChunk=True)
            cmds.undoInfo(printQueue=True)
            return functionReturn

    return decoratorCode
