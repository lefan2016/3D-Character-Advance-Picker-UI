try:
    import PySide.QtCore as qc
    import PySide.QtGui as qg
    from PySide.QtGui import QPen, QColor, QBrush, QLinearGradient, QFont, QRadialGradient
    from HitchAnimationModule.Widgets    import button
    import maya.utils as utils
    import maya.cmds as cmds
    CIRCULO = cmds.internalVar(usd=1) + 'HitchAnimationModule\Icons\circulo.png'
except:
    pass
#-------------------------------------------------------------------------------------------------#
NORMAL, DOWN, DISABLE = 1, 2, 3
INNER, OUTER = 1, 2
# -------------------------------------------------------------------------------------------------#
class Square_button_blue(qg.QPushButton):
    penTick = QPen(QColor(33, 213, 231), 2, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 3, qc.Qt.SolidLine)
    _glowPens = {}

    for index in range(1, 11):
        _glowPens[index] =  [QPen(QColor(33, 213, 231,  5   * index), 2, qc.Qt.SolidLine),
                            QPen(QColor(33, 213, 231, 10   * index), 2.5, qc.Qt.SolidLine),
                            QPen(QColor(33, 213, 231, 15   * index), 3, qc.Qt.SolidLine),
                            QPen(QColor(33, 213, 231, 25.5 * index), 6, qc.Qt.SolidLine)]

    _pen_text = QPen(QColor(125, 200, 100), 1, qc.Qt.SolidLine)
    _pen_textHover = QPen(QColor(150, 225, 125), 1, qc.Qt.SolidLine)
    _pen_Ticktext = QPen(QColor(125, 200, 100), 2, qc.Qt.SolidLine)
    _pen_TickHover = QPen(QColor(255, 0, 0), 2, qc.Qt.SolidLine)
    _pen_TickPressed = QPen(QColor(1, 1, 1), 3, qc.Qt.SolidLine)
    _pen_Shadow = QPen(QColor(9, 10, 12), 2, qc.Qt.SolidLine)
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

    _size = [35,35]


    def __init__(self, parent=None, *args, **kwargs):
        super(Square_button_blue, self).__init__( parent, *args, **kwargs)

        font = qg.QFont()
        font.setPointSize(12)
        font.setFamily('Calibri')
        font.setLetterSpacing(QFont.AbsoluteSpacing, float(1))
        self.setFont(font)
        self.hover = False
        self._glow_index = 0
        self._anim_timer = qc.QTimer()
        self._anim_timer.timeout.connect(self._animateGlow)
        self.setFixedSize(self._size[0],self._size[1])

        self.fontMetrics = qg.QFontMetrics(font)
        self.radius = 5
        self.setMouseTracking(True)

        self.setCursor(qg.QCursor(qc.Qt.PointingHandCursor))
        self.parent = parent


    def paintEvent(self, event):
        painter = qg.QPainter(self)
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

        glowIndex = self._glow_index
        glowPen = self._glowPens

        if self.isDown():
            gradient = self._gradient[DOWN]
            offSet = 1

        painter.setBrush(self._brushBorder)
        painter.setPen(self._pen_border)
        painter.drawRoundedRect(qc.QRect(x + 1, y + 1, width - 1, height - 1), radius, radius)
        painter.setPen(self._pen_clear)
        painter.setBrush(gradient[OUTER])
        painter.drawRoundedRect(qc.QRect(x + 2, y + 2, width - 3, height - 3), radius, radius)
        painter.setBrush(gradient[INNER])
        painter.drawRoundedRect(qc.QRect(x + 3, y + 3, width - 4, height - 4), radius - 1, radius - 1)
        painter.setBrush(self._brushClear)
        line_path = qg.QPainterPath()

        #------------------- IK- full ----------#
        # offset
        num_x = 5.5
        num_y = 2.5
        #######################################
        # F
        line_path.moveTo( 2 + num_x, 9 + num_y)
        line_path.lineTo( 2 + num_x, 21 + num_y)
        line_path.moveTo( 3 + num_x, 9 + num_y)
        line_path.lineTo( 10 + num_x, 9 + num_y)
        line_path.moveTo( 3 + num_x, 15 + num_y)
        line_path.lineTo( 8 + num_x, 15 + num_y)
        #########################################
        # K
        num_x = 7
        line_path.moveTo( 12 + num_x, 9 + num_y)
        line_path.lineTo( 12 + num_x, 21 + num_y)
        line_path.moveTo( 15 + num_x, 15 + num_y)
        line_path.lineTo( 20 + num_x, 10 + num_y)
        line_path.moveTo( 15 + num_x, 15 + num_y)
        line_path.lineTo( 20 + num_x, 21 + num_y)

        self.penTick.setCapStyle(qc.Qt.RoundCap)

        if self.isEnabled():
            painter.setPen(self.penborder)
            painter.drawPath(line_path)
            painter.setPen(self.penTick)
            painter.drawPath(line_path)

            if glowIndex > 0:
                for index in range(3):
                    painter.setPen(self._pen_clear)
                    painter.drawPath(line_path)
                    pen = self._glowPens[glowIndex][index]
                    pen.setCapStyle(qc.Qt.RoundCap)
                    painter.setPen(pen)
                    painter.drawPath(line_path)

    #################################################################
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

        utils.executeDeferred(self.update)
#-----------------------------------------------------------------------------------------------#
    def enterEvent(self, event):
        if not self.isEnabled():
            return

        self.hover = True
        self.startAnim()

        try:
            main_par = self.parent.parent()
            getattr(main_par,'header_label').setText(self.objectName())
        except:
            pass

    def leaveEvent(self, event):
        if not self.isEnabled():
            return

        self.hover = False
        self.startAnim()
        try:
            main_par = self.parent.parent()
            getattr(main_par,'header_label').setText('')

        except: pass


    def startAnim(self):
        if self._anim_timer.isActive():
            return

        self._anim_timer.start(20)



####################################################################################################
class Round_button_orange(Square_button_blue):
    penTick = QPen(QColor(232, 79, 17), 3, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 4, qc.Qt.SolidLine)
    _glowRed = {}

    _size = [35,35]
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(232, 79, 17,  5   * index), 3, qc.Qt.SolidLine),
                            QPen(QColor(232, 79, 17, 10   * index), 4, qc.Qt.SolidLine),
                            QPen(QColor(232, 79, 17, 15   * index), 5, qc.Qt.SolidLine),
                            QPen(QColor(232, 79, 17, 25.5 * index), 6, qc.Qt.SolidLine)]

    def __inin__(self, *args, **kwargs):
        super(Round_button_orange, self).__init__(self, *args, **kwargs)

        self.setFixedSize(self._size[0],self._size[1])


    def paintEvent(self, event):
        painter = qg.QPainter(self)
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
        glowIndex = self._glow_index
        glowPen = self._glowPens

        if self.isDown():
            gradient = self._gradient[DOWN]
            offSet = 1

        painter.setPen(self._pen_border)
        painter.drawEllipse(x + 1, y + 1, width - 1, height - 1)
        painter.setPen(self._pen_clear)
        painter.setBrush(gradient[OUTER])
        painter.drawEllipse(x + 2, y + 2, width - 3, height - 2)
        painter.setBrush(gradient[INNER])
        painter.drawEllipse(x + 3, y + 3, width - 5, height - 4)
        painter.setBrush(self._brushClear)
        line_path = qg.QPainterPath()

        ##################################################
        # CROSSSS
        x_off = 8
        y_off = 9
        height = option.rect.height()
        width = option.rect.width()

        line_path.moveTo(x + x_off, y + (height / 2))
        line_path.lineTo(width - x_off, y + (height / 2))

        line_path.moveTo(width / 2, y + y_off)
        line_path.lineTo(width / 2, height - y_off)

        self.penborder.setCapStyle(qc.Qt.RoundCap)
        self._pen_Ticktext.setCapStyle(qc.Qt.RoundCap)
        self._pen_TickPressed.setCapStyle(qc.Qt.RoundCap)
        self._pen_TickHover.setCapStyle(qc.Qt.RoundCap)

        painter.setPen(self.penborder)
        painter.drawPath(line_path)
        painter.setPen(self._pen_Ticktext)
        painter.drawPath(line_path)

        self.penTick.setCapStyle(qc.Qt.RoundCap)

        painter.setPen(self.penborder)
        painter.drawPath(line_path)
        painter.setPen(self.penTick)
        painter.drawPath(line_path)

        if glowIndex > 0:
            for index in range(3):
                painter.setPen(self._pen_clear)
                painter.drawPath(line_path)
                pen = self._glowRed[glowIndex][index]
                pen.setCapStyle(qc.Qt.RoundCap)
                painter.setPen(pen)
                painter.drawPath(line_path)

#-------------------------------------------------------------------------------------------------#
class Square_button_red(Square_button_blue):
    penTick = QPen(QColor(200, 20, 20), 2, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 3, qc.Qt.SolidLine)
    _glowRed = {}
    _size = [35,35]
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(255, 20, 20,  5   * index), 2, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 10   * index), 3, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 15   * index), 5, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 25.5 * index), 6, qc.Qt.SolidLine)]

    def __inin__(self, *args, **kwargs):
        super(Square_button_red, self).__init__(self, *args, **kwargs)
        self.setFixedSize(self._size[0],self._size[1])

    def paintEvent(self, event):
        painter = qg.QPainter(self)
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

        glowIndex = self._glow_index
        glowPen = self._glowPens

        if self.isDown():
            gradient = self._gradient[DOWN]
            offSet = 1

        painter.setBrush(self._brushBorder)
        painter.setPen(self._pen_border)
        painter.drawRoundedRect(qc.QRect(x + 1, y + 1, width - 1, height - 1), radius, radius)
        painter.setPen(self._pen_clear)
        painter.setBrush(gradient[OUTER])
        painter.drawRoundedRect(qc.QRect(x + 2, y + 2, width - 3, height - 3), radius, radius)
        painter.setBrush(gradient[INNER])
        painter.drawRoundedRect(qc.QRect(x + 3, y + 3, width - 4, height - 4), radius - 1, radius - 1)
        painter.setBrush(self._brushClear)
        line_path = qg.QPainterPath()
        #------------------- IK- full ----------#
        # offset
        num_x = 5.5
        num_y = 2
        #######################################
        # I
        line_path.moveTo( 6 + num_x, 9 + num_y)
        line_path.lineTo( 6 + num_x, 21 + num_y)
        #########################################
        # K
        line_path.moveTo( 12 + num_x, 9 + num_y)
        line_path.lineTo( 12 + num_x, 21 + num_y)
        line_path.moveTo( 15 + num_x, 15 + num_y)
        line_path.lineTo( 20 + num_x, 10 + num_y)
        line_path.moveTo( 15 + num_x, 15 + num_y)
        line_path.lineTo( 20 + num_x, 21 + num_y)

        self.penTick.setCapStyle(qc.Qt.RoundCap)

        if self.isEnabled():
            painter.setPen(self.penborder)
            painter.drawPath(line_path)
            painter.setPen(self.penTick)
            painter.drawPath(line_path)

            if glowIndex > 0:
                for index in range(3):
                    painter.setPen(self._pen_clear)
                    painter.drawPath(line_path)
                    pen = self._glowRed[glowIndex][index]
                    pen.setCapStyle(qc.Qt.RoundCap)
                    painter.setPen(pen)
                    painter.drawPath(line_path)


####################################################################################################
class Round_button_yellow(Square_button_blue):
    penTick = QPen(QColor(231, 238, 16), 14, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 17.5, qc.Qt.SolidLine)
    _glowRed = {}
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(231, 238, 16,  5   * index), 14, qc.Qt.SolidLine),
                            QPen(QColor(231, 238, 16, 10   * index), 15, qc.Qt.SolidLine),
                            QPen(QColor(231, 238, 16, 15   * index), 16, qc.Qt.SolidLine),
                            QPen(QColor(231, 238, 16, 10 * index), 17, qc.Qt.SolidLine)]

    _size = [35,35]
    def __inin__(self, *args, **kwargs):
        super(Round_button_yellow, self).__init__(self, *args, **kwargs)
        self.setFixedSize(self._size[0],self._size[1])


    def paintEvent(self, event):
        painter = qg.QPainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width = option.rect.width() - 1

        center = option.rect.center()
        point = qc.QPointF(center.x()  , center.y() + 0.5)

        painter.setRenderHint(qg.QPainter.Antialiasing)
        radius = self.radius
        offSet = 0
        gradient = self._gradient[NORMAL]
        glowIndex = self._glow_index
        glowPen = self._glowPens

        if self.isDown():
            gradient = self._gradient[DOWN]
            offSet = 1

        painter.setPen(self._pen_border)
        painter.drawEllipse(x + 1, y + 1, width - 1, height - 1)
        painter.setPen(self._pen_clear)
        painter.setBrush(gradient[OUTER])
        painter.drawEllipse(x + 2, y + 2, width - 3, height - 2)
        painter.setBrush(gradient[INNER])
        painter.drawEllipse(x + 3, y + 3, width - 5, height - 4)
        painter.setBrush(self._brushClear)

        ##################################################

        self.penborder.setCapStyle(qc.Qt.RoundCap)
        self._pen_Ticktext.setCapStyle(qc.Qt.RoundCap)
        self._pen_TickPressed.setCapStyle(qc.Qt.RoundCap)
        self._pen_TickHover.setCapStyle(qc.Qt.RoundCap)

        painter.setPen(self.penborder)
        painter.drawPoint(point)
        painter.setPen(self._pen_Ticktext)
        painter.drawPoint(point)

        self.penTick.setCapStyle(qc.Qt.RoundCap)

        painter.setPen(self.penborder)
        painter.drawPoint(point)
        painter.setPen(self.penTick)
        painter.drawPoint(point)

        if glowIndex > 0:
            for index in range(3):
                painter.setPen(self._pen_clear)
                painter.drawPoint(point)
                pen = self._glowRed[glowIndex][index]
                pen.setCapStyle(qc.Qt.RoundCap)
                painter.setPen(pen)
                painter.drawPoint(point)

#-------------------------------------------------------------------------------------------------#
####################################################################################################
class Round_button_red(Square_button_blue):
    penTick = QPen(QColor(200, 20, 20), 14, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 17, qc.Qt.SolidLine)
    _glowRed = {}
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(255, 20, 20,  5   * index), 14, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 10   * index), 15, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 15   * index), 16, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 10 * index), 17, qc.Qt.SolidLine)]

    _size = [35,35]
    def __inin__(self, *args, **kwargs):
        super(Round_button_red, self).__init__(self, *args, **kwargs)
        self.setFixedSize(self._size[0],self._size[1])

    def paintEvent(self, event):
        painter = qg.QPainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width = option.rect.width() - 1

        center = option.rect.center()
        point = qc.QPointF(center.x()  , center.y() + 0.5)

        painter.setRenderHint(qg.QPainter.Antialiasing)
        radius = self.radius
        offSet = 0
        gradient = self._gradient[NORMAL]
        glowIndex = self._glow_index
        glowPen = self._glowPens

        if self.isDown():
            gradient = self._gradient[DOWN]
            offSet = 1

        painter.setPen(self._pen_border)
        painter.drawEllipse(x + 1, y + 1, width - 1, height - 1)
        painter.setPen(self._pen_clear)
        painter.setBrush(gradient[OUTER])
        painter.drawEllipse(x + 2, y + 2, width - 3, height - 2)
        painter.setBrush(gradient[INNER])
        painter.drawEllipse(x + 3, y + 3, width - 5, height - 4)
        painter.setBrush(self._brushClear)

        ##################################################
        painter.setPen(self.penborder)
        painter.drawPoint(point)
        painter.setPen(self.penTick)
        painter.drawPoint(point)

        if glowIndex > 0:
            for index in range(3):
                painter.setPen(self._pen_clear)
                painter.drawPoint(point)
                pen = self._glowRed[glowIndex][index]
                painter.setPen(pen)
                painter.drawPoint(point)

#-------------------------------------------------------------------------------------------------#
####################################################################################################
class Round_button_small_green(Square_button_blue):
    penTick = QPen(QColor(67, 238, 16), 8, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 10, qc.Qt.SolidLine)
    _glowRed = {}
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(61, 244, 7,  5   * index), 7, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 10   * index), 8, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 15   * index), 9, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 10 * index), 10, qc.Qt.SolidLine)]
    _size = [20,20]
    def __inin__(self, *args, **kwargs):
        super(Round_button_small_green, self).__init__(self, *args, **kwargs)
        self.setFixedSize(self._size[0],self._size[1])


    def paintEvent(self, event):
        painter = qg.QPainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width = option.rect.width() - 1

        center = option.rect.center()
        point = qc.QPointF(center.x() + 0.8  , center.y() + 1)

        painter.setRenderHint(qg.QPainter.Antialiasing)
        radius = self.radius
        offSet = 0
        gradient = self._gradient[NORMAL]
        glowIndex = self._glow_index
        glowPen = self._glowPens

        if self.isDown():
            gradient = self._gradient[DOWN]
            offSet = 1

        painter.setPen(self._pen_border)
        painter.drawEllipse(x + 1, y + 1, width - 1, height - 1)
        painter.setPen(self._pen_clear)
        painter.setBrush(gradient[OUTER])
        painter.drawEllipse(x + 2, y + 2, width - 3, height - 2)
        painter.setBrush(gradient[INNER])
        painter.drawEllipse(x + 3, y + 3, width - 5, height - 4)
        painter.setBrush(self._brushClear)

        ##################################################
        self.penborder.setCapStyle(qc.Qt.RoundCap)
        self._pen_Ticktext.setCapStyle(qc.Qt.RoundCap)
        self._pen_TickPressed.setCapStyle(qc.Qt.RoundCap)
        self._pen_TickHover.setCapStyle(qc.Qt.RoundCap)

        painter.setPen(self.penborder)
        painter.drawPoint(point)
        painter.setPen(self._pen_Ticktext)
        painter.drawPoint(point)

        self.penTick.setCapStyle(qc.Qt.RoundCap)
        painter.setPen(self.penborder)
        painter.drawPoint(point)
        painter.setPen(self.penTick)
        painter.drawPoint(point)

        if glowIndex > 0:
            for index in range(3):
                painter.setPen(self._pen_clear)
                painter.drawPoint(point)
                pen = self._glowRed[glowIndex][index]
                pen.setCapStyle(qc.Qt.RoundCap)
                painter.setPen(pen)
                painter.drawPoint(point)
#-------------------------------------------------------------------------------------------------#
class Flat_button_red(Square_button_blue):
    penTick = QPen(QColor(200, 20, 20), 4, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 6, qc.Qt.SolidLine)
    _glowRed = {}
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(255, 20, 20,  5   * index), 4, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 10   * index), 4, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 15   * index), 5, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 25.5 * index), 6, qc.Qt.SolidLine)]

    _size = [150,18]
    def __inin__(self, *args, **kwargs):
        super(Flat_button_red, self).__init__(self, *args, **kwargs)
        self.setFixedSize(self._size[0],self._size[1])

    def paintEvent(self, event):
        painter = qg.QPainter(self)
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

        glowIndex = self._glow_index
        glowPen = self._glowPens

        if self.isDown():
            gradient = self._gradient[DOWN]
            offSet = 1

        painter.setBrush(self._brushBorder)
        painter.setPen(self._pen_border)
        painter.drawRoundedRect(qc.QRect(x + 1, y + 1, width - 1, height - 1), radius, radius)
        painter.setPen(self._pen_clear)
        painter.setBrush(gradient[OUTER])
        painter.drawRoundedRect(qc.QRect(x + 2, y + 2, width - 3, height - 3), radius, radius)
        painter.setBrush(gradient[INNER])
        painter.drawRoundedRect(qc.QRect(x + 3, y + 3, width - 4, height - 4), radius - 1, radius - 1)
        painter.setBrush(self._brushClear)
        line_path = qg.QPainterPath()
        #------------------- IK- full ----------#
        # offset
        num_x = 5
        num_y = 2
        #######################################
        # I
        height = option.rect.height()
        width = option.rect.width()

        line_path.moveTo( 6 + num_x, height / 2)
        line_path.lineTo( width - num_x - 7, height / 2)
        #########################################
        self.penTick.setCapStyle(qc.Qt.RoundCap)
        self.penborder.setCapStyle(qc.Qt.RoundCap)

        if self.isEnabled():
            painter.setPen(self.penborder)
            painter.drawPath(line_path)
            painter.setPen(self.penTick)
            painter.drawPath(line_path)

            if glowIndex > 0:
                for index in range(3):
                    painter.setPen(self._pen_clear)
                    painter.drawPath(line_path)
                    pen = self._glowRed[glowIndex][index]
                    pen.setCapStyle(qc.Qt.RoundCap)
                    painter.setPen(pen)
                    painter.drawPath(line_path)
####################################################################################################
class Flat_button_green(Flat_button_red):
    penTick = QPen(QColor(67, 238, 16), 4, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 6, qc.Qt.SolidLine)
    _glowRed = {}
    _size = [200,18]
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(61, 244, 7,  5   * index), 4, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 10   * index), 5, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 15   * index), 6, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 10 * index), 7, qc.Qt.SolidLine)]

####################################################################################################
class Round_button_small_red(Round_button_small_green):
    penTick = QPen(QColor(200, 20, 20), 8, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 10, qc.Qt.SolidLine)
    _glowRed = {}
    _size = [20,20]
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(255, 20, 20,  5   * index), 7, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 10   * index), 8, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 15   * index), 9, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 25.5 * index), 13, qc.Qt.SolidLine)]

####################################################################################################
class Round_button_small_orange(Round_button_small_green):
    penTick = QPen(QColor(232, 79, 17), 8, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 10, qc.Qt.SolidLine)
    _glowRed = {}
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(232, 79, 17,  5   * index), 7, qc.Qt.SolidLine),
                            QPen(QColor(232, 79, 17, 10   * index), 8, qc.Qt.SolidLine),
                            QPen(QColor(232, 79, 17, 15   * index), 9, qc.Qt.SolidLine),
                            QPen(QColor(232, 79, 17, 25.5 * index), 13, qc.Qt.SolidLine)]

#################################################################################################

class Flat_button_green_big(Flat_button_green):
    _size = [450,18]
    penTick = QPen(QColor(67, 238, 16), 4, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 6, qc.Qt.SolidLine)
    _glowRed = {}
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(61, 244, 7,  5   * index), 4, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 10   * index), 5, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 15   * index), 6, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 25.5 * index), 7, qc.Qt.SolidLine)]

#############################################################################################
class Round_button_cross_red(Round_button_orange):
    penTick = QPen(QColor(200, 20, 20), 5, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 7, qc.Qt.SolidLine)
    _glowRed = {}
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(255, 20, 20,  5   * index), 5, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 10   * index), 6, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 15   * index), 6, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 25.5 * index), 7, qc.Qt.SolidLine)]

####################################################################################################
class Round_button_small_red_face(Square_button_blue):
    penTick = QPen(QColor(200, 20, 20), 10, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 12, qc.Qt.SolidLine)
    _glowRed = {}


    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(255, 20, 20,  5   * index), 9, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 10   * index), 10, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 15   * index), 12, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 25.5 * index), 13, qc.Qt.SolidLine)]

    _size = [25,25]
    def __inin__(self, *args, **kwargs):
        super(Round_button_small_red_face, self).__init__(self, *args, **kwargs)
        self.setFixedSize(self._size[0],self._size[1])

    def paintEvent(self, event):
        painter = qg.QPainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width = option.rect.width() - 1

        center = option.rect.center()
        point = qc.QPointF(center.x() + 0.6  , center.y() + 0.75)

        painter.setRenderHint(qg.QPainter.Antialiasing)
        radius = self.radius
        offSet = 0
        gradient = self._gradient[NORMAL]
        glowIndex = self._glow_index
        glowPen = self._glowPens

        if self.isDown():
            gradient = self._gradient[DOWN]
            offSet = 1

        painter.setPen(self._pen_border)
        painter.drawEllipse(x + 1, y + 1, width - 1, height - 1)
        painter.setPen(self._pen_clear)
        painter.setBrush(gradient[OUTER])
        painter.drawEllipse(x + 2, y + 2, width - 3, height - 2)
        painter.setBrush(gradient[INNER])
        painter.drawEllipse(x + 3, y + 3, width - 5, height - 4)
        painter.setBrush(self._brushClear)

        ##################################################
        self.penborder.setCapStyle(qc.Qt.RoundCap)
        self._pen_Ticktext.setCapStyle(qc.Qt.RoundCap)
        self._pen_TickPressed.setCapStyle(qc.Qt.RoundCap)
        self._pen_TickHover.setCapStyle(qc.Qt.RoundCap)

        painter.setPen(self.penborder)
        painter.drawPoint(point)
        painter.setPen(self._pen_Ticktext)
        painter.drawPoint(point)

        self.penTick.setCapStyle(qc.Qt.RoundCap)
        painter.setPen(self.penborder)
        painter.drawPoint(point)
        painter.setPen(self.penTick)
        painter.drawPoint(point)

        if glowIndex > 0:
            for index in range(3):
                painter.setPen(self._pen_clear)
                painter.drawPoint(point)
                pen = self._glowRed[glowIndex][index]
                pen.setCapStyle(qc.Qt.RoundCap)
                painter.setPen(pen)
                painter.drawPoint(point)

####################################################################################################
class Round_button_small_yellow_face(Round_button_small_red_face):
    penTick = QPen(QColor(231, 238, 16), 9, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 12, qc.Qt.SolidLine)
    _glowRed = {}
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(231, 238, 16,  5   * index), 9, qc.Qt.SolidLine),
                            QPen(QColor(231, 238, 16, 10   * index), 10, qc.Qt.SolidLine),
                            QPen(QColor(231, 238, 16, 15   * index), 12, qc.Qt.SolidLine),
                            QPen(QColor(231, 238, 16, 10 * index), 13, qc.Qt.SolidLine)]
##############################################################################################################################################################

class Flat_button_green_thick_01(Square_button_blue):
    penTick = QPen(QColor(67, 238, 16), 4, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 6, qc.Qt.SolidLine)
    _glowRed = {}
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(61, 244, 7,  5   * index), 4, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 10   * index), 5, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 15   * index), 6, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 25.5 * index), 7, qc.Qt.SolidLine)]

    _size = [250,32]
    def __inin__(self, *args, **kwargs):
        super(Flat_button_green_thick_01, self).__init__(self, *args, **kwargs)
        self.setFixedSize(self._size[0],self._size[1])

    def paintEvent(self, event):
        painter = qg.QPainter(self)
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

        glowIndex = self._glow_index
        glowPen = self._glowPens

        if self.isDown():
            gradient = self._gradient[DOWN]
            offSet = 1

        painter.setBrush(self._brushBorder)
        painter.setPen(self._pen_border)
        painter.drawRoundedRect(qc.QRect(x + 1, y + 1, width - 1, height - 1), radius, radius)
        painter.setPen(self._pen_clear)
        painter.setBrush(gradient[OUTER])
        painter.drawRoundedRect(qc.QRect(x + 2, y + 2, width - 3, height - 3), radius, radius)
        painter.setBrush(gradient[INNER])
        painter.drawRoundedRect(qc.QRect(x + 3, y + 3, width - 4, height - 4), radius - 1, radius - 1)
        painter.setBrush(self._brushClear)
        line_path = qg.QPainterPath()
        #------------------- IK- full ----------#
        # offset
        num_x = 5
        num_y = 10
        #######################################
        # I
        height = option.rect.height()
        width = option.rect.width()

        line_path.moveTo( 6 + num_x, height / 2)
        line_path.lineTo( width - num_x - 7, height / 2)

        line_path.moveTo( width/ 2 , y + num_y)
        line_path.lineTo( width/ 2 , height - num_y)
        #########################################
        self.penTick.setCapStyle(qc.Qt.RoundCap)
        self.penborder.setCapStyle(qc.Qt.RoundCap)

        if self.isEnabled():
            painter.setPen(self.penborder)
            painter.drawPath(line_path)
            painter.setPen(self.penTick)
            painter.drawPath(line_path)

            if glowIndex > 0:
                for index in range(3):
                    painter.setPen(self._pen_clear)
                    painter.drawPath(line_path)
                    pen = self._glowRed[glowIndex][index]
                    pen.setCapStyle(qc.Qt.RoundCap)
                    painter.setPen(pen)
                    painter.drawPath(line_path)

########################################################################################################################################

class Flat_button_green_thick_02(Flat_button_green_thick_01):
    penTick = QPen(QColor(67, 238, 16), 4, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 6, qc.Qt.SolidLine)
    _glowRed = {}
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(61, 244, 7,  5   * index), 4, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 10   * index), 5, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 15   * index), 6, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 25.5 * index), 7, qc.Qt.SolidLine)]

    _size = [150,32]



########################################################################################################################################

class Flat_button_green_thick_03(Flat_button_green_thick_01):
    penTick = QPen(QColor(67, 238, 16), 4, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 6, qc.Qt.SolidLine)
    _glowRed = {}
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(61, 244, 7,  5   * index), 4, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 10   * index), 5, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 15   * index), 6, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 25.5 * index), 7, qc.Qt.SolidLine)]

    _size = [100,45]

########################################################################################################################################

class Flat_button_green_thick_04(Flat_button_green_thick_01):
    penTick = QPen(QColor(67, 238, 16), 4, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 6, qc.Qt.SolidLine)
    _glowRed = {}
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(61, 244, 7,  5   * index), 4, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 10   * index), 5, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 15   * index), 6, qc.Qt.SolidLine),
                            QPen(QColor(61, 244, 7, 25.5 * index), 7, qc.Qt.SolidLine)]

    _size = [80,30]

########################################################################################################################################
class Round_big_button_hole_red(Square_button_blue):
    penTick = QPen(QColor(200, 20, 20), 100, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 105, qc.Qt.SolidLine)
    penInner = QPen(QColor(9, 10, 12), 86, qc.Qt.SolidLine)
    penclear = QPen(QColor(0, 0, 0), 90, qc.Qt.SolidLine)

    _glowRed = {}
    pixMap = qg.QPixmap(CIRCULO)
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(255, 20, 20,  2   * index), 92, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 5   * index), 93, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 10   * index), 100, qc.Qt.SolidLine),
                            QPen(QColor(255, 20, 20, 15 * index), 110, qc.Qt.SolidLine)]

    _size = [122,122]
    def __inin__(self, *args, **kwargs):
        super(Round_big_button_hole_red, self).__init__(self, *args, **kwargs)
        self.setFixedSize(self._size[0],self._size[1])


    def paintEvent(self, event):
        painter = qg.QPainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width = option.rect.width() - 1

        center = option.rect.center()
        point = qc.QPointF(center.x() + 1.0 , center.y() + 1.5)

        painter.setRenderHint(qg.QPainter.Antialiasing)
        radius = self.radius
        offSet = 0
        gradient = self._gradient[NORMAL]
        glowIndex = self._glow_index
        glowPen = self._glowPens

        if self.isDown():
            gradient = self._gradient[DOWN]
            offSet = 1

        painter.setPen(self._pen_border)
        painter.drawEllipse(x + 1 , y + 1, width - 1 , height -1 )
        painter.setPen(self._pen_clear)
        painter.setBrush(gradient[OUTER])
        painter.drawEllipse(x + 2, y + 2, width - 3, height - 2)
        painter.setBrush(gradient[INNER])
        painter.drawEllipse(x + 3, y + 3, width - 5, height - 4)
        painter.setBrush(self._brushClear)

        ##################################################

        self.penborder.setCapStyle(qc.Qt.RoundCap)
        self._pen_Ticktext.setCapStyle(qc.Qt.RoundCap)
        self._pen_TickPressed.setCapStyle(qc.Qt.RoundCap)
        self._pen_TickHover.setCapStyle(qc.Qt.RoundCap)
        self.penInner.setCapStyle(qc.Qt.RoundCap)
        self.penclear.setCapStyle(qc.Qt.RoundCap)

        painter.setPen(self.penborder)
        painter.drawPoint(point)
        painter.setPen(self._pen_Ticktext)
        painter.drawPoint(point)

        self.penTick.setCapStyle(qc.Qt.RoundCap)

        painter.setPen(self.penborder)
        painter.drawPoint(point)
        painter.setPen(self.penTick)
        painter.drawPoint(point)

        painter.setPen(self.penInner)
        painter.drawPoint(point)


        image = qg.QImage(CIRCULO)
        image.convertToFormat(qg.QImage.Format_ARGB32)
        image.invertPixels(qg.QImage.InvertRgba)

        mask = qg.QPixmap.fromImage(image.createAlphaMask(qc.Qt.AutoColor))

        scaled = mask.scaled(width + 1 , height + 1   , qc.Qt.KeepAspectRatio, qc.Qt.SmoothTransformation)

        self.setMask(scaled)

        if glowIndex > 0:
            for index in range(3):
                painter.setPen(self._pen_clear)
                painter.drawPoint(point)
                pen = self._glowRed[glowIndex][index]
                pen.setCapStyle(qc.Qt.RoundCap)
                painter.setPen(pen)
                painter.drawPoint(point)




########################################################################################################################################
class Round_big_button_hole_yellow(Round_big_button_hole_red):
    penTick = QPen(QColor(231, 238, 16,240), 100, qc.Qt.SolidLine)
    penborder = QPen(QColor(9, 10, 12), 105, qc.Qt.SolidLine)
    penInner = QPen(QColor(9, 10, 12), 86, qc.Qt.SolidLine)
    penclear = QPen(QColor(0, 0, 0), 90, qc.Qt.SolidLine)

    _glowRed = {}
    pixMap = qg.QPixmap(CIRCULO)
    for index in range(1, 11):
        _glowRed[index] =  [QPen(QColor(231, 238, 16,  2   * index), 92, qc.Qt.SolidLine),
                            QPen(QColor(231, 238, 16, 5   * index), 93, qc.Qt.SolidLine),
                            QPen(QColor(231, 238, 16, 10   * index), 100, qc.Qt.SolidLine),
                            QPen(QColor(231, 238, 16, 15 * index), 110, qc.Qt.SolidLine)]


########################################################################################################################################




class GaugeWidget(qg.QWidget):

    def __init__(self, initialValue=0, *args, **kwargs):
        super(GaugeWidget, self).__init__(*args, **kwargs)
        self._bg = qg.QPixmap("bg.png")
        self.setValue(initialValue)

    def setValue(self, val):
        val = float(min(max(val, 0), 1))
        self._value = -270 * val
        self.update()


    def paintEvent(self, event):
        painter = qg.QPainter(self)
        painter.setRenderHint(painter.Antialiasing)
        rect = event.rect()

        gauge_rect = qc.QRect(rect)
        size = gauge_rect.size()
        pos = gauge_rect.center()
        gauge_rect.moveCenter( qc.QPoint(pos.x()-size.width(), pos.y()-size.height()) )
        gauge_rect.setSize(size*.9)
        gauge_rect.moveCenter(pos)

        refill_rect = qc.QRect(gauge_rect)
        size = refill_rect.size()
        pos = refill_rect.center()
        refill_rect.moveCenter( qc.QPoint(pos.x()-size.width(), pos.y()-size.height()) )
        # smaller than .9 == thicker gauge
        refill_rect.setSize(size*.9)
        refill_rect.moveCenter(pos)

        painter.setPen(qc.Qt.NoPen)

        painter.drawPixmap(rect, self._bg)

        painter.save()
        grad = qg.QConicalGradient(qc.QPointF(gauge_rect.center()), 270.0)
        grad.setColorAt(.75, qc.Qt.green)
        grad.setColorAt(.5, qc.Qt.yellow)
        grad.setColorAt(.25, qc.Qt.red)
        painter.setBrush(grad)
        painter.drawPie(gauge_rect, 225.0*16, self._value*16)
        painter.restore()

        painter.setBrush(qg.QBrush(self._bg.scaled(rect.size())))
        painter.drawEllipse(refill_rect)

        super(GaugeWidget,self).paintEvent(event)
