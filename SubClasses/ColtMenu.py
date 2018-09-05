from PySide import QtCore as qc
from PySide import QtGui as qg
try:
    from HitchAnimationModule.LogicData import BookMarksLogic
    import maya.cmds as cmds
    import maya.mel as mel
except:
    pass

import os
import json

###################################################################################################
# Globals
DIRECTORY = os.path.join(cmds.internalVar(usd=1), 'HitchAnimationModule', 'StoredData')
###################################################################################################
# -------------------------------------------------------------#
CSS = """QMenu
        {
            background : qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgb(53, 57, 60), stop:1 rgb(33, 34, 36));
            shadow : rgb(9, 10, 12);
            border: 1px solid rgb(9, 10, 12);
            border-radius: 2px;
            padding-top : 2px;
            padding-bottom : 2px;
            padding-left : 0px;
            padding-right : 0px;
            color : rgba(202, 207, 210, 255);

        }


        QMenu::item:selected
        {
            color : rgba(150,225,100,255);
            background-color: rgba(255, 255, 255,25);
        }"""
# -------------------------------------------------------------#


class ColtMenu(qg.QMenu):
    def __init__(self, *args, **kwargs):
        super(ColtMenu, self).__init__(*args, **kwargs)
        self.setStyleSheet(CSS)

    def enterEvent(self, event):
        super(ColtMenu, self).enterEvent(event)
        event.accept()

    def mouseMoveEvent(self, event):
        super(ColtMenu, self).mouseMoveEvent(event)
        # print("On Hover") # event.pos().x(), event.pos().y()
        #action = self.actionAt(event.pos())
        event.accept()

    def mousePressEvent(self, event):
        super(ColtMenu, self).mousePressEvent(event)
        if event.button() == qc.Qt.LeftButton:
            event.accept()

##########################################################
##########################################################


class ContextColt(ColtMenu):
    def __init__(self, item):
        super(ContextColt, self).__init__()
        self.POSER = BookMarksLogic.PoserLibrary()
        self.setObjectName('ContextColtClass')

        self.item = item
        self.ItemOldName = self.item.text()
        self.loadAct = qg.QAction('Load', self)
        self.addAction(self.loadAct)
        self.renameAct = qg.QAction('Rename', self)
        self.addAction(self.renameAct)
        self.deleteAct = qg.QAction('Delete', self)
        self.addAction(self.deleteAct)

        self.loadAct.triggered.connect(self.loadActionMethod)
        self.renameAct.triggered.connect(self.renameActionMethod)
        self.deleteAct.triggered.connect(self.deleteActionMethod)

    def loadActionMethod(self):
        print('loading ...')
        item = self.item.text()
        self.loadPath(item)

    def renameActionMethod(self):
        print('renaming..')
        self.item.listWidget().editItem(self.item)

    def deleteActionMethod(self):
        print('deleting...')
        bookMarkClass = self.getParents()
        bookMarkClass.deleteItems()

    def loadPath(self, name):
        path = os.path.join(DIRECTORY, "{}{}".format(name, '.json'))
        with open(path, 'r') as f:
            info = json.load(f)
            # pprint.pprint(info)
            self.POSER.LoadPose(info)

    def renameFiles(self, dir=DIRECTORY):
        if not os.path.exists(dir):
            return

        dummyItem = ''
        try:
            if self.item.listWidget().objectName().startswith('face'):
                if self.item.text().endswith('_FP'):
                    dummyItem = self.item.text()
                else:
                    dummyItem = self.item.text() + '_FP'

            if self.item.listWidget().objectName().startswith('body'):
                if self.item.text().endswith('_BP'):
                    dummyItem = self.item.text()
                else:
                    dummyItem = self.item.text() + '_BP'
        except:
            pass

        try:
            file2get = self.ItemOldName + '.json'
            files = os.listdir(dir)

            jsonData = [f for f in files if f == file2get][0]
            path = os.path.join(dir, jsonData)
            newPath = os.path.join(dir, dummyItem + '.json')
            replaceData = {}

            with open(path, 'r') as f:
                replaceData = json.load(f)

            with open(newPath, 'w') as f:
                json.dump(replaceData, f, indent=4)

            os.remove(path)
            self.item.setText(dummyItem)
        except:
            pass

    def getParents(self):
        scrollArea = self.item.listWidget().parent()
        ScroolWidget = scrollArea.parent()
        bookClass = ScroolWidget.parent().parent()
        return bookClass

    def leaveEvent(self, event):
        self.close()
        self.deleteLater()
        del(self)


##########################################################################################################
class ContextChannelBoxMenu(qg.QMenu):
    def __init__(self, item):
        super(ContextChannelBoxMenu, self).__init__()
        self.setStyleSheet(CSS)
        self.setObjectName('ContextChannelBoxMenu')
        self.node = cmds.ls(sl=True, tr=True)[0]
        self.item = item
        self.keyframe = qg.QAction('- Keyframe', self)
        self.addAction(self.keyframe)
        self.cut_keyframe = qg.QAction('- Cut Keyframe', self)
        self.addAction(self.cut_keyframe)
        self.break_connection = qg.QAction('- Break Connections', self)
        self.addAction(self.break_connection)

        self.keyframe.triggered.connect(self.set_keyframes)
        self.cut_keyframe.triggered.connect(lambda: self.set_keyframes(cut=True))
        self.break_connection.triggered.connect(self.breakConnections)

    ###############################################################################
    def set_keyframes(self, cut=False):
        node = self.node
        lista = self.item
        channel = lista[0][0].lower() + lista[0][1:]
        attributo = node + '.' + channel
        value = lista[1]
        timeVal = cmds.currentTime(q=True)
        if not cut:
            cmds.setKeyframe(attributo, time=[timeVal, timeVal], value=float(value))
        else:
            cmds.cutKey(attributo, time=(timeVal, timeVal), clear=True)

    def breakConnections(self):
        node = self.node
        lista = self.item
        channel = lista[0][0].lower() + lista[0][1:]
        attributo = node + '.' + channel
        mel.eval("source channelBoxCommand; CBdeleteConnection \"%s\"" % attributo)

    def leaveEvent(self, event):
        self.close()
        self.deleteLater()
        del(self)
