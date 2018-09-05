try:
    import maya.cmds       as cmds
    import pymel.core      as pm
    import maya.OpenMaya   as om
    import maya.OpenMayaUI as mui
    import shiboken        as shi
    import os

    from HitchAnimationModule.Widgets import Tabs
    from HitchAnimationModule.Widgets import CustomDial
    from HitchAnimationModule.Widgets import spliter
    from HitchAnimationModule.Widgets import CustomGroup
    from HitchAnimationModule.Widgets import label
    from HitchAnimationModule.Widgets import ColtSpinBox
    from HitchAnimationModule.SubClasses import ChannelBoxColt; reload(ChannelBoxColt)
    from HitchAnimationModule.LogicData import refreshUI
    from HitchAnimationModule.Widgets import button
    from HitchAnimationModule.Widgets import slider

except: pass
############
from PySide.QtGui import QPen, QColor, QBrush, QLinearGradient, QFont, QRadialGradient
from PySide import QtCore as qc
from PySide import QtGui as qg
from functools import partial
import random
import math
import re
#------------------------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------------------------#
# Globals
CHARACTER_BOUNDING_BOX = 'hitch_body_main'
#----------------------------------------------------------------------------------------#
class ViewportTab(qg.QWidget):
    def __init__(self):
        super(ViewportTab,self).__init__()

        self.setObjectName('ViewportClass')
        self.clean_cameras()
        #################################################
        # CAMERA AREA
        #
        self.UI_camera  = None
        self.UI_cameraShape = None
        self.UI_object  = CHARACTER_BOUNDING_BOX
        self.numLaps = None
        self.duration = None

        self.UI_object_height = 0
        self.UI_object_bottom = (0,0,0)
        self.UI_object_full_rotation = 0

        # start box
        self.cam_dist_start = 0
        self.cam_rot_start = 0
        self.cam_pos_start = 0
        self.cam_height_start = 0

        # end box
        self.cam_end_enabled = False
        self.cam_dist_end = 0
        self.cam_rot_end = 0
        self.cam_pos_end = 0
        self.cam_height_end = 0

        # timer Qtimer events
        self.timeline_timer = qc.QTimer()
        self.timeline_timer.setInterval(42)


        ##################################################
        general_lyt = qg.QVBoxLayout()
        self.setLayout(general_lyt)
        general_lyt.setObjectName('general_lyt')


        ##################################################
        # HELPER FINDER
        #

        self.scene = refreshUI.resetScene()

        #######################
        # ViewportTab
        #
        tabCentral_wdg = qg.QWidget()
        tabCentral_wdg.setObjectName('tabCentral_wdg')
        general_lyt.addWidget(tabCentral_wdg)
        fixedHBox_lyt = qg.QHBoxLayout(tabCentral_wdg)
        fixedHBox_lyt.setObjectName('fixedHBox_lyt')

        ####################
        # QGraphics Escene
        #
        self.graphics_scene = qg.QGraphicsScene()
        self.graphics_view  = qg.QGraphicsView()
        self.graphics_view.cacheMode()
        self.graphics_view.setObjectName('Viewport_graphicsView')
        self.graphics_view.setCacheMode(qg.QGraphicsItem.  DeviceCoordinateCache)
        self.graphics_view.setOptimizationFlags(qg.QGraphicsView.DontSavePainterState)
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.graphics_view.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.graphics_view.setFocusPolicy(qc.Qt.NoFocus)
        self.graphics_view.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)

        # Left panel channel box
        #
        ScrollWidget = qg.QWidget()
        scroll_area = qg.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOn)
        scroll_area.setFocusPolicy(qc.Qt.NoFocus)
        scroll_area.setFrameShape(qg.QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        scroll_area.setWidget(ScrollWidget)

        left_panel_lyt = qg.QVBoxLayout()
        holder = ScrollBackGround()
        holder_lyt = qg.QVBoxLayout(holder)
        holder_lyt.addWidget(scroll_area)
        left_panel_lyt.addWidget(holder)
        left_panel_lyt.setContentsMargins(0,0,0,0)
        holder_lyt.setContentsMargins(0,0,0,0)

        fixedHBox_lyt.addWidget(self.graphics_view)
        self.proxyView = self.graphics_view.setLayout(left_panel_lyt)

        # Viewport_layout right one!
        self.right_panel_lyt = qg.QVBoxLayout()
        fixedHBox_lyt.addLayout(self.right_panel_lyt)

        #######################
        # Scroll TurnAround Button
        #
        ScrollLayout = qg.QVBoxLayout(ScrollWidget)
        ScrollLayout.setContentsMargins(0,0,0,0)

        ###################################################
        # CHANNELBOX AREA
        #
        channelBox = ChannelBoxColt.ChannelBoxColt()
        ScrollLayout.addWidget(channelBox)

        self.stack_lytCameraZone = qg.QStackedLayout()
        ###################################
        # Camera Name
        self.stack_lytCameraZone.addWidget(qg.QWidget())
        self.stackedCamera_wdg_holder  = qg.QWidget()
        self.cameraNameLyt = qg.QVBoxLayout(self.stackedCamera_wdg_holder)
        self.stackedCamera_wdg_holder.setSizePolicy(qg.QSizePolicy.Expanding,qg.QSizePolicy.Minimum)
        self.turnAroundLabel = button.FlatBlackButton('Turn Around Zone')
        self.turnAroundLabel.setSizePolicy(qg.QSizePolicy.Expanding,qg.QSizePolicy.Minimum)
        ScrollLayout.addWidget(self.turnAroundLabel)
        ScrollLayout.addLayout(self.stack_lytCameraZone)

        self.stack_lytCameraZone.addWidget(self.stackedCamera_wdg_holder)


        self.cameraNameLyt.setContentsMargins(2,1,2,2)
        self.cameraNameLyt.addSpacing(20)
        self.cameraNameLyt.setAlignment(qc.Qt.AlignBottom)

        ####################################
        # SpinBox
        #
        gnlCam_options_lyt = qg.QFormLayout()
        self.cameraNameLyt.addLayout(gnlCam_options_lyt)
        self.numLapsSpin = ColtSpinBox.CustomSpinBox()
        self.numLapsSpin.setSizePolicy(qg.QSizePolicy.Expanding,qg.QSizePolicy.Minimum)
        self.numLapsSpin.setMinimum(1)
        self.numLapsSpin.setMaximum(100)
        self.framesSpin  = ColtSpinBox.CustomSpinBox()
        self.framesSpin.setSizePolicy(qg.QSizePolicy.Expanding,qg.QSizePolicy.Minimum)
        self.framesSpin.setMinimum(2)
        self.framesSpin.setMaximum(5000)

        laps_lb = label.CustomShortLabel('  - Number of  laps - ')
        frames_lb = label.CustomShortLabel(' - Frames per laps - ')

        laps_lb.hide()
        frames_lb.hide()
        self.framesSpin.hide()
        self.numLapsSpin.hide()

        #gnlCam_options_lyt.addRow(laps_lb, self.numLapsSpin)
        #gnlCam_options_lyt.addRow(frames_lb, self.framesSpin)

        # Start GroupBox
        #
        startBox = CustomGroup.CustomGroupBox("- Start -")
        startBox.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)
        self.cameraNameLyt.addWidget(startBox)
        startBox_lyt = qg.QFormLayout(startBox)

        # Distance Slider
        dist_start_lb = label.CustomShortLabel('Distance')
        self.Qslider_dist = slider.CustomSlider_glow()
        self.Qslider_dist.setRange(0,100)

        startBox_lyt.addRow(dist_start_lb,self.Qslider_dist)

        # Height Slider
        height_start_lb = label.CustomShortLabel('Height')
        self.Qslider_height = slider.CustomSlider_glow()
        self.Qslider_dist.setRange(0,100)

        startBox_lyt.addRow(height_start_lb,self.Qslider_height)

        # Rotation Slider
        rot_start_lb = label.CustomShortLabel('Rotation')
        self.Qslider_rot = slider.CustomSlider_glow()
        self.Qslider_dist.setRange(0,100)

        startBox_lyt.addRow(rot_start_lb,self.Qslider_rot)

        # QDial Position
        pos_start_lb = label.CustomShortLabel('Position')
        self.Qdial_pos = CustomDial.MyDial()
        startBox_lyt.addRow(pos_start_lb,self.Qdial_pos)
        self.Qdial_pos.setRange(0,360)

        # End GroupBox ######################################################################################################## END GROUP BOX
        #
        endBox = CustomGroup.CustomGroupBox("- End -")
        endBox.hide()
        endBox.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)
        self.cameraNameLyt.addWidget(endBox)
        endBox.setCheckable(True)
        endBox.setChecked(False)
        startBox_lyt = qg.QFormLayout(endBox)

        # Distance Slider
        dist_cb_end_lb = label.CustomShortLabel('Distance')
        self.Qslider_dist_end = slider.CustomSlider_glow()
        self.Qslider_dist_end.setRange(0,100)

        startBox_lyt.addRow(dist_cb_end_lb,self.Qslider_dist_end)

        # Height Slider
        height_end_lb = label.CustomShortLabel('Height')
        self.Qslider_height_end = slider.CustomSlider_glow()
        self.Qslider_height_end.setRange(0,100)

        startBox_lyt.addRow(height_end_lb,self.Qslider_height_end)

        # Rotation Slider
        rot_end_lb = label.CustomShortLabel('Rotation')
        self.Qslider_rot_end = slider.CustomSlider_glow()
        self.Qslider_rot_end.setRange(0,100)


        startBox_lyt.addRow(rot_end_lb,self.Qslider_rot_end)

        # self.Qdial_pos_end Position
        pos_end_lb = label.CustomShortLabel('Position')
        self.Qdial_pos_end = CustomDial.MyDial()
        startBox_lyt.addRow(pos_end_lb,self.Qdial_pos_end)
        self.Qdial_pos_end.setRange(0,360)

        splitter = spliter.Splitter(color=(35,180,93))
        splitter.setFixedHeight(2)
        splitter.setFixedWidth(50)
        splitter_lyt = spliter.SplitterLayout()

        general_lyt.addLayout(splitter_lyt)
        self.layout().setContentsMargins(0,0,0,0)

        ###################################
        # Viewport Add
        #
        panel = qg.QLabel()
        panel.setObjectName('panelLayoutName')
        panel.setStyleSheet("background-color: rgba(0,120,119,80) ")
        self.right_panel_lyt.addWidget(panel)
        self.right_panel_lyt.setObjectName('rt_panel_layout')
        self.panel_lyt = qg.QHBoxLayout(panel)
        self.right_panel_lyt.setContentsMargins(0,0,0,0)



        # SLIDER AND PLAY BUTTON ---------------------------------------------------------------#
        #
        #

        self.time_line_wdg = qg.QWidget()
        self.time_line_wdg.setFixedHeight(28)
        self.time_line_wdg.hide()

        time_line_lyt = qg.QHBoxLayout(self.time_line_wdg)
        time_line_lyt.setContentsMargins(0,0,0,0)
        time_line_lyt.setAlignment(qc.Qt.AlignVCenter)

        self.slider_timeline = slider.CustomSlider()
        self.slider_timeline.setRange(0,100)
        self.slider_timeline.setSizePolicy(qg.QSizePolicy.Expanding , qg.QSizePolicy.Minimum)
        button_timeline = qg.QPushButton()
        button_timeline.setCheckable(True)

        icon_route = os.path.join(cmds.internalVar(usd=1) , 'HitchAnimationModule','Icons','play_green.png')
        pix_icon = qg.QPixmap(icon_route)
        scaled = pix_icon.scaled(40, 20 , qc.Qt.KeepAspectRatio, qc.Qt.SmoothTransformation)
        icon = qg.QIcon(pix_icon)

        button_timeline.setIcon(icon)
        button_timeline.setFixedSize(40,20)
        button_timeline.setIconSize(scaled.rect().size())
        btn_css =   """QPushButton{
                        border: 0px solid;

                        }
                        QPushButton:pressed {
                            background-color: rgba(34, 181, 115,250);
                            border-style: inset;
                            border-width: 0px;
                            border-radius: 10px;


                        } """

        button_timeline.setStyleSheet(btn_css)

        time_line_lyt.addWidget(button_timeline)
        time_line_lyt.addWidget(self.slider_timeline)
        self.right_panel_lyt.addWidget(self.time_line_wdg)


        ########################################
        # some variables for elaborate functions and procress
        self._animation = None
        self.buttonSwitch = 0
        self.graphics_view .setFixedWidth(0)

        self._toogleCamera = 0
        self.stack_lytCameraZone.setCurrentIndex(0)

        # Opacity widget effect for the QscrollArea
        #
        self.opacity_wdt = qg.QGraphicsOpacityEffect(self.proxyView)
        ScrollWidget.setGraphicsEffect(self.opacity_wdt)

        # Opacity widget effect for the Camera_lyt
        #
        self.opacityCamera_wdt = qg.QGraphicsOpacityEffect(self.stack_lytCameraZone)
        self.stackedCamera_wdg_holder.setGraphicsEffect(self.opacity_wdt)
        self.opacityCamera_wdt.setOpacity(0.0)

        # HERE IS WHERE I ADD THE CAMERA TO THE VIEWPORT PANEL ...............................s
        #
        self.panels_array = []
        self.Viewport_maya, self.viewporName = self.add_viewport(self.panel_lyt)

        self.create_setup()
        self.update_cam_values()


# ---------------------------------------------------------------------------------------------------------- #
        # SIGNALS AND SLOTS:
        #

        self.turnAroundLabel.clicked.connect(lambda: self._toogleStackCamera(not(self._toogleCamera)))
        delete_cam = partial(cmds.delete, self.UI_camera)
        self.destroyed.connect(delete_cam)
        endBox.toggled.connect(lambda val:  self.camEndBox_state_change(val))

        self.numLapsSpin.valueChanged.connect(self.update_cam_values)
        self.framesSpin.valueChanged.connect(self.update_cam_values)

        # start widgets
        self.Qslider_dist.valueChanged.connect(self.update_cam_values)
        self.Qslider_height.valueChanged.connect(self.update_cam_values)
        self.Qslider_rot.valueChanged.connect(self.update_cam_values)
        self.Qdial_pos.valueChanged.connect(self.update_cam_values)

        # end widgets
        self.Qslider_dist_end.valueChanged.connect(self.update_cam_values)
        self.Qslider_height_end.valueChanged.connect(self.update_cam_values)
        self.Qslider_rot_end.valueChanged.connect(self.update_cam_values)
        self.Qdial_pos_end.valueChanged.connect(self.update_cam_values)

        self.timeline_timer.timeout.connect(self.timeline_nextStep)
        button_timeline.toggled.connect(lambda value: self.play_button_press(value))

        self.slider_timeline.valueChanged.connect(self.timeline_changed)

        top_panel = self.scene.findSceneChilds(qg.QFrame, 'topFrame')[0]
        top_panel.nameSpaceSignal.connect(lambda name: self.update_object(name))


# --------------------------------------------------------------------------------------------- #
    def update_object(self, name):
        line_edit = name
        nameSpace = line_edit.text() + ':' + CHARACTER_BOUNDING_BOX
        if line_edit.isReadOnly():
            self.UI_object = nameSpace
            print(self.UI_object)

        else:
            self.UI_object = CHARACTER_BOUNDING_BOX
            print(self.UI_object)


    ##########################################################################################
    def clean_cameras(self):
        sel = cmds.ls('Hitch_UI_Camera*')
        for itm in sel[1:-1]:
            try:
                m = re.search(r'\d+$', itm)
                if m is not None:
                    cmds.delete(itm)
            except:
                pass

    ##########################################################################################
    def update_cam_position(self):
        objeto = cmds.ls(self.UI_object)
        if len(objeto) < 1:
            return

        # cam position
        obj_pos = cmds.xform(objeto[0], q=True, t=True)

        # interpolacion lineal
        percentage =  0 #float((float(self.slider_timeline.value()) / 100) * 100)
        position = self.cam_pos_start + (self.UI_object_full_rotation * percentage)
        rotation = self.cam_rot_start + ((self.cam_rot_end - self.cam_dist_start) * percentage)
        distance = self.cam_dist_start + ((self.cam_rot_end - self.cam_dist_start) * percentage)
        height = self.cam_height_start + (self.cam_height_end - self.cam_height_start) * percentage

        # update de pos of the camera
        obj_pos[0] += math.sin(math.radians(position)) * distance
        obj_pos[1] += (float(height) / 100) * self.UI_object_height
        obj_pos[2] += math.cos(math.radians(position)) * distance

        cmds.xform(self.UI_camera, t=obj_pos)

        # update the rotation with the inverse of the position angle in obj space
        rotation_percentage = float(rotation) / 100
        xpos = self.UI_object_bottom[0]
        ypos = self.UI_object_bottom[1] + rotation_percentage * self.UI_object_height
        zpos = self.UI_object_bottom[2]

        try:
            cmds.viewPlace(self.UI_cameraShape, la=(xpos,ypos,zpos))
        except:
            cmds.viewFit(self.UI_cameraShape , all=True)


    ##########################################################################################
    def timeline_changed(self, value):
        percentage = float((float(self.slider_timeline.value()) / 100) * 100)
        valor = percentage * 3.6
        self.slider_timeline.blockSignals(True)
        self.Qdial_pos.setValue(valor)
        self.slider_timeline.blockSignals(False)

    ###########################################################################################
    def play_button_press(self, active):
        if active:
            self.slider_timeline.setAttribute(qc.Qt.WA_TransparentForMouseEvents, on=True)
            self.slider_timeline.changeColor(True)
            self.timeline_timer.start()

        else:
            self.slider_timeline.setAttribute(qc.Qt.WA_TransparentForMouseEvents, on=False)
            self.slider_timeline.changeColor(False)
            self.slider_timeline.repaint()
            self.timeline_timer.stop()
            self.slider_timeline.setValue(0)

    ##############################################################################################
    def timeline_nextStep(self):
        if self.slider_timeline.value() == self.slider_timeline.maximum():
            self.slider_timeline.setValue(0)

        else:
            self.slider_timeline.setValue(self.slider_timeline.value() + 1)


    #################################################################################################
    def camEndBox_state_change(self,Value):
        self.cam_end_enabled = Value
        self.update_cam_values()

    ###################################################################################################
    def update_cam_values(self):
        self.numLaps = self.numLapsSpin.value()
        self.duration = self.framesSpin.value()

        # start box
        self.cam_dist_start = self.Qslider_dist.value()
        self.cam_rot_start = self.Qslider_rot.value()
        self.cam_pos_start = self.Qdial_pos.value()
        self.cam_height_start = self.Qslider_height.value()

        if not self.cam_end_enabled:
            self.Qslider_dist_end.blockSignals(True)
            self.Qslider_height_end.blockSignals(True)
            self.Qslider_rot_end.blockSignals(True)
            self.Qdial_pos_end.blockSignals(True)

            self.Qslider_dist_end.setValue(self.cam_dist_start)
            self.Qslider_height_end.setValue(self.cam_height_start)
            self.Qslider_rot_end.setValue(self.cam_rot_start )
            self.Qdial_pos_end.setValue(self.cam_pos_start)

            self.Qslider_dist_end.blockSignals(False)
            self.Qslider_height_end.blockSignals(False)
            self.Qslider_rot_end.blockSignals(False)
            self.Qdial_pos_end.blockSignals(False)

        # end box
        self.cam_dist_end = self.Qslider_dist_end.value()
        self.cam_rot_end = self.Qslider_rot_end.value()
        self.cam_pos_end = self.Qdial_pos_end.value()
        self.cam_height_end = self.Qslider_height_end.value()

        self.updateFull_rotation()
        self.update_cam_position()


    ###################################################################
    def updateFull_rotation(self):
        if self.cam_pos_end == self.cam_pos_start:
            self.UI_object_full_rotation = 360

        # degrees between start and end
        else:
            self.UI_object_full_rotation = self.cam_pos_end - self.cam_pos_start

        ## multiply the lasps rot for each num laps
        if self.numLaps > 1:
            self.UI_object_full_rotation += (self.numLaps - 1 ) * 360

    ###################################################################
    # data for positioning the camera from the UI
    def getObjectData(self,object):

        xmin, ymin, zmin, xmax, ymax, zmax = cmds.xform(object, q=True, bb=True)
        width = xmax - xmin
        height = ymax - ymin
        depth = zmax - zmin

        center = ((xmin + xmax) / 2, (ymin + ymax) / 2, (zmin + zmax) / 2)
        bottom = (center[0], ymin, center[2])
        radius = max([width, height, depth]) / 2.0
        return width, depth, height, center, bottom, radius



    ############################################################################
    # creates the set up for the turn around procs
    def create_setup(self):
        objecto = cmds.ls(self.UI_object)
        cmds.viewFit(self.UI_cameraShape , all=True)
        if len(objecto) < 1:
            return

        # CREATE CAMERA OR CONFIGURE IT
        _width, _depth , height , _center , bottom, radius = self.getObjectData(objecto[0])

        self.UI_object_height = height
        self.UI_object_radius = radius
        self.UI_object_bottom = bottom

        # CENTRAR LOS WIDGETS THE TURN AROUND HERE
        # slider distancia
        self.Qslider_dist.blockSignals(True)
        medium = (radius * 5)
        self.Qslider_dist.setRange(0, radius  * 5)
        self.Qslider_dist.setValue(medium)
        self.Qslider_dist.blockSignals(False)

        self.Qslider_dist_end.setRange(radius, radius  * 5)

        # altura slider
        self.Qslider_height.blockSignals(True)
        self.Qslider_height.setValue(50 + 15)
        self.Qslider_height.blockSignals(False)

        # altura slider
        self.Qslider_rot.blockSignals(True)
        self.Qslider_rot.setValue(50 + 10)
        self.Qslider_rot.blockSignals(False)

        # timeline
        self.slider_timeline.setValue(0)


    #######################################################################################
    # Creates UI Camera Nodes function
    def create_camera(self):
        camera_name, camera_shape = cmds.camera(name='Hitch_UI_Camera')
        cmds.hide(camera_name)
        cmds.setAttr(camera_name + '.hiddenInOutliner', 1)
        #cmds.select(camera_shape)
        return camera_name, camera_shape


    #########################################################################################
    # i dont know what da fuck is doing this ....camera_name
    def _camera_lyt_anim(self, value):
        Proxy = self.opacityCamera_wdt
        opacity_anim = qc.QPropertyAnimation(Proxy, "opacity")
        opacity_anim.setStartValue(float(value))
        opacity_anim.setEndValue(float(not(value)))
        opacity_anim.setDuration(5000)
        opacity_anim_curve = qc.QEasingCurve()

        if value:
            #Proxy.setOpacity(float(0))
            opacity_anim_curve.setType(qc.QEasingCurve.InQuad)
            opacity_anim.setEasingCurve(opacity_anim_curve)
            opacity_anim.start(qc.QAbstractAnimation.DeleteWhenStopped)

        else:
            #Proxy.setOpacity(float(1))
            opacity_anim_curve.setType(qc.QEasingCurve.OutQuad)
            opacity_anim.setEasingCurve(opacity_anim_curve)
            opacity_anim.start(qc.QAbstractAnimation.DeleteWhenStopped)


    ###########################################################################
    # toogleStack layout
    def _toogleStackCamera(self, value):
        self.stack_lytCameraZone.setCurrentIndex(value)
        if not value:
            self.time_line_wdg.hide()
        elif value:
            self.time_line_wdg.show()

        self._camera_lyt_anim(value)
        self._toogleCamera = not(bool(self._toogleCamera))

    ############################################################################
    # UPDATE VIEWPORT PANEL
    #

    def updateViewport(self, *args, **kwargs):
        topPanel = self.scene.findSceneChilds(qg.QFrame, 'topFrame')[0]
        line_edit = topPanel.nameSpace_le
        self.update_object(line_edit)
        self.create_setup()
        self.update_cam_values()

        viewport = self.viewporName

        cmds.modelEditor(modelPanel=viewport, cam = self.UI_camera ,wireframeOnShaded=False,wireframeBackingStore=False,displayTextures=True,subdivSurfaces=False,
                         rnm='base_OpenGL_Renderer',displayAppearance = "smoothShaded", hud=False)


    #############################################################################
    def labelAnimationConnect(self, button):
        if self.buttonSwitch == 0:
            self._animateExpand(self.graphics_view ,not(button.isDown()))

        if self.buttonSwitch == 1:
            self._animateExpand(self.graphics_view ,button.isDown())

        if self.buttonSwitch != 1:
            self.buttonSwitch += 1
        else:
            self.buttonSwitch = 0


    def _animateExpand(self, widget, value):
        Proxy = self.opacity_wdt
        opacity_anim = qc.QPropertyAnimation(Proxy, "opacity")
        opacity_anim.setStartValue(not(value))
        opacity_anim.setEndValue(value)
        opacity_anim.setDuration(200)
        opacity_anim_curve = qc.QEasingCurve()

        if value is True:
            opacity_anim_curve.setType(qc.QEasingCurve.InQuad)
        else:
            opacity_anim_curve.setType(qc.QEasingCurve.OutQuad)

        opacity_anim.setEasingCurve(opacity_anim_curve)

        size_anim = qc.QPropertyAnimation(widget, "geometry")
        geometry = widget.geometry()
        height    = geometry.height()
        x, y, _, _ = geometry.getCoords()

        size_start = qc.QRect(x, y, int(not(value)) * 225, height)
        size_end   = qc.QRect(x, y, value * 225, height )

        size_anim.setStartValue(size_start)
        size_anim.setEndValue(size_end)
        size_anim.setDuration(250)

        size_anim_curve = qc.QEasingCurve()

        if value:
            size_anim_curve.setType(qc.QEasingCurve.InSine)
        else:
            size_anim_curve.setType(qc.QEasingCurve.OutCubic)

        size_anim.setEasingCurve(size_anim_curve)

        self._animation = qc.QSequentialAnimationGroup()

        if value:
            Proxy.setOpacity(0)
            self._animation.addAnimation(size_anim)
            self._animation.addAnimation(opacity_anim)
            self.turnAroundLabel.setEnabled(True)

        else:
            Proxy.setOpacity(1)
            self._animation.addAnimation(opacity_anim)
            self._animation.addAnimation(size_anim)
            self.turnAroundLabel.setEnabled(False)

        size_anim.valueChanged.connect(self._forceResize)
        self._animation.finished.connect(self._animation.clear)
        self._animation.start(qc.QAbstractAnimation.DeleteWhenStopped)


    def _forceResize(self, new_height):
        self.graphics_view.setFixedWidth(new_height.width())


    # hide menu panel because is annoying ....
    def hideIconMenu(self):
        # This turns off the icon button panel above all model editors. If you want it back on switch the 0 to a 1 on the top piece of code.
        #print ' THIS SHOULD BE TURNING OFF THE ICON BUTTON MENU '
        pm.mel.eval('optionVar -iv "collapseIconBarsInPanels" 0;') # switch this 0 to a 1 if you want it to come back on.
        pm.mel.eval("if (`optionVar -q collapseIconBarsInPanels`) {toggleModelEditorBarsInAllPanels 0;} else {toggleModelEditorBarsInAllPanels 1;};")


    # recreates the panel because everytime i close maya this dissapearss ...
    def re_create_panel(self):
        for idx in range(self.panel_lyt.count()):
            widget = self.panel_lyt.takeAt(idx).widget()
            widget.deleteLater()
            del(widget)

        self.Viewport_maya, self.viewporName = self.add_viewport(self.panel_lyt)
        print('panel editor re-created!')


    # HERE IS WHERE THE ACTION BEGGINS ....

    def add_viewport(self,lyt):
        OldPanels = [itm for itm in cmds.getPanel(type='modelPanel') if 'embeddedModelPanel' in itm]
        model_test = cmds.getPanel(withLabel='modelPanel_UI')

        for panel in OldPanels:
            if (cmds.modelPanel(panel, exists=True)):
                cmds.deleteUI(panel, panel=True)

        try:
            if (cmds.modelPanel(model_test, exists=True)):
                cmds.deleteUI(model_test, panel=True)
        except:
            pass


        lyt.setObjectName("mainLayout")
        layout = mui.MQtUtil.fullName(long(shi.getCppPointer(lyt)[0]))
        #print (layout)
        par = cmds.setParent(layout)
        panel_lyt_name = cmds.paneLayout()
        modelPanelName = "embeddedModelPanel{}".format(random.randrange(101,54612658412196513465))

        ptr = mui.MQtUtil.findControl(panel_lyt_name)
        paneLayout = shi.wrapInstance(long(ptr), qg.QWidget)

        self.UI_camera, self.UI_cameraShape = self.create_camera()

        modelPanel_Name = cmds.modelPanel(modelPanelName, label='modelPanel_UI', cam=self.UI_camera, menuBarVisible=False, init=True)
        cmds.modelEditor(modelPanel=modelPanel_Name,wireframeOnShaded=False,wireframeBackingStore=False,displayTextures=True,subdivSurfaces=False,
                         rnm='base_OpenGL_Renderer',displayAppearance = "smoothShaded", hud=False)

        self.hideIconMenu()
        ptr_01 = mui.MQtUtil.findControl(modelPanel_Name)
        modelPanelExit = shi.wrapInstance(long(ptr_01), qg.QWidget)

        return paneLayout, modelPanel_Name

 # -------------------------------------------------------- #

class ScrollBackGround(qg.QFrame):
    def __init__(self):
        super(ScrollBackGround, self).__init__()
        self.setObjectName('scrollFrame')
        self.setStyleSheet("""QFrame {background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(80,150,150,150), stop: 0.4 rgba(40,135,135,130), stop: 1.0 rgba(0,120,119,80));}""")
