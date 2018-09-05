import PySide.QtCore as qc
import PySide.QtGui as qg
from PySide.QtGui import QPen, QColor, QBrush, QLinearGradient
try:
    import maya.utils as utils
except:
    pass


#-------------------------------------------------------------#

NORMAL, DOWN, DISABLE = 1, 2, 3
INNER, OUTER = 1, 2


class CustomButton(qg.QPushButton):

    _pen_text = QPen(QColor(125, 200, 100), 1, qc.Qt.SolidLine)
    _pen_textHover = QPen(QColor(150, 225, 125), 1, qc.Qt.SolidLine)
    _pen_Ticktext = QPen(QColor(125, 200, 100), 1.5, qc.Qt.SolidLine)
    _pen_TickHover = QPen(QColor(255, 0, 0), 1.5, qc.Qt.SolidLine)
    _pen_TickPressed = QPen(QColor(1, 1, 1), 2, qc.Qt.SolidLine)
    _pen_Shadow = QPen(QColor(9, 10, 12), 1, qc.Qt.SolidLine)
    _pen_border = QPen(QColor(9, 10, 12), 2, qc.Qt.SolidLine)
    _pen_clear = QPen(QColor(0, 0, 0, 0), 1, qc.Qt.SolidLine)

    _penText_disable = QPen(QColor(102, 107, 110), 1, qc.Qt.SolidLine)
    _penShadow_disable = QPen(QColor(0, 0, 0), 1, qc.Qt.SolidLine)

    _brushClear = QBrush(QColor(0, 0, 0, 0))
    _brushBorder = QBrush(QColor(9, 10, 12))

    _gradient = {NORMAL: {}, DOWN: {}, DISABLE: {}}

    inner_gradient = QLinearGradient(0, 3, 0, 24)
    inner_gradient.setColorAt(0, QColor(53, 57, 60))
    inner_gradient.setColorAt(1, QColor(33, 34, 36))
    _gradient[NORMAL][INNER] = QBrush(inner_gradient)

    outer_gradient = QLinearGradient(0, 2, 0, 25)
    outer_gradient.setColorAt(0, QColor(69, 73, 76))
    outer_gradient.setColorAt(1, QColor(17, 18, 20))
    _gradient[NORMAL][OUTER] = QBrush(outer_gradient)

    inner_gradientDown = QLinearGradient(0, 3, 0, 24)
    inner_gradientDown.setColorAt(0, QColor(20, 21, 23))
    inner_gradientDown.setColorAt(1, QColor(48, 49, 51))
    _gradient[DOWN][INNER] = QBrush(inner_gradientDown)

    outer_gradientDown = QLinearGradient(0, 2, 0, 25)
    outer_gradientDown.setColorAt(0, QColor(20, 21, 23))
    outer_gradientDown.setColorAt(1, QColor(32, 33, 35))
    _gradient[DOWN][OUTER] = QBrush(outer_gradientDown)

    inner_gradientDisable = QLinearGradient(0, 3, 0, 24)
    inner_gradientDisable.setColorAt(0, QColor(33, 37, 39))
    inner_gradientDisable.setColorAt(1, QColor(13, 14, 16))
    _gradient[DISABLE][INNER] = QBrush(inner_gradientDisable)

    outer_gradientDisable = QLinearGradient(0, 2, 0, 25)
    outer_gradientDisable.setColorAt(0, QColor(49, 53, 56))
    outer_gradientDisable.setColorAt(1, QColor(9, 10, 12))
    _gradient[DISABLE][OUTER] = QBrush(outer_gradientDisable)

    def __init__(self, *args, **kwargs):
        qg.QPushButton.__init__(self, *args, **kwargs)

        font = qg.QFont()
        font.setPointSize(10)
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
        print " ANIMATE GLOW METHOD "

        if self.hover:
            if self._glow_index >= 10:
                self._glow_index = 10
                self._anim_timer.stop()

            else:
                self._glow_index += 1

        else:
            if self._glow_index <= 0:
                self._glow_index = 0
                self._anim_timer.stop()

            else:
                self._glow_index -= 1
        print self._glow_index
        utils.executeDeferred(self.update)

#-----------------------------------------------------------------------------------------------#
    def enterEvent(self, event):
        print 'Base enterEvent'

        if not self.isEnabled():
            return

        self.hover = True
        self.startAnim()

    def leaveEvent(self, event):
        print 'Base leaveEvent'

        if not self.isEnabled():
            return

        self.hover = False
        self.startAnim()

    def startAnim(self):
        if self._anim_timer.isActive():
            return

        self._anim_timer.start(20)

    def paintEvent(self, event):

        painter = qg.QStylePainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width = option.rect.width() - 1

        painter.setRenderHint(qg.QPainter.Antialiasing)
        radius = 10
        offSet = 0
        gradient = self._gradient[NORMAL]

        if self.isDown():
            gradient = self._gradient[DOWN]
            offSet = 1

        elif not self.isEnabled():
            gradient = self._gradient[DISABLE]

        painter.setBrush(self._brushBorder)
        painter.setPen(self._pen_border)
        painter.drawRoundedRect(qc.QRect(x + 1, y + 1, width - 1, height - 1), radius, radius)

        painter.setPen(self._pen_clear)
        painter.setBrush(gradient[OUTER])
        painter.drawRoundedRect(qc.QRect(x + 2, y + 2, width - 3, height - 3), radius, radius)

        painter.setBrush(gradient[INNER])
        painter.drawRoundedRect(qc.QRect(x + 3, y + 3, width - 4, height - 4), radius - 1, radius - 1)

        # draw TEXT
        #

        text = self.text()
        font = self.font()

        text_width = self.fontMetrics.width(text)
        text_height = font.pointSize()

        textPath = qg.QPainterPath()
        textPath.addText((width - text_width) / 2.1, height - ((height - text_height) / 2.1) / 1.2 + offSet, font, text)

        alignment = (qc.Qt.AlignHCenter | qc.Qt.AlignVCenter)

        if self.isEnabled():
            painter.setPen(self._pen_Shadow)
            painter.drawPath(textPath)

            painter.setPen(self._pen_text)
            painter.drawText(x, y + offSet, width, height, alignment, text)

        else:
            painter.setPen(self._penShadow_disable)
            painter.drawPath(textPath)

            painter.setPen(self._penText_disable)
            painter.drawText(x, y + offSet, width, height, alignment, text)

        """
        if self.underMouse():
            painter.setPen(self._pen_clear)
            painter.drawPath(textPath)
            painter.setPen(self._pen_textHover)
            painter.drawText(x, y + offSet, width, height, alignment, text)
            print('UnderMouse')


    def enterEvent(self,event):
        pass
        # print("entering event")


    def leaveEvent(self,event):
        pass
        # print("leaving event")"""


class CloseButton(CustomButton):
    def __inin__(self, *args, **kwargs):
        CustomButton.__init__(self, *args, **kwargs)

        self.radius = 10

    def paintEvent(self, event):

        self.setFixedSize(21, 21)

        painter = qg.QStylePainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width = option.rect.width() - 1

        painter.setRenderHint(qg.QPainter.Antialiasing)
        radius = self.radius
        offSet = 0
        gradient = self._gradient[NORMAL]

        if self.isDown():
            gradient = self._gradient[DOWN]
            offSet = 1

        elif not self.isEnabled():
            gradient = self._gradient[DISABLE]

        painter.setPen(self._pen_border)
        painter.drawEllipse(x + 1, y + 1, width - 1, height - 1)

        painter.setPen(self._pen_clear)
        painter.setBrush(gradient[OUTER])
        painter.drawEllipse(x + 2, y + 2, width - 3, height - 2)

        painter.setBrush(gradient[INNER])
        painter.drawEllipse(x + 3, y + 3, width - 5, height - 4)

        painter.setBrush(self._brushClear)

        line_path = qg.QPainterPath()

        line_path.moveTo(x + 7.5, y + 7.5)
        line_path.lineTo(x + 13, y + 14)

        line_path.moveTo(x + 13, y + 7.5)
        line_path.lineTo(x + 7.5, y + 14.2)

        painter.setPen(self._pen_Ticktext)
        painter.drawPath(line_path)

        if self.isDown():
            painter.setPen(self._pen_TickPressed)
            painter.drawPath(line_path)

        elif self.underMouse():
            painter.setPen(self._pen_TickHover)
            painter.drawPath(line_path)
