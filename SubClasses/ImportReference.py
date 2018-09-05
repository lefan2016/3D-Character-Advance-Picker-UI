# -*- coding: utf-8 -*-
import PySide.QtCore as qc
import PySide.QtGui as qg
from PySide.QtGui import QPen, QColor, QBrush, QLinearGradient, QFont, QRadialGradient
try:
    import maya.utils as utils
    import maya.cmds as cmds
    from HitchAnimationModule.Widgets import label
    from HitchAnimationModule.Widgets import button
    from HitchAnimationModule.Widgets import checkBox
    from HitchAnimationModule.Widgets import lineEdit
    from HitchAnimationModule.Widgets import spliter
except:
    pass
import os
import sys
# sys.path.append(r"C:\Program Files\Autodesk\Maya2016\devkit\other\pymel\extras\completion\py")
import maya.cmds as cmds

############################################

X = 0
X2 = 8  # !!!!
Y = 0
Y2 = 30  # !!!!
try:
    FONT = qg.QFont('Calibri', 10, qg.QFont.Bold)
    MAYAICON = os.path.join(cmds.internalVar(usd=1), 'HitchAnimationModule', 'Icons', 'Maya-icon.png')
    WORKSPACE = os.path.join(cmds.workspace(q=True, rd=True, l=True), "scenes")

except:
    pass
#-------------------------------------------------------------#


class ImportReferenceWindow(qg.QDialog):
    leftClick = False

    def __init__(self, parent=None):
        super(ImportReferenceWindow, self).__init__(parent)

        par_center = self.parent().frameGeometry().center()
        self.setLayout(qg.QVBoxLayout(self))
        self.setObjectName('import_reference')
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setFixedSize(600, 500)
        self.move(par_center.x() - (self.width() / 2), par_center.y() - (self.height() / 2))

        self.frame = qg.QFrame()
        self.frame.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Minimum)
        self.frame.setObjectName('importReference_frame')

        self.layout().addWidget(self.frame)
        self.frame.setStyleSheet("""QFrame#importReference_frame { background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(53, 57, 60,255), stop: 0.7 rgba(25,15,05,50), stop: 1.1 rgba(33, 34, 36, 240))};""")

        frame_lyt = qg.QVBoxLayout(self.frame)
        titleLabel = label.CustomClearLabel(' - Import Reference - ')

        close_btn = button.CloseButton()
        close_btn.setStyleSheet("background-color: transparent;")
        close_btn_lyt = qg.QHBoxLayout()
        close_btn_lyt.addWidget(titleLabel)
        close_btn_lyt.addSpacing(170)

        frame_lyt.addLayout(close_btn_lyt)
        close_btn_lyt.setAlignment(qc.Qt.AlignTop | qc.Qt.AlignRight)
        close_btn_lyt.addWidget(close_btn)
        ################################################################
        # LIST WIDGET
        #
        inside_lyt = qg.QHBoxLayout()
        frame_lyt.addLayout(inside_lyt)
        self.list_view_wgt = ListWidgetImport()
        self.list_view_wgt.setMaximumWidth(330)
        inside_lyt.addWidget(self.list_view_wgt)

        ####################################################################
        # RIGHT SIDE
        #
        right_lyt = qg.QVBoxLayout()
        inside_lyt.addLayout(right_lyt)
        right_lyt.setAlignment(qc.Qt.AlignVCenter)
        right_lyt.setSpacing(10)

        self.nameSpace_check = checkBox.CustomCheck(' - Set Name Space String: ')
        self.nameSpace_check.setSizePolicy(qg.QSizePolicy.Maximum, qg.QSizePolicy.Maximum)

        self.prefix_le = lineEdit.Import_LineEdit()
        self.prefix_le.setEnabled(False)
        reg_ex = qc.QRegExp("^(?!^_)[a-zA-Z0-9_:]+")
        textValidator = qg.QRegExpValidator(reg_ex, self.prefix_le)
        self.prefix_le.setValidator(textValidator)
        self.prefix_le.setPlaceholderMessage(' Set Name Space ')

        self.forceName = checkBox.CustomRedCheck('- Force ')
        self.forceName.setSizePolicy(qg.QSizePolicy.Maximum, qg.QSizePolicy.Maximum)
        forceName_lyt = qg.QHBoxLayout()
        forceName_lyt.addWidget(self.forceName)
        forceName_lyt.setAlignment(qc.Qt.AlignRight)
        load_button = button.Customflat_btn(' Load Reference ')
        load_button.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Maximum)

        right_lyt.addWidget(self.nameSpace_check)
        right_lyt.addWidget(self.prefix_le)
        right_lyt.addWidget(load_button)
        right_lyt.addLayout(forceName_lyt)

        ###################################################################
        # END SEPARATOR
        #
        splitter_lyt = spliter.SplitterLayout(content=(20, 1, 20, 0))
        frame_lyt.addLayout(splitter_lyt)
        ###################################################################################################################
        # SIGNALS AND SLOTS :::
        #

        close_btn.clicked.connect(self.close)
        self.nameSpace_check.toggled.connect(self.prefix_le.setEnabled)
        load_button.clicked.connect(self.loadReference)

    #############################################################################################################################
    def populateListWidget(self):
        # Import reference operation
        #
        workSpace_dir = WORKSPACE
        filtered = [file for file in os.listdir(workSpace_dir) if file.endswith('.ma') or file.endswith('.mb')]
        for file in filtered:
            item = qg.QListWidgetItem(file)
            item.setFont(FONT)
            item.setFlags(item.flags() | qc.Qt.ItemIsEnabled | qc.Qt.ItemIsSelectable | qc.Qt.ItemIsEditable)
            mayaIcon = MAYAICON
            icon = qg.QIcon(mayaIcon)
            item.setIcon(icon)
            self.list_view_wgt.addItem(item)

    def loadReference(self, *args, **kwargs):
        fileName = ''
        try:
            fileName = self.list_view_wgt.currentItem().text()
        except:
            cmds.warning('Please select a file to load')
            return

        if fileName is None or fileName == '':
            cmds.warning('Please select a file to load')
            return

        PATHTO = os.path.join(WORKSPACE, fileName)
        lineEditText = self.prefix_le.text()
        nameSpaceCheck = cmds.namespace(exists=':' + lineEditText.strip(' '))
        print(nameSpaceCheck)

        if not nameSpaceCheck or self.forceName.isChecked():
            if not self.nameSpace_check.isChecked():
                cmds.file(PATHTO, reference=True)
                self.close()

            else:
                cmds.file(PATHTO, reference=True, type='mayaAscii', namespace=self.prefix_le.text().strip(' '))
                self.close()

        else:
            cmds.warning('Name space choosen already loaded on file, please set a diferent name space')

    #######################################################################################################################

    def resizeEvent(self, event):
        pixmap = qg.QPixmap(self.size())
        pixmap.fill(qc.Qt.transparent)
        painter = qg.QPainter(pixmap)
        painter.setBrush(qc.Qt.black)
        painter.drawRoundedRect(pixmap.rect(), 12, 12)
        painter.end()

        self.setMask(pixmap.mask())

    def mouseMoveEvent(self, event):
        super(ImportReferenceWindow, self).mouseMoveEvent(event)
        if self.leftClick == True:
            self.move(event.globalPos().x() - X - X2, event.globalPos().y() - Y - Y2)
            event.accept()

    def mousePressEvent(self, event):
        super(ImportReferenceWindow, self).mousePressEvent(event)
        if event.button() == qc.Qt.LeftButton:
            self.leftClick = True
            global X, Y
            X = event.pos().x()
            Y = event.pos().y()
            event.accept()

    def mouseReleaseEvent(self, event):
        super(ImportReferenceWindow, self).mouseReleaseEvent(event)
        self.leftClick = False

    def showEvent(self, event):
        self.populateListWidget()
        event.accept()
        return True

    def closeEvent(self, event):
        self.parentWidget()._importDialog_open = False
        self.list_view_wgt.deleteLater()
        del(self.list_view_wgt)
        self.deleteLater()

#############################################################################################################
#
#


class ListWidgetImport(qg.QListWidget):
    left_clicked = qc.Signal(int)
    right_clicked = qc.Signal(int)
    doubleClickSignal = qc.Signal()
    penTick = qg.QPen(qg.QColor(35, 180, 93), 4, qc.Qt.SolidLine)

    def __init__(self, *args, **kwargs):
        super(ListWidgetImport, self).__init__(*args, **kwargs)
        self.setFont(FONT)
        size = 30
        buffer = 20

        self.setObjectName('listView_import')
        self.setStyleSheet("""#listView_import {background : qlineargradient(x1:0, y1:0, x2:0, y2:0, stop:0.0 rgba(53, 57, 60,125),
         stop:0.5 rgba(33, 34, 36,150),stop:1 rgba(53, 57, 60,125))};""")
        self.setUpdatesEnabled(True)
        self.setFocusPolicy(qc.Qt.NoFocus)
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

        ##############################
        self.delegate = MyDelegate()
        self.setItemDelegate(self.delegate)

    def mouseReleaseEvent(self, event):
        super(ListWidgetImport, self).mouseReleaseEvent(event)
        self.setSelectionMode(qg.QAbstractItemView.ExtendedSelection)
        event.accept()

    def mousePressEvent(self, event):
        super(ListWidgetImport, self).mousePressEvent(event)
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
