from PySide import QtCore as qc
from PySide import QtGui as qg


#---------------------------------------------------------------------------------#
style_sheet_file = """
                    QTabWidget::pane { /* The tab widget frame */
                    border-top: 2px solid #C2C7CB;
                    font-family: Calibri
                    }
                    QTabWidget::tab-bar {
                    left: 10px; /* move to the right by 5px */
                    }
                    /* Style the tab using the tab sub-control. Note that it reads QTabBar _not_ QTabWidget */
                    QTabBar::tab {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgb(53, 57, 60), stop:1 rgb(33, 34, 36));
                    border: 0.5px solid black;
                    border-bottom-color: #C2C7CB; /* same as the pane color */
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    min-width: 8ex;
                    padding: 2px;
                    }
                    QTabBar::tab:selected, QTabBar::tab:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgb(20, 21, 23), stop:1 rgb(48, 49, 51));
                    }
                    QTabBar::tab:selected {
                    border: 1px solid black;
                    border-color: black;
                    border-bottom-color: rgb(125, 250, 100); /* same as pane color */
                    }
                    QTabBar::tab:!selected {
                    margin-top: 2px; /* make non-selected tabs look smaller */
                    }
                    QTabBar::tab:selected { /* expand/overlap to the left and right by 4px */ margin-left: +0.5px; margin-right: +0.5px; } QTabBar::tab:first:selected { margin-left: 0; /* the first selected tab has nothing to overlap with on the left */ } QTabBar::tab:last:selected { margin-right: 0; /* the last selected tab has nothing to overlap with on the right */ } QTabBar::tab:only-one { margin: 0; /* if there is only one tab, we don't want overlapping margins */
                    }
                    QTabBar::tab:selected { font-size : 11.2px; color: gray;}"""


#---------------------------------------------------------------------------------#

style_sheet_file_02 = """
                    QTabWidget::pane { /* The tab widget frame */
                    border-top: 1px solid #C2C7CB;
                    font-family: Calibri
                    }

                    QTabWidget::tab-bar {
                    left: 10px; /* move to the right by 5px */
                    }

                    /* Style the tab using the tab sub-control. Note that it reads QTabBar _not_ QTabWidget */
                    QTabBar::tab {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgb(53, 57, 60), stop:1 rgb(33, 34, 36));
                    border: 0.5px solid black;
                    border-bottom-color: #C2C7CB; /* same as the pane color */
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    min-width: 8ex;
                    padding: 2px;
                    }
                    QTabBar::tab:selected, QTabBar::tab:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgb(20, 21, 23), stop:1 rgb(48, 49, 51));
                    }
                    QTabBar::tab:selected {
                    border: 1px solid black;
                    border-color: black;
                    border-bottom-color: rgb(125, 250, 100); /* same as pane color */
                    }
                    QTabBar::tab:!selected {
                    margin-top: 2px; /* make non-selected tabs look smaller */
                    }
                    QTabBar::tab:selected { /* expand/overlap to the left and right by 4px */ margin-left: +0.5px; margin-right: +0.5px; } QTabBar::tab:first:selected { margin-left: 0; /* the first selected tab has nothing to overlap with on the left */ } QTabBar::tab:last:selected { margin-right: 0; /* the last selected tab has nothing to overlap with on the right */ } QTabBar::tab:only-one { margin: 0; /* if there is only one tab, we don't want overlapping margins */
                    }
                    QTabBar::tab:selected { font-size : 11.2px; color: gray;}"""



#---------------------------------------------------------------------------------#
TABINDEX = int()

def getTabIndex(index):
    global TABINDEX
    if index == -1 or index == TABINDEX:
        return
    TABINDEX = index
    #print (TABINDEX)
    return TABINDEX

class ColtTab(qg.QTabWidget):
    def __init__(self):
        super(ColtTab,self).__init__()

        self.setObjectName('coltTab')
        self.setAcceptDrops(True)
        self.tabBar = self.tabBar()
        self.tabBar.setMouseTracking(True)
        self.setDocumentMode(True)
        self.indexTab = int()
        self.setMovable(True)
        self.setStyleSheet(style_sheet_file)


    # hovering over tabs and show then on the fly...
    def eventFilter(self, obj, event):
        if obj == self.tabBar:
            if event.type() == qc.QEvent.MouseMove:
                index=self.tabBar.tabAt(event.pos())
                self.tabBar.setCurrentIndex (index)
                event.accept()
                return True
            else:
                return
        else:
            return

    ##################################
    # Events
    #
    def mouseMoveEvent(self, e):
        if e.buttons() != qc.Qt.MiddleButton:
            return

        globalPos = self.mapToGlobal(e.pos())
        #print(globalPos)
        tabBar = self.tabBar
        #print(tabBar)
        posInTab = tabBar.mapFromGlobal(globalPos)
        #print(posInTab)
        self.indexTab = tabBar.tabAt(e.pos())
        #print(self.indexTab)
        tabRect = tabBar.tabRect(self.indexTab)
        #print(tabRect)
        #print(tabRect.size())

        pixmap = qg.QPixmap(tabRect.size())
        tabBar.render(pixmap,qc.QPoint(),qg.QRegion(tabRect))
        mimeData = qc.QMimeData()
        drag = qg.QDrag(tabBar)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        cursor = qg.QCursor(qc.Qt.OpenHandCursor)
        drag.setHotSpot(e.pos() - posInTab)
        drag.setDragCursor(cursor.pixmap(),qc.Qt.MoveAction)
        dropAction = drag.exec_(qc.Qt.MoveAction)


    def mousePressEvent(self, e):
        if e.button() == qc.Qt.RightButton:
            self.tabBar.installEventFilter(self)
            #print('Right button pressed')
            e.accept()

        super(ColtTab, self).mousePressEvent(e)


    def dragEnterEvent(self, e):
        e.accept()
        if e.source().parentWidget() != self:
            return

        # Helpper function for retreaving the Tab index into a global Var
        getTabIndex(self.indexOf(self.widget(self.indexTab)))


    def dragLeaveEvent(self,e):
        e.accept()


    def dropEvent(self, e):
        if e.source().parentWidget() == self:
            return

        e.setDropAction(qc.Qt.MoveAction)
        e.accept()
        counter = self.count()

        if counter == 0:
            self.addTab(e.source().parentWidget().widget(TABINDEX),e.source().tabText(TABINDEX))
        else:
            self.insertTab(counter + 1 ,e.source().parentWidget().widget(TABINDEX),e.source().tabText(TABINDEX))

        print ('Tab dropped')

    def mouseReleaseEvent(self, e):
        if e.button() == qc.Qt.RightButton:
            #print('Right button released')
            self.tabBar.removeEventFilter(self)
            e.accept()

        super(ColtTab, self).mouseReleaseEvent(e)


    #---------------------------------------------------------------------------------#
