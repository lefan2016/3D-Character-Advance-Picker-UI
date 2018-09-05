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
    from HitchAnimationModule.LogicData.refreshUI import  undo_pm
    from HitchAnimationModule.LogicData import refreshUI
except: pass
############
from PySide import QtCore as qc
from PySide import QtGui as qg
from functools import partial
import re
import operator
import copy
import os
from contextlib import contextmanager
#------------------------------------------------------------------------------------------------------------#
# GLOBALS:
try :
    LIMBS = ControlList.LIMBS_CONTROLS
    FEET = ControlList.FEET_CONTROLS
    HANDS = ControlList.HAND_CONTROLS
    CENTRAL = ControlList.CENTRAL_CONTROLS
    BENDY = ControlList.BENDY_CONTROLS
    BODYCONTROLS = ControlList.BODYCONTROLS
    BODYPICKER= os.path.join(pm.internalVar(usd=1) , 'HitchAnimationModule','Icons','Hitch_BodyForPicker.png')
except: pass

# ---------------------------------------------------------------------------#
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
    #print(channelBox_signal_count)

    panel_signal_count  =  topPanel.receivers(qc.SIGNAL('destroyed()'))
    #print(panel_signal_count)
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
    ######################################################################################################

# ---------------------------------------------------------------------------#
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
class BodyPicker(qg.QLabel):
    def __init__(self):
        super(BodyPicker,self).__init__()

        self.setStyleSheet(""" background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.2 ,
                         fx: 0.5 , fy: 0.5, stop: 0 rgba(53, 57, 60,255), stop: 0.7 rgba(25,15,05,50), stop: 1.1 rgba(33, 34, 36, 255));""")

        self.setAlignment(qc.Qt.AlignHCenter | qc.Qt.AlignVCenter)
        self.setContentsMargins(0,0,0,0)
        self.setObjectName('bodyPickerLabel')

        self.main_ui  = ConnectControls.getMainWindow(ConnectControls.windowObject)
        self.setParent(self.main_ui)
        self.op = OperationsFile.Operations()

        # PANELS CALLBACKS MANAGER ZONE  #######################################################
        #
        self.callbacks_array = []
        self._scene = refreshUI.resetScene()

        # NAME SPACE  #######################################################
        #
        self._child_widgets = []
        self._manager  = ConnectControls.ManageControls()
        self.prefix = None

        # STACK CONFIGURATION #######################################################
        #

        self.stackLayout = qg.QStackedLayout()
        self.stackLayout.setObjectName('Main_stacked_layout')
        self.stackLayout.setContentsMargins(0,0,0,0)
        self.stackLayout.setStackingMode(qg.QStackedLayout.StackAll)
        self.stackLayout.setAlignment(qc.Qt.AlignVCenter | qc.Qt.AlignHCenter)

        self.setLayout(self.stackLayout)

        ######################################################################################################################################################################
        #   PICKER HERE !!!!!
        #
        self.labelPicker = StaticPickerLabel()
        self.labelPicker.setParent(self.main_ui)
        self.layout().addWidget(self.labelPicker)

        ########################################################################################################################################################################
        #   MAIN WIDGET FROM PICKER
        #

        # this is on the top of the widgets... should be on the background in first place ....
        self._mainWidget = qg.QWidget()
        self._mainWidget.setContentsMargins(0,0,0,0)
        self.stackLayout.addWidget(self._mainWidget)

        self.main_lyt = qg.QHBoxLayout(self._mainWidget)
        self.main_lyt.setContentsMargins(1,1,1,1)

        #########################################################################################################################################################################
        # TOP LEFT CORNER WIDGETS
        self.top_left_corner_wdg = OpaqueWidget()
        self.top_left_corner_wdg.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)

        self.top_left_corner_wdg.setParent(self)
        self.top_left_corner_wdg_lyt = qg.QVBoxLayout(self.top_left_corner_wdg)

        self.top_left_corner_wdg_lyt.setContentsMargins(0,5,0,0)
        self.top_left_corner_wdg_lyt.setSpacing(10)
        self.top_left_corner_wdg_lyt.setAlignment(qc.Qt.AlignHCenter)

        ###########################################
        r_arm_top_form_lyt = qg.QFormLayout()

        ik_fk_value_label_r_arm = label.CustomShortLabel('IK FK Value')
        fk_Strectch_label_r_arm = label.CustomShortLabel('FK Stretch')
        auto_clavicle_label_r_arm = label.CustomShortLabel('Auto Clavicle')
        ctrl_vis_label_r_arm = label.CustomShortLabel('Two System Vis')
        finger_vis_label_r_arm = label.CustomShortLabel('Fingers Vis')

        self.ik_fk_value_spin_r_arm = ColtSpinBox.CustomSpinBox()
        self.ik_fk_value_spin_r_arm.setRange(0,1)
        self.fk_Strectch_spin_r_arm = ColtSpinBox.CustomDoubleSpinBox()
        self.fk_Strectch_spin_r_arm.setRange(-50,50)
        self.auto_clavicle_Spin_r_arm = ColtSpinBox.CustomSpinBox()
        self.auto_clavicle_Spin_r_arm.setRange(0,1)
        self.ctrl_vis_Spin_r_arm = ColtSpinBox.CustomSpinBox()
        self.ctrl_vis_Spin_r_arm.setRange(0,1)
        self.finger_vis_Spin_r_arm = ColtSpinBox.CustomSpinBox()
        self.finger_vis_Spin_r_arm.setRange(0,1)


        r_arm_top_form_lyt.addRow(fk_Strectch_label_r_arm, self.fk_Strectch_spin_r_arm)
        r_arm_top_form_lyt.addRow(ik_fk_value_label_r_arm, self.ik_fk_value_spin_r_arm)
        r_arm_top_form_lyt.addRow(auto_clavicle_label_r_arm, self.auto_clavicle_Spin_r_arm)
        r_arm_top_form_lyt.addRow(ctrl_vis_label_r_arm, self.ctrl_vis_Spin_r_arm)
        r_arm_top_form_lyt.addRow(finger_vis_label_r_arm, self.finger_vis_Spin_r_arm)


        self.bottom_r_arm_snap_btn_lyt = qg.QHBoxLayout()
        self.bottom_r_arm_snap_btn_lyt.setSpacing(0)
        self.r_arm_snap_label = Snap_custom_label('Ready!')

        self.rigth_arm_snap_btn = button.Customflat_btn('R arm Snap')
        self.rigth_arm_snap_btn.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Minimum)
        self.r_arm_snap_label.setFixedSize(85 , self.rigth_arm_snap_btn.height())

        self.bottom_r_arm_snap_btn_lyt.addWidget(self.r_arm_snap_label)
        self.bottom_r_arm_snap_btn_lyt.addWidget(self.rigth_arm_snap_btn)


        self.attributes_r_arm_layout = qg.QHBoxLayout()
        self.attributes_r_arm_layout.setAlignment(qc.Qt.AlignCenter)

        self.attributes_r_arm_layout.addLayout(r_arm_top_form_lyt)
        self.top_left_corner_wdg_lyt.addLayout(self.attributes_r_arm_layout)
        self.top_left_corner_wdg_lyt.addLayout(self.bottom_r_arm_snap_btn_lyt)


       ########################################################################################################################################################################
        # BOTTOM LEFT CORNER WIDGETS
        self.bottom_left_corner_wdg = OpaqueWidget()
        self.bottom_left_corner_wdg.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)
        self.bottom_left_corner_wdg.setParent(self)
        self.bottom_left_corner_wdg_lyt = qg.QVBoxLayout(self.bottom_left_corner_wdg)
        self.bottom_left_corner_wdg_lyt.setDirection(qg.QBoxLayout.BottomToTop)

        self.bottom_left_corner_wdg_lyt.setContentsMargins(0,5,0,0)
        self.bottom_left_corner_wdg_lyt.setSpacing(10)
        self.bottom_left_corner_wdg_lyt.setAlignment(qc.Qt.AlignHCenter)

        ###########################################
        r_leg_top_form_lyt = qg.QFormLayout()

        ik_fk_value_label_r_leg = label.CustomShortLabel('IK FK Value')
        fk_Strectch_label_r_leg = label.CustomShortLabel('FK Stretch')
        ctrl_vis_label_r_leg = label.CustomShortLabel('Two System Vis')
        foot_vis_label_r_leg = label.CustomShortLabel('Foot Vis')

        self.ik_fk_value_spin_r_leg = ColtSpinBox.CustomSpinBox()
        self.ik_fk_value_spin_r_leg.setRange(0,1)
        self.fk_Strectch_spin_r_leg = ColtSpinBox.CustomDoubleSpinBox()
        self.fk_Strectch_spin_r_leg.setRange(-50,50)
        self.ctrl_vis_Spin_r_leg = ColtSpinBox.CustomSpinBox()
        self.ctrl_vis_Spin_r_leg.setRange(0,1)
        self.foot_vis_Spin_r_leg = ColtSpinBox.CustomSpinBox()
        self.foot_vis_Spin_r_leg.setRange(0,1)

        r_leg_top_form_lyt.addRow(fk_Strectch_label_r_leg, self.fk_Strectch_spin_r_leg)
        r_leg_top_form_lyt.addRow(ik_fk_value_label_r_leg, self.ik_fk_value_spin_r_leg)
        r_leg_top_form_lyt.addRow(ctrl_vis_label_r_leg, self.ctrl_vis_Spin_r_leg)
        r_leg_top_form_lyt.addRow(foot_vis_label_r_leg, self.foot_vis_Spin_r_leg)


        self.bottom_r_leg_snap_btn_lyt = qg.QHBoxLayout()
        self.bottom_r_leg_snap_btn_lyt.setSpacing(0)
        self.r_leg_snap_label = Snap_custom_label('Ready!')

        self.rigth_leg_snap_btn = button.Customflat_btn('R leg Snap')
        self.rigth_leg_snap_btn.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Minimum)
        self.r_leg_snap_label.setFixedSize(85 , self.rigth_leg_snap_btn.height())

        self.bottom_r_leg_snap_btn_lyt.addWidget(self.r_leg_snap_label)
        self.bottom_r_leg_snap_btn_lyt.addWidget(self.rigth_leg_snap_btn)


        self.attributes_r_leg_layout = qg.QHBoxLayout()
        self.attributes_r_leg_layout.setAlignment(qc.Qt.AlignCenter)

        self.attributes_r_leg_layout.addLayout(r_leg_top_form_lyt)
        self.bottom_left_corner_wdg_lyt.addLayout(self.attributes_r_leg_layout)
        self.bottom_left_corner_wdg_lyt.addLayout(self.bottom_r_leg_snap_btn_lyt)


       #####################################################################################################################################################################
        # TOP RIGTH CORNER WIDGETS
        self.top_rigth_corner_wdg = OpaqueWidget()
        self.top_rigth_corner_wdg.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)
        self.top_rigth_corner_wdg.setParent(self)
        self.top_rigth_corner_wdg_lyt = qg.QVBoxLayout(self.top_rigth_corner_wdg)


        self.top_rigth_corner_wdg_lyt.setContentsMargins(0,5,0,0)
        self.top_rigth_corner_wdg_lyt.setSpacing(10)
        self.top_rigth_corner_wdg_lyt.setAlignment(qc.Qt.AlignHCenter)

        ###########################################

        l_arm_top_form_lyt = qg.QFormLayout()

        l_arm_ik_fk_value_label= label.CustomShortLabel('IK FK Value')
        l_arm_fk_Strectch_label= label.CustomShortLabel('FK Stretch')
        l_arm_auto_clavicle_label = label.CustomShortLabel('Auto Clavicle')
        l_arm_ctrl_vis_label = label.CustomShortLabel('Two System Vis')
        finger_vis_label_l_arm = label.CustomShortLabel('Fingers Vis')

        self.ik_fk_value_spin_l_arm = ColtSpinBox.CustomSpinBox()
        self.ik_fk_value_spin_l_arm.setRange(0,1)
        self.fk_Strectch_spin_l_arm = ColtSpinBox.CustomDoubleSpinBox()
        self.fk_Strectch_spin_l_arm.setRange(-50,50)
        self.auto_clavicle_Spin_l_arm = ColtSpinBox.CustomSpinBox()
        self.auto_clavicle_Spin_l_arm.setRange(0,1)
        self.ctrl_vis_Spin_l_arm = ColtSpinBox.CustomSpinBox()
        self.ctrl_vis_Spin_l_arm.setRange(0,1)
        self.finger_vis_Spin_l_arm = ColtSpinBox.CustomSpinBox()
        self.finger_vis_Spin_l_arm.setRange(0,1)

        l_arm_top_form_lyt.addRow(l_arm_fk_Strectch_label, self.fk_Strectch_spin_l_arm)
        l_arm_top_form_lyt.addRow(l_arm_ik_fk_value_label, self.ik_fk_value_spin_l_arm)
        l_arm_top_form_lyt.addRow(l_arm_auto_clavicle_label, self.auto_clavicle_Spin_l_arm)
        l_arm_top_form_lyt.addRow(l_arm_ctrl_vis_label, self.ctrl_vis_Spin_l_arm)
        l_arm_top_form_lyt.addRow(finger_vis_label_l_arm, self.finger_vis_Spin_l_arm)

        self.bottom_l_arm_snap_btn_lyt = qg.QHBoxLayout()
        self.bottom_l_arm_snap_btn_lyt.setDirection(qg.QBoxLayout.RightToLeft)
        self.bottom_l_arm_snap_btn_lyt.setSpacing(0)
        self.l_arm_snap_label = Snap_custom_label('Ready!')

        self.left_arm_snap_btn = button.Customflat_btn('L arm Snap')
        self.left_arm_snap_btn.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Minimum)
        self.l_arm_snap_label.setFixedSize(85 , self.left_arm_snap_btn.height())

        self.bottom_l_arm_snap_btn_lyt.addWidget(self.l_arm_snap_label)
        self.bottom_l_arm_snap_btn_lyt.addWidget(self.left_arm_snap_btn)


        self.attributes_l_arm_layout = qg.QHBoxLayout()
        self.attributes_l_arm_layout.setDirection(qg.QBoxLayout.RightToLeft)
        self.attributes_l_arm_layout.setAlignment(qc.Qt.AlignCenter)

        self.attributes_l_arm_layout.addLayout(l_arm_top_form_lyt)
        self.top_rigth_corner_wdg_lyt.addLayout(self.attributes_l_arm_layout)
        self.top_rigth_corner_wdg_lyt.addLayout(self.bottom_l_arm_snap_btn_lyt)

        #####################################################################################################################################################################
        # BOTTOM RIGTH CORNER WIDGETS
        self.bottom_rigth_corner_wdg = OpaqueWidget()
        self.bottom_rigth_corner_wdg.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)
        self.bottom_rigth_corner_wdg.setParent(self)
        self.bottom_rigth_corner_wdg_lyt = qg.QVBoxLayout(self.bottom_rigth_corner_wdg)
        self.bottom_rigth_corner_wdg_lyt.setDirection(qg.QBoxLayout.BottomToTop)
        self.bottom_rigth_corner_wdg_lyt.setContentsMargins(0,5,0,0)
        self.bottom_rigth_corner_wdg_lyt.setSpacing(10)
        self.bottom_rigth_corner_wdg_lyt.setAlignment(qc.Qt.AlignHCenter)

        ###########################################
        l_leg_top_form_lyt = qg.QFormLayout()
        ik_fk_value_label_l_leg = label.CustomShortLabel('IK FK Value')
        fk_Strectch_label_l_leg = label.CustomShortLabel('FK Stretch')
        ctrl_vis_label_l_leg = label.CustomShortLabel('Two System Vis')
        foot_vis_label_l_leg = label.CustomShortLabel('Foot Vis')

        self.ik_fk_value_spin_l_leg = ColtSpinBox.CustomSpinBox()
        self.ik_fk_value_spin_l_leg.setRange(0,1)
        self.fk_Strectch_spin_l_leg = ColtSpinBox.CustomDoubleSpinBox()
        self.fk_Strectch_spin_l_leg.setRange(-50,50)
        self.ctrl_vis_Spin_l_leg = ColtSpinBox.CustomSpinBox()
        self.ctrl_vis_Spin_l_leg.setRange(0,1)
        self.foot_vis_Spin_l_leg = ColtSpinBox.CustomSpinBox()
        self.foot_vis_Spin_l_leg.setRange(0,1)

        l_leg_top_form_lyt.addRow(fk_Strectch_label_l_leg, self.fk_Strectch_spin_l_leg)
        l_leg_top_form_lyt.addRow(ik_fk_value_label_l_leg, self.ik_fk_value_spin_l_leg)
        l_leg_top_form_lyt.addRow(ctrl_vis_label_l_leg, self.ctrl_vis_Spin_l_leg)
        l_leg_top_form_lyt.addRow(foot_vis_label_l_leg, self.foot_vis_Spin_l_leg)


        self.bottom_l_leg_snap_btn_lyt = qg.QHBoxLayout()
        self.bottom_l_leg_snap_btn_lyt.setDirection(qg.QBoxLayout.RightToLeft)
        self.bottom_l_leg_snap_btn_lyt.setSpacing(0)
        self.l_leg_snap_label = Snap_custom_label('Ready!')

        self.left_leg_snap_btn = button.Customflat_btn('L leg Snap')
        self.left_leg_snap_btn.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Minimum)
        self.l_leg_snap_label.setFixedSize(85 , self.left_leg_snap_btn.height())

        self.bottom_l_leg_snap_btn_lyt.addWidget(self.l_leg_snap_label)
        self.bottom_l_leg_snap_btn_lyt.addWidget(self.left_leg_snap_btn)


        self.attributes_l_leg_layout = qg.QHBoxLayout()
        self.attributes_l_leg_layout.setDirection(qg.QBoxLayout.LeftToRight)
        self.attributes_l_leg_layout.setAlignment(qc.Qt.AlignCenter)

        self.attributes_l_leg_layout.addLayout(l_leg_top_form_lyt)
        self.bottom_rigth_corner_wdg_lyt.addLayout(self.attributes_l_leg_layout)
        self.bottom_rigth_corner_wdg_lyt.addLayout(self.bottom_l_leg_snap_btn_lyt)


       ######################################################################################################################################################################
        # RIGTH SIDE
        self.right_side_holder = OpaqueWidget()
        self.right_side_holder.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)
        self.right_side_holder.setParent(self)
        self.right_side_holder_lyt = qg.QVBoxLayout(self.right_side_holder)
        self.right_side_holder_lyt.setContentsMargins(0,0,0,0)
        self.right_side_holder_lyt.setSpacing(2)
        self.right_side_holder_lyt.setAlignment(qc.Qt.AlignCenter)

        self.right_side_holder.setFixedSize(70,240)

        label_rig_disc = label.CustomShortLabel('Rigging')
        label_rig_envs = label.CustomShortLabel('Envelope')

        label_breath = label.CustomShortLabel('Breath')
        label_breath_super = label.CustomShortLabel('Hyper')

        self.disc_rig_btn = button.Customflat_toogle_name_btn('On')
        self.disc_rig_btn.setChecked(True)
        self.envs_rig_btn = button.Customflat_toogle_name_btn('On')
        self.envs_rig_btn.setChecked(True)

        #self.select_geo_btn.setChecked(False)

        self.breath_spin = ColtSpinBox.CustomSpinBox()
        self.breath_spin.setRange(0,1)

        self.hyper_breath_spin = ColtSpinBox.CustomSpinBox()
        self.hyper_breath_spin.setRange(-1,10)

        self.right_side_holder_lyt.addWidget(label_rig_disc)
        self.right_side_holder_lyt.addWidget(self.disc_rig_btn)
        self.right_side_holder_lyt.addWidget(label_rig_envs)
        self.right_side_holder_lyt.addWidget(self.envs_rig_btn)

        breath_layout = qg.QVBoxLayout()
        self.right_side_holder_lyt.addLayout(breath_layout)
        breath_layout.setContentsMargins(5,0,5,1)


        breath_layout.addWidget(label_breath)
        breath_layout.addWidget(self.breath_spin)
        breath_layout.addWidget(label_breath_super)
        breath_layout.addWidget(self.hyper_breath_spin)



        ####################################################################################################################################################################
        # LEFT SIDE
        self.left_side_holder = OpaqueWidget()
        self.left_side_holder.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)
        self.left_side_holder.setParent(self)

        self.left_side_holder_lyt = qg.QVBoxLayout(self.left_side_holder)
        self.left_side_holder_lyt.setContentsMargins(0,0,0,0)
        self.left_side_holder_lyt.setSpacing(5)
        self.left_side_holder_lyt.setAlignment(qc.Qt.AlignCenter)

        self.left_side_holder.setFixedSize(70,240)

        self.select_all_btn = button.FlatBlackButton_picker('Select/all')
        self.deselect_all_btn = button.FlatBlackButton_picker('Clear/all')
        self.proxy_btn = button.Customflat_toogle_btn('Rig Proxy')
        self.proxy_btn.setCheckable(True)

        self.select_geo_btn = button.Customflat_toogle_name_btn('Sel/Geo', 'Geo/Off')

        self.keyframe_btn = button.KeyButton()

        button_key_lyt = qg.QHBoxLayout()
        button_key_lyt.setAlignment(qc.Qt.AlignCenter)

        self.left_side_holder_lyt.addWidget(self.select_all_btn)
        self.left_side_holder_lyt.addWidget(self.deselect_all_btn)
        self.left_side_holder_lyt.addWidget(self.proxy_btn)

        self.left_side_holder_lyt.addWidget(self.select_geo_btn)

        button_key_lyt.addWidget(self.keyframe_btn)
        self.left_side_holder_lyt.addLayout(button_key_lyt)

        ######################################################################################################################################################################
        #   TOP LABEL TOOL TIP
        #
        self.header_label = Header_custom_label(parent=self)

        ############################
        # CONTENT MARGING HANDLE
        #
        self._margin = 2

        # CONNECT SIGNALS AND SLOTS
        self.rigth_leg_snap_btn.clicked.connect(self.makeSnaps)
        self.left_leg_snap_btn.clicked.connect(self.makeSnaps)

        self.rigth_arm_snap_btn.clicked.connect(self.makeSnaps)
        self.left_arm_snap_btn.clicked.connect(self.makeSnaps)

        self.keyframe_btn.clicked.connect(lambda: self.op.keyNotZero(cmds.ls(sl=True)))

        self.makeCorner_connections()
        self.deselect_all_btn.clicked.connect(lambda: cmds.select(clear=True))
        self.select_all_btn.clicked.connect(self.selectAllControls)

        self.snap_labels = [self.l_leg_snap_label , self.r_leg_snap_label, self.r_arm_snap_label, self.l_arm_snap_label]

        self.updateAllWidgets()

        todelete = partial(deletingIndex, self.callbacks_array)
        self.destroyed.connect(todelete)

        self.create_callbacks()

        # clear all spin focus
        self.clear_focus()


    ###########################################################################################################################################################################
    ###########################################################################################################################################################################
    ###########################################################################################################################################################################

    def clear_focus(self):
        spins = self.findChildren(qg.QSpinBox)
        double_spin = self.findChildren(qg.QDoubleSpinBox)
        spins.extend(double_spin)
        for itm in spins:
            itm.clearFocus()


    def makeSnaps(self):
        sender = self.sender()
        name = self._manager.getNameSpace()

        if name is not None and len(name) > 0:
            name  = self._manager.getNameSpace() + ':'
        else:
            name = ''

        with delete_callbacks():
            if sender == self.rigth_arm_snap_btn:
                new_snaps.Hitch_R_arm_Snap(name)
                self.ik_fk_value_spin_r_arm.setValue(not(self.ik_fk_value_spin_r_arm.value()))

            elif sender == self.left_arm_snap_btn:
                new_snaps.Hitch_L_arm_Snap(name)
                self.ik_fk_value_spin_l_arm.setValue(not(self.ik_fk_value_spin_l_arm.value()))

            elif sender == self.rigth_leg_snap_btn:
                new_snaps.Hitch_R_LegSnap(name)
                self.ik_fk_value_spin_r_leg.setValue(not(self.ik_fk_value_spin_r_leg.value()))

            elif sender == self.left_leg_snap_btn:
                new_snaps.Hitch_L_LegSnap(name)
                self.ik_fk_value_spin_l_leg.setValue(not(self.ik_fk_value_spin_l_leg.value()))


    ###############################################

    def selectAllControls(self):
        with pause_callBacks():
            if self.prefix is not None:
                 for itm in BODYCONTROLS:
                    cmds.select(self.prefix + ':' + itm, add=True)

            elif self.prefix is  None:
                try:
                    for itm in BODYCONTROLS:
                        cmds.select(itm, add=True)

                except:
                    cmds.warning('- Not Name Space set for controls -')
                    return

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
            print('job not killed maybe')


        for itm in widgets:
            attribute = itm.objectName()
            try:
                job_num = cmds.scriptJob( runOnce=False, attributeChange=[attribute, self.updateAllWidgets] )
                self.callbacks_array.append(job_num)
            except:
                pass


    def makeCorner_connections(self):
        # TOP LEFT CONER
        loc = 'Arm_r_Attributes.'
        self.ik_fk_value_spin_r_arm.setObjectName(loc + 'IK_1_FK_0')
        self.ik_fk_value_spin_r_arm.valueChanged.connect(self.setAttributes)
        self.fk_Strectch_spin_r_arm.setObjectName(loc + 'FK_Stretch')
        self.fk_Strectch_spin_r_arm.valueChanged.connect(self.setAttributes)
        self.auto_clavicle_Spin_r_arm.setObjectName(loc + 'Auto_Clavicle')
        self.auto_clavicle_Spin_r_arm.valueChanged.connect(self.setAttributes)
        self.ctrl_vis_Spin_r_arm.setObjectName(loc + 'BothControls')
        self.ctrl_vis_Spin_r_arm.valueChanged.connect(self.setAttributes)
        self.finger_vis_Spin_r_arm.setObjectName('Hand_r_Motions.ShowControls')
        self.finger_vis_Spin_r_arm.valueChanged.connect(self.setAttributes)


        # TOP RIGTH CONER
        loc = 'Arm_l_Attributes.'
        self.ik_fk_value_spin_l_arm.setObjectName(loc + 'IK_1_FK_0')
        self.ik_fk_value_spin_l_arm.valueChanged.connect(self.setAttributes)
        self.fk_Strectch_spin_l_arm.setObjectName(loc + 'FK_Stretch')
        self.fk_Strectch_spin_l_arm.valueChanged.connect(self.setAttributes)
        self.auto_clavicle_Spin_l_arm.setObjectName(loc + 'Auto_Clavicle')
        self.auto_clavicle_Spin_l_arm.valueChanged.connect(self.setAttributes)
        self.ctrl_vis_Spin_l_arm.setObjectName(loc + 'BothControls')
        self.ctrl_vis_Spin_l_arm.valueChanged.connect(self.setAttributes)
        self.finger_vis_Spin_l_arm.setObjectName('Hand_l_Motions.ShowControls')
        self.finger_vis_Spin_l_arm.valueChanged.connect(self.setAttributes)


        # BOTTOM LEFT CORNER
        loc = 'Leg_r_Attributes.'
        self.ik_fk_value_spin_r_leg.setObjectName(loc + 'IK_1_FK_0')
        self.ik_fk_value_spin_r_leg.valueChanged.connect(self.setAttributes)
        self.fk_Strectch_spin_r_leg.setObjectName(loc + 'FK_Stretch')
        self.fk_Strectch_spin_r_leg.valueChanged.connect(self.setAttributes)
        self.ctrl_vis_Spin_r_leg.setObjectName(loc + 'Both_Controls')
        self.ctrl_vis_Spin_r_leg.valueChanged.connect(self.setAttributes)
        self.foot_vis_Spin_r_leg.setObjectName('Foot_r_IK_Animation_Values.Show_Controls')
        self.foot_vis_Spin_r_leg.valueChanged.connect(self.setAttributes)


        # BOTTOM RIGTH CORNER
        loc = 'Leg_l_Attributes.'
        self.ik_fk_value_spin_l_leg.setObjectName(loc + 'IK_1_FK_0')
        self.ik_fk_value_spin_l_leg.valueChanged.connect(self.setAttributes)
        self.fk_Strectch_spin_l_leg.setObjectName(loc + 'FK_Stretch')
        self.fk_Strectch_spin_l_leg.valueChanged.connect(self.setAttributes)
        self.ctrl_vis_Spin_l_leg.setObjectName(loc + 'Both_Controls')
        self.ctrl_vis_Spin_l_leg.valueChanged.connect(self.setAttributes)
        self.foot_vis_Spin_l_leg.setObjectName('Foot_l_IK_Animation_Values.Show_Controls')
        self.foot_vis_Spin_l_leg.valueChanged.connect(self.setAttributes)

        #################
        # RIGTH PANEL
        self.proxy_btn.setObjectName('Hitch_COG_CtrlShape.Proxy')
        self.proxy_btn.clicked.connect(self.setAttributes)

        #################
        # LEFT PANEL

        self.disc_rig_btn.setObjectName('Hitch_COG_CtrlShape.Connect_Disconnect_Rig')
        self.disc_rig_btn.clicked.connect(self.setAttributes)

        self.envs_rig_btn.setObjectName('Hitch_COG_CtrlShape.Envelopes')
        self.envs_rig_btn.clicked.connect(self.setAttributes)

        self.select_geo_btn.setObjectName('Premium_Attributes.Geo_Selectable')
        self.select_geo_btn.clicked.connect(self.setAttributes)

        self.breath_spin.setObjectName('Premium_Attributes.Breathing')
        self.breath_spin.valueChanged.connect(self.setAttributes)

        self.hyper_breath_spin.setObjectName('Premium_Attributes.HyperBreathing')
        self.hyper_breath_spin.valueChanged.connect(self.setAttributes)

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
                    self.update_ik_fk_headers(self.sender())
                except:
                    cmds.warning('No Name Space set for: {}'.format(attribute))

    ############################################################################################
    def updateAllWidgets(self):
        # updates the nameSpace first
        spins = self.findChildren(qg.QSpinBox)
        doubleSpins = self.findChildren(qg.QDoubleSpinBox)
        buttons = [self.proxy_btn, self.envs_rig_btn, self.disc_rig_btn, self.select_geo_btn]
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


    ##########################################################################################
    def update_ik_fk_headers(self, sender):
        checker = [self.ik_fk_value_spin_l_leg, self.ik_fk_value_spin_r_leg, self.ik_fk_value_spin_l_arm, self.ik_fk_value_spin_r_arm]
        if sender not in checker[:]:
            return

        ik = 'IK Sys'
        fk = 'FK Sys'
        value = sender.value()

        for itm in self.snap_labels:
            par_1 = itm.parent()
            if par_1 == sender.parent():
                if value == 1:
                    itm.setText(ik)
                elif value == 0:
                    itm.setText(fk)


    ##########################################################################################
    def resizeEvent(self, event):
        super(BodyPicker,self).resizeEvent(event)
        self._mainWidget.setFixedSize(self.width(), self.height())
        self.header_label.move((self.width() / 2) - (self.header_label.width() / 2), self.y())
        ################################################################
        # ADD CORNER WIDGETS PROCS
        #
        marg = self._margin
        #
        self.top_left_corner_wdg.move(self.x() + marg, self.y() + marg)
        self.top_rigth_corner_wdg.move((self.width() - self.top_rigth_corner_wdg.width()) - marg , self.y() + marg)

        self.left_side_holder.move(self.x() + marg , self.y() + marg + 418)
        self.right_side_holder.move((self.width() - self.right_side_holder.width()) - marg , self.y() + marg + 418)

        if self.width() >= 850:
            self.bottom_left_corner_wdg.move(self.x() + marg , (self.height() - self.bottom_left_corner_wdg.height()) - marg)
            self.bottom_rigth_corner_wdg.move((self.width() - self.bottom_rigth_corner_wdg.width()) - marg , (self.height() - self.bottom_rigth_corner_wdg.height()) - marg)

        else:
            y_offset = 53

            self.bottom_left_corner_wdg.move(self.x() + marg , (self.height() - self.bottom_left_corner_wdg.height())  - y_offset)
            self.bottom_rigth_corner_wdg.move((self.width() - self.bottom_rigth_corner_wdg.width())  - marg, (self.height() - self.bottom_rigth_corner_wdg.height()) - y_offset)






#######################################################################################################################################
class OpaqueWidget(qg.QLabel):
    def __init__(self, parent = None):
        super(OpaqueWidget, self).__init__(parent)
        self.setStyleSheet("QLabel {background-color: rgba(1,1,1,50)};")
        self.setMaximumWidth(250)
        self.setMaximumHeight(200)

        main_ui  = ConnectControls.getMainWindow(ConnectControls.windowObject)
        self.bodyPick = main_ui.findChildren(qg.QFrame,'bodyPickerLabel')[0]
########################################################################################################################################



class StaticPickerLabel(qg.QLabel):
    def __init__(self,*args, **kwargs):
        super(StaticPickerLabel, self).__init__(*args, **kwargs)

        self.setAlignment(qc.Qt.AlignHCenter | qc.Qt.AlignVCenter)
        self.setObjectName('body_static_picker_label')
        self.setStyleSheet('background-color: transparent;')
        self.bodyPickerPixmap = qg.QPixmap(BODYPICKER)
        myScaledPixmap = self.bodyPickerPixmap.scaled(800, 800 , qc.Qt.KeepAspectRatio, qc.Qt.SmoothTransformation)
        self.setPixmap(myScaledPixmap)
        self.setAttribute(qc.Qt.WA_AlwaysShowToolTips)

        ##################
        # CONTROLS MANAGER
        #
        self.co_manager = ConnectControls.ManageControls()

        ############################
        # CREATES THE CENTER BUTTONS
        #
        self.central_buttons = self.createButtons(CENTRAL, 'central')
        self.limbs_buttons = self.createButtons(LIMBS, 'limbs')
        self.feet_buttons = self.createButtons(FEET, 'feet')
        self.bendy_buttons = self.createButtons(BENDY, 'bendy')
        self.topControls = self.create_top_control_buttons()

        self.limbsbuttons_list = []
        for value in self.limbs_buttons.values():
            self.limbsbuttons_list.append(value)



        ################
        # HAND SHOLDERS
        #
        self.rigth_hand_holder = self.create_hands_holder('rigth_holder')

        self.left_hand_holder = self.create_hands_holder('left_holder')

        self.rigth_holder_lyt = qg.QVBoxLayout(self.rigth_hand_holder)
        self.left_holder_lyt = qg.QVBoxLayout(self.left_hand_holder)

        self.rigth_finger_btns = self.fingers_procs(HANDS, self.rigth_holder_lyt, 'right')
        self.left_finger_btns = self.fingers_procs(HANDS, self.left_holder_lyt, 'left')


    ################################################################################################
        for key, val in self.central_buttons.items():
            val.clicked.connect(self.buttons_manager)

        for key, val in self.limbs_buttons.items():
            val.clicked.connect(self.buttons_manager)

        for key, val in self.feet_buttons.items():
            val.clicked.connect(self.buttons_manager)

        for key, val in self.bendy_buttons.items():
            val.clicked.connect(self.buttons_manager)

        for key, val in self.topControls.items():
            val.clicked.connect(self.buttons_manager)

        for key, val in self.rigth_finger_btns.items():
            val.clicked.connect(self.buttons_manager)

        for key, val in self.left_finger_btns.items():
            val.clicked.connect(self.buttons_manager)

    ################################################################################################

###
###
    def buttons_manager(self):
        buttonName = self.sender().objectName()
        print(buttonName)
        self.co_manager.getComand_to_connect(buttonName)

    ###############################################
    def fingers_procs(self, lista, layout, side):
        dictionary = {}
        fingers_lyt = qg.QHBoxLayout()

        thumb_lyt = qg.QHBoxLayout()
        thumb_lyt.setSpacing(4)
        pinky_lyt = qg.QVBoxLayout()
        pinky_lyt.setSpacing(4)
        ring_lyt = qg.QVBoxLayout()
        ring_lyt.setSpacing(4)
        middle_lyt = qg.QVBoxLayout()
        middle_lyt.setSpacing(4)
        index_lyt = qg.QVBoxLayout()
        index_lyt.setSpacing(4)
        thumb_lyt.addSpacing(20)
        #############################
        if side == 'right':
            for itm in lista:
                if '_r_' in itm[:]:
                    thumbs = []
                    if 'thumb' in itm[:]:
                        thumbs.append(itm)
                        for obj in reversed(thumbs):
                            btn = self.hookUp_button(str(itm), 'Round_button_small_green')
                            dictionary[itm] = btn
                            thumb_lyt.addWidget(btn)

                    elif 'pinky' in itm[:]:
                        btn = self.hookUp_button(str(itm), 'Round_button_small_orange')
                        pinky_lyt.addWidget(btn)
                        dictionary[itm] = btn

                    elif 'ring' in itm[:]:
                        btn = self.hookUp_button(str(itm), 'Round_button_small_orange')
                        ring_lyt.addWidget(btn)
                        dictionary[itm] = btn

                    elif 'middle' in itm[:]:
                        btn = self.hookUp_button(str(itm), 'Round_button_small_orange')
                        middle_lyt.addWidget(btn)
                        dictionary[itm] = btn

                    elif 'index' in itm[:]:
                        btn = self.hookUp_button(str(itm), 'Round_button_small_red')
                        index_lyt.addWidget(btn)
                        dictionary[itm] = btn

            ############################
            layout.addLayout(thumb_lyt)
            layout.setSpacing(2)

            fingers_lyt.addLayout(pinky_lyt)
            fingers_lyt.addLayout(ring_lyt)
            fingers_lyt.addLayout(middle_lyt)
            fingers_lyt.addLayout(index_lyt)
            fingers_lyt.addSpacing(10)
            layout.addLayout(fingers_lyt)

            return dictionary


        if side == 'left':
            for itm in lista:
                if '_l_' in itm[:]:
                    thumbs = []
                    if 'thumb' in itm[:]:
                        thumbs.append(itm)
                        for obj in reversed(thumbs):
                            btn = self.hookUp_button(str(itm), 'Round_button_small_green')
                            dictionary[itm] = btn
                            thumb_lyt.addWidget(btn)

                    elif 'pinky' in itm[:]:
                        btn = self.hookUp_button(str(itm), 'Round_button_small_orange')
                        pinky_lyt.addWidget(btn)
                        dictionary[itm] = btn

                    elif 'ring' in itm[:]:
                        btn = self.hookUp_button(str(itm), 'Round_button_small_orange')
                        ring_lyt.addWidget(btn)
                        dictionary[itm] = btn

                    elif 'middle' in itm[:]:
                        btn = self.hookUp_button(str(itm), 'Round_button_small_orange')
                        middle_lyt.addWidget(btn)
                        dictionary[itm] = btn

                    elif 'index' in itm[:]:
                        btn = self.hookUp_button(str(itm), 'Round_button_small_red')
                        index_lyt.addWidget(btn)
                        dictionary[itm] = btn

            ############################
            thumb_lyt.setDirection(qg.QBoxLayout.RightToLeft)
            fingers_lyt.setDirection(qg.QBoxLayout.RightToLeft)
            layout.addLayout(thumb_lyt)
            layout.setSpacing(2)

            fingers_lyt.addLayout(pinky_lyt)
            fingers_lyt.addLayout(ring_lyt)
            fingers_lyt.addLayout(middle_lyt)
            fingers_lyt.addLayout(index_lyt)
            fingers_lyt.addSpacing(10)
            layout.addLayout(fingers_lyt)

            return dictionary
            ################################################


    def apply_regex(self, String, finder):
        list2Check = String.split("_")
        pattern2Check = '(?:' + '|'.join(list2Check) + ')'
        regex = r'(?:\b|_){}(?=\b|_)'.format(pattern2Check)
        find = re.compile(regex, re.IGNORECASE)
        resultado = find.findall(finder)
        return resultado
        ###################################################


        ###################################################
        # HANDS HOLDER

    def create_hands_holder(self, name):
        label = qg.QLabel()
        label.setObjectName(name)
        label.setParent(self)
        label.setStyleSheet("background-color: rgba(1,1,1,20);")
        label.setFixedSize(160,180)
        label.setAlignment(qc.Qt.AlignCenter)
        return label
        #####################################################


    def create_top_control_buttons(self):
        dictionary = {}

        Hitch_global_Ground_Ctrl = 'Hitch_global_Ground_Ctrl'
        Hitch_COG_Ctrl = 'Hitch_COG_Ctrl'
        Hitch_head_IK_Ctrl = 'Hitch_head_IK_Ctrl'

        gbl_ctrl = self.hookUp_button(Hitch_global_Ground_Ctrl,'Flat_button_green_big')
        cog_ctrl = self.hookUp_button(Hitch_COG_Ctrl,'Flat_button_green')
        head_ctrl = self.hookUp_button(Hitch_head_IK_Ctrl,'Round_button_cross_red')

        dictionary[Hitch_global_Ground_Ctrl] = gbl_ctrl
        dictionary[Hitch_COG_Ctrl] = cog_ctrl
        dictionary[Hitch_head_IK_Ctrl] = head_ctrl

        return dictionary


    def createButtons(self, control_list, keyword = None ):
        dictionary = {}

        for ctrl in control_list:
            if keyword == 'limbs':
                IK = self.apply_regex(ctrl, 'IK')
                PV = self.apply_regex(ctrl, 'PV')
                if len(IK) or len(PV) > 0:
                    ik_btn = self.hookUp_button(ctrl,'Square_button_red')
                    dictionary[ctrl] = ik_btn
                else:
                    fk_btn = self.hookUp_button(ctrl,'Square_button_blue')
                    dictionary[ctrl] = fk_btn

            elif keyword == 'feet':
                IK = self.apply_regex(ctrl, 'IK')
                FK = self.apply_regex(ctrl, 'FK')
                if len(IK) > 0:
                    ik_btn = self.hookUp_button(ctrl,'Round_button_small_red')
                    dictionary[ctrl] = ik_btn

                elif len(FK) > 0:
                    fk_btn = self.hookUp_button(ctrl,'Round_button_small_green')
                    dictionary[ctrl] = fk_btn

                else:
                    neutral_btn = self.hookUp_button(ctrl, 'Round_button_small_orange')
                    dictionary[ctrl] = neutral_btn

            elif keyword == 'central':
                IK = self.apply_regex(ctrl, 'IK')
                if len(IK) > 0:
                    ik_btn = self.hookUp_button(ctrl,'Round_button_yellow')
                    dictionary[ctrl] = ik_btn
                else:
                    fk_btn = self.hookUp_button(ctrl,'Flat_button_red')
                    dictionary[ctrl] = fk_btn


        if keyword == 'bendy':
            for ctrl in control_list:
                bendy_btn = self.hookUp_button(ctrl,'Round_button_orange')
                dictionary[ctrl] = bendy_btn

        return  dictionary

        #################################################################################

    def hookUp_button(self, name, button_type):
        button = getattr(PickerButtons,button_type)(parent=self)
        button.setParent(self)
        button.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)
        button.setObjectName(name)

        return button

    def resizeEvent(self, event):
        super(StaticPickerLabel,self).resizeEvent(event)
        off_x = (self.width() / 2 )
        off_y = (self.height() / 2)

        ################################################
        # RIGHT SIDE BUTTONS
        #
        # BUTTONS
        Hitch_r_clavicle_FK_Ctrl = self.limbs_buttons['Hitch_r_clavicle_FK_Ctrl']
        Hitch_r_upperarm_FK_Ctrl = self.limbs_buttons['Hitch_r_upperarm_FK_Ctrl']

        Hitch_r_lowerarm_FK_Ctrl = self.limbs_buttons['Hitch_r_lowerarm_FK_Ctrl']
        Hitch_r_arm_PV_Ctrl = self.limbs_buttons['Hitch_r_arm_PV_Ctrl']

        Hitch_r_hand_FK_Ctrl = self.limbs_buttons['Hitch_r_hand_FK_Ctrl']
        Hitch_r_hand_IK_Ctrl = self.limbs_buttons['Hitch_r_hand_IK_Ctrl']

        Hitch_upperleg_r_FK_Ctrl = self.limbs_buttons['Hitch_upperleg_r_FK_Ctrl']

        Hitch_lowerleg_r_FK_Ctrl = self.limbs_buttons['Hitch_lowerleg_r_FK_Ctrl']
        Hitch_r_leg_PV_Ctrl = self.limbs_buttons['Hitch_r_leg_PV_Ctrl']

        Hitch_r_foot_FK_Ctrl = self.limbs_buttons['Hitch_r_foot_FK_Ctrl']
        Hitch_r_foot_IK_Ctrl = self.limbs_buttons['Hitch_r_foot_IK_Ctrl']

        hitch_clavicle_l_IK_Ctrl = self.limbs_buttons['hitch_clavicle_l_IK_Ctrl']
        hitch_clavicle_r_IK_Ctrl = self.limbs_buttons['hitch_clavicle_r_IK_Ctrl']

        # BUTTONS POSITION

        hitch_clavicle_l_IK_Ctrl.move((self.width() / 2) + 22, (self.height() / 2) - 204)
        hitch_clavicle_r_IK_Ctrl.move((self.width() / 2) - 55, (self.height() / 2) - 204)

        Hitch_r_clavicle_FK_Ctrl.move((off_x - 55) , (off_y - 240))
        Hitch_r_upperarm_FK_Ctrl.move((off_x - 100) , (off_y - 220))

        Hitch_r_lowerarm_FK_Ctrl.move((off_x - 180) , (off_y - 155))
        Hitch_r_arm_PV_Ctrl.move((off_x - 180) , (off_y - 195))

        Hitch_r_hand_FK_Ctrl.move((off_x - 300)  , (off_y - 100))
        Hitch_r_hand_IK_Ctrl.move((off_x - 340)  , (off_y - 100))

        Hitch_upperleg_r_FK_Ctrl.move((off_x - 65) , (off_y - 10))

        Hitch_lowerleg_r_FK_Ctrl.move((off_x - 35) , (off_y + 165))
        Hitch_r_leg_PV_Ctrl.move((off_x - 75) , (off_y + 165))

        Hitch_r_foot_FK_Ctrl.move((off_x - 35) , (off_y + 320))
        Hitch_r_foot_IK_Ctrl.move((off_x - 75) , (off_y + 320))

        #################################################
        # CENTER BUTTONS
        # BUTTONS
        #
        hitch_neck_FK_Ctrl = self.central_buttons['hitch_neck_FK_Ctrl']
        hitch_chest_IK_Ctrl = self.central_buttons['hitch_chest_IK_Ctrl']
        hitch_topSpine_IK_Ctrl = self.central_buttons['hitch_topSpine_IK_Ctrl']
        hitch_midSpine_IK_Ctrl = self.central_buttons['hitch_midSpine_IK_Ctrl']
        hitch_midSpine_FK_Ctrl = self.central_buttons['hitch_midSpine_FK_Ctrl']
        hitch_lowerSpine_IK_Ctrl = self.central_buttons['hitch_lowerSpine_IK_Ctrl']
        hitch_hips_FK_Ctrl = self.central_buttons['hitch_hips_FK_Ctrl']
        hitch_hips__IK_Ctrl = self.central_buttons['hitch_hips__IK_Ctrl']

        # BUTTONS POSITION
        hitch_neck_FK_Ctrl.move(off_x - (hitch_neck_FK_Ctrl.width() / 2) , off_y - 270)
        hitch_chest_IK_Ctrl.move(off_x - (hitch_chest_IK_Ctrl.width() / 2) , off_y - 240)
        hitch_topSpine_IK_Ctrl.move(off_x - (hitch_topSpine_IK_Ctrl.width() / 2) , off_y - 200)
        hitch_midSpine_IK_Ctrl.move(off_x - (hitch_midSpine_IK_Ctrl.width() / 2) , off_y - 160 )
        hitch_midSpine_FK_Ctrl.move(off_x - (hitch_midSpine_FK_Ctrl.width() / 2) , off_y - 120)
        hitch_lowerSpine_IK_Ctrl.move(off_x - (hitch_lowerSpine_IK_Ctrl.width() / 2) , off_y - 95)
        hitch_hips_FK_Ctrl.move(off_x - (hitch_hips_FK_Ctrl.width() / 2) , off_y - 55)
        hitch_hips__IK_Ctrl.move(off_x - (hitch_hips__IK_Ctrl.width() / 2) , off_y - 10)

        #################################################
        # LEFT SIDE BUTTONS
        #
        # BUTTONS
        Hitch_l_clavicle_FK_Ctrl = self.limbs_buttons['Hitch_l_clavicle_FK_Ctrl']
        Hitch_l_upperarm_FK_Ctrl = self.limbs_buttons['Hitch_l_upperarm_FK_Ctrl']

        Hitch_l_lowerarm_FK_Ctrl = self.limbs_buttons['Hitch_l_lowerarm_FK_Ctrl']
        Hitch_l_arm_PV_Ctrl = self.limbs_buttons['Hitch_l_arm_PV_Ctrl']

        Hitch_l_hand_FK_Ctrl = self.limbs_buttons['Hitch_l_hand_FK_Ctrl']
        Hitch_l_hand_IK_Ctrl = self.limbs_buttons['Hitch_l_hand_IK_Ctrl']

        Hitch_upperleg_l_FK_Ctrl = self.limbs_buttons['Hitch_upperleg_l_FK_Ctrl']

        Hitch_lowerleg_l_FK_Ctrl = self.limbs_buttons['Hitch_lowerleg_l_FK_Ctrl']
        Hitch_l_leg_PV_Ctrl = self.limbs_buttons['Hitch_l_leg_PV_Ctrl']

        Hitch_l_foot_FK_Ctrl = self.limbs_buttons['Hitch_l_foot_FK_Ctrl']
        Hitch_l_foot_IK_Ctrl = self.limbs_buttons['Hitch_l_foot_IK_Ctrl']

        # BUTTONS POSITION
        off_x = (self.width() / 2 ) - 34

        Hitch_l_clavicle_FK_Ctrl.move((off_x + 55) , (off_y - 240))
        Hitch_l_upperarm_FK_Ctrl.move((off_x + 100) , (off_y - 220))

        Hitch_l_lowerarm_FK_Ctrl.move((off_x + 180) , (off_y - 155))
        Hitch_l_arm_PV_Ctrl.move((off_x + 180) , (off_y - 195))

        Hitch_l_hand_FK_Ctrl.move((off_x + 300)  , (off_y - 100))
        Hitch_l_hand_IK_Ctrl.move((off_x + 340)  , (off_y - 100))

        Hitch_upperleg_l_FK_Ctrl.move((off_x + 65) , (off_y - 10))

        Hitch_lowerleg_l_FK_Ctrl.move((off_x + 35) , (off_y + 165))
        Hitch_l_leg_PV_Ctrl.move((off_x + 75) , (off_y + 165))

        Hitch_l_foot_FK_Ctrl.move((off_x + 35) , (off_y + 320))
        Hitch_l_foot_IK_Ctrl.move((off_x + 75) , (off_y + 320))

        ##########################################################################
        # BENDY AREA BUTTONS
        #
        # LEFT SIDE
        off_x = (self.width() / 2 )

        Hitch_r_upperarmGimbal_FK_Ctrl = self.bendy_buttons['Hitch_r_upperarmGimbal_FK_Ctrl']
        Hitch_r_bendy_arm_Ctrl = self.bendy_buttons['Hitch_r_bendy_arm_Ctrl']
        Hitch_r_HandMotion_Ctrl = self.bendy_buttons['Hitch_r_HandMotion_Ctrl']
        Hitch_r_bendy_leg_Ctrl = self.bendy_buttons['Hitch_r_bendy_leg_Ctrl']

        Hitch_r_upperarmGimbal_FK_Ctrl.move((off_x - 120) , (off_y - 270))
        Hitch_r_bendy_arm_Ctrl.move((off_x - 200) , (off_y - 230))

        Hitch_r_HandMotion_Ctrl.move((off_x - 320) , (off_y - 145))
        Hitch_r_bendy_leg_Ctrl.move((off_x - 115) , (off_y + 165))

        ###################
        #   RIGTH SIDE

        off_x = (self.width() / 2 ) - 34
        Hitch_l_upperarmGimbal_FK_Ctrl = self.bendy_buttons['Hitch_l_upperarmGimbal_FK_Ctrl']
        Hitch_l_bendy_arm_Ctrl = self.bendy_buttons['Hitch_l_bendy_arm_Ctrl']
        Hitch_l_HandMotion_Ctrl = self.bendy_buttons['Hitch_l_HandMotion_Ctrl']
        Hitch_l_bendy_leg_Ctrl = self.bendy_buttons['Hitch_l_bendy_leg_Ctrl']

        Hitch_l_upperarmGimbal_FK_Ctrl.move((off_x + 120) , (off_y - 270))
        Hitch_l_bendy_arm_Ctrl.move((off_x + 200) , (off_y - 230))

        Hitch_l_HandMotion_Ctrl.move((off_x + 320) , (off_y - 145))
        Hitch_l_bendy_leg_Ctrl.move((off_x + 115) , (off_y + 165))

        ###################################################################################
        # FEET CONTROLS BUTTONS
        #
        # RIGTH SIDE
        off_x = (self.width() / 2 )
        off_y = (self.height())

        Hitch_r_heel_IK_Ctrl = self.feet_buttons['Hitch_r_heel_IK_Ctrl']
        Hitch_r_tillOut_Ctrl = self.feet_buttons['Hitch_r_tillOut_Ctrl']
        Hitch_r_tillIn_Ctrl = self.feet_buttons['Hitch_r_tillIn_Ctrl']
        Hitch_r_toes_FK_Ctrl = self.feet_buttons['Hitch_r_toes_FK_Ctrl']
        Hitch_r_ball_IK_Ctrl = self.feet_buttons['Hitch_r_ball_IK_Ctrl']
        Hitch_r_toes_IK_Ctrl = self.feet_buttons['Hitch_r_toes_IK_Ctrl']
        Hitch_r_toesTip_IK_Ctrl = self.feet_buttons['Hitch_r_toesTip_IK_Ctrl']

        Hitch_r_heel_IK_Ctrl.move((off_x - 25) , (off_y - 50))
        Hitch_r_tillOut_Ctrl.move((off_x - 50) , (off_y - 50))
        Hitch_r_tillIn_Ctrl.move((off_x - 75) , (off_y - 50))
        Hitch_r_toes_FK_Ctrl.move((off_x - 100) , (off_y - 50))
        Hitch_r_ball_IK_Ctrl.move((off_x - 125) , (off_y - 50))
        Hitch_r_toes_IK_Ctrl.move((off_x - 150) , (off_y - 50))
        Hitch_r_toesTip_IK_Ctrl.move((off_x - 175) , (off_y - 50))

        ##################
        # LEFT SIDE
        #
        off_x = (self.width() / 2 ) - 25

        Hitch_l_heel_IK_Ctrl = self.feet_buttons['Hitch_l_heel_IK_Ctrl']
        Hitch_l_tillOut_Ctrl = self.feet_buttons['Hitch_l_tillOut_Ctrl']
        Hitch_l_tillIn_Ctrl = self.feet_buttons['Hitch_l_tillIn_Ctrl']
        Hitch_l_toes_FK_Ctrl = self.feet_buttons['Hitch_l_toes_FK_Ctrl']
        Hitch_l_ball_IK_Ctrl = self.feet_buttons['Hitch_l_ball_IK_Ctrl']
        Hitch_l_toes_IK_Ctrl = self.feet_buttons['Hitch_l_toes_IK_Ctrl']
        Hitch_l_toesTip_IK_Ctrl = self.feet_buttons['Hitch_l_toesTip_IK_Ctrl']

        Hitch_l_heel_IK_Ctrl.move((off_x + 25) , (off_y - 50))
        Hitch_l_tillOut_Ctrl.move((off_x + 50) , (off_y - 50))
        Hitch_l_tillIn_Ctrl.move((off_x + 75) , (off_y - 50))
        Hitch_l_toes_FK_Ctrl.move((off_x + 100) , (off_y - 50))
        Hitch_l_ball_IK_Ctrl.move((off_x + 125) , (off_y - 50))
        Hitch_l_toes_IK_Ctrl.move((off_x + 150) , (off_y - 50))
        Hitch_l_toesTip_IK_Ctrl.move((off_x + 175) , (off_y - 50))

        ##############################################################
        # TOP LAYER CONTROLS
        #
        off_x = (self.width() / 2 )
        off_y = (self.height() / 2)

        Hitch_head_IK_Ctrl = self.topControls['Hitch_head_IK_Ctrl']
        Hitch_COG_Ctrl = self.topControls['Hitch_COG_Ctrl']
        Hitch_global_Ground_Ctrl = self.topControls['Hitch_global_Ground_Ctrl']

        Hitch_head_IK_Ctrl.move((off_x - (Hitch_head_IK_Ctrl.width() / 2 )) , (off_y - 390))
        Hitch_COG_Ctrl.move((off_x - (Hitch_COG_Ctrl.width() / 2 )) , (off_y - 35))
        off_y = (self.height())
        Hitch_global_Ground_Ctrl.move((off_x - (Hitch_global_Ground_Ctrl.width() / 2 )) , (off_y - 25))

        #####################################################################
        #labels for fingers
        #
        self.rigth_hand_holder.move((self.width() / 2) - 285 ,(self.height() / 2) - 40)

        self.left_hand_holder.move((self.width() / 2) + 285 - self.left_hand_holder.width()  ,(self.height() / 2) - 40)

##################################################################################################################
#
CSS = """QLabel
        {
        background-color: rgba(255,255,255,1);
        color: rgba(225,40,40,220);
        font-family: Source Code Pro Black;
        font: bold 18px;

        }"""

class Header_custom_label(qg.QLabel):
    def __init__(self, *args, **kwargs):
        super(Header_custom_label, self).__init__(*args, **kwargs)
        self.setFixedSize(300,30)
        self.setStyleSheet(CSS)
        self.setIndent(4)
        self.setAlignment(qc.Qt.AlignCenter)

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


