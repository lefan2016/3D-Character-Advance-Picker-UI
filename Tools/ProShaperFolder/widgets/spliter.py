from PySide import QtCore as qc
from PySide import QtGui as qg

class Splitter(qg.QWidget):
    def __init__(self,text=None,shadow=True,color=(45,45,45)):
        qg.QWidget.__init__(self)
        
        self.setMinimumHeight(2)
        self.setLayout(qg.QHBoxLayout())
        self.layout().setContentsMargins(02,0,02,0)
        self.layout().setSpacing(0)
        self.layout().setAlignment(qc.Qt.AlignVCenter)
        
        first_line = qg.QFrame()
        first_line.setFrameStyle(qg.QFrame.HLine)
        self.layout().addWidget(first_line)
        
        mainColor = 'rgba(%s,%s,%s,255)'%color
        shadowColor = 'rgba(25,25,25,255)'
        
        bottomBorder = ''
        if shadow:
            bottomBorder='border-bottom:1px solid %s;'%shadowColor
        
        
        
        style_sheet = "border:0px solid rgba(0,0,0,0); \
                       background-color: %s; \
                       max-height:1px; \
                       %s"%(mainColor,bottomBorder) 
                       
        first_line.setStyleSheet(style_sheet)


        if text is None:
            return
            
        first_line.setMaximumWidth(10)
        first_line.setFrameStyle(qg.QFrame.HLine)
        first_line.setStyleSheet(style_sheet)
        font = qg.QFont("Helvetica",11)
        font.setBold(True)
        
        textWidth = qg.QFontMetrics(font) 
        width = textWidth.width(text) + 6
        
        label = qg.QLabel()
        label.setText(text)
        label.setFont(font)
        label.setMaximumWidth(width)
        label.setAlignment(qc.Qt.AlignHCenter | qc.Qt.AlignVCenter)
        
        self.layout().addWidget(label)
        
        second_line = qg.QFrame()
        second_line.setFrameStyle(qg.QFrame.HLine)
        second_line.setStyleSheet(style_sheet)
        self.layout().addWidget(second_line)
        
        
        
class SplitterLayout(qg.QHBoxLayout):
    def __init__(self):
        qg.QHBoxLayout.__init__(self)
        
        self.setContentsMargins(40,1,40,1)
        
        splitter = Splitter(shadow=False,color=(35,180,93))
        splitter.setFixedHeight(1)
        self.addWidget(splitter)
        