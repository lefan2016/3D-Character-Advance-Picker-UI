import PySide.QtCore as qc
import PySide.QtGui as qg
from PySide.QtGui import QPen, QColor, QBrush, QLinearGradient
try:
    import maya.utils as utils
except:
    pass
#-------------------------------------------------------------#
class CustomSlider(qg.QSlider):
    _pen_dark   = qg.QPen(qg.QColor(0 , 1, 3),1, qc.Qt.SolidLine)
    _pen_bright = qg.QPen(qg.QColor(25,26,29),1.5, qc.Qt.SolidLine)

    _gradient_inner = qg.QLinearGradient(0,9,0,15)
    _gradient_inner.setColorAt(0,qg.QColor(69,73,66))
    _gradient_inner.setColorAt(1,qg.QColor(17,18,20))

    _gradient_outer = qg.QLinearGradient(0,9,0,15)
    _gradient_outer.setColorAt(0,qg.QColor(53,57,60))
    _gradient_outer.setColorAt(1,qg.QColor(33,34,36))

    _glowBrushes = {}
    for index in range(1, 11):
        _glowBrushes[index] = [QBrush(QColor(0, 255, 0,    1   * index)),
                               QBrush(QColor(0, 255, 0,    3   * index)),
                               QBrush(QColor(0, 255, 0,   15   * index)),
                               QBrush(QColor(0, 255, 0,   25.5 * index)),
                               QBrush(QColor(125, 200, 100, 15 * index))]

    _pen_Shadow      = QPen(QColor(9, 10, 12), 1, qc.Qt.SolidLine)
    _pen_clear       = QPen(QColor(0, 0, 0, 0), 1, qc.Qt.SolidLine)
    _brushClear = QBrush(QColor(0, 0, 0, 0))
    _brushBorder = QBrush(QColor(9, 10, 12))

    def __init__(self,*args,**kwargs):
        qg.QSlider.__init__(self,*args,**kwargs)

        self.setOrientation(qc.Qt.Horizontal)
        self.setFixedHeight(22)
        self.setMinimumWidth(50)

        self.hover = False
        self._glow_index = 0
        self._anim_timer = qc.QTimer()
        self._anim_timer.timeout.connect(self._animateGlow)

        self._track = False
        self._tracking_points = {}
        self._anim_followTimer = qc.QTimer()
        self._glow_index2 = 0
        self._anim_followTimer.timeout.connect(self._animateGlow2)
        self._anim_followTimer.timeout.connect(self._removeTrackingPoints)

        self.valueChanged.connect(self._trackChanges)

    def setRange(self,*args,**kwargs):
        qg.QSlider.setRange(self,*args,**kwargs)
        self._updateTracking()

    def setMinimum(self,*args,**kwargs):
        qg.QSlider.setMinimum(self,*args,**kwargs)
        self._updateTracking()

    def setMaximum(self,*args,**kwargs):
        qg.QSlider.setMaximum(self,*args,**kwargs)
        self._updateTracking()

    def _updateTracking(self):
        self._tracking_points = [0] * (abs(self.maximum() - self.minimum()) + 1)

    def setValue(self,*args,**kwargs):
        qg.QSlider.setValue(self,*args,**kwargs)
        for index in range(len(self._tracking_points)):
            self._tracking_points[index] = 0
#-----------------------------------------------------------------------------------------------#
    def mouseMoveEvent(self,event):
        qg.QSlider.mouseMoveEvent(self,event)

        if self._anim_followTimer.isActive():
            return

        self._anim_followTimer.start(20)
#-----------------------------------------------------------------------------------------------#

    def _trackChanges(self,value):
        value = value - self.minimum()
        self._tracking_points[value] = 10
#-----------------------------------------------------------------------------------------------#

    def _removeTrackingPoints(self):
        self._track = False
        for index , value in enumerate(self._tracking_points):
            if value > 0:
                self._tracking_points[index] -= 1
                if value == 0:
                    self._anim_followTimer.stop()
                self._track = True

        if self._track is False:
            self._anim_followTimer.stop()

#-----------------------------------------------------------------------------------------------#
    def _animateGlow2(self):
        if self._glow_index2  >= 10:
            self._glow_index2 = 10
            while self._glow_index2 > 0:
                self._glow_index2 -= 1
                if self._glow_index2 == 0:
                    self._anim_followTimer.stop()

        self.update()
#-----------------------------------------------------------------------------------------------#
    def _animateGlow(self):
        if self.hover:
            if self._glow_index >= 10:
                self._glow_index = 10
                while self._glow_index > 8:
                    self._glow_index -= 0.25
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
        self._startAnim()

    def leaveEvent(self, event):
        if not self.isEnabled():
            return

        self.hover = False
        self._startAnim()

    def _startAnim(self):
        if self._anim_timer.isActive():
            return

        self._anim_timer.start(20)
#-----------------------------------------------------------------------------------------------------#

    def paintEvent(self,event):
        painter = qg.QPainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width = option.rect.width() - 1

        painter.setRenderHint(qg.QPainter.Antialiasing)
        painter.setRenderHint(qg.QPainter.TextAntialiasing)

        painter.setPen(self._pen_Shadow)
        painter.setBrush(self._brushBorder)
        painter.drawRoundedRect(qc.QRect(x+1,y+1,width-1,height-1),10,10)

        mid_height = (height / 2) + 1
        painter.setPen(self._pen_dark)
        painter.drawLine(10, mid_height,width-8,mid_height)
        painter.setRenderHint(qg.QPainter.Antialiasing,False)
        painter.setPen(self._pen_bright)
        painter.drawLine(10, mid_height,width-8,mid_height)
        painter.setRenderHint(qg.QPainter.Antialiasing,True)

        minimum = self.minimum()
        maximum = self.maximum()
        value_range = maximum - minimum
        value = self.value() - minimum

        increment = ((width - 20) / float(value_range))
        center    = 10 + (increment * value)
        center_point = qc.QPoint(x + center, y + mid_height)

        painter.setPen(self._pen_clear)

        glowIndex = self._glow_index
        glowBrushes = self._glowBrushes

        if self._track is True:
            for index, track_value in enumerate(self._tracking_points):
                if track_value == 0:
                    continue
                track_center = 10 + (increment * index)
                painter.setBrush(glowBrushes[track_value][4])
                painter.drawEllipse(qc.QPoint(track_center,mid_height),7,7)


        if glowIndex > 0:
            for index, size in zip(range(4),range(13,8,-1)):
                painter.setBrush(glowBrushes[glowIndex][index])
                painter.drawEllipse(center_point,size,size)

        painter.setBrush(qg.QBrush(self._gradient_outer))
        painter.drawEllipse(center_point,8,8)

        painter.setBrush(qg.QBrush(self._gradient_inner))
        painter.drawEllipse(center_point,7,7)

#-----------------------------------------------------------------------------------------------#
