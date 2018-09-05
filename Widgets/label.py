import PySide.QtCore as qc
import PySide.QtGui as qg
from PySide.QtGui import QPen, QColor, QBrush, QLinearGradient
try:
    import maya.utils as utils
except:
    pass
#-------------------------------------------------------------#
class CustomLabel(qg.QLabel):
    _pen_text = QPen(QColor(180, 255, 180,200), 1, qc.Qt.SolidLine)
    _pen_Shadow = QPen(QColor(9, 10, 12), 1, qc.Qt.SolidLine)
    _pen_border = QPen(QColor(9, 10, 12), 2, qc.Qt.SolidLine)
    _pen_clear = QPen(QColor(0, 0, 0, 0), 1, qc.Qt.SolidLine)

    _fontSize = 12
    _fontMargin = 2
    def __init__(self, *args, **kwargs):
        qg.QLabel.__init__(self,*args,**kwargs)
        font = qg.QFont()
        font.setPointSize(self._fontSize)
        font.setFamily('Calibri')
        self.setFont(font)
        self.setMargin(self._fontMargin)
        self.setStyleSheet("background-color: transparent;")

    def paintEvent(self, event):
        painter = qg.QPainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width = option.rect.width() - 1

        painter.setRenderHint(qg.QPainter.Antialiasing)
        painter.setRenderHint(qg.QPainter.TextAntialiasing)

        alignment = (qc.Qt.AlignHCenter | qc.Qt.AlignVCenter)

        text = self.text()
        if text == '': return

        font = self.font()
        font_metrics = qg.QFontMetrics(font)
        text_width = font_metrics.width(text)
        text_height = font.pointSize()

        textPath = qg.QPainterPath()
        textPath.addText((width - text_width) / 2, height - ((height - text_height) / 2) , font, text)

        if self.isEnabled():
            pens_text   = self._pen_text
            pens_shadow = self._pen_Shadow


            painter.setPen(pens_shadow)
            painter.drawPath(textPath)
            painter.setPen(pens_text)
            painter.drawText(x,y,width,height,alignment,text)

##########################################################################################
class CustomClearLabel(CustomLabel):
    _pen_text = QPen(QColor(180, 200, 180,250), 2, qc.Qt.SolidLine)
    _fontSize = 14
    _fontMargin = 4

    def __init__(self,*args, **kwargs):
        super(CustomClearLabel, self).__init__(*args, **kwargs)


class CustomShortLabel(CustomLabel):
    _pen_text = QPen(QColor(250, 250, 250,220), 1, qc.Qt.SolidLine)
    _fontSize = 12
    _fontMargin = 3

    def __init__(self,*args, **kwargs):
        super(CustomShortLabel, self).__init__(*args, **kwargs)

class CustomBlackLabel(CustomLabel):
    _pen_text = QPen(QColor(220, 220, 220,240), 1, qc.Qt.SolidLine)
    _fontSize = 15
    _fontMargin = 8


    def __init__(self,*args, **kwargs):
        super(CustomBlackLabel, self).__init__(*args, **kwargs)
        self.label =  qg.QLabel()
        self.setLayout(qg.QVBoxLayout())
        self.layout().addWidget(self.label)
        self.label.setStyleSheet("""background : qlineargradient(x1:0, y1:0, x2:0, y2:0, stop:0.0 rgba(220, 220, 220,35),
         stop:0.5 rgba(20, 20, 20,75), stop:1 rgba(220, 220, 220,35));""")
        self.label.setFixedHeight(60)
        self.label.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Expanding)
        self.layout().setContentsMargins(0,0,0,0)
        self.label.installEventFilter(self)


class CustomCBLabel(CustomLabel):
    _pen_text = QPen(QColor(240, 240, 240,250), 1, qc.Qt.SolidLine)
    _fontMargin = 2

    def __init__(self,*args, **kwargs):
        super(CustomCBLabel, self).__init__(*args, **kwargs)

############################################################################################

class CustomFBX_Label(qg.QLabel):
    _pen_text = QPen(QColor(180, 255, 180,200), 1, qc.Qt.SolidLine)
    _pen_Shadow = QPen(QColor(9, 10, 12), 1, qc.Qt.SolidLine)
    _pen_border = QPen(QColor(9, 10, 12), 2, qc.Qt.SolidLine)
    _pen_clear = QPen(QColor(0, 0, 0, 0), 1, qc.Qt.SolidLine)

    _fontSize = 16
    _fontMargin = 2

    def __init__(self, *args, **kwargs):
        super(CustomFBX_Label, self).__init__(*args,**kwargs)


        font = qg.QFont()
        font.setPointSize(self._fontSize)
        font.setFamily('Source Code Pro SemiBold')
        self.setFont(font)
        self.setMargin(self._fontMargin)
        self.setStyleSheet("background-color: transparent;")
        self.setMargin(self._fontMargin)
        #self.setStyleSheet("background-color: transparent;")

    def paintEvent(self, event):
        painter = qg.QPainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width = option.rect.width() - 1

        painter.setRenderHint(qg.QPainter.Antialiasing)
        painter.setRenderHint(qg.QPainter.TextAntialiasing)

        alignment = (qc.Qt.AlignHCenter | qc.Qt.AlignVCenter)

        text = self.text()
        if text == '': return

        font = self.font()
        font_metrics = qg.QFontMetrics(font)
        text_width = font_metrics.width(text)
        text_height = font.pointSize()

        textPath = qg.QPainterPath()
        textPath.addText((width - text_width) / 2, height - ((height - text_height) / 2) , font, text)

        if self.isEnabled():
            pens_text   = self._pen_text
            pens_shadow = self._pen_Shadow


            painter.setPen(pens_shadow)
            painter.drawPath(textPath)
            painter.setPen(pens_text)
            painter.drawText(x,y,width,height,alignment,text)
