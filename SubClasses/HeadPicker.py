try:
    import maya.cmds       as cmds
    import pymel.core      as pm
    import maya.OpenMaya   as om
    import maya.OpenMayaUI as mui
    import shiboken        as shi
    from HitchAnimationModule.Widgets import button
    from HitchAnimationModule.Widgets    import PickerButtons
    from HitchAnimationModule.ControlList import ControlList
    from HitchAnimationModule.LogicData import ConnectControls
    from HitchAnimationModule.LogicData import new_snaps
    from HitchAnimationModule.Widgets import label
    from HitchAnimationModule.Widgets import ColtSpinBox
    from HitchAnimationModule.LogicData import OperationsFile
    from HitchAnimationModule.LogicData import refreshUI

except: pass
############
from PySide import QtCore as qc
from PySide import QtGui as qg
from PySide.QtCore import Signal
from functools import partial
import math
import copy
import os
from contextlib import contextmanager
#------------------------------------------------------------------------------------------------------------#

try:
    FACEPICKER = os.path.join(pm.internalVar(usd=1) , 'HitchAnimationModule','Icons','Hitch_FaceForPicker.png')

    FACE_RED_CONTROLS = ControlList.FACE_RED_CONTROLS
    FACE_YELLOW_CONTROLS = ControlList.FACE_YELLOW_CONTROLS
    FACE_ORANGE_CONTROLS = ControlList.FACE_ORANGE_CONTROLS
    LIPS_CONTROLS = ControlList.FACE_LIPS_CONTROLS
    FACECONTROLS = ControlList.FACECONTROLS
    pause_callBacks = refreshUI.pause_callBacks
except: pass



######################################################################################################
@contextmanager
def pause_callBacks():
    scene = refreshUI.resetScene()
    ################# Get the instances of the classes witch contains callbacks
    channelBox = scene.findSceneChilds(qg.QFrame, 'ChannelBoxColt')[0]
    ###
    topPanel = scene.findSceneChilds(qg.QFrame, 'topFrame')[0]

    try:
        channelBox.disconnect( channelBox , qc.SIGNAL('destroyed()'), channelBox.callbackkill)
        topPanel.disconnect( topPanel , qc.SIGNAL('destroyed()') , topPanel.callbackkill)
        channelBox.destroyed.disconnect()

        print('Old Signals disconnected')

    except:
        print('Failed to disconnect',  channelBox.callbackkill)
        print('Failed to disconnect' , topPanel.callbackkill)

    ### TO DEBUGG THE SIGNALS CONNECTED
    channelBox_signal_count  =  channelBox.receivers(qc.SIGNAL('destroyed()'))
    print(channelBox_signal_count)

    panel_signal_count  =  topPanel.receivers(qc.SIGNAL('destroyed()'))
    print(panel_signal_count)
    ##########################
    ###
    # Kill both callbacks for a moment
    om.MMessage.removeCallback(channelBox.sel_idx)
    om.MMessage.removeCallback(topPanel.sel_idx)

    channelBox.callbackkill = None
    topPanel.callbackkill = None

    channelBox.sel_idx = None
    topPanel.sel_idx = None

    channelBox.destroy_callback = None
    topPanel.destroy_callback = None

    yield  ################## YIIIIIIIIEEELLLDDDDDD !!!!!!!!!!!!!!!!!!!!!!!!

    # CHANNELBOX NEW CALLBACKS
    channelBox.sel_idx = om.MEventMessage.addEventCallback("SelectionChanged", channelBox.refresDisplay)
    channelBox.callbackkill = partial(om.MMessage.removeCallback, channelBox.sel_idx)
    channelBox.destroy_callback = channelBox.destroyed.connect(channelBox.callbackkill)

    # TOP PANEL NEWCALLBACKS
    topPanel.sel_idx = om.MEventMessage.addEventCallback("SelectionChanged", topPanel.populate_space_list)
    topPanel.callbackkill = partial(om.MMessage.removeCallback, topPanel.sel_idx)
    topPanel.destroy_callback = channelBox.destroyed.connect(topPanel.callbackkill)

    del(scene)
    # End of the contextmanager ...
#------------------------------------------------------------------------------------------------------------#
@contextmanager
def delete_callbacks():

    scene = refreshUI.resetScene()
    ################# Get the instances of the classes witch contains callbacks
    channelBox = scene.findSceneChilds(qg.QFrame, 'ChannelBoxColt')[0]

    for item in channelBox.callBacks_ids:
        #print(item)
        #print(item[-1].length())

        #om.MMessage.removeCallback(item[0])
        call = om.MMessage.removeCallbacks(item[-1])

        method = item[1]
        channelBox.disconnect( channelBox , qc.SIGNAL('destroyed()'), method)

    #clean the arrays after delete everything inside .....
    channelBox.ids_array.clear()  # callback id array

    if len (channelBox.callBacks_ids) < 1000:
        channelBox.callBacks_ids = []

    yield

    # just continues the proceess, other  methods will createm back again ..
    getattr(channelBox, 'refresDisplay')()

#------------------------------------------------------------------------------------------------------------#

def deletingIndex(jobs):
    try:
        for index in jobs:
            cmds.scriptJob(kill=index, force=True)
            #print('index: {} killed'.format(index))
            del(index)
    except:
        pass
# ---------------------------------------------------------------------------#

@contextmanager
def noSignals(obj):
    obj.blockSignals(True)
    yield
    obj.blockSignals(False)

# ---------------------------------------------------------------------------#
class HeadPicker(qg.QLabel):
    def __init__(self):
        super(HeadPicker,self).__init__()
        ######### Pixmap Head ##########
        self.setStyleSheet(""" background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.2 ,
                         fx: 0.5 , fy: 0.5, stop: 0 rgba(53, 57, 60,255), stop: 0.7 rgba(25,15,05,50), stop: 1.1 rgba(33, 34, 36, 255));""")

        self.setAlignment(qc.Qt.AlignHCenter | qc.Qt.AlignVCenter)
        self.setContentsMargins(0,0,0,0)
        self.setObjectName('HeadPicker')
        main_ui  = ConnectControls.getMainWindow(ConnectControls.windowObject)
        self.setParent(main_ui)
        self.op = OperationsFile.Operations()

        # NAME SPACE  #######################################################
        #
        self._child_widgets = []
        self._manager  = ConnectControls.ManageControls()
        self.prefix = None

        # PANELS CALLBACKS MANAGER ZONE  #######################################################
        #
        self.callbacks_array = []
        self._scene = refreshUI.resetScene()

        # STACK CONFIGURATION #######################################################
        #
        #
        self.stackLayout = qg.QStackedLayout()
        self.stackLayout.setObjectName('Main_stacked_layout')
        self.stackLayout.setContentsMargins(0,0,0,0)
        self.stackLayout.setStackingMode(qg.QStackedLayout.StackAll)
        self.stackLayout.setAlignment(qc.Qt.AlignVCenter | qc.Qt.AlignHCenter)

        self.setLayout(self.stackLayout)

        top_loc = 'TopBody_Attrributes.'

        ######################################################################################################################################################################
        #   PICKER HERE !!!!!
        #
        self.labelPicker = StaticFacePickerLabel()
        self.layout().addWidget(self.labelPicker)
        self.wire_bottom_btn = self.labelPicker.HitchHeadWire_Down_Ctrl

        ########################################################################################################################################################################
        #   MAIN WIDGET FROM PICKER

        # this is on the top of the widgets... should be on the background in first place ....
        self._mainWidget = qg.QWidget()
        self._mainWidget.setContentsMargins(0,0,0,0)
        self.stackLayout.addWidget(self._mainWidget)

        self.main_lyt = qg.QVBoxLayout(self._mainWidget)
        self.main_lyt.setContentsMargins(2,1,2,1)
        self.main_lyt.setAlignment(qc.Qt.AlignBottom)

        self.layout().addWidget(self._mainWidget)
        ###############################################################################

        ###############################################################################
        # TOP RIGTH CORNER WIDGETS
        self.top_rigth_corner_wdg = OpaqueWidget()
        self.top_rigth_corner_wdg.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)
        self.top_rigth_corner_wdg.setParent(self)
        self.top_rigth_corner_wdg.setFixedHeight(400)
        self.top_rigth_corner_wdg.setFixedWidth(180)
        self.top_rigth_corner_wdg_lyt = qg.QHBoxLayout(self.top_rigth_corner_wdg)
        self.top_rigth_corner_wdg_lyt.setContentsMargins(0,0,0,0)
        self.top_rigth_corner_wdg_lyt.setAlignment(qc.Qt.AlignCenter)

        vertical_lyt_top = qg.QVBoxLayout()
        vertical_lyt_top.setAlignment(qc.Qt.AlignRight)
        vertical_lyt_top.setContentsMargins(0,5,0,5)
        self.top_rigth_corner_wdg_lyt.addLayout(vertical_lyt_top)

        vis_label = label.CustomClearLabel('Visibility panel')
        vertical_lyt_top.addWidget(vis_label)
        vertical_lyt_top.addSpacing(20)

        form_vis_layout = qg.QFormLayout()
        form_vis_layout.setContentsMargins(15,0,0,0)
        form_vis_layout.setAlignment(qc.Qt.AlignCenter)
        vertical_lyt_top.addLayout(form_vis_layout)


        self.headWire_spin = ColtSpinBox.CustomSpinBox()
        self.headWire_spin.setObjectName(top_loc + 'HeadWire_Vis')
        form_vis_layout.addRow(label.CustomShortLabel('HeadWire'),self.headWire_spin)
        self.top_layer_spin = ColtSpinBox.CustomSpinBox()
        self.top_layer_spin.setObjectName(top_loc + 'HeadTop_layer_Vis')
        form_vis_layout.addRow(label.CustomShortLabel('TopLayer'),self.top_layer_spin)
        self.face_refine_spin = ColtSpinBox.CustomSpinBox()
        self.face_refine_spin.setObjectName(top_loc + 'Face_Refine_Vis')
        form_vis_layout.addRow(label.CustomShortLabel('FaceRef'),self.face_refine_spin)
        self.eyebrow_spin = ColtSpinBox.CustomSpinBox()
        self.eyebrow_spin.setObjectName(top_loc + 'eyeBrows_Vis')
        form_vis_layout.addRow(label.CustomShortLabel('Brows'),self.eyebrow_spin)
        self.eyes_refine_spin = ColtSpinBox.CustomSpinBox()
        self.eyes_refine_spin.setObjectName(top_loc + 'Eyes_Refine_Vis')
        form_vis_layout.addRow(label.CustomShortLabel('EyesRef'),self.eyes_refine_spin)

        self.eyes_main_spin = ColtSpinBox.CustomSpinBox()
        self.eyes_main_spin.setObjectName(top_loc + 'EyesMain_lookAt_Vis')
        form_vis_layout.addRow(label.CustomShortLabel('EyesMain'),self.eyes_main_spin)
        self.eyes_local_spin = ColtSpinBox.CustomSpinBox()
        self.eyes_local_spin.setObjectName(top_loc + 'EyesManual_lookAt_Vis')
        form_vis_layout.addRow(label.CustomShortLabel('EyesLocal'),self.eyes_local_spin)
        self.lips_spin = ColtSpinBox.CustomSpinBox()
        self.lips_spin.setObjectName(top_loc + 'Lips_Vis')
        form_vis_layout.addRow(label.CustomShortLabel('Lips'),self.lips_spin)
        self.tonge_spin = ColtSpinBox.CustomSpinBox()
        self.tonge_spin.setObjectName(top_loc + 'Tonge_Vis')
        form_vis_layout.addRow(label.CustomShortLabel('Tonge'),self.tonge_spin)
        self.hair_spin = ColtSpinBox.CustomSpinBox()
        self.hair_spin.setObjectName(top_loc + 'HairFK_Vis')
        form_vis_layout.addRow(label.CustomShortLabel('Hair'),self.hair_spin)


        _toggle_all = button.FlatBlackButton_picker('Toggle/all')
        _toggle_all.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Minimum)
        vertical_lyt_top.addWidget(_toggle_all)

        spins = self.top_rigth_corner_wdg.findChildren(qg.QSpinBox)
        for spin in spins:
            spin.setRange(0,1)

        _toggle_all.clicked.connect(self.toogle_vis)


        #####################################################################################################################################################
        # BOTTOM RIGTH CORNER WIDGETS
        self.bottom_rigth_corner_wdg = OpaqueWidget()
        self.bottom_rigth_corner_wdg.setSizePolicy(qg.QSizePolicy.Fixed,qg.QSizePolicy.Minimum)
        self.bottom_rigth_corner_wdg.setParent(self)
        self.bottom_rigth_corner_wdg.setFixedHeight(145)

        self.bottom_rigth_corner_wdg_lyt = qg.QHBoxLayout(self.bottom_rigth_corner_wdg)
        bottom_rigth_01_lyt = qg.QFormLayout()

        self.bottom_rigth_corner_wdg_lyt.addLayout(bottom_rigth_01_lyt)

        self.envelope_button = button.Customflat_toogle_name_btn('On','Off')
        self.envelope_button.setObjectName(top_loc + 'EnvelopesFace')
        self.envelope_button.setChecked(True)
        self.envelope_button.setFixedWidth(60)
        bottom_rigth_01_lyt.addRow(label.CustomShortLabel('Envelopes'),self.envelope_button)

        self.dynamic_button = button.Customflat_toogle_name_btn('On','Off')
        self.dynamic_button.setObjectName(top_loc + 'Dynamic_Off')
        self.dynamic_button.setFixedWidth(60)
        self.dynamic_button.setChecked(False)
        bottom_rigth_01_lyt.addRow(label.CustomShortLabel('Dynamic Hair'),self.dynamic_button)

        self.dynamicValue_spin = ColtSpinBox.CustomSpinBox()
        self.dynamicValue_spin.setObjectName(top_loc + 'HAIR_Dyn_0_Fk_10')
        self.dynamicValue_spin.setRange(0,10)
        self.dynamicValue_spin.setValue(6)

        bottom_rigth_01_lyt.addRow(label.CustomShortLabel('Dynamic Value: Full/Fk'),self.dynamicValue_spin)


        #########################################################################################################################################################
        # BOTTOM RIGTH CORNER WIDGETS
        self.bottom_left_corner_wdg = OpaqueWidget()
        self.bottom_left_corner_wdg.setSizePolicy(qg.QSizePolicy.Fixed,qg.QSizePolicy.Minimum)
        self.bottom_left_corner_wdg.setParent(self)
        self.bottom_left_corner_wdg.setFixedHeight(180)
        self.bottom_left_corner_wdg.setFixedWidth(270)

        self.bottom_left_corner_wdg_lyt = qg.QHBoxLayout(self.bottom_left_corner_wdg)
        self.bottom_left_corner_wdg_lyt.setContentsMargins(1,1,1,1)

        bottom_left_layout = qg.QVBoxLayout()
        bottom_left_layout.setSpacing(10)
        bottom_left_layout.setAlignment(qc.Qt.AlignCenter)
        self.bottom_left_corner_wdg_lyt.addLayout(bottom_left_layout)

        horizontal_bottom_left_lyt = qg.QHBoxLayout()
        horizontal_bottom_left_lyt.setAlignment(qc.Qt.AlignCenter)
        horizontal_bottom_left_lyt.setSpacing(2)
        horizontal_bottom_left_lyt.setContentsMargins(1,1,1,1)

        settings_label = label.CustomClearLabel('Settings')
        bottom_left_layout.addWidget(settings_label)

        bottom_left_form_lyt = qg.QFormLayout()
        bottom_left_form_lyt.setAlignment(qc.Qt.AlignRight)
        bottom_left_form_lyt.setSpacing(5)

        bottom_left_layout.addLayout(horizontal_bottom_left_lyt)
        horizontal_bottom_left_lyt.addLayout(bottom_left_form_lyt)

        bottom_left_form_lyt_02 = qg.QFormLayout()
        bottom_left_form_lyt_02.setSpacing(5)
        horizontal_bottom_left_lyt.addLayout(bottom_left_form_lyt_02)


        self.l_eyelipUp_spin = ColtSpinBox.CustomDoubleSpinBox()


        self.l_eyelipUp_spin.setObjectName(top_loc + 'L_eyelip_up')
        bottom_left_form_lyt.addRow(label.CustomShortLabel('L eyelipUp'),self.l_eyelipUp_spin)
        self.l_eyelipDw_spin = ColtSpinBox.CustomDoubleSpinBox()
        self.l_eyelipDw_spin.setObjectName(top_loc + 'L_eyelip_Dw')
        bottom_left_form_lyt.addRow(label.CustomShortLabel('L eyelipDw'),self.l_eyelipDw_spin)
        self.r_eyelipUp_spin = ColtSpinBox.CustomDoubleSpinBox()
        self.r_eyelipUp_spin.setObjectName(top_loc + 'R_eyelip_Up')
        bottom_left_form_lyt.addRow(label.CustomShortLabel('R eyelipUp'),self.r_eyelipUp_spin)
        self._r_eyelipDw_spin = ColtSpinBox.CustomDoubleSpinBox()
        self._r_eyelipDw_spin.setObjectName(top_loc + 'R_eyelip_Dw')
        bottom_left_form_lyt.addRow(label.CustomShortLabel('R eyelipDw'),self._r_eyelipDw_spin)

        self.l_sneer_spin = ColtSpinBox.CustomDoubleSpinBox()
        self.l_sneer_spin.setObjectName("Sneer_l_Ctrl.Sneer_Breath_In")
        bottom_left_form_lyt_02.addRow(label.CustomShortLabel('L Sneer'),self.l_sneer_spin)
        self.r_sneer_spin = ColtSpinBox.CustomDoubleSpinBox()
        self.r_sneer_spin.setObjectName("Sneer_r_Ctrl.Sneer_Breath_In")
        bottom_left_form_lyt_02.addRow(label.CustomShortLabel('R Sneer'),self.r_sneer_spin)

        self.sticky_spin = ColtSpinBox.CustomSpinBox()
        self.sticky_spin.setObjectName("jaw_bind_Ctrl.Sticky_Lips")
        bottom_left_form_lyt_02.addRow(label.CustomShortLabel('Sticky L'),self.sticky_spin)

        spins = self.bottom_left_corner_wdg.findChildren(qg.QDoubleSpinBox)
        for spin in spins:
            spin.setRange(-1,1)

        self.sticky_spin.setRange(0,100)

        #################################################################################
        self.header_label = Header_custom_label()
        self.header_label.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)
        self.header_label.setParent(self)


        ####################################################################################################################################################################
        # LEFT SIDE
        self.left_side_holder = OpaqueWidget()
        self.left_side_holder.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)
        self.left_side_holder.setParent(self)

        self.left_side_holder_lyt = qg.QVBoxLayout(self.left_side_holder)
        self.left_side_holder_lyt.setContentsMargins(0,0,0,0)
        self.left_side_holder_lyt.setSpacing(20)
        self.left_side_holder_lyt.setAlignment(qc.Qt.AlignCenter)

        self.left_side_holder.setFixedSize(70,200)

        self.select_all_btn = button.FlatBlackButton_picker('Select/all')
        self.deselect_all_btn = button.FlatBlackButton_picker('Clear/all')

        self.keyframe_btn = button.KeyButton()

        button_key_lyt = qg.QHBoxLayout()
        button_key_lyt.setAlignment(qc.Qt.AlignCenter)

        self.left_side_holder_lyt.addWidget(self.select_all_btn)
        self.left_side_holder_lyt.addWidget(self.deselect_all_btn)

        button_key_lyt.addWidget(self.keyframe_btn)
        self.left_side_holder_lyt.addLayout(button_key_lyt)

        self._toogle = False

        ######################################################################################################################################################################
        # CONNECT SIGNALS AND SLOTS
        #
        self.select_all_btn.clicked.connect(self.selectAllControls)
        self.deselect_all_btn.clicked.connect(lambda: cmds.select(clear=True))
        self.keyframe_btn.clicked.connect(lambda: self.op.keyNotZero(cmds.ls(sl=True)))
        self.makeCorner_connections()

        # clear all spin focus
        self.clear_focus()
        self.updateAllWidgets()

        todelete = partial(deletingIndex, self.callbacks_array)
        self.destroyed.connect(todelete)

        self.create_callbacks()


    ############################################################################################################################################
    ##################################################################
    #### this time trying with maya scriptjob
    #
    def create_callbacks(self):
        widgets = self._child_widgets

        try:
            for idx,job in enumerate(self.callbacks_array):
                cmds.scriptJob(kill=job, force=True)
                garb = self.callbacks_array.pop(idx)
                del(garb)

            #cmds.scriptJob(killall=True)

        except:
            print('job_not killed maybe')

        #######################################

        for itm in widgets:
            attribute = itm.objectName()
            try:
                job_num = cmds.scriptJob( runOnce=False, attributeChange=[attribute, self.updateAllWidgets] )
                self.callbacks_array.append(job_num)
            except:
                pass

    ##########################################################################################
    def toogle_vis(self):
        spins = self.top_rigth_corner_wdg.findChildren(qg.QSpinBox)
        for spin in spins:
            spin.setValue(int(not(self._toogle)))

        self._toogle = not(self._toogle)


    ##########################################################################################

    def update_nameSpace(self):
        name_space = self._manager.getNameSpace()
        self.prefix = name_space

        if name_space is None and ':' in self._child_widgets[0].objectName()[:]:
            for item in self._child_widgets:
                if ':' in str(item.objectName())[:]:
                    splited = item.objectName().split(':')
                    item.setObjectName(splited[-1])

            return

        elif name_space is None:
            return

        for item in self._child_widgets:
            tag = item.objectName()
            if ':' in item.objectName()[:]:
                tag = tag.split(':')[-1]

            new_name = name_space + ":" + tag
            item.setObjectName(new_name)

        om.MGlobal.displayInfo("Name Space '%s' Activated! " % name_space)

    ##########################################################################################

    def updateAllWidgets(self):
        spins = self.findChildren(qg.QSpinBox)
        doubleSpins = self.findChildren(qg.QDoubleSpinBox)
        buttons = [self.dynamic_button, self.envelope_button]
        spins.extend(doubleSpins)

        try:
            for itm in spins:
                with noSignals(itm):
                    val = cmds.getAttr(itm.objectName())
                    itm.setValue(val)


            for btn in buttons:
                with noSignals(btn):
                    val = bool(int(cmds.getAttr(btn.objectName())))
                    btn.setChecked(val)
        except:
            pass

        self._child_widgets = copy.copy(spins)
        self._child_widgets.extend(buttons)

    ########################################################
    def clear_focus(self):
        spins = self.findChildren(qg.QSpinBox)
        double_spin = self.findChildren(qg.QDoubleSpinBox)
        spins.extend(double_spin)
        for itm in spins:
            itm.clearFocus()


    def makeCorner_connections(self):
        widgets = self.findChildren(qg.QSpinBox)
        double_spin = self.findChildren(qg.QDoubleSpinBox)
        buttons = self.bottom_rigth_corner_wdg.findChildren(qg.QPushButton)

        widgets.extend(double_spin)

        for wgd in widgets:
            wgd.valueChanged.connect(self.setAttributes)

        for btn in buttons:
            btn.clicked.connect(self.setAttributes)


    ################################################################################################

    def resizeEvent(self, event):
        super(HeadPicker,self).resizeEvent(event)
        ################################################################
        # ADD CORNER WIDGETS PROCS
        #
        marg = 2

        self.left_side_holder.move(self.x() + marg, 120)

        self.bottom_rigth_corner_wdg.setFixedWidth(self.width() / 2 - 120)
        self.bottom_rigth_corner_wdg.move((self.width() - self.bottom_rigth_corner_wdg.width()) - marg , (self.height() - 145) + marg)

        self.bottom_left_corner_wdg.move(self.x() + marg  , (self.height() - 182))
        self.top_rigth_corner_wdg.move((self.width() - self.top_rigth_corner_wdg.width()) - marg , self.y() + marg)


    ########################################################################################

    def selectAllControls(self):
        with pause_callBacks():
            if self.prefix is not None:
                 for itm in FACECONTROLS:
                    cmds.select(self.prefix+':'+itm, add=True)

            elif self.prefix is  None:
                try:
                    for itm in FACECONTROLS:
                        cmds.select(itm, add=True)

                except:
                    cmds.warning('- Not Name Space set for controls -')
                    return

    ##########################################################################################

    ##########################################################################################
    def setAttributes(self):
        attribute = self.sender().objectName()
        with delete_callbacks():
            if isinstance(self.sender(), qg.QPushButton):
                value = int(self.sender().isChecked())

                try:
                    cmds.setAttr(attribute, value)
                except:
                    cmds.warning('No Name Space set for: {}'.format(attribute))

            else:
                value = self.sender().value()
                try:
                    cmds.setAttr(attribute, value)
                except:
                    cmds.warning('No Name Space set for: {}'.format(attribute))


    ##########################################################################################
    def showEvent(self, event):
        #self.settingMask()
        marg = 2
        self.bottom_rigth_corner_wdg.move((self.width() - self.bottom_rigth_corner_wdg.width()) - marg , (self.height() - 145) + marg)
        self.bottom_left_corner_wdg.move(self.x() + marg , (self.height() - 182))

#######################################################################################################################################
class OpaqueWidget(qg.QLabel):
    def __init__(self, parent = None):
        super(OpaqueWidget, self).__init__(parent)
        self.setStyleSheet("QLabel {background-color: rgba(1,1,1,50)};")


########################################################################################################################################

class StaticFacePickerLabel(qg.QLabel):
    def __init__(self,*args, **kwargs):
        super(StaticFacePickerLabel, self).__init__(*args, **kwargs)

        self.setAlignment(qc.Qt.AlignHCenter | qc.Qt.AlignVCenter)
        self.setStyleSheet('background-color: transparent;')

        self.setAttribute(qc.Qt.WA_AlwaysShowToolTips)
        self.setObjectName('facePickerLabel')
        main_ui  = ConnectControls.getMainWindow(ConnectControls.windowObject)
        self.setParent(main_ui)

        ########### PIXMAP ##########################
        self.facePickerPixmap = qg.QPixmap(FACEPICKER)
        myScaledPixmap = self.facePickerPixmap.scaled(900, 900 , qc.Qt.KeepAspectRatio, qc.Qt.SmoothTransformation)
        self.setPixmap(myScaledPixmap)

        ##################
        # CONTROLS MANAGER
        #
        self.co_manager = ConnectControls.ManageControls()

        ############################
        # CREATES THE BUTTONS
        #
        self.face_lips_ctrl    = self.createButtons(LIPS_CONTROLS, 'lips')
        self.face_red_ctrl = self.createButtons(FACE_RED_CONTROLS, 'red')
        self.face_yellow_ctrl = self.createButtons(FACE_YELLOW_CONTROLS, 'yellow')
        face_orange_ctrl = self.createButtons(FACE_ORANGE_CONTROLS, 'orange')


        #####################################################################################################################################################################
        # BUTTONS LIST FOR BUTTONS LOCATOR
        # LIPS CONTROLS
        self.Lip_r_top_02_Ctrl = self.face_lips_ctrl['Lip_r_top_02_Ctrl']
        self.Lip_r_top_01_Ctrl = self.face_lips_ctrl['Lip_r_top_01_Ctrl']
        self.Lip_Center_top_0_Ctrl = self.face_lips_ctrl['Lip_Center_top_0_Ctrl']
        self.Lip_l_top_01_Ctrl = self.face_lips_ctrl['Lip_l_top_01_Ctrl']
        self.Lip_l_top_02_Ctrl = self.face_lips_ctrl['Lip_l_top_02_Ctrl']

        self.Lip_l_Corner_Ctrl = self.face_lips_ctrl['Lip_l_Corner_Ctrl']
        self.Lip_r_Corner_Ctrl = self.face_lips_ctrl['Lip_r_Corner_Ctrl']

        self.Lip_r_DW_02_Ctrl = self.face_lips_ctrl['Lip_r_DW_02_Ctrl']
        self.Lip_r_DW_01_Ctrl = self.face_lips_ctrl['Lip_r_DW_01_Ctrl']
        self.Lip_Center_Dw_0_Ctrl = self.face_lips_ctrl['Lip_Center_Dw_0_Ctrl']
        self.Lip_l_DW_01_Ctrl = self.face_lips_ctrl['Lip_l_DW_01_Ctrl']
        self.Lip_l_DW_02_Ctrl = self.face_lips_ctrl['Lip_l_DW_02_Ctrl']

        self.lips_buttons_list = [self.Lip_r_top_02_Ctrl, self.Lip_r_top_01_Ctrl, self.Lip_Center_top_0_Ctrl, self.Lip_l_top_01_Ctrl, self.Lip_l_top_02_Ctrl,self.Lip_l_Corner_Ctrl,
                                 self.Lip_r_Corner_Ctrl, self.Lip_r_DW_02_Ctrl, self.Lip_r_DW_01_Ctrl, self.Lip_Center_Dw_0_Ctrl, self.Lip_l_DW_01_Ctrl, self.Lip_l_DW_02_Ctrl]

        #######################################################################################################################################################################
        # FACE RED BUTTONS
        #
        self.eyeBrow_r_wireCrv_5_Ctrl = self.face_red_ctrl['eyeBrow_r_wireCrv_5_Ctrl']
        self.eyeBrow_r_wireCrv_4_Ctrl = self.face_red_ctrl['eyeBrow_r_wireCrv_4_Ctrl']
        self.eyeBrow_r_wireCrv_3_Ctrl = self.face_red_ctrl['eyeBrow_r_wireCrv_3_Ctrl']
        self.eyeBrow_r_wireCrv_2_Ctrl = self.face_red_ctrl['eyeBrow_r_wireCrv_2_Ctrl']
        self.eyeBrow_r_wireCrv_1_Ctrl = self.face_red_ctrl['eyeBrow_r_wireCrv_1_Ctrl']
        self.eyeBrow_r_wireCrv_0_Ctrl = self.face_red_ctrl['eyeBrow_r_wireCrv_0_Ctrl']

        self.eyeBrow_l_wireCrv_0_Ctrl = self.face_red_ctrl['eyeBrow_l_wireCrv_0_Ctrl']
        self.eyeBrow_l_wireCrv_1_Ctrl = self.face_red_ctrl['eyeBrow_l_wireCrv_1_Ctrl']
        self.eyeBrow_l_wireCrv_2_Ctrl = self.face_red_ctrl['eyeBrow_l_wireCrv_2_Ctrl']
        self.eyeBrow_l_wireCrv_3_Ctrl = self.face_red_ctrl['eyeBrow_l_wireCrv_3_Ctrl']
        self.eyeBrow_l_wireCrv_4_Ctrl = self.face_red_ctrl['eyeBrow_l_wireCrv_4_Ctrl']
        self.eyeBrow_l_wireCrv_5_Ctrl = self.face_red_ctrl['eyeBrow_l_wireCrv_5_Ctrl']

        self.Cheek_r_Ctrl = self.face_red_ctrl['Cheek_r_Ctrl']
        self.Cheek_l_Ctrl = self.face_red_ctrl['Cheek_l_Ctrl']
        self.ear_r_Tip_bind_Ctrl = self.face_red_ctrl['ear_r_Tip_bind_Ctrl']
        self.ear_l_Tip_bind_Ctrl = self.face_red_ctrl['ear_l_Tip_bind_Ctrl']

        self.nose_bind_Ctrl = self.face_red_ctrl['nose_bind_Ctrl']

        self.red_buttons_list = [self.eyeBrow_r_wireCrv_5_Ctrl, self.eyeBrow_r_wireCrv_4_Ctrl, self.eyeBrow_r_wireCrv_3_Ctrl, self.eyeBrow_r_wireCrv_2_Ctrl, self.eyeBrow_r_wireCrv_1_Ctrl,
                                 self.eyeBrow_r_wireCrv_0_Ctrl, self.eyeBrow_l_wireCrv_0_Ctrl, self.eyeBrow_l_wireCrv_1_Ctrl, self.eyeBrow_l_wireCrv_2_Ctrl, self.eyeBrow_l_wireCrv_3_Ctrl,
                                 self.eyeBrow_l_wireCrv_4_Ctrl, self.eyeBrow_l_wireCrv_5_Ctrl, self.Cheek_r_Ctrl, self.Cheek_l_Ctrl, self.ear_r_Tip_bind_Ctrl,self.ear_l_Tip_bind_Ctrl,
                                 self.nose_bind_Ctrl]

        #####################################################################################################################################################################
        # BUTTONS LIST FOR BUTTONS LOCATOR
        # LIPS CONTROLS
        self.ear_r_bind_Ctrl = self.face_yellow_ctrl['ear_r_bind_Ctrl']
        self.ear_l_bind_Ctrl = self.face_yellow_ctrl['ear_l_bind_Ctrl']

        self.browOut_l_bind_Ctrl = self.face_yellow_ctrl['browOut_l_bind_Ctrl']
        self.browMid_l_bind_Ctrl = self.face_yellow_ctrl['browMid_l_bind_Ctrl']
        self.browIn_l_bind_Ctrl  = self.face_yellow_ctrl['browIn_l_bind_Ctrl']

        self.browIn_r_bind_Ctrl  = self.face_yellow_ctrl['browIn_r_bind_Ctrl']
        self.browMid_r_bind_Ctrl = self.face_yellow_ctrl['browMid_r_bind_Ctrl']
        self.browOut_r_bind_Ctrl = self.face_yellow_ctrl['browOut_r_bind_Ctrl']

        self.pomulo_l_cls_Ctrl = self.face_yellow_ctrl['pomulo_l_cls_Ctrl']
        self.pomulo_r_cls_Ctrl = self.face_yellow_ctrl['pomulo_r_cls_Ctrl']

        self.Sneer_r_Ctrl = self.face_yellow_ctrl['Sneer_r_Ctrl']
        self.Sneer_l_Ctrl = self.face_yellow_ctrl['Sneer_l_Ctrl']

        self.MouthUp_Ctrl = self.hookUp_button('MouthUp_Ctrl', 'Round_button_small_yellow_face')
        self.mouthDw_Ctrl = self.face_yellow_ctrl['mouthDw_Ctrl']

        self.yellow_buttons_list = [self.MouthUp_Ctrl,
                                    self.mouthDw_Ctrl,
                                    self.Sneer_r_Ctrl,
                                    self.pomulo_r_cls_Ctrl,
                                    self.Sneer_l_Ctrl,
                                    self.pomulo_l_cls_Ctrl,
                                    self.browOut_r_bind_Ctrl,
                                    self.browMid_r_bind_Ctrl,
                                    self.browIn_r_bind_Ctrl,
                                    self.browIn_l_bind_Ctrl,
                                    self.browMid_l_bind_Ctrl,
                                    self.browOut_l_bind_Ctrl,
                                    self.ear_r_bind_Ctrl,
                                    self.ear_l_bind_Ctrl]


        #####################################################################################################################################################################
        # BUTTONS LIST FOR BUTTONS LOCATOR
        # ORANGE CONTROLS
        self.chin_bind_Ctrl = face_orange_ctrl['chin_bind_Ctrl']
        self.nose_r_tip_bind_Ctrl = face_orange_ctrl['nose_r_tip_bind_Ctrl']
        self.nose_l_tip_bind_Ctrl = face_orange_ctrl['nose_l_tip_bind_Ctrl']

        self.orange_controls_list = [self.chin_bind_Ctrl, self.nose_r_tip_bind_Ctrl,self.nose_l_tip_bind_Ctrl]

        #####################################################################################################################################################################
        # BUTTONS LIST FOR BUTTONS LOCATOR
        # EXTRA CONTROLS
        self.jaw_bind_Ctrl = self.hookUp_button('jaw_bind_Ctrl', 'Round_button_cross_red')
        self.HitchHeadWire_top_Ctrl = self.hookUp_button('HitchHeadWire_top_Ctrl', 'Flat_button_green_thick_01')
        self.HitchHeadWire_Down_Ctrl = self.hookUp_button('HitchHeadWire_Down_Ctrl', 'Flat_button_green_thick_02')
        self.HitchHeadWire_Mid_Ctrl = self.hookUp_button('HitchHeadWire_Mid_Ctrl', 'Flat_button_green_thick_03')
        self.eyeBall_r_Aim_Ctrl = self.hookUp_button('eyeBall_r_Aim_Ctrl', 'Round_big_button_hole_yellow')
        self.eyeBall_l_Aim_Ctrl = self.hookUp_button('eyeBall_l_Aim_Ctrl', 'Round_big_button_hole_red')

        self.eyesMain_LookAt_Ctrl = self.hookUp_button('eyesMain_LookAt_Ctrl', 'Flat_button_green_thick_04')

        self.extra_buttons_list = [self.jaw_bind_Ctrl ,self.HitchHeadWire_top_Ctrl ,self.HitchHeadWire_Down_Ctrl, self.HitchHeadWire_Mid_Ctrl,self.eyeBall_l_Aim_Ctrl,
                                   self.eyeBall_r_Aim_Ctrl,self.eyesMain_LookAt_Ctrl]




    ################################################################################################
    ###

    def buttons_manager(self):
        buttonName = self.sender().objectName()
        print(buttonName)
        self.co_manager.getComand_to_connect(buttonName)

        ################################################
    def resizeEvent(self, event):
        super(StaticFacePickerLabel,self).resizeEvent(event)
        off_x = (self.width() / 2 )
        off_y = (self.height() / 2)

        ##################################################
        # LIPS BUTTONS
        # POSITIONING
        #
        self.Lip_r_Corner_Ctrl.move((self.width() / 2) - 108, (self.height() / 2) + 139)
        self.Lip_Center_top_0_Ctrl.move((self.width() / 2) - 29, (self.height() / 2) + 134)

        self.Lip_l_Corner_Ctrl.move((self.width() / 2) + 50, (self.height() / 2) + 140)
        self.Lip_Center_Dw_0_Ctrl.move((self.width() / 2) - 29, (self.height() / 2) + 161)

        self.Lip_r_top_02_Ctrl.move((self.width() / 2) - 83, (self.height() / 2) + 129)
        self.Lip_r_top_01_Ctrl.move((self.width() / 2) - 55, (self.height() / 2) + 129)

        self.Lip_l_top_02_Ctrl.move((self.width() / 2) + 25, (self.height() / 2) + 129)
        self.Lip_l_top_01_Ctrl.move((self.width() / 2) - 3, (self.height() / 2) + 129)

        self.Lip_r_DW_01_Ctrl.move((self.width() / 2) - 56, (self.height() / 2) + 161)
        self.Lip_r_DW_02_Ctrl.move((self.width() / 2) - 84, (self.height() / 2) + 156)

        self.Lip_l_DW_01_Ctrl.move((self.width() / 2) - 2, (self.height() / 2) + 161)
        self.Lip_l_DW_02_Ctrl.move((self.width() / 2) + 27, (self.height() / 2) + 156)

        ##################################################
        # RED BUTTONS
        # POSITIONING
        #
        self.nose_bind_Ctrl.move((self.width() / 2) - 32, (self.height() / 2) + 71)

        self.ear_r_Tip_bind_Ctrl.move((self.width() / 2) - 245, (self.height() / 2) + 19)
        self.ear_l_Tip_bind_Ctrl.move((self.width() / 2) + 177, (self.height() / 2) + 18)
        self.Cheek_l_Ctrl.move((self.width() / 2) + 104, (self.height() / 2) + 130)
        self.Cheek_r_Ctrl.move((self.width() / 2) - 168, (self.height() / 2) + 131)

        self.eyeBrow_l_wireCrv_0_Ctrl.move((self.width() / 2) - 13, (self.height() / 2) - 117)
        self.eyeBrow_l_wireCrv_1_Ctrl.move((self.width() / 2) + 22, (self.height() / 2) - 119)
        self.eyeBrow_l_wireCrv_2_Ctrl.move((self.width() / 2) + 56, (self.height() / 2) - 128)
        self.eyeBrow_l_wireCrv_3_Ctrl.move((self.width() / 2) + 91, (self.height() / 2) - 135)
        self.eyeBrow_l_wireCrv_4_Ctrl.move((self.width() / 2) + 125, (self.height() / 2) - 126)
        self.eyeBrow_l_wireCrv_5_Ctrl.move((self.width() / 2) + 150, (self.height() / 2) - 103)

        self.eyeBrow_r_wireCrv_0_Ctrl.move((self.width() / 2) - 56, (self.height() / 2) - 116)
        self.eyeBrow_r_wireCrv_1_Ctrl.move((self.width() / 2) - 90, (self.height() / 2) - 119)
        self.eyeBrow_r_wireCrv_2_Ctrl.move((self.width() / 2) - 124, (self.height() / 2) - 127)
        self.eyeBrow_r_wireCrv_5_Ctrl.move((self.width() / 2) - 219, (self.height() / 2) - 104)
        self.eyeBrow_r_wireCrv_4_Ctrl.move((self.width() / 2) - 193, (self.height() / 2) - 126)
        self.eyeBrow_r_wireCrv_3_Ctrl.move((self.width() / 2) - 159, (self.height() / 2) - 134)

        ##################################################
        # YELLOW BUTTONS
        # POSITIONING
        #
        self.mouthDw_Ctrl.move((self.width() / 2) - 33, (self.height() / 2) + 189)
        self.MouthUp_Ctrl.move((self.width() / 2) - 29, (self.height() / 2) + 109)
        self.Sneer_l_Ctrl.move((self.width() / 2) + 14, (self.height() / 2) + 64)
        self.Sneer_r_Ctrl.move((self.width() / 2) - 80, (self.height() / 2) + 64)

        self.pomulo_l_cls_Ctrl.move((self.width() / 2) + 121, (self.height() / 2) + 9)
        self.pomulo_r_cls_Ctrl.move((self.width() / 2) - 184, (self.height() / 2) + 9)

        self.browOut_r_bind_Ctrl.move((self.width() / 2) - 227, (self.height() / 2) - 138)
        self.browMid_r_bind_Ctrl.move((self.width() / 2) - 136, (self.height() / 2) - 162)
        self.browIn_r_bind_Ctrl.move((self.width() / 2) - 69, (self.height() / 2) - 149)

        self.browIn_l_bind_Ctrl.move((self.width() / 2) + 5, (self.height() / 2) - 149)
        self.browMid_l_bind_Ctrl.move((self.width() / 2) + 69, (self.height() / 2) - 162)
        self.browOut_l_bind_Ctrl.move((self.width() / 2) + 158, (self.height() / 2) - 138)

        self.ear_l_bind_Ctrl.move((self.width() / 2) + 173, (self.height() / 2) + 57)
        self.ear_r_bind_Ctrl.move((self.width() / 2) - 236, (self.height() / 2) + 57)

        ##################################################
        # ORANGE BUTTONS BUTTONS
        # POSITIONING
        #

        self.chin_bind_Ctrl.move((self.width() / 2) + 54, (self.height() / 2) + 210)
        self.nose_r_tip_bind_Ctrl.move((self.width() / 2) - 57, (self.height() / 2) + 35)
        self.nose_l_tip_bind_Ctrl.move((self.width() / 2) - 10, (self.height() / 2) + 35)

        ##################################################
        # EXTRA BUTTONS BUTTONS
        # POSITIONING
        #
        self.HitchHeadWire_Down_Ctrl.move((self.width() / 2) - 90, (self.height() / 2) + 326)
        self.HitchHeadWire_Mid_Ctrl.move((self.width() / 2) + 170, (self.height() / 2) + 124)
        self.HitchHeadWire_top_Ctrl.move((self.width() / 2) - 147, (self.height() / 2) - 367)
        self.jaw_bind_Ctrl.move((self.width() / 2) - 32, (self.height() / 2) + 284)

        self.eyeBall_r_Aim_Ctrl.move((self.width() / 2) - 173, (self.height() / 2) - 93)
        self.eyeBall_l_Aim_Ctrl.move((self.width() / 2) + 20, (self.height() / 2) - 93)
        self.eyesMain_LookAt_Ctrl.move((self.width() / 2) - 56, (self.height() / 2) - 48)



    ###################################################

    def createButtons(self, control_list, keyword = None ):
        dictionary = {}

        for ctrl in control_list:
            if keyword == 'red':
                btn = self.hookUp_button(ctrl,'Round_button_red')
                dictionary[ctrl] = btn

            elif keyword == 'yellow':
                btn = self.hookUp_button(ctrl,'Round_button_yellow')
                dictionary[ctrl] = btn

            elif keyword == 'orange':
                btn = self.hookUp_button(ctrl,'Round_button_orange')
                dictionary[ctrl] = btn

            elif keyword == 'lips':
                btn = self.hookUp_button(ctrl,'Round_button_small_red_face')
                dictionary[ctrl] = btn
        return  dictionary

        #################################################################################

    def hookUp_button(self, name, button_type):
        button = getattr(PickerButtons,button_type)(parent=self)
        button.setParent(self)
        button.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)
        button.setObjectName(name)
        button.clicked.connect(self.buttons_manager)
        return button





##################################################################################################################



##################################################################################################################
##################################################################################################################
#

CSS = """QLabel
        {
        background-color: rgba(240,220,220,1);
        color: rgba(225,40,40,220);
        font-family: Source Code Pro Black;
        font: bold 18px;

        }"""

class Header_custom_label(qg.QLabel):
    def __init__(self, *args, **kwargs):
        super(Header_custom_label, self).__init__(*args, **kwargs)
        self.setFixedSize(300,100)
        self.setStyleSheet(CSS)
        self.setIndent(4)
        self.setAlignment(qc.Qt.AlignCenter)

        font = qg.QFont('Source Code Pro Semibold')
        font.setPointSize(14)
        font.setBold(True)
        self.setFont(font)

CSS2 = """QLabel
        {
        background-color: transparent;
        font-family: Calibri;
        font: bold 20px;
        color: rgba(225,40,40,220);

        }"""

class Snap_custom_label(qg.QLabel):
    def __init__(self, *args, **kwargs):
        super(Snap_custom_label, self).__init__(*args, **kwargs)
        self.setStyleSheet(CSS2)
        self.setIndent(4)
        self.setAlignment(qc.Qt.AlignCenter)

