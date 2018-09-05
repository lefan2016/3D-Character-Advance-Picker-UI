try:
    import maya.cmds       as cmds
    import pymel.core      as pm
    import maya.OpenMaya   as om
    import maya.OpenMayaUI as mui
    import shiboken        as shi
except: pass

############
from PySide import QtCore as qc
from PySide import QtGui as qg

##############################################################################
windowObject = "HitchAnimationUI_Object"
#############################################################################
def getMainWindow(windowName):
    mayaMainWindowPtr = mui.MQtUtil.mainWindow()
    mayaMainWindow = shi.wrapInstance(long(mayaMainWindowPtr), qg.QMainWindow) # Important that it's
    # Go through main window's children to find any previous instances
    for obj in mayaMainWindow.children():
        if isinstance(obj,qg.QMainWindow):
            if obj.objectName() == windowName:
                return obj

################################################################
class resetScene(qc.QObject):
    def __init__(self):
        super(resetScene, self).__init__()

        self.mainWindow = getMainWindow(windowObject)
        self.mainWindow.update()

    def findSceneChilds(self, objectType, objectName):
        result = self.mainWindow.findChildren(objectType, objectName)
        return result

def refresh():
    scene = resetScene()
    widgetPort = scene.findSceneChilds(qg.QWidget,'ViewportClass')[0]
    widgetTop = scene.findSceneChilds(qg.QFrame,'topFrame')[0]
    pickerBody = scene.findSceneChilds(qg.QLabel, 'bodyPickerLabel')[0]
    pickerface = scene.findSceneChilds(qg.QLabel, 'HeadPicker')[0]

    nameSpace_le = [itm for itm in  vars(widgetTop) if  'nameSpace_le' in itm ][0]
    nameSpace_bx = [itm for itm in  vars(widgetTop) if 'nameSpace_chbox' in itm ][0]


    getattr(pickerBody,'update_nameSpace')()
    getattr(pickerface,'update_nameSpace')()

    getattr(pickerBody,'create_callbacks')()
    getattr(pickerface,'create_callbacks')()

    getattr(pickerBody, 'updateAllWidgets')()
    getattr(pickerface, 'updateAllWidgets')()

    widgetPort.updateViewport()
    ####################################################################################################


def undo(func):
    def wrapper(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        try:
            ret = func(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)
        return ret
    return wrapper


def undo_pm(func):
    def wrapper(*args, **kwargs):
        pm.undoInfo(openChunk=True)
        try:
            ret = func(*args, **kwargs)
        finally:
            pm.undoInfo(closeChunk=True)
        return ret
    return wrapper

#----------------------------------a--------------------------------------------#


if __name__ == '__main__':
    pass
