# -*- coding: utf-8 -*-
try:
    import maya.cmds as cmds
    import pymel.core as pm
    import maya.OpenMaya as om
    import maya.OpenMayaUI as mui
    import shiboken as shi
    from HitchAnimationModule.Widgets import button
    from HitchAnimationModule.Widgets import checkBox
    from HitchAnimationModule.Widgets import lineEdit
    from HitchAnimationModule.Widgets import spliter
    from HitchAnimationModule.LogicData import BookMarksLogic
    from HitchAnimationModule.SubClasses import ColtMenu
    from HitchAnimationModule.LogicData import refreshUI
except:
    pass
###############################
from PySide import QtCore as qc
from PySide import QtGui as qg
from PySide.QtCore import Signal
from functools import partial
import random
import pprint
import copy
import os
import json
#------------------------------------------------------------------------------------------------------------#
CAMERABODY = 'BodySnapShotCamera'
CAMERAFACE = 'SnapFronFace_camera'
FONT = qg.QFont('Calibri', 10, qg.QFont.Bold)
DIRECTORY = os.path.join(cmds.internalVar(usd=1), 'HitchAnimationModule', 'StoredData')
# ---------------------------------------------------------------------------#


class BookMarks(qg.QWidget):
    def __init__(self):
        super(BookMarks, self).__init__()
        self.library = BookMarksLogic.PoserLibrary()
        self.setObjectName('Bookmark_objName')

        ######### Bookmarks Tab ##########
        self.lyt = qg.QVBoxLayout(self)
        self.lyt.setAlignment(qc.Qt.AlignVCenter | qc.Qt.AlignHCenter)

        ##############################################################################################
        #
        # child finder helper !!!
        #
        self.scene = refreshUI.resetScene()

        ###################
        # Store Operations layout
        #
        saveWidget = qg.QWidget()
        save_layout = qg.QHBoxLayout(saveWidget)
        saveWidget.setSizePolicy(qg.QSizePolicy.Maximum, qg.QSizePolicy.Minimum)
        save_layout.setAlignment(qc.Qt.AlignLeft)

        #################################
        # Linee edit name Field
        self.saveNamefield = lineEdit.CustomLineEdit()
        self.saveNamefield.setPlaceholderMessage('Set Pose Name')
        reg_ex = qc.QRegExp("^(?!^_)[a-zA-Z0-9_]+")
        textValidator = qg.QRegExpValidator(reg_ex, self.saveNamefield)
        self.saveNamefield.setValidator(textValidator)

        self.saveNamefield.setFixedWidth(200)
        save_layout.addWidget(self.saveNamefield)
        save_layout.addSpacerItem(qg.QSpacerItem(15, 0))
        self.saveNamefield.setMaxLength(25)

        checkBox_lyt = qg.QVBoxLayout()
        self.faceCheck = checkBox.CustomCheck('Face')
        self.bodyCheck = checkBox.CustomCheck('Body')
        checkBox_lyt.addWidget(self.faceCheck)
        checkBox_lyt.addWidget(self.bodyCheck)

        save_layout.addLayout(checkBox_lyt)
        save_layout.addSpacerItem(qg.QSpacerItem(15, 0))

        self.saveBtn = button.CustomButton(' Save ')
        self.saveBtn.setFixedWidth(100)
        save_layout.addWidget(self.saveBtn)

        self.lyt.addWidget(saveWidget)

        ###################
        # Scroll Area
        #
        ScrollWidget = qg.QWidget()
        ScrollWidget.setParent(self)
        ScrollWidget.setObjectName('ScrollWidget')
        scroll_area = qg.QScrollArea()
        scroll_area.setObjectName('scroll_area')
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOn)
        scroll_area.setFocusPolicy(qc.Qt.NoFocus)
        scroll_area.setFrameShape(qg.QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        scroll_area.setWidget(ScrollWidget)
        scroll_area.setStyleSheet("""#scroll_area {background : qlineargradient(x1:0, y1:0, x2:0, y2:0, stop:0 rgba(53, 57, 60,100),
         stop:0.5 rgba(33, 34, 36,150),stop:1 rgba(53, 57, 60,100))};""")

        self.lyt.addWidget(scroll_area)
        inside_layout = qg.QVBoxLayout(ScrollWidget)
        inside_layout.setObjectName('insideScroll')

        ##################################
        # first List Widget #
        self.faceList_wdg = ListWidgetColt()
        self.faceList_wdg.setObjectName("faceList_wdg")

        self.faceList_wdg.setStyleSheet("#faceList_wdg {background-color: transparent;}")
        inside_layout.addWidget(self.faceList_wdg)

        ##################################
        # Separator splitter
        ##
        splitter_lyt = spliter.SplitterLayout(content=(50, 5, 50, 5))
        inside_layout.addLayout(splitter_lyt)

        ######################
        # first List Widget #
        self.bodyList_wdg = ListWidgetColt()
        self.bodyList_wdg.setObjectName("bodyListWidget")
        self.bodyList_wdg.setStyleSheet("#bodyListWidget {background-color: transparent};")
        inside_layout.addWidget(self.bodyList_wdg)

        ######################
        # Buttons from operations
        #
        Bottom_btns_wdg = qg.QWidget()
        Bottom_btns_wdg.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Minimum)

        bottom_layout = qg.QHBoxLayout(Bottom_btns_wdg)
        bottom_layout.setAlignment(qc.Qt.AlignHCenter)
        self.lyt.addWidget(Bottom_btns_wdg)

        self.refreshBtn = button.CustomButton('Refresh')
        self.delete_btn = button.CustomButton('Delete')

        btnButtons = [self.refreshBtn, self.delete_btn]
        for btn in btnButtons:
            btn.setFixedWidth(250)
            bottom_layout.addWidget(btn)

        #############################################################################
        # connect operations:
        #
        self._toggle = True
        self.faceCheck.setChecked(self._toggle)
        self.bodyCheck.setChecked(not self._toggle)
        self.faceCheck.clicked.connect(self.toggle)
        self.bodyCheck.clicked.connect(self.toggle)

        # Connect Signals:

        self.delete_btn.clicked.connect(self.deleteItems)
        self.refreshBtn.clicked.connect(self.connectRefreshMethod)
        self.saveBtn.clicked.connect(self.save)

        self.faceList_wdg.itemDoubleClicked.connect(self.showItem)
        self.bodyList_wdg.itemDoubleClicked.connect(self.showItem)

        self.populate(self.library.find())

    #---------------------------------------------------------------------------------#
    def deleteItems(self):
        bodySelection = self.bodyList_wdg.selectedItems()
        faceSelection = self.faceList_wdg.selectedItems()
        mayor = max(bodySelection, faceSelection, key=len)
        self.library.deleteBookmark(mayor)

    #---------------------------------------------------------------------------------#
    def toggle(self):
        self._toggle = not self._toggle
        self.faceCheck.setChecked(self._toggle)
        self.bodyCheck.setChecked(not self._toggle)
    #-----------------------------------------------------------------------------#

    def showItem(self, val):
        if val is not None:
            self.load(val)
        else:
            print('{} was skippet'.format(val))

    """ populate of items the list Widget """
    # adding the list items here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def populate(self, NEWDATA):
        for name, info in NEWDATA.items():
            if name.endswith('_FP'):
                item = qg.QListWidgetItem(name)
                item.setFont(FONT)
                item.setFlags(item.flags() | qc.Qt.ItemIsEnabled | qc.Qt.ItemIsSelectable | qc.Qt.ItemIsEditable)
                screenShot = info.get('screenShot')
                icon = qg.QIcon(screenShot)
                item.setIcon(icon)
                self.faceList_wdg.addItem(item)

            elif name.endswith('_BP'):
                item = qg.QListWidgetItem(name)
                item.setFont(FONT)
                item.setFlags(item.flags() | qc.Qt.ItemIsEnabled | qc.Qt.ItemIsSelectable | qc.Qt.ItemIsEditable)
                screenShot = info.get('screenShot')
                icon = qg.QIcon(screenShot)
                item.setIcon(icon)
                self.bodyList_wdg.addItem(item)

    def load(self, current_item):
        if not current_item:
            return
        name = current_item.text()
        path = os.path.join(DIRECTORY, "{}{}".format(name, '.json'))
        with open(path, 'r') as f:
            info = json.load(f)
            self.library.LoadPose(info)

    def save(self):
        topPanel = self.scene.findSceneChilds(qg.QFrame, 'topFrame')[0]
        lineEdit = topPanel.nameSpace_le
        #
        name = ''
        datos = {}
        cam_face = CAMERAFACE
        cam_body = CAMERABODY
        ###################
        # Check for nameSpace here

        if lineEdit.isReadOnly():
            nameSpace = lineEdit.text() + ':'
            cam_face = nameSpace + CAMERAFACE
            cam_body = nameSpace + CAMERABODY
         # -------------#

        if self.faceCheck.isChecked():
            name = self.saveNamefield.text() + '_FP'
            datos = self.library.save(name, cam_face, head=True)

        if self.bodyCheck.isChecked():
            name = self.saveNamefield.text() + '_BP'
            datos = self.library.save(name, cam_body, body=True)

        if not name.strip():
            cmds.warning('You Must Give a name to save the Pose')
            return

        self.saveDataMethod(datos)
        self.saveNamefield.clear()

    ########################################################################################################
    def saveDataMethod(self, datos):
        for name, info in datos.items():
            item = qg.QListWidgetItem(name)
            item.setFont(FONT)
            item.setFlags(item.flags() | qc.Qt.ItemIsEnabled | qc.Qt.ItemIsSelectable | qc.Qt.ItemIsEditable)
            screenShot = info.get('screenShot')
            icon = qg.QIcon(screenShot)
            item.setIcon(icon)
            if name.endswith('_FP'):
                self.faceList_wdg.addItem(item)
            elif name.endswith('_BP'):
                self.bodyList_wdg.addItem(item)

    def refreshMethod(self, listWidget):
        list_widget = listWidget
        files = os.listdir(DIRECTORY)
        toCheck = [f.replace('.json', '') for f in files if not f.endswith('.jpg')]
        toDelete = []

        for idx in range(list_widget.count()):
            toDelete.append([idx, list_widget.item(idx).text()])

        checker = []
        for a, b in [(a, b) for a in toCheck for b in toDelete]:
            if b[1] == a:
                checker.append(b)

        this = [x.pop() for x in toDelete if x not in checker]

        for itm in this:
            item = list_widget.findItems(itm, qc.Qt.MatchExactly)[0]
            row = list_widget.row(item)
            list_widget.takeItem(row)

    def connectRefreshMethod(self):
        self.refreshMethod(self.faceList_wdg)
        self.refreshMethod(self.bodyList_wdg)

#############################################################################################################
#
#


class ListWidgetColt(qg.QListWidget):
    left_clicked = qc.Signal(int)
    right_clicked = qc.Signal(int)
    doubleClickSignal = Signal()

    def __init__(self, *args, **kwargs):
        super(ListWidgetColt, self).__init__(*args, **kwargs)
        self.setFont(FONT)
        size = 60
        buffer = 60

        self.setUpdatesEnabled(True)
        self.setFrameShape(qg.QFrame.NoFrame)
        self.setViewMode(qg.QListWidget.IconMode)
        self.setIconSize(qc.QSize(size, size))
        self.setResizeMode(qg.QListWidget.Adjust)
        self.setGridSize(qc.QSize(size + buffer, size + buffer))
        self.Timer = qc.QTimer()
        self.Timer.setInterval(250)
        self.Timer.setSingleShot(True)
        self.Timer.timeout.connect(self.timeout)
        self.left_click_count = self.right_click_count = 0
        self.setContextMenuPolicy(qc.Qt.CustomContextMenu)
        # < -- DELEGATE HERE
        self.delegate = MyDelegate()
        self.setItemDelegate(self.delegate)

    def mouseReleaseEvent(self, event):
        super(ListWidgetColt, self).mouseReleaseEvent(event)
        self.setSelectionMode(qg.QAbstractItemView.ExtendedSelection)
        event.accept()

    def mousePressEvent(self, event):
        super(ListWidgetColt, self).mousePressEvent(event)
        self.setSelectionMode(qg.QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(qg.QAbstractItemView.NoDragDrop)
        if event.button() == qc.Qt.LeftButton:
            self.left_click_count += 1
            if not self.Timer.isActive():
                self.Timer.start()
                if self.itemAt(event.pos()) is None:
                    self.clearSelection()
                    self.clearFocus()
            event.accept()

        if event.button() == qc.Qt.RightButton:
            self.right_click_count += 1
            if not self.Timer.isActive():
                self.Timer.start()
                if self.itemAt(event.pos()) is None:
                    self.clearSelection()
                    self.clearFocus()
                if self.itemAt(event.pos()) is not None:
                    self.contextMenu(event.pos())
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == qc.Qt.LeftButton:
            self.itemDoubleClicked.emit(self.currentItem())
            # print(self.itemAt(event.pos()))
            if self.itemAt(event.pos()) is None:
                self.clearSelection()
                self.clearFocus()
            event.accept()

    def timeout(self):
        if self.left_click_count >= self.right_click_count:
            self.left_clicked.emit(self.left_click_count)
        else:
            self.right_clicked.emit(self.right_click_count)
        self.left_click_count = self.right_click_count = 0

    def contextMenu(self, point):
        self.setSelectionMode(qg.QAbstractItemView.SingleSelection)
        popup = ColtMenu.ContextColt(self.itemAt(point))
        popup.exec_(self.mapToGlobal(point))
        self.delegate.closeEditor.connect(lambda: popup.renameFiles())


####################################################################
class MyDelegate(qg.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = qg.QLineEdit(parent)
        reg_ex = qc.QRegExp("^(?!^_)[a-zA-Z0-9_]+")
        textValidator = qg.QRegExpValidator(reg_ex, editor)
        editor.setValidator(textValidator)
        editor.setAttribute(qc.Qt.WA_DeleteOnClose)
        return editor
        return super(MyDelegate, self).createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        # Gets display text if edit data hasn't been set.
        text = index.data(qc.Qt.EditRole) or index.data(qc.Qt.DisplayRole)
        editor.setText(text)
