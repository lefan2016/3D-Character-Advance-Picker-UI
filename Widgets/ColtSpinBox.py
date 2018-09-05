from PySide import QtCore as qc
from PySide import QtGui as qg
########################################################
QSpinCSS = """
            QSpinBox {
            background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(53, 57, 60,255), stop: 0.5 rgba(25,15,05,50), stop: 1.1 rgba(33, 34, 36, 255));
            border: 1px solid black;
            border-radius: 4px;
            font: bold 12px;
            font-family: Calibri;
            nohighlights;
            }

            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right; /* position at the top right corner */

                width: 27px; /* 16 + 2*1px border-width = 15px padding + 3px parent border */
                border-width: 1px;
                background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(150, 150, 150,85), stop: 0.3 rgba(1,1,1,50), stop: 1.0 rgba(125, 10, 1, 200));
                border-left-width: 0.5px;
                border-left-color: black;
                border-left-style: solid; /* just a single line */
                border-top-right-radius: 4px; /* same radius as the QComboBox */
                border-bottom-width: 0.5px;
                border-bottom-color: black;
                border-bottom-style: solid; /* just a single line */

            }

            QSpinBox::up-button:hover {
                background-color: rgba(255,255,255,20)
            }

            QSpinBox::down-button:hover {
                background-color: rgba(255,255,255,20)
            }

            QSpinBox::up-button:pressed {
                background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(80, 10, 1, 100), stop: 0.3 rgba(1,1,1,50), stop: 1.0 rgba(200, 200, 200,125));
            }

            QSpinBox::down-button:pressed {
                background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(80, 10, 1, 100), stop: 0.3 rgba(1,1,1,50), stop: 1.0 rgba(200, 200, 200,125));
            }

            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right; /* position at the top right corner */

                width: 27px; /* 16 + 2*1px border-width = 15px padding + 3px parent border */
                border-width: 1px;
                background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(150, 150, 150,85), stop: 0.3 rgba(1,1,1,50), stop: 1.0 rgba(125, 10, 1, 200));
                border-left-width: 0.5px;
                border-left-color: black;
                border-left-style: solid; /* just a single line */
                border-bottom-right-radius: 4px; /* same radius as the QComboBox */
                border-top-width: 0.5px;
                border-top-color: black;
                border-top-style: solid; /* just a single line */
            }
          """
########################################################
class CustomSpinBox(qg.QSpinBox):
    def __init__(self,*args,**kwargs):
        super(CustomSpinBox, self).__init__(*args,**kwargs)
        self.setStyleSheet(QSpinCSS)
        font = qg.QFont('Calibri', 8)
        self.setFont(font)
        self.lineEditChild = self.findChild(qg.QLineEdit)

        self.connect(self, qc.SIGNAL('valueChanged(int)'), qc.SLOT('onSpinBoxValueChanged(int)'), qc.Qt.QueuedConnection)

        self.lineEditChild.installEventFilter(self)
        self.setAccelerated(True)
        self.drag_origin = None

        self.timerShot = qc.QTimer()
        self.timerShot.setInterval(3000)
        self.timerShot.timeout.connect(self.deselectWidget)



    def deselectWidget(self):
        self.lineEditChild.deselect()
        self.lineEditChild.clearFocus()

    def get_is_dragging( self ):
        # are we the widget that is also the active mouseGrabber?
        return self.mouseGrabber( ) == self

    ### Dragging Handling Methods ################################################
    def do_drag_start( self ):
        # Record position
        # Grab mouse
        self.drag_origin = qg.QCursor( ).pos( )
        self.grabMouse( )

    def do_drag_update( self ):
        # Transpose the motion into values as a delta off of the recorded click position
        curPos = qg.QCursor( ).pos( )
        offsetVal = self.drag_origin.y( ) - curPos.y( )
        self.setValue( offsetVal )


    def do_drag_end( self ):
        self.releaseMouse( )
        # Restore position
        # Reset drag origin value
        self.drag_origin = None

    def eventFilter(self, obj , event):
        if obj == self.lineEditChild:
            if event.type() == qc.QEvent.Leave:
                self.timerShot.start()
                event.accept()
                return True

        return False

    ### Mouse Override Methods ################################################
    def mousePressEvent( self, event ):
        if qc.Qt.LeftButton:
            self.do_drag_start( )
        elif self.get_is_dragging( ) and qc.Qt.RightButton:
            # Cancel the drag
            self.do_drag_end( )
        else:
            super( CustomDoubleSpinBox, self ).mouseReleaseEvent( event )


    def mouseMoveEvent( self, event ):
        if self.get_is_dragging( ):
            self.do_drag_update( )
        else:
            super( CustomDoubleSpinBox, self ).mouseReleaseEvent( event )


    def mouseReleaseEvent( self, event ):
        if self.get_is_dragging( ) and qc.Qt.LeftButton:
            self.do_drag_end( )
        else:
            super( CustomDoubleSpinBox, self ).mouseReleaseEvent( event )

########################################################
QSpinCSS_2 = """
            QDoubleSpinBox {
            background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(53, 57, 60,255), stop: 0.5 rgba(25,15,05,50), stop: 1.1 rgba(33, 34, 36, 255));
            border: 1px solid black;
            border-radius: 4px;
            font: bold 12px;
            font-family: Calibri;
            nohighlights;
            }

            QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right; /* position at the top right corner */

                width: 27px; /* 16 + 2*1px border-width = 15px padding + 3px parent border */
                border-width: 1px;
                background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(150, 150, 150,85), stop: 0.3 rgba(1,1,1,50), stop: 1.0 rgba(125, 10, 1, 200));
                border-left-width: 0.5px;
                border-left-color: black;
                border-left-style: solid; /* just a single line */
                border-top-right-radius: 4px; /* same radius as the QComboBox */
                border-bottom-width: 0.5px;
                border-bottom-color: black;
                border-bottom-style: solid; /* just a single line */

            }

            QDoubleSpinBox::up-button:hover {
                background-color: rgba(255,255,255,20)
            }

            QDoubleSpinBox::down-button:hover {
                background-color: rgba(255,255,255,20)
            }

            QDoubleSpinBox::up-button:pressed {
                background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(80, 10, 1, 100), stop: 0.3 rgba(1,1,1,50), stop: 1.0 rgba(200, 200, 200,125));
            }

            QDoubleSpinBox::down-button:pressed {
                background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(80, 10, 1, 100), stop: 0.3 rgba(1,1,1,50), stop: 1.0 rgba(200, 200, 200,125));
            }

            QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right; /* position at the top right corner */

                width: 27px; /* 16 + 2*1px border-width = 15px padding + 3px parent border */
                border-width: 1px;
                background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(150, 150, 150,85), stop: 0.3 rgba(1,1,1,50), stop: 1.0 rgba(125, 10, 1, 200));
                border-left-width: 0.5px;
                border-left-color: black;
                border-left-style: solid; /* just a single line */
                border-bottom-right-radius: 4px; /* same radius as the QComboBox */
                border-top-width: 0.5px;
                border-top-color: black;
                border-top-style: solid; /* just a single line */
            }
          """



class CustomDoubleSpinBox(qg.QDoubleSpinBox):
    def __init__(self,*args,**kwargs):
        super(CustomDoubleSpinBox, self).__init__(*args,**kwargs)
        self.setStyleSheet(QSpinCSS_2)
        font = qg.QFont('Calibri', 8)
        self.setFont(font)
        self.setSingleStep(0.10)

        self.lineEditChild = self.findChild(qg.QLineEdit)
        self.connect(self, qc.SIGNAL('valueChanged(int)'), qc.SLOT('onSpinBoxValueChanged(int)'), qc.Qt.QueuedConnection)

        self.lineEditChild.installEventFilter(self)
        self.setAccelerated(True)
        self.drag_origin = None

        self.timerShot = qc.QTimer()
        self.timerShot.setInterval(3000)
        self.timerShot.timeout.connect(self.deselectWidget)



    def deselectWidget(self):
        self.lineEditChild.deselect()
        self.lineEditChild.clearFocus()

    def get_is_dragging( self ):
        # are we the widget that is also the active mouseGrabber?
        return self.mouseGrabber( ) == self

    ### Dragging Handling Methods ################################################
    def do_drag_start( self ):
        # Record position
        # Grab mouse
        self.drag_origin = qg.QCursor( ).pos( )
        self.grabMouse( )

    def do_drag_update( self ):
        # Transpose the motion into values as a delta off of the recorded click position
        curPos = qg.QCursor( ).pos( )
        offsetVal = self.drag_origin.y( ) - curPos.y( )
        self.setValue( offsetVal )


    def do_drag_end( self ):
        self.releaseMouse( )
        # Restore position
        # Reset drag origin value
        self.drag_origin = None


    def eventFilter(self, obj , event):
        if obj == self.lineEditChild:
            if event.type() == qc.QEvent.Leave:
                self.timerShot.start()
                event.accept()
                return True

        return False

    ### Mouse Override Methods ################################################
    def mousePressEvent( self, event ):
        if qc.Qt.LeftButton:
            self.do_drag_start( )
        elif self.get_is_dragging( ) and qc.Qt.RightButton:
            # Cancel the drag
            self.do_drag_end( )
        else:
            super( CustomDoubleSpinBox, self ).mouseReleaseEvent( event )


    def mouseMoveEvent( self, event ):
        if self.get_is_dragging( ):
            self.do_drag_update( )
        else:
            super( CustomDoubleSpinBox, self ).mouseReleaseEvent( event )


    def mouseReleaseEvent( self, event ):
        if self.get_is_dragging( ) and qc.Qt.LeftButton:
            self.do_drag_end( )
        else:
            super( CustomDoubleSpinBox, self ).mouseReleaseEvent( event )

#################################################################################################
#
#

QSpinCSS_03 = """
            QSpinBox {
            background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(53, 57, 60,255), stop: 0.5 rgba(25,15,05,50), stop: 1.1 rgba(33, 34, 36, 255));
            border: 1px solid black;
            border-radius: 4px;
            font: bold 12px;
            font-family: Calibri;
            nohighlights;
            }

            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right; /* position at the top right corner */

                width: 27px; /* 16 + 2*1px border-width = 15px padding + 3px parent border */
                border-width: 1px;
                background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(150, 150, 150,85), stop: 0.3 rgba(1,1,1,50), stop: 1.0 rgba(125, 10, 1, 200));
                border-left-width: 0.5px;
                border-left-color: black;
                border-left-style: solid; /* just a single line */
                border-top-right-radius: 4px; /* same radius as the QComboBox */
                border-bottom-width: 0.5px;
                border-bottom-color: black;
                border-bottom-style: solid; /* just a single line */

            }

            QSpinBox::up-button:hover {
                background-color: rgba(255,255,255,20)
            }

            QSpinBox::down-button:hover {
                background-color: rgba(255,255,255,20)
            }

            QSpinBox::up-button:pressed {
                background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(80, 10, 1, 100), stop: 0.3 rgba(1,1,1,50), stop: 1.0 rgba(200, 200, 200,125));
            }

            QSpinBox::down-button:pressed {
                background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(80, 10, 1, 100), stop: 0.3 rgba(1,1,1,50), stop: 1.0 rgba(200, 200, 200,125));
            }

            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right; /* position at the top right corner */

                width: 27px; /* 16 + 2*1px border-width = 15px padding + 3px parent border */
                border-width: 1px;
                background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(150, 150, 150,85), stop: 0.3 rgba(1,1,1,50), stop: 1.0 rgba(125, 10, 1, 200));
                border-left-width: 0.5px;
                border-left-color: black;
                border-left-style: solid; /* just a single line */
                border-bottom-right-radius: 4px; /* same radius as the QComboBox */
                border-top-width: 0.5px;
                border-top-color: black;
                border-top-style: solid; /* just a single line */
            }"""

class CustomSpinBox_02(CustomSpinBox):
    def __init__(self):
        super(CustomSpinBox_02, self).__init__()
        self.setStyleSheet(QSpinCSS_03)
