import PySide.QtCore as qc
import PySide.QtGui as qg
from PySide.QtGui import QPen, QColor, QBrush, QLinearGradient
try:
    import maya.utils as utils
except:
    pass
#-------------------------------------------------------------#
class CustomLineEdit(qg.QLineEdit):
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

    _penText_disable = QPen(QColor(100, 100, 100), 1, qc.Qt.SolidLine)
    _penShadow_disable = QPen(QColor(0, 0, 0), 1, qc.Qt.SolidLine)

    _brushClear = QBrush(QColor(0, 0, 0, 0))
    _brushBorder = QBrush(QColor(9, 10, 12))
#---------------------------------------------------------------------------------------------------------------------------#
    def __init__(self, *args, **kwargs):
        qg.QLineEdit.__init__(self, *args, **kwargs)

        font = qg.QFont()
        font.setPixelSize(16)
        self.setFont(font)
        font.setFamily('Helvetic')
        self.font_metrics = qg.QFontMetrics(font)
        self.setFixedHeight(self.font_metrics.height() + 5)

        self._placeholder_message = ''
        self._text_glow = {}
        self._previous_text = ''

        text = self.text()
        if text:
            self.setText(text)

        self._animTimer = qc.QTimer()
        self._animTimer.timeout.connect(self._animateText)

#---------------------------------------------------------------------------------------------------------------------------#
    def setText(self, *args):
        qg.QLineEdit.setText(self,*args)
        self._text_glow = {}
        for index in range(len(text)):
            self._text_glow[index] = 0

    def setPlaceholderMessage(self,text):
        self._placeholder_message = str(text)
#---------------------------------------------------------------------------------------------------------------------------#
    def _animateText(self):
        stop_animating = True
        for key,value in self._text_glow.items():
            if value > 0:
                stop_animating = False
                self._text_glow[key] = value - 1

        if stop_animating:
            self._animTimer.stop()

        #print self._text_glow
        utils.executeDeferred(self.update)
#---------------------------------------------------------------------------------------------------------------------------#
    def keyPressEvent(self,*args):
        qg.QLineEdit.keyPressEvent(self,*args)
        text = self.text()

        if text == self._previous_text: return

        len_text = len(text)

        if len_text > len(self._previous_text):
            self._animTimer.start(20)
            self._text_glow[len_text-1] = 0
            self._text_glow[self.cursorPosition()-1] = 10

        elif len(self._text_glow.keys()) == 0:
            self._animTimer.stop()

        self._previous_text = text

        #print self._text_glow

#---------------------------------------------------------------------------------------------------------------------------#
    def paintEvent(self,event):
        painter = qg.QStylePainter(self)
        option  = qg.QStyleOptionFrame()
        self.initStyleOption(option)

        painter.setRenderHint(qg.QPainter.Antialiasing)
        painter.setRenderHint(qg.QPainter.TextAntialiasing)
        contents = self.style().subElementRect(qg.QStyle.SE_LineEditContents, option,self)

        contents.setLeft(contents.left() + 2)
        contents.setRight(contents.right() - 2)
        alignment = (qc.Qt.AlignLeft | qc.Qt.AlignVCenter)

        text = self.text()
        font = self.font()
        fontMetrics = self.font_metrics

        if not text:
            painter.setPen(self._penText_disable)
            painter.drawText(contents,alignment,self._placeholder_message)

        selected = self.hasSelectedText()
        if selected:
            selection = self.selectedText()
            selection_start = self.selectionStart()
            selection_end = selection_start + len(selection)

        left_edge = contents.left()

        for index,letter in enumerate(text):
            text_width = fontMetrics.width(text[0:index])
            contents.setLeft(left_edge + text_width)

            x,y,width,height = contents.getRect()
            painter.setPen(self._pen_Shadow)
            painter.drawText(x+1,y+1,width,height,alignment,letter)
            painter.setPen(self._pen_text)
            painter.drawText(contents,alignment,letter)

            glow_index = self._text_glow[index]
            if selected and (index >= selection_start and index < selection_end):
                glow_index = 10

            if glow_index > 0:
                text_path = qg.QPainterPath()
                text_path.addText(contents.left(),font.pixelSize() + 2 ,font,letter)

                for index in range(3):
                    painter.setPen(self._glowPens[glow_index][index])
                    painter.drawPath(text_path)

                painter.setPen(self._glowPens[glow_index][3])
                painter.drawText(contents,alignment,letter)

        if not self.hasFocus():
            return

        contents.setLeft(left_edge)
        x,y,width,height = contents.getRect()

        painter.setPen(self._pen_text)

        cursor_pos = self.cursorPosition()
        text_width = fontMetrics.width(text[0:cursor_pos])
        pos = x + text_width
        top = y + 1
        bottom = y + height -1
        painter.drawLine(pos,top,pos,bottom)

        try:
            cursor_glow = self._text_glow[cursor_pos - 1]
        except KeyError:
            return

        if cursor_glow > 0:
            for index in range(4):
                painter.setPen(self._glowPens[cursor_glow][index])
                painter.drawLine(pos,top,pos,bottom)

