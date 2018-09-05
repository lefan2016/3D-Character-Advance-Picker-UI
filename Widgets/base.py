import PySide.QtCore as qc
import PySide.QtGui as qg
from PySide.QtGui import QPen, QColor, QBrush, QLinearGradient


try:
    import maya.utils as utils
except:
    pass


class Base(qc.QObject):
    def __init__(self):

        font = qg.QFont()
        font.setPointSize(10)
        font.setFamily('Helvetic')
        self.setFont(font)

        self.hover = False
        self._glow_index = 0
        self._anim_timer = qc.QTimer()
        self._anim_timer.timeout.connect(self._animateGlow)

    #----------------------------------------------------------------------#

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
        super(self.__class__, self).enterEvent(event)
        print 'Base enterEvent'

        if not self.isEnabled():
            return

        self.hover = True
        self.startAnim()

    def leaveEvent(self, event):
        super(self.__class__, self).leaveEvent(event)
        print 'Base leaveEvent'

        if not self.isEnabled():
            return

        self.hover = False
        self.startAnim()

    def startAnim(self):
        if self._anim_timer.isActive():
            return

        self._anim_timer.start(20)
