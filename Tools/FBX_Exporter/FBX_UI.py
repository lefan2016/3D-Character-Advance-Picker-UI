# -*- coding: utf-8 -*-
import PySide.QtCore as qc
import PySide.QtGui as qg
import os
import sys
from PySide.QtGui import QPen, QColor, QBrush, QLinearGradient, QFont, QRadialGradient
try:
    # sys.path.append(r"C:\Program Files\Autodesk\Maya2016\devkit\other\pymel\extras\completion\py")
    import maya.cmds as cmds
    import pymel.core      as pm
    import maya.OpenMaya   as om
    import maya.OpenMayaUI as mui
    import shiboken        as shi
    from HitchAnimationModule.Widgets import label
    from HitchAnimationModule.Widgets import Tabs
    from HitchAnimationModule.Widgets   import button
    from HitchAnimationModule.Widgets   import checkBox
    from HitchAnimationModule.Widgets   import lineEdit
    from HitchAnimationModule.Widgets   import spliter
    from HitchAnimationModule.Widgets   import ColtSpinBox
    from HitchAnimationModule.Tools.FBX_Exporter.FBX_Logic   import FBX_Exporter_logic; reload(FBX_Exporter_logic)

except:
    pass
from functools import partial

###############################################################
# GLOBALS:
FBX_GLOBAL  = None
MAINOBJNAME = 'Colt_FBX_Export'
#
#
X=0
X2=8  #!!!!
Y=0
Y2=30 #!!!!
#---------------------------------------------------------------------------------#
try:
    CSS_tabs = Tabs.style_sheet_file_02
    FONT = qg.QFont('Calibri', 10, qg.QFont.Bold)
    MAYAICON = os.path.join(cmds.internalVar(usd=1) , 'HitchAnimationModule','Icons','Maya-icon.png')
    WORKSPACE = os.path.join(cmds.workspace( q=True ,rd=True, l=True) , "scenes")

except: pass
#---------------------------------------------------------------------------------#
def cleanData(dictionary):
    for key,val in dictionary.items():
        try:
            val.delete_all_data()
        except:
            pass

#---------------------------------------------------------------------------------#
def undo(func):
    def wrapper(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        try:
            ret = func(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)
        return ret
    return wrapper
#-------------------------------------------------------------#
def getMayaWindow():
    mainWinPtr = mui.MQtUtil.mainWindow()
    return shi.wrapInstance(long(mainWinPtr),qg.QWidget)

#---------------------------------------------------------------------------------#

standBy_lb_css = """QLabel{
                    color: rgba(225,40,40,220);
                    border: 1px  solid black;
                    font-family: Calibri;
                    font: bold 14px;
                    background : qlineargradient(x1:0, y1:0, x2:0, y2:0, stop:0.0 rgba(53, 57, 60,125),
                                                          stop:0.5 rgba(33, 34, 36,150),stop:1 rgba(53, 57, 60,125));


                 }"""
#---------------------------------------------------------------------------------#
# delete ANY maya child with given object name to mantain clean the memory
#
def deleteFromGlobal(windowObject):
    mayaMainWindowPtr = mui.MQtUtil.mainWindow()
    mayaMainWindow = shi.wrapInstance(long(mayaMainWindowPtr), qg.QMainWindow) # Important that it's QMainWindow, and not QWidget
    # Go through main window's children to find any previous instances
    for obj in mayaMainWindow.children():
        if isinstance(obj,qg.QDialog):
            if obj.objectName() == windowObject:
                print obj.objectName()
                obj.setParent(None)
                obj.deleteLater()
                print('Object Deleted...', obj.objectName())
                del(obj)
                global FBX_GLOBAL
                FBX_GLOBAL = None

#---------------------------------------------------------------------------------#
class Colt_FBX_Export(qg.QDialog):
    leftClick = False
    exportSignal = qc.Signal(bool)

    def __init__(self, parent=getMayaWindow()):
        super(Colt_FBX_Export, self).__init__(parent)
        self.setObjectName(MAINOBJNAME)

        self.setLayout(qg.QStackedLayout(self))
        self.layout().setContentsMargins(0,0,0,0)
        self.setFixedSize(1000,750)


        self.setAttribute(qc.Qt.WA_DeleteOnClose)
        self.setStyleSheet("QDialog {background-color : rgba(35, 36, 38,247);}")

        self.frame = qg.QFrame()
        self.frame.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)
        self.frame.setObjectName('Colt_FBX_Export_Frame')

        self.layout().addWidget(self.frame)
        self.frame.setStyleSheet("""QFrame#Colt_FBX_Export_Frame { background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(85, 87, 90,225), stop: 0.5 rgba(25,15,05,50), stop: 1.0 rgba(33, 34, 36, 230))};""")

        frame_lyt = qg.QVBoxLayout(self.frame)
        titleLabel = label.CustomFBX_Label('   Colt Custom Character FBX Exporter   ')

        self.exportSetup_btn = button.ExportSetup_button('Export Setup')
        self.exportSetup_btn.setParent(self)
        self.exportSetup_btn.setEnabled(False)

        # exporting procedure ::::
        #
        self.cover_css = """QLabel
                        {
                        background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 0.5 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(1, 1, 1,0), stop: 0.05 rgba(1, 1, 1,1), stop: 0.9 rgba(1, 1, 1, 125));

                        shadow : rgb(9, 10, 12);
                        border: 1px solid rgb(9, 10, 12);
                        border-radius: 12px;
                        color : rgba(202, 207, 210, 255);
                        font-Family: Source Code Pro SemiBold;
                        font-size: 25px

                        }"""


        self.exportingCover = qg.QLabel()
        self.exportingCover.setWordWrap(True)
        self.exportingCover.setObjectName('cover')

        self.exportingCover.setAlignment(qc.Qt.AlignBottom)

        self.exportingCover.setStyleSheet("background-color: transparent;")

        self.exportingCover.setContentsMargins(10,25,10,15)

        self.layout().addWidget(self.exportingCover)
        self.layout().setCurrentIndex(0)
        self.layout().setStackingMode(qg.QStackedLayout.StackAll)

        self._timer = qc.QTimer()
        self._timer.setSingleShot(3000)

        self._timer.timeout.connect(lambda : self.layout().setCurrentIndex(0))



        ############################################################
        self.close_btn = button.CloseButton()
        self.close_btn.setStyleSheet("background-color: transparent;")
        close_btn_lyt = qg.QHBoxLayout()
        close_btn_lyt.addSpacing(170)

        frame_lyt.addLayout(close_btn_lyt)
        close_btn_lyt.setAlignment(qc.Qt.AlignTop | qc.Qt.AlignRight)
        close_btn_lyt.addWidget(self.close_btn)

        frame_lyt.addWidget(titleLabel)

        #####################
        # tab container
        #
        self.tabWidget = qg.QTabWidget()
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setStyleSheet(CSS_tabs)
        self.tabWidget.setObjectName('tabWidget_FBX')

        frame_lyt.addWidget(self.tabWidget)

        ##############################################################
        # Exporter tabs
        #

        self.animation_tab = qg.QFrame()
        self.animation_tab.setStyleSheet("background-color: rgba(35, 36, 38,254);")
        self.tabWidget.addTab(self.animation_tab,'- 1 Animation ')

        self.model_tab = qg.QFrame()
        self.model_tab.setStyleSheet("background-color: rgba(35, 36, 38,254);")
        self.tabWidget.addTab(self.model_tab,'- 2 Model ')

        ################################################################
        # LIST WIDGET
        #

        inside_lyt =qg.QHBoxLayout(self.animation_tab)

        list_view_01_lyt = qg.QVBoxLayout()
        list_view_01_lyt.setAlignment(qc.Qt.AlignVCenter | qc.Qt.AlignHCenter)
        list_01_lb = label.CustomShortLabel('Actors')
        list_01_lb.setFixedHeight(25)
        list_01_lb.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Minimum)

        stackHolder_widget = qg.QWidget()
        stackHolder_widget.setFixedWidth(250)
        stackHolder_widget.setMaximumHeight(450)

        self.stack_layout = qg.QStackedLayout(stackHolder_widget)
        self.stack_layout.setAlignment(qc.Qt.AlignVCenter | qc.Qt.AlignHCenter)

        self.list_view_wgt_01 = ListWidgetFBX()
        self.list_view_wgt_01.setFixedWidth(250)
        self.list_view_wgt_01.setMaximumHeight(450)
        self.list_view_wgt_01.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        self.actor_stack_lb = qg.QLabel('Select The Main Control from your Character and Click Populate to Activate the UI')
        self.actor_stack_lb.setStyleSheet(standBy_lb_css)

        self.actor_stack_lb.setFixedWidth(250)
        self.actor_stack_lb.setMaximumHeight(450)
        self.actor_stack_lb.setWordWrap(True)
        self.actor_stack_lb.setMargin(2)
        self.actor_stack_lb.setAlignment(qc.Qt.AlignVCenter | qc.Qt.AlignHCenter)
        self.actor_stack_lb.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)


        self.populate_button = button.Customflat_btn(' Populate ')
        self.populate_button.setObjectName('anim_populate_button')
        self.populate_button.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Minimum)

        self.stack_layout.addWidget(self.list_view_wgt_01)
        self.stack_layout.addWidget(self.actor_stack_lb)

        list_view_01_lyt.addWidget(list_01_lb)
        list_view_01_lyt.addWidget(stackHolder_widget)
        list_view_01_lyt.addWidget(self.populate_button)
        inside_lyt.addLayout(list_view_01_lyt)


        list_view_02_lyt = qg.QVBoxLayout()
        list_view_02_lyt.setAlignment(qc.Qt.AlignVCenter)
        list_02_lb = label.CustomShortLabel('Root Skinned Joints')
        list_02_lb.setFixedHeight(25)

        self.list_view_wgt_02 = ListWidgetFBX()
        self.list_view_wgt_02.setFixedWidth(250)
        self.list_view_wgt_02.setMaximumHeight(450)

        self.tag_as_origin_button = button.Customflat_btn(' Tag as Origin ')
        self.tag_as_origin_button.setObjectName('anim_new_export_node_button')
        self.tag_as_origin_button.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Expanding)


        list_view_02_lyt.addWidget(list_02_lb)
        list_view_02_lyt.addWidget(self.list_view_wgt_02)
        list_view_02_lyt.addWidget(self.tag_as_origin_button)
        inside_lyt.addLayout(list_view_02_lyt)

        self.stack_layout.setCurrentIndex(1)

        ####################################################################
        # RIGHT SIDE
        #
        right_lyt = qg.QVBoxLayout()
        inside_lyt.addLayout(right_lyt)
        right_lyt.setAlignment(qc.Qt.AlignHCenter)
        right_lyt.addSpacing(85)

        #  CHECK BUTTONS HERE
        first_r_horiz_lyt = qg.QFormLayout()
        first_r_horiz_lyt.setFormAlignment(qc.Qt.AlignRight)
        first_r_horiz_lyt.setRowWrapPolicy(qg.QFormLayout.WrapAllRows)
        first_r_horiz_lyt.setVerticalSpacing(15)
        right_lyt.addLayout(first_r_horiz_lyt)

        self.export_check = checkBox.CustomCheck('Export')
        self.export_check.setChecked(True)
        self.export_check.setObjectName('export')
        self.export_check.setSizePolicy(qg.QSizePolicy.Maximum, qg.QSizePolicy.Maximum)

        self.move_to_check = checkBox.CustomCheck('Move to Origin')
        self.move_to_check.setObjectName('moveToOrigin')
        self.move_to_check.setSizePolicy(qg.QSizePolicy.Maximum, qg.QSizePolicy.Maximum)

        self.zero_motion_check = checkBox.CustomCheck('Zero Motion on Origin')
        self.zero_motion_check.setObjectName('zeroOrigin')
        self.zero_motion_check.setSizePolicy(qg.QSizePolicy.Maximum, qg.QSizePolicy.Maximum)

        self.use_zero_check = checkBox.CustomCheck('Use Sub Range')
        self.use_zero_check.setObjectName('useSubRange')
        self.use_zero_check.setSizePolicy(qg.QSizePolicy.Maximum, qg.QSizePolicy.Maximum)

        inside_lyt.addLayout(right_lyt)

        first_r_horiz_lyt.addRow(self.export_check, self.move_to_check)
        first_r_horiz_lyt.addRow(self.zero_motion_check, self.use_zero_check )


        ##############################################################################
        # COMBO BOX AREA
        #
        MaxRange = cmds.playbackOptions(q=1,max=True)
        MinRange = cmds.playbackOptions(q=1,min=True)

        start_layout = qg.QHBoxLayout()
        end_layout = qg.QHBoxLayout()

        start_label = label.CustomShortLabel('Start Frame')
        end_label = label.CustomShortLabel('Ending Frame')

        self.start_spin = ColtSpinBox.CustomSpinBox()
        self.start_spin.setObjectName('startFrame')
        self.start_spin.setValue(1)
        self.start_spin.setRange(MinRange,MaxRange)
        self.start_spin.setEnabled(False)

        self.end_spin = ColtSpinBox.CustomSpinBox()
        self.end_spin.setObjectName('endFrame')
        self.end_spin.setValue(1)
        self.end_spin.setRange(MinRange,MaxRange)
        self.end_spin.setEnabled(False)

        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_spin)
        end_layout.addWidget(end_label)
        end_layout.addWidget(self.end_spin)

        horizontal_layout_row = qg.QHBoxLayout()
        horizontal_layout_row.addLayout(start_layout)
        horizontal_layout_row.addLayout(end_layout)

        first_r_horiz_lyt.addRow(horizontal_layout_row)

        #########################################################################################
        # EXPORT LINE EDIT
        #
        export_label = label.CustomShortLabel('Export File Name')
        self.export_name_le = lineEdit.FBX_LineEdit()
        self.export_name_le.setObjectName('anim_export_name_le')
        self.export_name_le.setEnabled(True)

        self.export_name_le.setFixedWidth(230)
        self.export_name_le.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Minimum)
        self.export_name_le.setAlignment(qc.Qt.AlignRight)

        self.browse_button = button.Customflat_btn(' Browse')
        self.browse_button.setObjectName('anim_browse_button')
        self.browse_button.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Maximum)

        line_edit_layout = qg.QHBoxLayout()
        line_edit_layout.addWidget(export_label)
        line_edit_layout.addWidget(self.export_name_le)
        line_edit_layout.addWidget(self.browse_button)

        first_r_horiz_lyt.addRow(line_edit_layout)

        ###################################################################
        # BUTTONS SEPARATOR
        #
        mid_lyt = qg.QVBoxLayout()
        mid_lyt.setAlignment(qc.Qt.AlignTop)

        splitter_lyt = spliter.SplitterLayout(content=(20,1,20,0))
        mid_lyt.addLayout(splitter_lyt)

        right_lyt.addLayout(mid_lyt)

        ###################################################################☺
        # ANIM LAYERS BUTTONS
        #

        buttton_layer_lyt = qg.QHBoxLayout()
        mid_lyt.addLayout(buttton_layer_lyt)
        buttton_layer_lyt.setSpacing(0)

        self.record_layers_btn = button.Customflat_toogle_name_btn_02('Recording Layers', 'Record Layers')
        self.record_layers_btn.setObjectName('anim_record_layers_btn')
        self.record_layers_btn.setChecked(True)
        self.preview_layers_btn = button.Customflat_btn('Preview Layers')
        self.preview_layers_btn.setObjectName('anim_preview_layers_btn')
        self.clear_layers_btn = button.Customflat_btn('Clear Layers')
        self.clear_layers_btn.setObjectName('anim_clear_layers_btn')

        self.record_layers_btn.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Minimum)
        self.preview_layers_btn.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Minimum)
        self.clear_layers_btn.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Minimum)


        buttton_layer_lyt.addWidget(self.record_layers_btn)
        buttton_layer_lyt.addWidget(self.preview_layers_btn)
        buttton_layer_lyt.addWidget(self.clear_layers_btn)

        ############################################################################################
        # END Buttons row export buttons
        #
        right_lyt.addSpacing(5)

        export_buttons_layout = qg.QVBoxLayout()
        export_buttons_layout.setAlignment(qc.Qt.AlignTop)

        self.export_selected_btn = button.Customflat_btn('Export Selected Animation')
        self.export_selected_btn.setObjectName('anim_export_selected_btn')

        self.export_all_from_all_btn = button.Customflat_btn('Export all Animations')
        self.export_all_from_all_btn.setObjectName('anim_export_all_from_all_btn')

        export_buttons_layout.addWidget(self.export_selected_btn)
        export_buttons_layout.addWidget(self.export_all_from_all_btn)

        self.export_selected_btn.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Minimum)
        self.export_all_from_all_btn.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Minimum)

        export_buttons_layout.addSpacing(100)

        right_lyt.addLayout(export_buttons_layout)

        #################################################################################################################
        # SECOND TAB AREA
        #
        #
        mode_vertical_lyt = qg.QVBoxLayout(self.model_tab)
        model_inside_lyt =qg.QHBoxLayout()


        #########################################################################################
        # EXPORT LINE EDIT
        #
        model_export_label = label.CustomShortLabel('Export File Name')
        self.model_export_name_le = lineEdit.FBX_LineEdit()
        self.model_export_name_le.setObjectName('model_export_name_le')
        self.model_export_name_le.setEnabled(True)

        #self.model_export_name_le.setFixedWidth(230)
        self.model_export_name_le.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Minimum)

        self.model_browse_button = button.Customflat_btn(' Browse')
        self.model_browse_button.setObjectName('model_browse_button')
        self.model_browse_button.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Minimum)

        model_line_edit_layout = qg.QHBoxLayout()
        model_line_edit_layout.addWidget(model_export_label)
        model_line_edit_layout.addWidget(self.model_export_name_le)
        model_line_edit_layout.addWidget(self.model_browse_button)


        ##########################################################################################    LIST WIDGETS MODEL TAB
        # LIST WIDGETS
        #

        ############ 01
        #
        model_list_view_01_lyt = qg.QVBoxLayout()
        model_list_view_01_lyt.setAlignment(qc.Qt.AlignVCenter)
        model_list_01_lb = label.CustomShortLabel('Origin Joint')
        model_list_01_lb.setFixedHeight(25)

        self.model_list_view_wgt_01 = ListWidgetFBX()
        self.model_list_view_wgt_01.setMaximumWidth(250)
        self.model_list_view_wgt_01.setMaximumHeight(450)

        model_fill_widget_01 = qg.QLabel()

        model_list_view_01_lyt.addSpacing(19)

        model_list_view_01_lyt.addWidget(model_list_01_lb)
        model_list_view_01_lyt.addWidget(self.model_list_view_wgt_01)
        model_list_view_01_lyt.addWidget(model_fill_widget_01)
        model_inside_lyt.addLayout(model_list_view_01_lyt)


        ############ 02
        #
        model_list_view_02_lyt = qg.QVBoxLayout()
        model_list_view_02_lyt.setAlignment(qc.Qt.AlignVCenter)
        model_list_02_lb = label.CustomShortLabel('Export Nodes')
        model_list_02_lb.setFixedHeight(25)

        self.model_list_view_wgt_02 = ListWidgetFBX()
        self.model_list_view_wgt_02.setMaximumWidth(250)
        self.model_list_view_wgt_02.setMaximumHeight(450)

        self.model_new_export_node_button = button.Customflat_btn(' New Export Node ')
        self.model_new_export_node_button.setObjectName('model_new_export_node_button')
        self.model_new_export_node_button.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Expanding)


        model_list_view_02_lyt.addWidget(model_list_02_lb)
        model_list_view_02_lyt.addWidget(self.model_list_view_wgt_02)
        model_list_view_02_lyt.addWidget(self.model_new_export_node_button)
        model_inside_lyt.addLayout(model_list_view_02_lyt)


        ############ 03
        #
        model_list_view_03_lyt = qg.QVBoxLayout()
        model_list_view_03_lyt.setAlignment(qc.Qt.AlignVCenter)
        model_list_03_lb = label.CustomShortLabel('Meshes')
        model_list_03_lb.setFixedHeight(25)

        self.model_list_view_wgt_03 = ListWidgetFBX()
        self.model_list_view_wgt_03.setMaximumWidth(250)
        self.model_list_view_wgt_03.setMaximumHeight(450)

        self.model_meshes_node_button = button.Customflat_btn(' Add Selected Meshes ')
        self.model_meshes_node_button.setObjectName('model_meshes_node_button')
        self.model_meshes_node_button.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Expanding)


        model_list_view_03_lyt.addWidget(model_list_03_lb)
        model_list_view_03_lyt.addWidget(self.model_list_view_wgt_03)
        model_list_view_03_lyt.addWidget(self.model_meshes_node_button)
        model_inside_lyt.addLayout(model_list_view_03_lyt)

        ##########################################################################################    BUTTONS MODEL TAB

        model_vertical_tercer_lyt = qg.QVBoxLayout()
        model_vertical_tercer_lyt.setAlignment(qc.Qt.AlignLeft | qc.Qt.AlignTop)
        model_vertical_tercer_lyt.addSpacing(45)
        model_inside_lyt.addLayout(model_vertical_tercer_lyt)

        self.model_export_check = checkBox.CustomCheck('Export')
        self.model_export_check.setChecked(True)
        self.model_export_check.setObjectName('model_export_checkbox')
        self.model_export_check.setSizePolicy(qg.QSizePolicy.Maximum, qg.QSizePolicy.Maximum)

        self.model_export_selected_button = button.Customflat_btn('Export Selected Character')
        self.model_export_selected_button.setObjectName('model_export_selected_button')
        self.model_export_selected_button.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Expanding)

        self.model_export_all_button = button.Customflat_btn('Export All Characters')
        self.model_export_all_button.setObjectName('model_export_all_button')
        self.model_export_all_button.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Expanding)

        model_vertical_tercer_lyt.addWidget(self.model_export_check)
        model_vertical_tercer_lyt.addWidget(self.model_export_selected_button)
        model_vertical_tercer_lyt.addWidget(self.model_export_all_button)


        ##############################################################################################################
        # MODEL TAB LAYOUT # ORGANIZACION DE LAS TABS AQUI
        #
        mode_vertical_lyt.addLayout(model_line_edit_layout)
        mode_vertical_lyt.addLayout(model_inside_lyt)


        #################################################################################################################
        # END SEPARATOR
        #
        splitter_lyt = spliter.SplitterLayout(content=(20,1,20,0))
        frame_lyt.addLayout(splitter_lyt)


        ###################################################################################################################
        # MORE VARIABLES:::
        #
        self._exporting = False
        self.current_export_deque = []
        self.exportCounter = 1
        self.current_export_data = []


        self.actors_dictionary = {}
        self.instances_dictionary = {}

        ###################################################################################################################
        # SIGNALS AND SLOTS :::
        #
        self.export_check.setEnabled(False)
        self.model_export_check.setEnabled(False)

        self.model_export_check.stateChanged.connect(self.update_export_model_check)
        self.list_view_wgt_01.itemClicked.connect(lambda val: self.populate_all_panels(val))


        self.browse_button.clicked.connect(lambda: self.browser_widgets(self.export_name_le, 'animation'))
        self.model_browse_button.clicked.connect(lambda: self.browser_widgets(self.model_export_name_le, 'model'))

        self.populate_button.clicked.connect(self.populate_actor_panel)
        self.tag_as_origin_button.clicked.connect(self.tag_as_origin)

        self.close_btn.clicked.connect(self.close)

        self.all_childs = self.create_childs_array()

        self.export_check.stateChanged.connect(self.setAttributesExport)
        self.move_to_check.stateChanged.connect(self.setAttributesExport)
        self.zero_motion_check.stateChanged.connect(self.setAttributesExport)
        self.use_zero_check.stateChanged.connect(self.setAttributesExport)
        self.use_zero_check.stateChanged.connect(lambda val: self.use_sub_range_widgets(val))

        self.start_spin.valueChanged.connect(self.setSpinAttribute)
        self.end_spin.valueChanged.connect(self.setSpinAttribute)
        self.model_new_export_node_button.clicked.connect(self.create_model_export_node)
        self.model_meshes_node_button.clicked.connect(self.add_selected_meshes)

        self.record_layers_btn.clicked.connect(self.anim_layer_method)
        self.preview_layers_btn.clicked.connect(self.anim_layer_method)
        self.clear_layers_btn.clicked.connect(self.anim_layer_method)

        self.export_selected_btn.clicked.connect(lambda :self.setup_export_process(keyword='animation'))
        self.model_export_selected_button.clicked.connect(lambda :self.setup_export_process(keyword='model'))
        self.exportSetup_btn.clicked.connect(lambda : self.setup_export_process(keyword=None))

        self.export_all_from_all_btn.clicked.connect(lambda : self.export_all_buttons(keyword='animation'))
        self.model_export_all_button.clicked.connect(lambda : self.export_all_buttons(keyword='model'))

        self.exportSignal.connect(lambda val: self.exporting_procedure(val))

        cmds.select(clear=True)
        self.deactivate_UI_widgets()

        to_send = partial(cleanData , self.instances_dictionary)
        self.destroyed.connect(to_send)

        ##################################################################
        # context menus
        #
        self.list_view_wgt_01.setContextMenuPolicy(qc.Qt.CustomContextMenu)
        self.model_list_view_wgt_03.setContextMenuPolicy(qc.Qt.CustomContextMenu)

        self.list_view_wgt_01.customContextMenuRequested.connect(lambda pos : self.context_menu_clear_all(pos))
        self.model_list_view_wgt_03.customContextMenuRequested.connect(lambda pos : self.context_menu_remove_mesh(pos))

        #self._timer.timeout.connect(self.off_covering)

        ###################################################################################################################
        # callBaacks:::
        #
        """
        self._before_export_callBackID = om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeExport,self.exportCoverMaker)
        _before_export_delCallBack = partial(om.MMessage.removeCallback,self._before_export_callBackID)
        self.destroyed.connect(_before_export_delCallBack)


    ######################################################################################

    def off_covering(self):
        self.exportCoverMaker(exporting=False, before=False)


    def exportCoverMaker(self,exporting=True, before=True):

        if exporting:
            self.layout().setCurrentIndex(1)
            self.exportingCover.setStyleSheet(self.cover_css)
            self._timer.start()


        if not exporting:
            self.layout().setCurrentIndex(0)
            self.exportingCover.setText('')
            self.exportCounter = 1
            self.exportingCover.setStyleSheet("background-color: transparent;")

        if before:
            self.layout().setCurrentIndex(1)
            lenght = len(self.current_export_data)
            self.exportingCover.setStyleSheet(self.cover_css)
            print (lenght)
            try:
                zeroIndex = self.current_export_data.pop(0)
                current = zeroIndex[0]
                tipo = zeroIndex[1]

                current_text = "Current {}:\n\t\t{}\n\t\t\t\tProcess {} of {} , please wait ... ".format(current, tipo.capitalize(),self.exportCounter, lenght)

                self.exportingCover.setText(current_text)
            except:
                pass
            self.exportCounter += 1
            self._timer.start()"""




    #####################################################################################

    def export_all_buttons(self, keyword):

        for key, val in self.instances_dictionary.items():
            instance = val

            export_node = instance.current_exportNodes.get(keyword)

            if export_node:
                filename = cmds.getAttr(export_node + ".exportName")
                if filename:

                    if keyword == 'animation':
                        instance.exportFBXAnimation(export_node)

                    if keyword == 'model':
                        instance.exportFBXCharacter(export_node)
                else:
                    om.MGlobal.displayWarning(' - {} Skippet , No Filename Found On Export Node'.format(key))

    ######################################################################################
    def create_modalDialog(self, width, height, buttons=True, text=''):
        modal = modal_dialog(width,height)
        modal.setParent(self)
        modal.setWindowModality(qc.Qt.ApplicationModal)

        label_01 = qg.QLabel(text)
        label_01.setAlignment(qc.Qt.AlignCenter)
        css = """QLabel{
                color : rgba(225,40,40,250);
                font: bold 14px;
                font-family: Calibri;

                }"""

        label_01.setStyleSheet(css)


        modal.frame.layout().addWidget(label_01)
        modal.setGeometry((self.width()  / 2) - (modal.width() / 2), ((self.height() / 2) - modal.height() / 2), width, height)

        if buttons:
            btn = button.Customflat_btn('Accept')
            modal.frame.layout().addWidget(btn)
            btn.clicked.connect(lambda: modal.close())

        return modal

    ######################################################################################
    def exporting_procedure(self, val):
        if val:
            #self.exportCoverMaker(exporting=True, before=True)
            om.MGlobal.displayWarning(' - Starting Export Procedure Please Wait . . .')

            for idx,item in enumerate(self.current_export_deque):
                #self.current_export_data.append(item)
                if item[1] == 'animation':
                    item[2].exportFBXAnimation(item[-1])


                elif item[1] == 'model':
                    item[2].exportFBXCharacter(item[-1])

        self.current_export_deque = []

    ######################################################################################
    def setup_export_process(self, keyword):
        current = self.list_view_wgt_01.currentItem()

        if current is None:
            return

        exportNode,instance = self.getInstances(current, keyword)
        if exportNode is not None:

            if keyword == 'model':

                filename = cmds.getAttr(exportNode + ".exportName")
                if filename:
                    self.current_export_deque.append([current, keyword, instance, exportNode])
                else:
                    cmds.warning("No File Path Set For Export")

            elif keyword == 'animation':

                filename = cmds.getAttr(exportNode + ".exportName")
                if filename:
                    self.current_export_deque.append([current, keyword, instance, exportNode])
                else:
                    cmds.warning("No File Path Set For Export")


        if keyword is None:
            if len(instance.current_exportNodes) > 0:

                for key,val in instance.current_exportNodes.items():
                    if key == 'model':
                        filename = cmds.getAttr(val + ".exportName")
                        if filename:
                            self.current_export_deque.append([current, 'model', instance, val])
                        else:
                            pass

                    elif key == 'animation':

                        filename = cmds.getAttr(val + ".exportName")
                        if filename:
                            self.current_export_deque.append([current, 'animation', instance, val])
                        else:
                            pass


        # emits the signals to beggin
        self.exportSignal.emit(True)

    ######################################################################################
    def enable_setup_button(self):
        current = self.list_view_wgt_01.currentItem()
        if current is None:
            return

        export_node_model, instance = self.getInstances(current, 'model')
        export_node_animation, _ = self.getInstances(current, 'animation')

        if export_node_model and export_node_animation != None:

            model_file_val = cmds.getAttr(export_node_model + ".exportName")
            anim_file_val = cmds.getAttr(export_node_animation + ".exportName")

            if model_file_val and anim_file_val != None:
                self.exportSetup_btn.setEnabled(True)

            else:
                self.exportSetup_btn.setEnabled(False)

        else:
            self.exportSetup_btn.setEnabled(False)


     ######################################################################################
    def getInstances(self, currentSelection, key):

        instance = self.instances_dictionary[currentSelection.text()]
        exportNode = ''
        try:
            exportNode = instance.current_exportNodes.get(key)
            return (exportNode  , instance)
        except:
            exportNode = None
            return exportNode

    ######################################################################################
    def anim_layer_method(self):
        sender = self.sender()

        current = self.list_view_wgt_01.currentItem()
        if current is None:
            return

        instance = self.instances_dictionary[current.text()]
        exportNode = ''
        try:
            exportNode = instance.current_exportNodes['animation']
        except:
            exportNode = None

        if exportNode is not None:
            ##################################################
            if sender == self.record_layers_btn:
                if sender.isChecked():
                    print(True)

            elif sender == self.preview_layers_btn:
                instance.setAnimLayersFromSettings(exportNode)


            elif sender == self.clear_layers_btn:
                instance.clearAnimLayerSettings(exportNode)


    ######################################################################################
    def use_sub_range_widgets(self, value):
        self.start_spin.setEnabled(value)
        self.end_spin.setEnabled(value)

    ######################################################################################
    def add_selected_meshes(self):
        selection = cmds.ls(sl=True)
        current = self.list_view_wgt_01.currentItem()
        if current is None:
            return

        instance = self.instances_dictionary[current.text()]
        meshes = instance.current_meshes
        for item in selection:
            meshes.append(item)

        self.populate_all_panels(current)

    ######################################################################################

    def context_menu_clear_all(self, position):
        sender = self.list_view_wgt_01
        itemAt = sender.itemAt(position)
        current_char = sender.currentItem()

        if itemAt is None:
            return

        if current_char:
            instance  = self.instances_dictionary[current_char.text()]

            menu = Context_FBX_Menu()
            resetAction = qg.QAction(' Reset Export Settings ', menu)
            menu.addAction(resetAction)

            deleteChar = qg.QAction(' Remove Character ', menu)
            menu.addAction(deleteChar)

            resetAction.triggered.connect( lambda : self.clear_all_action(instance))
            deleteChar.triggered.connect( lambda : self.remove_character(instance, itemAt, position ))

            menu.exec_(sender.mapToGlobal(position))

    ######################################################################################
    def set_UI_to_none(self):
        counter = self.list_view_wgt_01.count()
        if counter == 0:
            self.list_view_wgt_02.clear()
            self.export_name_le.clear()
            self.model_export_name_le.clear()
            self.model_list_view_wgt_03.clear()
            self.start_spin.setValue(self.start_spin.minimum())
            self.end_spin.setValue(self.end_spin.minimum())
            self.record_layers_btn.setChecked(True)
            self.move_to_check.setChecked(False)
            self.zero_motion_check.setChecked(False)
            self.use_zero_check.setChecked(False)
            self.start_spin.clearFocus()
            self.end_spin.clearFocus()
            self.model_export_name_le.clearFocus()
            self.export_name_le.clearFocus()

    ######################################################################################
    def context_menu_remove_mesh(self, position):
        sender = self.model_list_view_wgt_03
        itemAt = sender.itemAt(position)
        current_char = self.list_view_wgt_01.currentItem()
        meshes = ''

        if current_char:
            instance  = self.instances_dictionary[current_char.text()]
            meshes = instance.current_meshes

            if itemAt is None:
                return

            menu = Context_FBX_Menu()
            removeAction = qg.QAction(' Remove Mesh ', menu)
            menu.addAction(removeAction)
            removeAction.triggered.connect(lambda: self.remove_current_mesh(instance, itemAt))

            menu.exec_(sender.mapToGlobal(position))
    #######################################################################################
    def remove_current_mesh(self, instance, item):
        curItem = item.text()
        #model = self.model_list_view_wgt_03.model()
        characterName = item.text()

        # takes the item and delete it
        index = self.model_list_view_wgt_03.row(item)
        self.model_list_view_wgt_03.takeItem(index)
        self.model_list_view_wgt_03.removeItemWidget(item)
        #model.removeRow(index)

        meshes_array = instance.current_meshes
        if curItem in meshes_array: meshes_array.remove(curItem)

        print(meshes_array)



    #######################################################################################
    def clear_all_action(self, instance):
        instance.delete_all_data()
        self.populate_all_panels(self.list_view_wgt_01.currentItem())
        self.update_exportCheck()
        print('All Current Export Data Deleted')

    #######################################################################################
    def remove_character(self, instance, itemWidget, pos):

        self.clear_all_action(instance)
        # data for remove the item
        #model = self.list_view_wgt_01.model()
        characterName = itemWidget.text()
        # takes the item and delete it
        index = self.list_view_wgt_01.row(itemWidget)
        self.list_view_wgt_01.takeItem(index)
        self.list_view_wgt_01.removeItemWidget(itemWidget)
        #model.removeRow(index)

        # remove from the UI DICTIONARY
        # AND DELETE THE INSTANCE
        del(instance)

        key = self.instances_dictionary.pop(characterName, None)
        actor= self.actors_dictionary.pop(characterName, None)
        del (key)
        del (actor)
        # # # # # #

        #######################################################

        counter = self.list_view_wgt_01.count()
        if counter > 0:
            item = self.list_view_wgt_01.row(1)
            self.list_view_wgt_01.setCurrentRow(1)
            self.list_view_wgt_01.setCurrentItem(item, qg.QItemSelectionModel.select)
        else:
            self.set_UI_to_none()

        print('Character: {} Removed'.format(characterName))
        self.enable_setup_button()


    #######################################################################################
    def browser_widgets(self, lineEdit, exportNode):
        selected = self.list_view_wgt_01.selectedItems()

        if len(selected)  >  0:
            instance = self.instances_dictionary[self.list_view_wgt_01.currentItem().text()]
            dictionary = instance.current_exportNodes
            export_node = False
            try:
                export_node = dictionary[exportNode]
            except:
                pass

            if export_node:
                # get the route to the path
                project_path = cmds.workspace(q=True, rd=True)
                fileList = cmds.fileDialog2(fileMode = 0, startingDirectory = project_path, fileFilter= "FBX export (*.fbx)", okCaption="Save", caption="Colt FBX Browser")

                # update the line edit
                if fileList is not None:
                    lineEdit.setText(fileList[0])

                    #update the export node
                    cmds.setAttr(export_node + '.exportName', str(lineEdit.text()), type = "string" )
                    self.enable_setup_button()

                else:
                    lineEdit.setText('None')

            else:
                modal = self.create_modalDialog(255,95 , True, 'Create an Export Node From Origin First')
                modal.exec_()

    #######################################################################################
    def update_exportCheck(self):
        selected = self.list_view_wgt_01.selectedItems()

        if len(selected)  >  0:
            instance = self.instances_dictionary[self.list_view_wgt_01.currentItem().text()]
            dictionary = instance.current_exportNodes

            try:
                anim_node = dictionary['animation']
                if anim_node:
                    self.export_check.setEnabled(True)
            except:
                self.export_check.setEnabled(False)
            ############

            try:
                model_node = dictionary['model']
                if model_node:
                    self.model_export_check.setEnabled(True)
            except:
                self.model_export_check.setEnabled(False)
            ############

    #######################################################################################
    def create_model_export_node(self):
        if self.model_list_view_wgt_01.count() == 0:
            return

        instance = self.instances_dictionary[self.list_view_wgt_01.currentItem().text()]
        characterName = self.list_view_wgt_01.currentItem().text()
        selected = self.model_list_view_wgt_01.selectedItems()

        if len(selected)  >  0:
            origin = selected[0].text()
            exportNode = instance.createFBXExportNode(characterName, 'model')
            # 1 - export node - 2 - origin
            if exportNode is None:
                return

            instance.connectFBXExportNodeToOrigin(exportNode, origin)

        else:
            modal = self.create_modalDialog(255,95 , True, 'Select a Joint from Origin List First')
            modal.exec_()


        self.update_exportCheck()
        self.populate_all_panels(self.list_view_wgt_01.currentItem())

    #######################################################################################
    def deactivate_UI_widgets(self):

        if self.list_view_wgt_01.count() == 0:
            self.stack_layout.setCurrentIndex(1)
            for widget in self.all_childs.values():
                widget.setAttribute(qc.Qt.WA_TransparentForMouseEvents)

            self.populate_button.setAttribute(qc.Qt.WA_TransparentForMouseEvents, on=False)
            self.close_btn.setAttribute(qc.Qt.WA_TransparentForMouseEvents, on=False)

        if self.list_view_wgt_01.count() > 0:
            self.stack_layout.setCurrentIndex(0)

            for widget in self.all_childs.values():
                widget.setAttribute(qc.Qt.WA_TransparentForMouseEvents, on=False)


    #######################################################################################
    def update_export_model_check(self):
        item = self.sender()
        if not item.isEnabled():
            return

        name = item.text()

        instance = self.instances_dictionary[self.list_view_wgt_01.currentItem().text()]
        model_node = instance.current_exportNodes['model']

        cmds.setAttr(model_node + '.' + name.lower() , int(item.isChecked()))


    #######################################################################################
    @undo
    def update_attribute(self, node, attribute, value):
        cmds.setAttr(node +'.'+ attribute, int(value))

    #######################################################################################
    def setSpinAttribute(self):
        current_item = self.list_view_wgt_01.currentItem()

        if current_item is None:
            return

        instance = self.instances_dictionary[self.list_view_wgt_01.currentItem().text()]
        currentExportNode = instance.current_exportNodes['animation']
        objecto = self.sender()
        self.update_attribute(currentExportNode , objecto.objectName(), objecto.value())

    #######################################################################################

    def setAttributesExport(self):
        current_item = self.list_view_wgt_01.currentItem()

        if current_item is None:
            return

        instance = self.instances_dictionary[self.list_view_wgt_01.currentItem().text()]
        currentExportNode = instance.current_exportNodes['animation']
        objecto = self.sender()
        self.update_attribute(currentExportNode , objecto.objectName(), objecto.isChecked())

    #######################################################################################
    def update_export_values(self):
        instance = self.instances_dictionary[self.list_view_wgt_01.currentItem().text()]
        currentExportNode = instance.current_exportNodes['animation']
        # get the names first
        export = '.export'
        moveToOrigin = '.moveToOrigin'
        zeroOrigin = '.zeroOrigin'
        useSubRange = '.useSubRange'
        startFrame = '.startFrame'
        endFrame = '.endFrame'

        # get the attribtues second
        self.export_check.setChecked(cmds.getAttr(currentExportNode + export))
        self.move_to_check.setChecked(cmds.getAttr(currentExportNode + moveToOrigin))
        self.zero_motion_check.setChecked(cmds.getAttr(currentExportNode + zeroOrigin))
        self.use_zero_check.setChecked(cmds.getAttr(currentExportNode + useSubRange))
        self.start_spin.setValue(int(cmds.getAttr(currentExportNode + startFrame)))
        self.end_spin.setValue(int(cmds.getAttr(currentExportNode + endFrame)))

        ######################################
        #
        export_anim = '.exportName'
        self.export_name_le.setText(str(cmds.getAttr(currentExportNode + export_anim)))

        curr_modelExportNode = instance.current_exportNodes['model']
        export_model = '.exportName'
        self.model_export_name_le.setText(str(cmds.getAttr(curr_modelExportNode + export_anim)))
        self.enable_setup_button()


    #######################################################################################
    def tag_as_origin(self):
        selected = self.list_view_wgt_01.selectedItems()
        selected_02 = self.list_view_wgt_02.selectedItems()

        if len(selected) and len(selected_02) >  0:
            instance = self.instances_dictionary[self.list_view_wgt_01.currentItem().text()]


            instance.tagForOrigin(self.list_view_wgt_02.currentItem().text(), self.list_view_wgt_01.currentItem().text())

            self.populate_all_panels(self.list_view_wgt_01.currentItem())

    #######################################################################################
    def populate_all_panels(self, item):
        FBX_Exporter = self.instances_dictionary[item.text()]
        data = FBX_Exporter.current_character_data

        # root joints panel
        self.create_list_items(data[1], self.list_view_wgt_02)

        # export Nodes
        self.export_node_panel(FBX_Exporter)

        # origin current joint
        current_origin = [FBX_Exporter.current_origin]

        if current_origin[0] is  None:
            current_origin = []
            self.create_list_items(current_origin, self.model_list_view_wgt_01)

        elif current_origin[0] is not None:
            self.create_list_items(current_origin, self.model_list_view_wgt_01)


        # meshes  panel
        self.create_list_items(FBX_Exporter.current_meshes, self.model_list_view_wgt_03)

        # export anim panel values
        try:
            self.update_export_values()
        except:
            pass

        self.update_exportCheck()
        self.enable_setup_button()

    #######################################################################################
    def export_node_panel(self, instance):
        exportNode_dic = instance.current_exportNodes
        exportNodes = []
        for key, val in exportNode_dic.items():
            exportNodes.append(val)


        if len(exportNodes) > 0:
            self.create_list_items(exportNodes, self.model_list_view_wgt_02)

        else:
            self.create_list_items([], self.model_list_view_wgt_02)

    #######################################################################################
    def create_list_items(self, data, widget):
        origin = ''
        try:
            instance = self.instances_dictionary[self.list_view_wgt_01.currentItem().text()]
            origin = instance.current_origin
        except:
            origin = ''


        model = widget.model()
        def item_remover():
            count = widget.count()
            for idx in range(count):
                item = widget.takeItem(idx)
                index = widget.row(item)
                widget.removeItemWidget(item)
                model.removeRow(index)
                del(item)
                if widget.count() > 0:
                    item_remover()

        item_remover()

        for itm in data:
            name = str(itm)
            item = qg.QListWidgetItem(name)

            if name == origin:
                item.setBackground( qg.QColor(225,40,40,75))

            widget.addItem(item)

    ################################################
    def populate_actor_panel(self):
        selection = cmds.ls(sl=True)
        if len(selection) == 0:
            return

        MAIN = selection[0]

        FBX_Exporter = FBX_Exporter_logic.FBX_ExporterClass()
        data = FBX_Exporter.get_nodes_in_proccess(MAIN)
        root_folder = data[0][0]

        if root_folder in self.actors_dictionary.keys():
            return

        for itm in data[0]:
            name = str(itm)
            item = qg.QListWidgetItem(name)
            self.list_view_wgt_01.addItem(item)

        self.actors_dictionary[root_folder] = selection[0]
        self.instances_dictionary[root_folder] = FBX_Exporter
        self.deactivate_UI_widgets()


    ###############################################
    def create_childs_array(self):
        widgets = self.findChildren(qg.QPushButton)
        widgets.extend(self.findChildren(qg.QSpinBox))
        widgets.extend(self.findChildren(qg.QCheckBox))
        widgets.extend(self.findChildren(qg.QLineEdit))
        dict_to = {}

        for item in widgets:
            name = item.objectName()
            #print("'%s',")%(name)
            dict_to[name] = item

        return dict_to

    #####################################################################################

    def resizeEvent(self, event):

        pixmap = qg.QPixmap(self.size())
        pixmap.fill(qc.Qt.transparent)
        painter = qg.QPainter(pixmap)
        painter.setBrush(qc.Qt.black)
        painter.drawRoundedRect(pixmap.rect(), 12, 12)
        painter.end()

        self.setMask(pixmap.mask())
        self.exportSetup_btn.move((self.width() - self.exportSetup_btn.width() ) - 25, (self.height() - self.exportSetup_btn.height() ) - 35  )

    def mouseMoveEvent(self, event):
        super(Colt_FBX_Export, self).mouseMoveEvent(event)
        if self.leftClick == True:
            self.move(event.globalPos().x()-X-X2,event.globalPos().y()-Y-Y2)
            event.accept()

    def mousePressEvent(self, event):
        super(Colt_FBX_Export, self).mousePressEvent(event)
        if event.button() == qc.Qt.LeftButton:
            self.leftClick = True
            global X,Y
            X=event.pos().x()
            Y=event.pos().y()
            event.accept()

    def mouseReleaseEvent(self, event):
        super(Colt_FBX_Export, self).mouseReleaseEvent(event)
        self.leftClick = False

    def showEvent(self, event):

        event.accept()
        return True


    def closeEvent(self,event):
        deleteFromGlobal(self.objectName())
        global FBX_GLOBAL
        FBX_GLOBAL = None

#############################################################################################################
#
#
listWi_css = """QListWidget{
                    font-family: Calibri;
                    font: bold 14px;
                    background : qlineargradient(x1:0, y1:0, x2:0, y2:0, stop:0.0 rgba(53, 57, 60,125),
                                                          stop:0.5 rgba(33, 34, 36,150),stop:1 rgba(53, 57, 60,125));

                }

                QListWidget::item:selected
                {
                    color : rgba(150,225,100,255);
                    background-color: rgba(255, 255, 255,25);


                }"""

class ListWidgetFBX(qg.QListWidget):

    def __init__(self, *args, **kwargs):
        super(ListWidgetFBX, self).__init__( *args, **kwargs)
        self.setFont(FONT)

        self.setObjectName('listView_import')

        self.setStyleSheet(listWi_css)
        self.setWordWrap(True)
        self.setUpdatesEnabled(True)
        self.setFocusPolicy(qc.Qt.NoFocus)

        self.setResizeMode(qg.QListWidget.Adjust)
        self.setContextMenuPolicy(qc.Qt.CustomContextMenu)


    def mousePressEvent(self, event):
        super(ListWidgetFBX, self).mousePressEvent(event)
        self.setSelectionMode(qg.QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(qg.QAbstractItemView.NoDragDrop)
        if event.button() == qc.Qt.LeftButton:
            if self.itemAt(event.pos()) is None:
                self.clearSelection()
                self.clearFocus()
            event.accept()

        if event.button() == qc.Qt.RightButton:

            if self.itemAt(event.pos()) is None:
                self.clearSelection()
                self.clearFocus()

            event.accept()




#---------------------------------------------------------------------------------#
CSSMENU = """QMenu
        {
            background : qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgb(53, 57, 60), stop:1 rgb(33, 34, 36));
            shadow : rgb(9, 10, 12);
            border: 1px solid rgb(9, 10, 12);
            border-radius: 2px;
            padding-top : 2px;
            padding-bottom : 2px;
            padding-left : 0px;
            padding-right : 0px;
            color : rgba(202, 207, 210, 255);

        }


        QMenu::item:selected
        {
            color : rgba(150,225,100,255);
            background-color: rgba(255, 255, 255,25);
        }"""



##########################################################################################################
class Context_FBX_Menu(qg.QMenu):
    def __init__(self):
        super(Context_FBX_Menu, self).__init__()
        self.setStyleSheet(CSSMENU)
        self.setObjectName('Context_FBX_Menu')


    ###############################################################################

    def leaveEvent(self, event):
        self.close()
        self.deleteLater()
        del(self)


#---------------------------------------------------------------------------------#
class modal_dialog(qg.QDialog):
    leftClick = False
    def __init__(self, WIDTH ,HEIGHT):
        super(modal_dialog, self).__init__()

        self.setLayout(qg.QVBoxLayout(self))
        self.layout().setContentsMargins(0,0,0,0)
        self.setFixedWidth(WIDTH)
        self.setFixedHeight(HEIGHT)

        self.setAttribute(qc.Qt.WA_DeleteOnClose)
        self.setModal(True)

        css_internal = """QDialog{
            background-color : rgba(35, 36, 38,255);
            shadow : rgb(9, 10, 12);
            border: 1px solid rgb(9, 10, 12);
            border-radius: 12px;
            }"""

        self.setStyleSheet(css_internal)

        self.frame = qg.QFrame()
        self.frame.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)
        self.frame.setObjectName('modal_frame')

        self.layout().addWidget(self.frame)
        self.frame.setStyleSheet("""QFrame#modal_frame { background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.0 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(85, 87, 90,200), stop: 0.5 rgba(25,15,05,25), stop: 1.0 rgba(33, 34, 36, 200))};""")

        frame_lyt = qg.QVBoxLayout(self.frame)
        frame_lyt.setContentsMargins(0,0,0,0)


    def resizeEvent(self, event):

        pixmap = qg.QPixmap(self.size())
        pixmap.fill(qc.Qt.transparent)
        painter = qg.QPainter(pixmap)
        painter.setBrush(qc.Qt.black)
        painter.drawRoundedRect(pixmap.rect(), 12, 12)
        painter.end()

        self.setMask(pixmap.mask())


    def closeEvent(self,event):
        self.deleteLater()
        del (self)




#################################################################################################################
def FBX_Run():
    deleteFromGlobal(MAINOBJNAME)
    global FBX_GLOBAL
    if FBX_GLOBAL is None:
        FBX_GLOBAL = Colt_FBX_Export()
        FBX_GLOBAL.setAttribute(qc.Qt.WA_DeleteOnClose)
        FBX_GLOBAL.show()


#################################################################################################################
if __name__ == '__main__':
    FBX_Run()

