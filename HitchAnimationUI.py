import maya.cmds as cmds
import pymel.core as pm
import maya.OpenMaya as om
import maya.OpenMayaUI as mui
import shiboken as shi
from PySide import QtCore as qc
from PySide import QtGui as qg
from functools import partial
import time
import random
from HitchAnimationModule.Widgets import spliter
from HitchAnimationModule.Widgets import Tabs
from HitchAnimationModule.Widgets import button
from HitchAnimationModule.SubClasses import viewportClass
from HitchAnimationModule.SubClasses import HeadPicker
from HitchAnimationModule.SubClasses import BodyPicker
from HitchAnimationModule.SubClasses import BookMarks
from HitchAnimationModule.SubClasses import ColtMenu
from HitchAnimationModule.SubClasses import DockColt
from HitchAnimationModule.SubClasses import TopPanel
from HitchAnimationModule.SubClasses import LeftPanel
from HitchAnimationModule.LogicData import refreshUI
from HitchAnimationModule.SubClasses import ImportReference
import os
import sys

reload(TopPanel)
reload(viewportClass)
reload(button)
reload(spliter)
reload(HeadPicker)
reload(BodyPicker)
reload(Tabs)
reload(LeftPanel)

#---------------------------------------------------------------------------------#
HITCH_UI = None
windowTitle = "Hitch Animation Manager"
windowObject = "HitchAnimationUI_Object"

STYLESHEET = os.path.join(pm.internalVar(usd=1), 'HitchAnimationModule', 'StyleSheets', 'scheme.txt')
HEADERPIXMAP = os.path.join(pm.internalVar(usd=1), 'HitchAnimationModule', 'Icons', 'hitchNameUIHeaderNoBackground.png')
WINDOWICON = os.path.join(pm.internalVar(usd=1), 'HitchAnimationModule', 'Icons', 'Hitch_FaceForLogo.png')

#---------------------------------------------------------------------------------#
# delete ANY maya child with given object name to mantain clean the memory
#


def deleteFromGlobal():
    mayaMainWindowPtr = mui.MQtUtil.mainWindow()
    mayaMainWindow = shi.wrapInstance(long(mayaMainWindowPtr), qg.QMainWindow)  # Important that it's QMainWindow, and not QWidget
    try:
        # Go through main window's children to find any previous instances
        for obj in mayaMainWindow.children():
            # print(obj.objectName())
            if isinstance(obj, qg.QMainWindow):
                if obj.objectName() == windowObject:
                    # print obj
                    # print obj.objectName()
                    obj.setParent(None)
                    obj.deleteLater()
                    del(obj)
                    print('Object Deleted')
    except:
        pass
#---------------------------------------------------------------------------------#


def getMayaWindow():
    mainWinPtr = mui.MQtUtil.mainWindow()
    return shi.wrapInstance(long(mainWinPtr), qg.QWidget)

#---------------------------------------------------------------------------------#
# This is where everything starts


class HitchAnimUI(qg.QMainWindow):
    def __init__(self, parent=getMayaWindow()):
        super(HitchAnimUI, self).__init__(parent)

        self.setAttribute(qc.Qt.WA_DeleteOnClose)
        self.extraDialog = ''
        self.tabIndex = None

        style_sheet_file = STYLESHEET
        with open(style_sheet_file, 'r') as styleSheet:
            data = str(styleSheet.read())
            self.setStyleSheet(data)

        self.setObjectName(windowObject)
        self.setWindowTitle(windowTitle)
        self.setMinimumWidth(1000)
        self.setMinimumHeight(500)
        self.resize(1650, 1000)  # re-size the window
        self.setWindowIcon(qg.QIcon(os.path.join('icon', WINDOWICON)))

        centralWidget = qg.QWidget()
        centralWidget.setObjectName('centralWidget')
        mainHhorizontal_lyt = qg.QHBoxLayout()
        mainHhorizontal_lyt.setContentsMargins(5, 5, 5, 5)
        mainHhorizontal_lyt.setSpacing(0)
        centralWidget.setLayout(mainHhorizontal_lyt)

        mainHhorizontal_lyt.setObjectName('mainHhorizontal_lyt')
        central_layout = qg.QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setObjectName('central_layout')

        self._importDialog_open = False

        ####################
        # QGraphics Escene
        #
        self.graphics_scene = qg.QGraphicsScene()
        self.graphics_view = qg.QGraphicsView()
        self.graphics_view.cacheMode()
        self.graphics_view.setCacheMode(qg.QGraphicsItem.  DeviceCoordinateCache)
        self.graphics_view.setOptimizationFlags(qg.QGraphicsView.DontSavePainterState)
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.graphics_view.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.graphics_view.setFocusPolicy(qc.Qt.NoFocus)
        self.graphics_view.setStyleSheet("QGraphicsView {border-style: none;}")
        self.graphics_view.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Minimum)
        self.setCentralWidget(self.graphics_view)
        self.graphics_view.setLayout(mainHhorizontal_lyt)

        ###########################################
        # Left Menu Panel
        #
        leftPanel = LeftPanel.LeftPanel()
        mainHhorizontal_lyt.addWidget(leftPanel)
        mainHhorizontal_lyt.addLayout(central_layout)

        ###########################################
        # Menu Bar and action gestion ..
        #
        menuBar = qg.QMenuBar()

        File_menu = ColtMenu.ColtMenu('File')
        Colt_menu = ColtMenu.ColtMenu('About Me')

        menuBar.addMenu(File_menu)
        menuBar.addMenu(Colt_menu)

        referenceAction = qg.QAction('Import Reference', self)
        refreshAction = qg.QAction('Refresh UI', self)
        closeAction = qg.QAction('Exit', self)
        ExportAnimAction = qg.QAction('Export Animation', self)
        AboutMeAction = qg.QAction('About NestorColt', self)

        File_menu.addAction(referenceAction)
        File_menu.addAction(refreshAction)
        File_menu.addAction(closeAction)
        Colt_menu.addAction(AboutMeAction)

        menuBar.addSeparator()
        self.setMenuBar(menuBar)

        # connect Accions from menu bar
        #

        # referenceAction.triggered.connect(self.importReferenceRig)
        closeAction.triggered.connect(self.close)
        refreshAction.triggered.connect(self.refreshScene)
        referenceAction.triggered.connect(self.importReferenceUI)
        AboutMeAction.triggered.connect(lambda: AboutMeDialog(parent=self))

        ############################
        # widget for dockWidget
        #
        self.insideDock_wgt = qg.QWidget()
        self.insideDock_wgt_lyt = qg.QVBoxLayout(self.insideDock_wgt)

        self.dockTab_dgt = Tabs.ColtTab()
        self.dockTab_dgt.setObjectName('DockTabWidget')
        self.restore_btn = button.CustomButton(' Restore ')
        self.insideDock_wgt_lyt.addWidget(self.restore_btn)
        self.insideDock_wgt_lyt.addWidget(self.dockTab_dgt)
        self.insideDock_wgt_lyt.setSpacing(10)
        self.insideDock_wgt_lyt.setContentsMargins(0, 0, 0, 0)
        self.restore_btn.setEnabled(False)

        ############################
        #   Q Dock Widgets
        #
        self.dock = DockColt.DockColt('Dock Area', self)
        self.addDockWidget(qc.Qt.RightDockWidgetArea, self.dock)
        self.dock.setWidget(self.insideDock_wgt)

        #############################
        # Animation of layouts
        #

        ###########################################
        # Top Menu Panel
        #
        topPanel = TopPanel.TopPanel()
        central_layout.addWidget(topPanel)
        central_layout.addSpacing(5)
        ######################
        # tab container
        #
        self.tabWidget = Tabs.ColtTab()
        self.tabWidget.setObjectName('self.tabWidget')
        self.tab_layout = qg.QVBoxLayout(self.tabWidget)
        self.tab_layout.setObjectName('tab_layout')
        central_layout.addWidget(self.tabWidget)

        #######################
        # ViewportTab
        #
        self.viewport_tab = viewportClass.ViewportTab()
        self.tabWidget.addTab(self.viewport_tab, '- 1 Viewport ')

        #######################
        # Face picker Tab
        #

        self.facePicker = HeadPicker.HeadPicker()
        self.tabWidget.addTab(self.facePicker, '- 2 FacePicker ')

        #######################
        # Body Picker Tab
        #
        self.bodyPicker = BodyPicker.BodyPicker()
        self.tabWidget.addTab(self.bodyPicker, '- 3 BodyPicker ')

        #######################
        # BookMarks Tab
        #
        self.bookMarks = BookMarks.BookMarks()
        self.tabWidget.addTab(self.bookMarks, '- 4 Bookmarks ')

    #---------------------------------------------------------------------------------#
        # connect widgets slots
        self.dockTab_dgt.currentChanged.connect(self.activateButtons)
        self.restore_btn.clicked.connect(self.restore_tabsFunction)
        self.tabWidget.currentChanged.connect(self.fix_some_focuses)

        ###########################
        # Callback fron escene
        #
        self._callBackID = om.MEventMessage.addEventCallback('SceneOpened', self.re_openScene)
        delCallBack = partial(om.MMessage.removeCallback, self._callBackID)
        self.destroyed.connect(delCallBack)
   #----------------------------------------------------------------------------------#

    def fix_some_focuses(self):
        self.bodyPicker.clear_focus()
        self.facePicker.clear_focus()

    def importReferenceUI(self):
        if not self._importDialog_open:
            self._importDialog_open = True
            UI = ImportReference.ImportReferenceWindow(parent=self)
            UI.show()

    def re_openScene(self, *args, **kwargs):
        widgetPort = self.findChildren(qg.QWidget, 'ViewportClass')[0]
        widgetPort.re_create_panel()
        self.refreshScene()

    def refreshScene(self):
        refreshUI.refresh()

    def activateButtons(self):
        count = self.dockTab_dgt.count()
        if count > 0:
            self.restore_btn.setEnabled(True)

        else:
            self.restore_btn.setEnabled(False)

    def restore_tabsFunction(self):
        count = self.dockTab_dgt.count()
        tabs = []
        for idx in range(count):
            obj = [lt for lt in self.dockTab_dgt.tabText(idx) if lt.isdigit()]
            num = int(obj[0])
            tabs.append([num, self.dockTab_dgt.widget(idx), self.dockTab_dgt.tabText(idx)])

        def getKey(item):
            return item[0]

        for tab in sorted(tabs, key=getKey):
            self.tabWidget.insertTab(tab[0] - 1, tab[1], tab[2])

    #---------------------------------------------------------------------------------------------------------------------------------------#
    def showEvent(self, event):
        super(HitchAnimUI, self).showEvent(event)
        # maya can lag in how it repaints UI. Force it to repaint
        # when we show the window.
        self.viewport_tab.Viewport_maya.repaint()

    def closeEvent(self, event):
        super(HitchAnimUI, self).closeEvent(event)
        deleteFromGlobal()

#---------------------------------------------------------------------------------#


class AboutMeDialog(qg.QDialog):
    leftClick = False

    def __init__(self, parent):
        super(AboutMeDialog, self).__init__(parent)

        self.setLayout(qg.QStackedLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setFixedWidth(800)
        self.setFixedHeight(440)
        self.setStyleSheet("background-color: rgba(1,1,1,200);")

        self.setAttribute(qc.Qt.WA_DeleteOnClose)
        self.setModal(True)

        route = os.path.join(pm.internalVar(usd=1), 'HitchAnimationModule', 'Icons', 'Hitch_UI_aboutMe.jpg')
        pixmap = qg.QPixmap(route)
        scaled = pixmap.scaled(self.width(), self.height(), qc.Qt.KeepAspectRatio, qc.Qt.SmoothTransformation)

        self.frame = qg.QLabel()
        self.frame.setPixmap(scaled)
        self.frame.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Expanding)

        self.layout().addWidget(self.frame)

        frame_lyt = qg.QVBoxLayout(self.frame)
        frame_lyt.setContentsMargins(0, 0, 0, 0)

        self.layout().setStackingMode(qg.QStackedLayout.StackAll)

        self.close_btn = button.CloseButton()
        self.close_btn.setParent(self)
        self.close_btn.clicked.connect(lambda: self.close())

        self.show()

    def resizeEvent(self, event):
        self.close_btn.move(self.width() - 30, self.y() - 288)
        pixmap = qg.QPixmap(self.size())
        pixmap.fill(qc.Qt.transparent)
        painter = qg.QPainter(pixmap)
        painter.setBrush(qc.Qt.black)
        painter.drawRoundedRect(pixmap.rect(), 12, 12)
        painter.end()

        self.setMask(pixmap.mask())

    def closeEvent(self, event):
        self.deleteLater()
        del (self)

#---------------------------------------------------------------------------------#


def run():
    deleteFromGlobal()
    global HITCH_UI
    if HITCH_UI is None:
        HITCH_UI = HitchAnimUI()
        HITCH_UI.show()


#---------------------------------------------------------------------------------#
if __name__ == '__main__':
    run()
    print ('UI Created...')
