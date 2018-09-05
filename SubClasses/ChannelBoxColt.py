# -*- coding: utf-8 -*-
try:
    import maya.cmds as cmds
    import pymel.core as pm
    import maya.OpenMaya as om
    import maya.OpenMayaUI as mui
    import shiboken as shi
    import maya.utils as utils
    import pymel.core
    import pymel.core as pm
    from HitchAnimationModule.Widgets import slider
    from HitchAnimationModule.Widgets import Tabs
    from HitchAnimationModule.Widgets import CustomDial
    from HitchAnimationModule.Widgets import spliter
    from HitchAnimationModule.Widgets import button
    from HitchAnimationModule.Widgets import CustomGroup
    from HitchAnimationModule.Widgets import label
    from HitchAnimationModule.Widgets import ColtSpinBox
    from HitchAnimationModule.SubClasses import ColtMenu

except:
    pass
############
from PySide import QtCore as qc
from PySide import QtGui as qg
from functools import partial
import random
from contextlib import contextmanager
import os
import json
########################################################################################
# globals:::
FILENAME = 'channelBoxCallBack.json'
DIRECTORY = os.path.join(cmds.internalVar(usd=1), 'HitchAnimationModule', 'CallBacks')
PATHTOCALLS = os.path.join(DIRECTORY, FILENAME)
windowObject = "HitchAnimationUI_Object"
#########################################################################################


def getMainWindow(windowName):
    mayaMainWindowPtr = mui.MQtUtil.mainWindow()
    mayaMainWindow = shi.wrapInstance(long(mayaMainWindowPtr), qg.QMainWindow)  # Important that it's
    # Go through main window's children to find any previous instances
    for obj in mayaMainWindow.children():
        if isinstance(obj, qg.QMainWindow):
            if obj.objectName() == windowName:
                return obj
#------------------------------------------------------------------------------------------------------------#


@contextmanager
def noSignals(obj):
    obj.blockSignals(True)
    yield
    obj.blockSignals(False)

################################################################


def deletingIndex(index):
    try:
        #print('Callback deleted...', index)
        om.MMessage.removeCallback(index)
        del(index)
    except:
        pass


# utils.executeDeferred(deletingGarbage)
# ------------------------------------------------------------------------------------------------------------#
tableCSS = """
            QTableView {
                selection-background-color: qlineargradient(x1: 0, y1: 0, x2: 0.5, y2: 0.5,
                                            stop: 0 rgba(171, 206, 169,100), stop: 1.2 rgba(255,255,255,75));
                background-color: transparent;
                color: rgba(250,250,250,185);
            }"""
# -------------------------------------------------------------------------------------------------------------#


class ChannelBoxColt(qg.QFrame):
    selectedSignal = qc.Signal(bool)
    updateAllSignal = qc.Signal(list)
    storeCallbackSignal = qc.Signal(int)

    def __init__(self):
        super(ChannelBoxColt, self).__init__()
        self.setObjectName('ChannelBoxColt')
        self.setMinimumHeight(500)
        self.setStyleSheet('#ChannelBoxColt {background: transparent};')
        self.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Minimum)
        self.setLayout(qg.QStackedLayout())
        self.QFont = qg.QFont('Calibri', 12)
        self.QFont.setBold(True)

        mainWin = getMainWindow(windowObject)
        self.setParent(mainWin)

        self._currentNode = None
        self._isUpdating = False
        self._allNodes = []

        #############################
        # Blank Widget from stacked layout to clear the panel
        self.blankWidget = qg.QLabel()
        self.blankWidget.setObjectName('blankpage')
        self.blankWidget.setStyleSheet('#blankpage {background: transparent};')
        self.layout().addWidget(self.blankWidget)

        ###############################
        # Channel Box cristal pannel widget
        #
        self.channelBoxHolder = CustomGroup.CustomGroupColt()
        cb_layout = qg.QVBoxLayout(self.channelBoxHolder)
        self.layout().addWidget(self.channelBoxHolder)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setAlignment(qc.Qt.AlignTop)
        cb_lyt = self.channelBoxHolder.layout()
        cb_data_lyt = qg.QVBoxLayout()
        cb_lyt.addLayout(cb_data_lyt)
        cb_data_lyt.setContentsMargins(0, 1, 0, 0)
        cb_data_lyt.setAlignment(qc.Qt.AlignTop | qc.Qt.AlignVCenter | qc.Qt.AlignRight)

        ###################################
        # Table
        self.CB_table = CustomTableView(1, 2)
        self.CB_table .setStyleSheet(tableCSS)
        self.CB_table.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.CB_table.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.CB_table.setFrameShape(qg.QFrame.NoFrame)
        self.CB_table.setFocusPolicy(qc.Qt.NoFocus)
        self.CB_table.verticalHeader().setVisible(False)
        self.CB_table.horizontalHeader().setVisible(False)
        cb_data_lyt.addWidget(self.CB_table)
        self.CB_table.setShowGrid(False)
        editTriggers = self.CB_table.DoubleClicked | self.CB_table.SelectedClicked | self.CB_table.AnyKeyPressed
        self.CB_table.setEditTriggers(editTriggers)

        #########################
        # using a custoom Item protoptype, this will always set my custom item to the table
        self.CB_table.setItemPrototype(CustomTableItem())

        #######################################################
        ####################################
        # Connections and callbacks from maya API
        #
        self.sel_idx = om.MEventMessage.addEventCallback("SelectionChanged", self.refresDisplay)
        self.callbackkill = partial(om.MMessage.removeCallback, self.sel_idx)

        self.destroy_callback = self.destroyed.connect(self.callbackkill)

        ######################################
        # Signals from QWidgets Conection Area
        #
        self.CB_table.itemChanged.connect(self.itemChanged)
        self.selectedSignal.connect(self.connectionBridgeTest)
        self.updateAllSignal.connect(self.updateAllNodes)

        self.CB_table.installEventFilter(self)
        self.layout().currentChanged.connect(self.clearCallbackFromNode)
        ##########################################################
        # Clears any maya selection before launch the UI
        #
        self.layout().setCurrentIndex(0)
        cmds.select(clear=True)
        ##########################################################
        # CALLBACKS ID TO DELETE:
        #
        self.callBacks_ids = []
        self._node_callbackID = ''

        self.ids_array = om.MCallbackIdArray()
# --------------------------------------------------------------------------------------------------#

    def clearCallbackFromNode(self, value):
        if value == 0:
            try:
                self.removeCallback(self._node_callbackID)
                #print(self._node_callbackID, '< -- CALLBACK ID DELETED ...')
                self._currentNode = None
                self._node_callbackID = ''
            except:
                pass

    # Changes the stacked layout visibility to index One or Zero
    #
    def connectionBridgeTest(self, value):
        self.layout().setCurrentIndex(int(value))
        self.flushMemory()

    ##################################################################
    # Gets the node and open the channel box
    #
    def refresDisplay(self, *args, **kwargs):
        # Refresh the display to always show attributes of selected node
        node = ''
        sel = cmds.ls(sl=True, tr=True)
        if sel:
            node = sel[0]
            if cmds.objectType(node, i='transform') or cmds.objectType(node, i='joint'):
                self._allNodes = [itm for itm in sel if itm != node]
                self.setNodeTag(node)
                self._currentNode = node
                self.populateChannels(node)
                self.selectedSignal.emit(bool(sel))
                return True

            else:
                self.setNodeTag(False)
                self.selectedSignal.emit(bool(not(sel)))

        else:
            self.setNodeTag(False)
            self.selectedSignal.emit(bool(sel))
            return False

    ##############################################################
    #  Flush memory
    #
    def flushMemory(self):
        callbacks = []
        try:
            callbacks = self.callBacks_ids
        except:
            pass
        if len(callbacks) >= 5000:
            for idx in range(len(sorted(callbacks)) - 500):
                try:
                    poped = self.callBacks_ids.pop(idx)
                    om.MMessage.removeCallback(poped[0])
                    del(poped)
                except:
                    pass

            # print(len(self.callBacks_ids))

    ##############################################################
    # SET THE CALLBACK TO THE SELECTED NODE
    #
    def setCallback(self, node):
        sel = om.MSelectionList()
        sel.add(node)
        obj = om.MObject()
        sel.getDependNode(0, obj)
        idx = om.MNodeMessage.addAttributeChangedCallback(obj, self.reading_node)
        return idx, obj

    #################################################################
    # READS THE NODE FOR ATT CHANGED CALLBACK IN NODE
    #
    def reading_node(self, msg, plug, otherplug, *clientData):
        if msg & om.MNodeMessage.kAttributeSet:

            self.format_and_set(plug.name())

        if msg & om.MNodeMessage.kConnectionMade:
            self.refresDisplay()
            #print('Connection Created On: %s' % str(plug.partialName()))
        if msg & om.MNodeMessage.kConnectionBroken:
            self.refresDisplay()
            #print ("Broken Connection On: %s" % str(plug.partialName()))

    ####################################################################

    def format_and_set(self, plug):
        value = cmds.getAttr(plug)
        niceName = cmds.attributeName(plug)
        if isinstance(value, list):
            channels = ['X', 'Y', 'Z']
            tup = value[0]
            for idx, val in enumerate(tup):
                checkingAtt = "%s %s" % (niceName, channels[idx])

                try:
                    _, val_ch = self.matchItems(checkingAtt)
                except:
                    return

                try:
                    if val_ch is not None:

                        with noSignals(self.CB_table):
                            val_ch.setAttrValue(val)
                except:
                    return

        elif isinstance(value, float):
            toMatch = niceName

            try:
                _, val_ch = self.matchItems(toMatch)
            except:
                return

            try:

                if val_ch is None:
                    return

                else:
                    with noSignals(self.CB_table):
                        val_ch.setAttrValue(value)
            except:
                return

    ####################################################################
    def matchItems(self, toMatch):
        mainUI = getMainWindow(windowObject)
        child = mainUI.findChildren(qg.QFrame, 'ChannelBoxColt')[0]
        listWidget = child.findChildren(qg.QTableWidget)[0]

        # try:
        match = listWidget.findItems(toMatch, qc.Qt.MatchWrap)

        if len(match) == 0:
            return

        attr = match[0]
        Row = attr.row()
        value = listWidget.item(Row, 1)

        return attr, value

    ####################################################################
    #   REEMOVES THE CALLBACK FROM THE NODE AND UI IN RUNTIME ...
    #
    def removeCallback(self, index):
        try:
            om.MMessage.removeCallback(index)
        except:
            pass

# -------------------------------------------------------------#
# GET ATTRIBUTES FROM ALL NODES
# --------------------------------------------------------------#
    def getAllattributesData(self, base, niceName=False):
        attribute_names = []

        def getAttributes(node):
            attrs = []
            if isinstance(node, pymel.core.nodetypes.Transform):
                for transform in 'trs':
                    for axis in 'xyz':
                        channel = '%s%s' % (transform, axis)
                        if node.attr(channel).isLocked():
                            continue
                        attrs.append(channel)

            for attr in node.listAttr(ud=True, u=True, c=True, sn=True):
                if attr.type() not in ('double', 'int'):
                    continue
                if attr.isLocked():
                    continue
                attrs.append(attr.name().split('.')[-1])
            return attrs
        ############################################# DIVISOR ################ #

        def resetAttributes(node, N_name=False):
            attrs = getAttributes(node)
            for attr in attrs:
                if N_name:
                    name = cmds.attributeName(node + '.' + attr)
                    attribute_names.append(name)
                if not N_name:
                    name = cmds.attributeName(node + '.' + attr, long=True)
                    attribute_names.append(name)

        ##################################################
        def execute(base, nice_Name):
            node = pm.PyNode(base)
            resetAttributes(node, nice_Name)

            shape = node.getShape()

            if shape != None:
                if shape.listAttr(ud=True) > 0:
                    resetAttributes(node.getShape(), nice_Name)
                locs = [obj for obj in node.getShapes() if isinstance(obj, pymel.core.nodetypes.Locator)]
                if len(locs) > 0:
                    for loc in locs:
                        resetAttributes(loc, nice_Name)

        if niceName:
            execute(base, nice_Name)
            return attribute_names
        else:
            execute(base, niceName)
            return attribute_names

    #------------------------------------------------------------------------------#
    # CHECK IF SHAPES HAS UD ATTRIBUTES TO MAKE A CALL BACK
    def checkShapes(self, base):
        node = pm.PyNode(base)
        nodes = []
        shape = node.getShape()

        if shape != None:
            if len(shape.listAttr(ud=True)) >= 1:
                nodes.append(node.getShape().name())
            locs = [obj for obj in node.getShapes() if isinstance(obj, pm.nodetypes.Locator)]
            if len(locs) > 0:
                for loc in locs:
                    nodes.append(loc.name())

            nodes.append(base)
            return nodes

        else:
            return []

    #------------------------------------------------------------------------------#
    # WRAP THE CALL BACKS FOR THE OUTCOMING LIST FROMA ABOVE PROCS
    def callbackNodeWrapper(self, nodeList):
        for node in nodeList:
            self._node_callbackID, MObject = self.setCallback(node)
            index = self._node_callbackID

            deleteThis = partial(deletingIndex, index)
            self.ids_array.append(index)
            self.destroyed.connect(deleteThis)
            self.callBacks_ids.append([index, deleteThis, MObject, self.ids_array])
    #########################################################
    #------------------------------------------------------------------------------#
    # POPULATES THE TABLEW WIDGET
    #

    def populateChannels(self, node):
        # will populate the channel box with the channels
        # but first will remove any callback previous ....
        self.removeCallback(self._node_callbackID)
        with noSignals(self.CB_table):

            self.callbackNodeWrapper(self.checkShapes(node))

            for itm in range(self.CB_table.rowCount()):
                self.CB_table.removeRow(itm)

            if not node or not cmds.objExists(node):
                return

            attr = self.getAllattributesData(node, niceName=False)
            self.CB_table.setRowCount(len(attr))

            for row, name in enumerate(attr):
                self.CB_table.setRowHeight(row, 20)
                attr = "{}.{}".format(node, name)
                niceName = cmds.attributeName(attr)

                item = qg.QTableWidgetItem(niceName)
                item.setFont(self.QFont)
                item.setFlags(item.flags() ^ qc.Qt.ItemIsEditable)
                item.setTextAlignment(qc.Qt.AlignRight | qc.Qt.AlignVCenter)
                self.CB_table.setItem(row, 0, item)

                val = cmds.getAttr(attr)
                item = CustomTableItem()
                item.setTextAlignment(qc.Qt.AlignLeft | qc.Qt.AlignVCenter)
                if self.lookforKeys(attr):
                    item.setBackground(qg.QColor(220, 1, 1, 100))
                else:
                    item.setBackground(qg.QColor(1, 1, 1, 100))
                item.attrName = attr
                item.attrVal = val
                item.setAttrValue(val)
                self.CB_table.setItem(row, 1, item)

    ######################################################################
    # sends the name of the node to the top tag of the channelbox
    #
    def setNodeTag(self, data):
        self.channelBoxHolder.updateNodeTag(data)
        # THIS SEND THE NAME TO THE TOP TAG

    # filtering the key press and stop them to go to maya UI
    def eventFilter(self, obj, event):
        if obj is self.CB_table:
            if event.type() == qc.QEvent.KeyPress:
                self.CB_table.keyPressEvent(event)
                # print('key')
                event.accept()
                return True

        return False

    # UPDATE ALL NODES IN SELECTION TO AS ORIGINA CHANNEL BOX
    def updateAllNodes(self, items):
        value = items[1]
        attr = items[0].split('.')[1]
        nodes = self._allNodes
        for node in nodes:
            cmds.setAttr(node + '.' + attr, value)

    ################################################################################
    # watch for channel with keysFRAMES ON IT
    #
    def lookforKeys(self, channel):
        TRange = cmds.playbackOptions(q=1, max=True)
        this = cmds.keyframe(channel, time=(0, TRange), query=True)
        if this:
            return True
        else:
            return False

    ##############################################################
    # CUSTOM PROCEDURE TO FORMAT THE CHANNEL BOX VALUES
    #
    def itemChanged(self, item):
        # selfmande signal item changed for custom widget
        row = item.row()
        col = item.column()
        # we are updating the attr value ..
        if col == 1:
            text = str(item.text())
            attrType = type(item.attrVal)

            # formating the diferent values of the Node
            try:
                if attrType is bool:
                    attrVal = text.lower() in ('1', 'on', 'yes', 'true')
                else:
                    attrVal = attrType(text)

            except ValueError:
                cmds.warning("'%s' is not a valid attribute type. Expected: %s " % (text, attrType))
                with noSignals(self.CB_table):
                    item.setAttrValue(item.attrVal)
                return

            ##########################
            # set the attribute to the actual node in maya
            cmds.setAttr(item.attrName, attrVal)
            self.updateAllSignal.emit([item.attrName, attrVal])
            # let the custom item reformat the value
            with noSignals(self.CB_table):
                item.setAttrValue(attrVal)

            ##########################################
            # This block will update all selected items
            # on a row
            if not self._isUpdating:
                self._isUpdating = True
                for idx in self.CB_table.selectedItems():
                    if idx is item:
                        continue

                    idx.setAttrValue(attrVal)
                self._isUpdating = False


################################################## ###########################################################################################################
class CustomTableItem(qg.QTableWidgetItem):
    def __init__(self, val=None):
        super(CustomTableItem, self).__init__(self.UserType)
        self.attrName = ''
        self.attrVal = None
        QFont = qg.QFont('Calibri', 12)
        self.setFont(QFont)
        if val is not None:
            self.setAttrValue(val)

    ########################################
    def setAttrValue(self, val):
        if self.attrVal is None:
            return

        typ = type(self.attrVal)
        try:
            val = typ(val)
        except ValueError:
            val = self.attrVal

        if isinstance(val, float):
            self.setText('%0.3f' % val)

        else:
            self.setText(str(val))

#############################################################################################################
#  QTable widget sub class
#


class CustomTableView(qg.QTableWidget):
    def __init__(self, *args, **kwargs):
        super(CustomTableView, self).__init__(*args, **kwargs)
        self.setObjectName('customTable')
        self.delegate = MyDelegate()
        self.setItemDelegate(self.delegate)

    def mousePressEvent(self, event):
        super(CustomTableView, self).mousePressEvent(event)
        if event.button() == qc.Qt.RightButton:
            event.accept()
            oPos = event.pos()
            y_pos = oPos.y()
            row = self.rowAt(y_pos)
            if row >= 0:
                channel = [str(self.item(row, 0).text().replace(' ', '')), str(self.item(row, 1).text())]
                CB_menu = ColtMenu.ContextChannelBoxMenu(channel)
                CB_menu.exec_(self.mapToGlobal(oPos))
            else:
                return
####################################################################


class MyDelegate(qg.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = qg.QLineEdit(parent)
        reg_ex = qc.QRegExp("[+-]?([0-9]*[.])?[0-9]+")
        textValidator = qg.QRegExpValidator(reg_ex, editor)
        editor.setValidator(textValidator)
        editor.setAttribute(qc.Qt.WA_DeleteOnClose)
        return editor
        return super(MyDelegate, self).createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        # Gets display text if edit data hasn't been set.
        text = index.data(qc.Qt.EditRole) or index.data(qc.Qt.DisplayRole)
        editor.setText(text)
