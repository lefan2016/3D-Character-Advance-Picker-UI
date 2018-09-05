try:
    import maya.cmds       as cmds
    import pymel.core      as pm
    import maya.OpenMaya   as om
    import maya.OpenMayaUI as mui
    import shiboken        as shi
    from HitchAnimationModule.Widgets import button
    from HitchAnimationModule.ControlList import ControlList

except: pass
############
from PySide import QtCore as qc
from PySide import QtGui as qg
from functools import partial
import random
#------------------------------------------------------------------------------------------------------------#
# GLOBALS:
BODYCONTROLS = ControlList.BODYCONTROLS
FACECONTROLS = ControlList.FACECONTROLS
# ---------------------------------------------------------------------------#
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
# ---------------------------------------------------------------------------#

class ManageControls(qc.QObject):
    def __init__(self):
        super(ManageControls, self).__init__()


    #########################################
    # READ THE FUNCTION NAME ....
    #
    def getNameSpace(self):
        mainWindow = getMainWindow(windowObject)
        topPanel   = mainWindow.findChildren(qg.QFrame, 'topFrame')[0]
        nm_lineEdit = getattr(topPanel,'nameSpace_le').text()
        if len(nm_lineEdit) == 0:
            return None
        else:
            return nm_lineEdit

    #########################################
    ### TO CONNECT THE BUTTONS WITH CONTROLS
    ###
    def getComand_to_connect(self, ctrl):
        mods = cmds.getModifiers()
        shift = (mods & 1) > 0
        control = (mods & 4) > 0
        nameSpace = self.getNameSpace()

        if nameSpace is None:
            try:
                cmds.select(ctrl, add = shift, deselect = control )
                return self.getComand_to_connect
            except: pass
        else:
            newControl = nameSpace + ':' + ctrl
            try:
               cmds.select(newControl, add = shift, deselect = control )
               return self.getComand_to_connect
            except: pass
        #######################################




