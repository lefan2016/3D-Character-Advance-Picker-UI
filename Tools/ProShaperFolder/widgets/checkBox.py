import PySide.QtCore as qc
import PySide.QtGui as qg
from PySide.QtGui import QPen, QColor, QBrush, QLinearGradient
try:
    import maya.utils as utils
except:
    pass
#-------------------------------------------------------------#
class CustomCheck(qg.QCheckBox):

    _glowBrushes = {}
    for index in range(1, 11):
        _glowBrushes[index] = [QBrush(QColor(0, 255, 0,  1 * index)),
                               QBrush(QColor(0, 255, 0,  3 * index)),
                               QBrush(QColor(0, 255, 0, 15 * index)),
                               QBrush(QColor(50, 200, 50 , 25.5 * index))]
    _glowOffBrushes = {}
    for index in range(1, 11):
        _glowOffBrushes[index] = [QBrush(QColor(0, 150, 0,     1 * index)),
                                  QBrush(QColor(0, 150, 0,     6 * index)),
                                  QBrush(QColor(0, 150, 0,     9 * index)),
                                  QBrush(QColor(50, 200, 50 , 12 * index))]

    _disableGlowBrushes = {}
    for index in range(1, 11):
        _disableGlowBrushes[index] = [QBrush(QColor(80, 80, 80,   1   * index)),
                                      QBrush(QColor(80, 80, 80,   5   * index)),
                                      QBrush(QColor(80, 80, 80,  15   * index)),
                                      QBrush(QColor(80, 80, 80, 25.5 * index))]


    _pen_text = QPen(QColor(200, 200, 200), 1, qc.Qt.SolidLine)
    _pen_Shadow = QPen(QColor(9, 10, 12), 1, qc.Qt.SolidLine)
    _pen_border = QPen(QColor(9, 10, 12), 2, qc.Qt.SolidLine)
    _pen_clear = QPen(QColor(0, 0, 0, 0), 1, qc.Qt.SolidLine)

    _penText_disable = QPen(QColor(102, 107, 110), 1, qc.Qt.SolidLine)
    _penShadow_disable = QPen(QColor(0, 0, 0), 1, qc.Qt.SolidLine)

    _brushClear = QBrush(QColor(0, 0, 0, 0))
    _brushBorder = QBrush(QColor(9, 10, 12))

    def __init__(self, *args, **kwargs):
        qg.QCheckBox.__init__(self, *args, **kwargs)

        font = qg.QFont()
        font.setPointSize(9)
        font.setFamily('Helvetic')
        self.setFont(font)

        self.hover = False
        self._glow_index = 0
        self._anim_timer = qc.QTimer()
        self._anim_timer.timeout.connect(self._animateGlow)
        self.setFixedHeight(27)

        self.fontMetrics = qg.QFontMetrics(font)
        self.radius = 5

    def _animateGlow(self):
        if self.hover:
            if self._glow_index >= 10:
                self._glow_index = 10
                while self._glow_index > 8:
                    self._glow_index -= 0.25
                    #print self._glow_index
                    if self._glow_index == 8:
                        self._anim_timer.stop()

            else:
             self._glow_index += 1

        else:
            if self._glow_index <= 0:
                self._glow_index = 0
                self._anim_timer.stop()

            else:
                self._glow_index -= 1

       #print self._glow_index

        utils.executeDeferred(self.update)

#-----------------------------------------------------------------------------------------------#
    def enterEvent(self, event):
        if not self.isEnabled():
            return

        self.hover = True
        self.startAnim()

    def leaveEvent(self, event):
        if not self.isEnabled():
            return

        self.hover = False
        self.startAnim()

    def startAnim(self):
        if self._anim_timer.isActive():
            return

        self._anim_timer.start(20)
#-----------------------------------------------------------------------------------------------------#

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

        glowIndex = self._glow_index

        text = self.text()

        painter.setPen(self._pen_border)
        painter.setBrush(self._brushBorder)
        rounded = painter.drawRoundedRect(qc.QRect(x+5,y+8,12,12),5,5)


        if self.isEnabled():
            painter.setPen(self._pen_Shadow)
            painter.drawText(11, y+2 , width+1, height+1, alignment, text)

            painter.setPen(self._pen_text)
            painter.drawText(10, y+1 , width, height, alignment, text)

        else:
            painter.setPen(self._penShadow_disable)
            painter.drawText(11, y+2 , width, height, alignment, text)

            painter.setPen(self._penText_disable)
            painter.drawText(10, y+1 , width, height, alignment, text)

        painter.setPen(self._pen_clear)

        if self.isEnabled():
            glowBrushes = self._glowBrushes
            glowOffBrush = self._glowOffBrushes
        else:
            glowBrushes = self._disableGlowBrushes

        if self.checkState():
            for index, pos, size, corner in zip(range(4), (6,7,8,9), (11,10,10,8), (6,6,6,6)):
                painter.setBrush(glowBrushes[10][index])
                painter.drawRoundedRect(qc.QRect((x * pos) + 6, pos+1, size, size), corner, corner)

        glowIndex = self._glow_index
        if glowIndex > 0:
            for index, pos, size, corner in zip(range(4), (6,7,8,9), (10,9,10,9), (6,6,6,6)):
                painter.setBrush(glowOffBrush[glowIndex][index])
                painter.drawRoundedRect(qc.QRect((x * pos) + 6, pos+1, size, size), corner, corner)
#-----------------------------------------------------------------------------------------------------#
