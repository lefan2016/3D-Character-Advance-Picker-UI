from PySide import QtCore as qc
from PySide import QtGui as qg
#---------------------------------------------------------------------------------#
class MyDial(qg.QDial):
    style =''' 
    QDial
    {
        background-color:QLinearGradient( 
            x1: 0.177, y1: 0.004, x2: 0.831, y2: 0.911, 
            stop: 0 white, 
            stop: 0.061 white, 
            stop: 0.066 lightgray, 
            stop: 0.5 #242424, 
            stop: 0.505 #000000,
            stop: 0.827 #040404,
            stop: 0.966 #292929,
            stop: 0.983 #2e2e2e
        );
    }
    '''
    def __init__(self, parent=None):
        super(MyDial, self).__init__(parent)

        self.setStyleSheet(self.style)

        self.setRange(0,100)
        self.setValue(0)
        self.setWrapping(True) # Smooth transition from 99 to 0
        self.setNotchesVisible(True)

     #---------------------------------------------------------------------------------#