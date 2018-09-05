# -*- coding: utf-8 -*-
try:
    import maya.cmds       as cmds
    import pymel.core      as pm
    import maya.OpenMaya   as om
    import maya.OpenMayaUI as mui
    import shiboken        as shi
    from HitchAnimationModule.Widgets   import button
    from HitchAnimationModule.Widgets   import checkBox
    from HitchAnimationModule.Widgets   import lineEdit
    from HitchAnimationModule.Widgets   import spliter
    from HitchAnimationModule.Widgets   import label

except: pass
###############################
from PySide import QtCore as qc
from PySide import QtGui as qg
from PySide.QtCore import Signal
from functools import partial
import os

#------------------------------------------------------------------------------------------------------------#
ICON = os.path.join('Icons' , 'Arrow-down.png')

CCSCombo = """#QComboColt,
            QComboBox {
            border: 1px  solid black;
            border-radius: 4px;
            padding: 1px 10px 1px 10px;
            color: rgba(225,40,40,220);
            font-family: Calibri;
            font: bold 12px;
            padding-left: 10px
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;

            border-left-width: 1px;
            border-left-color: darkgray;
            border-left-style: solid; /* just a single line */
            border-top-right-radius: 4px; /* same radius as the QComboBox */
            border-bottom-right-radius: 4px
        }

        QComboBox::down-arrow {
            image: url(%s)
        }

        /* shift the arrow when popup is open */
        QComboBox::down-arrow:on {
            top: 1px;
            left: 1px
        }

        QComboBox QAbstractItemView {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgb(53, 57, 60), stop:1 rgba(50, 50, 50,200));
            color : rgba(150,225,100,200);
            selection-background-color: rgba(255,255,255,10);
            selection-color: lightgray;
            padding: 2px 2px 2px 10px;


        }

        QComboBox:!editable, QComboBox::drop-down:editable {
            background : qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgb(53, 57, 60), stop:1 rgba(50, 50, 50,10))
        }

        /* QComboBox gets the "on" state when the popup is open */
        QComboBox:!editable:on, QComboBox::drop-down:editable:on {
            background : qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgb(53, 57, 60), stop:1 rgba(50, 50, 50,1))
        }

        QComboBox:on { /* shift the text when the popup opens */
            padding-top: 2px;
            padding-left: 10px

        }"""%ICON

####################################################################################################################

class ComboColt(qg.QComboBox):
    def __init__(self):
        super(ComboColt, self).__init__()
        self.setObjectName('QComboColt')
        self.setStyleSheet(CCSCombo)

        self.setEnabled(True)


    def showPopup(self):
        super(ComboColt,self).showPopup()
        popup = self.findChild(qg.QFrame)
        popup.move(popup.x(), popup.y()+1)


    def spaceSwitch_operation(self, node):
        spaces = []
        for item in node:
            attributes = cmds.listAttr(item,  k=True, se=True, c=True)
            if attributes is not None:

                check = [itm  for itm in attributes if cmds.attributeQuery(itm, node=item, enum=True)]
                if len(check) > 0:
                    attribute = check[0]
                    values = cmds.attributeQuery(attribute, node=item, le=True)[0].split(':')

                    for idx, att in enumerate(values):
                        spaces.append([item,idx,attribute,att])
                        #print("['{}','{}','{}','{}']".format(item,idx,attribute,att))

        return spaces

    #data = spaceSwitch_operation(sel)

    #---------------------------------------------------------------------------------------------------------------------#
    # defe function for head isolate
    def Space_matching(self,array):
        # checker::::
        node = array[0]
        index = array[1]
        attribute = array[2]
        space = array[3]

        max = cmds.xform(node, q=True, m=True, ws=1)
        formato = '{}.{}'.format(node,attribute)
        cmds.setAttr(formato, int(index))
        cmds.xform(node, m=max, ws=1)
        om.MGlobal.displayInfo("Node: {} now working on '{}' space ".format(node, space))


    # call function for head Isolate

    #----------------------------------------------------------------------------------------------------#
