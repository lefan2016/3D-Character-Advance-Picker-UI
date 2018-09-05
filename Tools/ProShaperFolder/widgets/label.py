import PySide.QtCore as qc
import PySide.QtGui as qg
from PySide.QtGui import QPen, QColor, QBrush, QLinearGradient
try:
    import maya.utils as utils
except:
    pass

#-------------------------------------------------------------#

class CustomLabel(qg.QLabel):

    _glowPens = {}
    for index in range(1, 11):
        _glowPens[index] = [QPen(QColor(0, 255, 0, 12 * index), 1, qc.Qt.SolidLine),
                            QPen(QColor(0, 255, 0, 5 * index), 1, qc.Qt.SolidLine),
                            QPen(QColor(0, 255, 0, 2 * index), 1, qc.Qt.SolidLine),
                            QPen(QColor(125, 200, 100), 1, qc.Qt.SolidLine)]

    _pen_text = QPen(QColor(200, 200, 200), 1, qc.Qt.SolidLine)
    _pen_Shadow = QPen(QColor(9, 10, 12), 1, qc.Qt.SolidLine)
    _pen_border = QPen(QColor(9, 10, 12), 2, qc.Qt.SolidLine)
    _pen_clear = QPen(QColor(0, 0, 0, 0), 1, qc.Qt.SolidLine)

    _penText_disable = QPen(QColor(102, 107, 110), 1, qc.Qt.SolidLine)
    _penShadow_disable = QPen(QColor(0, 0, 0), 1, qc.Qt.SolidLine)

    _brushClear = QBrush(QColor(0, 0, 0, 0))
    _brushBorder = QBrush(QColor(9, 10, 12))

    glow_index = 0

    def __init__(self, *args, **kwargs):
        qg.QLabel.__init__(self,*args,**kwargs)

        font = qg.QFont()
        font.setPointSize(10)
        font.setFamily('Helvetic')
        self.setFont(font)

        self.setMargin(2)
        self._glow_index = 0

    def setGlowValue(self,value):
        self._glow_index = min(max(value / 10, 0), 10)
        utils.executeDeferred(self.update)


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

        else:
            pens_text   = self._penText_disable
            pens_shadow = self._penShadow_disable

        painter.setPen(pens_shadow)
        painter.drawPath(textPath)
        painter.setPen(pens_text)
        painter.drawText(x,y,width,height,alignment,text)

        glow_index = self._glow_index
        glow_pens  = self._glowPens

        if glow_index > 0:
            for index in range(3):
                painter.setPen(glow_pens[glow_index - (glow_index/2)][index])
                painter.drawPath(textPath)

            painter.setPen(glow_pens[glow_index][3])
            painter.drawText(x,y,width,height,alignment,text)
