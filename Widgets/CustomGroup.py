from PySide import QtCore as qc
from PySide import QtGui as qg
from PySide.QtGui import QPen, QColor, QBrush, QLinearGradient, QFont, QRadialGradient
from HitchAnimationModule.Widgets import label; reload(label)
########################################################
GBoxCSS = """
            QGroupBox {
            background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(53, 57, 60,255), stop: 0.5 rgba(25,15,05,50), stop: 1.1 rgba(33, 34, 36, 255));

            border: 1px solid black;
            border-radius: 4px;
            margin-top: 6ex; /* leave space at the top for the title */
            }

            QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left; /* position at the top center */
            padding: 0 2px;
            background-color: rgba(20,20,20,150);
            border: 1px solid ligthgray;
            border-radius: 3px;
            }

            QGroupBox::indicator {
                width: 8px;
                height: 8px;
                background-color: rgba(20,20,20,100);
                border: 1px solid gray;
                border-radius: 2px;
            }

            QGroupBox::indicator:unchecked:hover {
                background-color: rgba(100,20,20,150);
            }

            QGroupBox::indicator:checked {
                background-color: rgba(150,20,20,180);
            }
          """
########################################################
class CustomGroupBox(qg.QGroupBox):
    def __init__(self,*args,**kwargs):
        super(CustomGroupBox, self).__init__(*args,**kwargs)
        self.setStyleSheet(GBoxCSS)
        font = qg.QFont('Calibri', 8)
        self.setFont(font)


class CustomGroupColt(qg.QGroupBox):
    _brushClear = QBrush(QColor(0, 0, 0, 0))
    _brushBorder = QBrush(QColor(9, 10, 12))
    MAINBRUSH = QBrush(QColor(255, 50, 50,25))
    BRUSHHOVER = QBrush(QColor(255, 255, 255,100))
    penTick =   QPen(QColor(1,1,1), 1, qc.Qt.SolidLine)
    _pen_text = QPen(QColor(125, 200, 100), 5, qc.Qt.SolidLine)
    _pen_line = QPen(QColor(125, 200, 100), 2, qc.Qt.SolidLine)

    # Radius Colors for radial gradient ::::
    #
    multy = 2
    col1= QColor(1*  multy ,1 *multy ,1 *multy, 10)
    multy = 200
    col2= QColor(1 *multy,1 *multy,1 *multy, 15)
    multy = 150
    col3= QColor(1 *multy,1 *multy,1 *multy, 10)
    multy = 200
    col4= QColor(1 *multy,1 *multy,1 *multy, 10)
    multy = 2
    col5= QColor(1 *multy,1 *multy,1 *multy, 10)

    def __init__(self,*args,**kwargs):
        super(CustomGroupColt, self).__init__(*args,**kwargs)
        self.setSizePolicy(qg.QSizePolicy.Expanding,qg.QSizePolicy.Minimum)
        self.setObjectName('CB_GroupBox')
        self.setStyleSheet('#CB_GroupBox {background-color: transparent;}')
        self.setLayout(qg.QVBoxLayout())

        topLabel = qg.QLabel()
        self.labeltop_lyt = qg.QHBoxLayout(topLabel)
        self.labeltop_lyt.setContentsMargins(0,0,0,0)

        self.nodetag = label.CustomCBLabel()
        self.labeltop_lyt.addWidget(self.nodetag)

        topLabel.setContentsMargins(0,0,0,0)
        self.layout().setContentsMargins(0,0,0,0)
        topLabel.setSizePolicy(qg.QSizePolicy.Expanding,qg.QSizePolicy.Expanding)
        topLabel.setStyleSheet("background-color: rgba(1,1,1,40);")
        topLabel.setMaximumHeight(44)

        self.layout().setAlignment(qc.Qt.AlignTop)
        self.layout().addWidget(topLabel)


    def updateNodeTag(self, value):
        if value:
            self.nodetag.setText(value)
        else:
            self.nodetag.setText('')

    def paintEvent(self, event):
        painter = qg.QPainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height()
        width = option.rect.width()
        painter.setRenderHint(qg.QPainter.Antialiasing)

        gradient = QRadialGradient(float(width / 2),float(height / 2),float(height/2),float(width/2),float(height /2))
        #################################

        alignment = (qc.Qt.AlignHCenter | qc.Qt.AlignVCenter)
        inner_gradient = QLinearGradient(0, 0, height , 0)
        inner_gradient.setColorAt(0, QColor(255, 255, 255,35))
        inner_gradient.setColorAt(1, QColor(1, 1, 1,100))
        gradient.setColorAt(0.0, self.col1)
        gradient.setColorAt(0.2, self.col2)
        gradient.setColorAt(0.5, self.col3)
        gradient.setColorAt(0.7, self.col4)
        gradient.setColorAt(1.0, self.col5)

        painter.setOpacity(1.0)
        painter.fillRect(x,y,width,height, gradient)

        painter.fillRect(x,y,width,height, self.MAINBRUSH)
        #painter.setOpacity(0.5)
        painter.fillRect(x,y,width,height, inner_gradient)

        painter.setBrush(self._brushClear)

        line_path = qg.QPainterPath()
        line_path.moveTo( x , height)
        line_path.lineTo( width , height,)
        self.penTick.setCapStyle(qc.Qt.RoundCap)
        self._pen_line.setCapStyle(qc.Qt.RoundCap)

        painter.setPen(self._pen_text)
        painter.drawPath(line_path)
        painter.setPen(self.penTick)
        painter.drawPath(line_path)

        offset_y = 1
        offset_x = 6

        line_path_2 = qg.QPainterPath()
        line_path_2.moveTo(offset_x,50 - offset_y )
        line_path_2.lineTo((width - offset_x), 50 - offset_y)
        painter.setOpacity(0.85)

        painter.setPen(self._pen_line)
        painter.drawPath(line_path_2)

        painter.setBrush(self._brushClear)
        painter.end()


