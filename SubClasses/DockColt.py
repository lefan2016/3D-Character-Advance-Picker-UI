from PySide import QtCore as qc
from PySide import QtGui as qg
################################################################################################################
STYLE =  """QDock
        {
            background : qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgb(53, 57, 60), stop:1 rgb(33, 34, 36));
        }"""

#---------------------------------------------------------------------------------#
# This is where everything starts
class DockColt(qg.QDockWidget):
    def __init__(self, *args, **kwargs):
        super(DockColt,self).__init__(*args, **kwargs)

        self.setStyleSheet(STYLE)
        self.setMaximumWidth(735)
        self.setAcceptDrops(True)
        self.setFeatures(0x00)
        self.setLayout(qg.QVBoxLayout())

    def catchProcess(self, value):
        if value:
            geometry = self.geometry()
            #print(geometry)
            height   = geometry.height()
            width    = geometry.width()
            x, y, _, _ = geometry.getCoords()
            self.setGeometry(x,y,500,height)
            self.adjustSize()
            self.repaint()

        else:
            pass

    def ResizeEvent(self, event):
        super(DockColt, self).resizeEvent(event)
        #print(self.size())
