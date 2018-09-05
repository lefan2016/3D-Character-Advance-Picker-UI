# -*- coding: utf-8 -*-
try:
    import maya.cmds       as cmds
    import pymel.core      as pm
    import maya.OpenMaya   as om
    import maya.OpenMayaUI as mui
    import shiboken        as shi
    from HitchAnimationModule.Widgets    import button
    from HitchAnimationModule.Widgets    import checkBox
    from HitchAnimationModule.Widgets    import lineEdit
    from HitchAnimationModule.Widgets    import spliter
    from HitchAnimationModule.Widgets    import label
    from HitchAnimationModule.SubClasses import ComboColt
    from HitchAnimationModule.LogicData import OperationsFile; reload(OperationsFile)
    from HitchAnimationModule.ControlList import ControlList; reload(ControlList)
    from HitchAnimationModule.LogicData import ConnectControls
    from HitchAnimationModule.LogicData import refreshUI

except: pass
###############################
from PySide import QtCore as qc
from PySide import QtGui as qg
from PySide.QtCore import Signal
from functools import partial
import copy
from contextlib import contextmanager

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
def noSignals(obj):
    obj.blockSignals(True)
    yield
    obj.blockSignals(False)
#------------------------------------------------------------------------------------------------------------#

class TopPanel(qg.QFrame):
    nameSpaceSignal = qc.Signal(list)

    def __init__(self):
        super(TopPanel, self).__init__()

        self.setLayout(qg.QHBoxLayout())
        self.setObjectName('topFrame')
        self.setStyleSheet("""#topFrame {background : qlineargradient(x1:0, y1:0, x2:0, y2:0, stop:0.0 rgba(53, 57, 60,125),
         stop:0.5 rgba(33, 34, 36,150),stop:1 rgba(53, 57, 60,125))};""")
        self.setFrameStyle(qg.QFrame.Raised)
        self.setFixedHeight(100)
        self.layout().setAlignment(qc.Qt.AlignVCenter)
        self.layout().setContentsMargins(2,5,2,5)

        ##############################################
        # Operatios RIG class
        #
        self.OperationsRig = OperationsFile.Operations()
        self.face = ControlList.FACECONTROLS
        self.body = ControlList.BODYCONTROLS

        self._scene = refreshUI.resetScene()


        #############################
        #
        firstLeftWidget = qg.QWidget()
        firstLeftWidget.setMaximumWidth(450)
        firstLeftWidget.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)
        leftPanel_lyt = qg.QVBoxLayout(firstLeftWidget)
        self.layout().addWidget(firstLeftWidget)

        ##############################
        # Name space field
        #
        namespace_lyt = qg.QHBoxLayout()
        self.nameSpace_le = lineEdit.SpecialLineEdit()
        self.nameSpace_le.setSizePolicy(qg.QSizePolicy.Expanding,qg.QSizePolicy.Minimum)
        self.nameSpace_le.setPlaceholderMessage(' Name Space Here ')
        reg_ex = qc.QRegExp("^(?!^_)[a-zA-Z0-9_:]+")
        textValidator = qg.QRegExpValidator(reg_ex,self.nameSpace_le)
        self.nameSpace_le.setValidator(textValidator)

        nameSpaceLabel = label.CustomLabel(' Name Space: ')
        nameSpaceLabel.setObjectName('nameSpaceLineEdit')
        self.nameSpace_le.setEnabled(False)
        self.nameSpace_chbox = checkBox.CustomRedCheck(' Enable ')
        self.nameSpace_chbox.setObjectName('nameSpaceCheckbox')

        namespace_lyt.addWidget(nameSpaceLabel)
        namespace_lyt.addWidget(self.nameSpace_le)
        namespace_lyt.addWidget(self.nameSpace_chbox)
        leftPanel_lyt.addLayout(namespace_lyt)

        ###################################
        # Space Switch field
        #
        spaceSitch_lyt = qg.QHBoxLayout()
        spaceSitch_lyt.setContentsMargins(0,0,0,0)
        spaceSitch_lyt.setSpacing(0)

        self.spaceSwitch_combo = ComboColt.ComboColt()

        self.spaceSwitch_combo.setSizePolicy(qg.QSizePolicy.Expanding,qg.QSizePolicy.Minimum)
        spaceSwitch_btn = button.CustomButton(' Match ')
        spacer = qg.QSpacerItem(6,0)

        SpaceSwitchLabel = label.CustomLabel('Switch Space: ')
        spaceSitch_lyt.addWidget(SpaceSwitchLabel)
        spaceSitch_lyt.addWidget(self.spaceSwitch_combo)
        spaceSitch_lyt.addSpacerItem(spacer)
        spaceSitch_lyt.addWidget(spaceSwitch_btn)

        leftPanel_lyt.addLayout(spaceSitch_lyt)


        #######################################
        # Middle splitter separator decorator
        #
        splite = spliter.SplitterVLayout()
        self.layout().addLayout(splite)

        #######################################
        # Horizontal splitter separator decorator
        #
        CrossWidget = CustomCrossWidget()
        rigth_Side_layout = qg.QVBoxLayout(CrossWidget)
        rigth_Side_layout.setContentsMargins(0,0,0,0)
        self.layout().addWidget(CrossWidget)

        operations_1st_row_lyt = qg.QHBoxLayout()
        operations_1st_row_lyt.setContentsMargins(2,0,2,0)
        operations_2nd_row_lyt = qg.QHBoxLayout()
        operations_2nd_row_lyt.setContentsMargins(2,0,2,0)

        rigth_Side_layout.addLayout(operations_1st_row_lyt)
        rigth_Side_layout.addLayout(operations_2nd_row_lyt)

        #############################
        # Mirror Zone operation
        #
        mirror_lyt = qg.QHBoxLayout()
        mirrorButton = button.CustomButton(' Mirror ')
        mirrorButton.setMaximumWidth(200)
        self.mirror_left_chckBox = checkBox.CustomCheck('Left')
        self.mirror_rigth_chckBox = checkBox.CustomCheck('Rigth')
        mirror_lyt.addWidget(mirrorButton)
        mirror_lyt.addWidget(self.mirror_left_chckBox)
        mirror_lyt.addWidget(self.mirror_rigth_chckBox)
        operations_1st_row_lyt.addLayout(mirror_lyt)

        self.mirror_left_chckBox.setSizePolicy(qg.QSizePolicy.Maximum,qg.QSizePolicy.Minimum)
        self.mirror_rigth_chckBox.setSizePolicy(qg.QSizePolicy.Maximum,qg.QSizePolicy.Minimum)

        #############################
        # Flip Zone operation
        #
        flip_lyt = qg.QHBoxLayout()
        flipButton = button.CustomButton(' Flip ')
        flipButton.setMaximumWidth(225)
        self.keycycle_chckBox = checkBox.CustomRedCheck('KeyCycle')
        flip_lyt.addWidget(flipButton)
        flip_lyt.addWidget(self.keycycle_chckBox)
        operations_1st_row_lyt.addLayout(flip_lyt)

        self.keycycle_chckBox.setSizePolicy(qg.QSizePolicy.Maximum,qg.QSizePolicy.Minimum)

        #############################
        # Reset Zone operation
        #
        resetHztal_lyt = qg.QHBoxLayout()
        resetButton = button.CustomButton(' Reset ')
        resetButton.setMaximumWidth(310)
        resetHztal_lyt.addWidget(resetButton)
        operations_2nd_row_lyt.addLayout(resetHztal_lyt)

        #############################
        # Visibility Zone operation
        #
        visibilityHztal_lyt = qg.QHBoxLayout()
        visibilityButton = button.CustomButton(' Visibility ')
        visibilityButton.setMaximumWidth(310)
        visibilityHztal_lyt.addWidget(visibilityButton)
        operations_2nd_row_lyt.addLayout(visibilityHztal_lyt)

        #######################################
        # Rightsplitter separator decorator
        #
        spliterRight = spliter.SplitterVLayout()
        self.layout().addLayout(spliterRight)
        ########################################
        # Face and body selectors
        #
        selectors_lyt = qg.QVBoxLayout()
        selectors_lyt.setContentsMargins(0,0,10,0)
        self.face_chckBox = checkBox.CustomCheck(' Face Controls ')
        self.body_chckBox = checkBox.CustomCheck(' Body Controls ')
        self.showHide_chckBox = checkBox.CustomCheck(' Show / Hide ')
        selectors_lyt.addWidget(self.face_chckBox)
        selectors_lyt.addWidget(self.body_chckBox)
        selectors_lyt.addWidget(self.showHide_chckBox)

        self.face_chckBox.setSizePolicy(qg.QSizePolicy.Maximum,qg.QSizePolicy.Minimum)
        self.body_chckBox.setSizePolicy(qg.QSizePolicy.Maximum,qg.QSizePolicy.Minimum)
        self.showHide_chckBox.setSizePolicy(qg.QSizePolicy.Maximum,qg.QSizePolicy.Minimum)

        self.showHide_chckBox.setChecked(True)
        self.layout().addLayout(selectors_lyt)
        ########################################################################
        #
        #
        self._toggle = True
        self.mirror_left_chckBox.setChecked(self._toggle)
        self.mirror_rigth_chckBox.setChecked(not self._toggle)
        self.mirror_left_chckBox.clicked.connect(self.toggle)
        self.mirror_rigth_chckBox.clicked.connect(self.toggle)

        # Connections and callbacks from maya API
        #
        self.sel_idx = om.MEventMessage.addEventCallback("SelectionChanged", self.populate_space_list)
        self.callbackkill = partial(om.MMessage.removeCallback, self.sel_idx)

        self.destroy_callback = self.destroyed.connect(self.callbackkill)

        ########################################################################
        #
        #
        self._current_space = None

        #########################################
        # Connections :
        #
        self.nameSpace_chbox.stateChanged.connect(lambda val: self.handle_nameSpace_le(val))

        mirrorButton.clicked.connect(self.manage_naming)
        flipButton.clicked.connect(self.manage_naming)
        resetButton.clicked.connect(self.manage_naming)
        visibilityButton.clicked.connect(self.manage_naming)

        self.spaceSwitch_combo.currentIndexChanged.connect(self.matchSpace)
        spaceSwitch_btn.clicked.connect(lambda: self._go_to_space(self._current_space))

        self.nameSpace_le.editingAccepted.connect(self.set_widgets_to_nameSpace)

    #---------------------------------------------------------------------------------#
    def set_widgets_to_nameSpace(self):
        pickerBody = self._scene.findSceneChilds(qg.QLabel, 'bodyPickerLabel')[0]
        pickerface = self._scene.findSceneChilds(qg.QLabel, 'HeadPicker')[0]

        text = self.nameSpace_le.text()
        prefix = pickerBody.prefix
        if prefix ==  text:
            return

        else:
            self.nameSpaceSignal.emit(self.nameSpace_le)
            getattr(pickerBody,'update_nameSpace')()
            getattr(pickerBody,'create_callbacks')()
            getattr(pickerBody,'updateAllWidgets')()

            getattr(pickerface,'update_nameSpace')()
            getattr(pickerface,'create_callbacks')()
            getattr(pickerface,'updateAllWidgets')()


    #############################################################################
    def handle_nameSpace_le(self, val):
        self.nameSpace_le.setEnabled(val)
        self.nameSpace_le.clear()
        self.nameSpace_le.setReadOnly(False)

        if not self.nameSpace_le.isEnabled():
            pickerBody = self._scene.findSceneChilds(qg.QLabel, 'bodyPickerLabel')[0]
            pickerface = self._scene.findSceneChilds(qg.QLabel, 'HeadPicker')[0]

            self.nameSpaceSignal.emit(self.nameSpace_le)
            getattr(pickerBody,'update_nameSpace')()
            getattr(pickerBody,'create_callbacks')()
            getattr(pickerBody,'updateAllWidgets')()

            getattr(pickerface,'update_nameSpace')()
            getattr(pickerface,'create_callbacks')()
            getattr(pickerface,'updateAllWidgets')()

    ##################################################################################################################################

    def populate_space_list(self, *args , **kwargs ):

        sel = cmds.ls(sl=True)
        data = self.spaceSwitch_combo.spaceSwitch_operation(sel)

        for index in range(self.spaceSwitch_combo.count()):
            self.spaceSwitch_combo.removeItem(0)

        if len(data) < 1:
            return

        else:
            for item in data:
                name = '{} - {} space'.format(item[1], item[-1])
                self.spaceSwitch_combo.addItem(name, userData=(item))

    ##################################################################################################################################

    def manage_naming(self):
        face = copy.copy(self.face)
        body = copy.copy(self.body)

        if not self.nameSpace_le.isReadOnly():
            #try:
            with delete_callbacks():
                self.operations_modules(face,body)

            #except:
                #cmds.warning('Not Matching Name Space Found')

        elif self.nameSpace_le.isReadOnly():
            cara = []
            cuerpo = []
            name = self.nameSpace_le.text()

            for itm in face:
                formato = '{}:{}'.format(name,itm)
                cara.append(formato)

            for itm in body:
                formato = '{}:{}'.format(name,itm)
                cuerpo.append(formato)

            with delete_callbacks():
                self.operations_modules(cara,cuerpo)



    ##################################################################################################################################

    def matchSpace(self, index):
        data = self.spaceSwitch_combo.itemData(index)
        self._current_space = data

    def _go_to_space(self, data):
        with delete_callbacks():
            if data is not None:
                if len(data) > 1:
                    self.spaceSwitch_combo.Space_matching(data)

    def toggle(self):
        self._toggle = not self._toggle
        self.mirror_left_chckBox.setChecked(self._toggle)
        self.mirror_rigth_chckBox.setChecked(not self._toggle)


    def operations_modules(self, face, body):
        channelBox = self._scene.findSceneChilds(qg.QFrame, 'ChannelBoxColt')[0]

        # This var is a list to pass to the Method
        Sel_list = cmds.ls(sl=True)
        # Text gives me the name to Match ------------------#
        text = self.sender().text()
        # ------------------------#
        #checkers:
        faceCheck = self.face_chckBox.isChecked()
        bodyCheck = self.body_chckBox.isChecked()
        keycycle  = self.keycycle_chckBox.isChecked()
        visiCheck = self.showHide_chckBox.isChecked()
        # have 3 ways of getting the class instance methods into a list to iterate ..
        method_list = [func for func in dir(self.OperationsRig) if callable(getattr(self.OperationsRig, func))]
        # iterate over the "self.OperationsRig" methods
        """ option 1 """
        for meth in method_list:
            if text.strip().lower() in meth.lower()[:]:
                print('Calling " {} " Method'.format(meth))
                if not faceCheck and not bodyCheck:
                    if 'visibility' in meth.lower()[:]:
                        getattr(self.OperationsRig,meth)(Sel_list,check=visiCheck)
                    elif 'mirrorpose' in meth.lower()[:]:
                        getattr(self.OperationsRig,meth)(Sel_list,self._toggle)
                    elif 'flippose' in meth.lower()[:]:
                        getattr(self.OperationsRig,meth)(Sel_list, keycycle)
                    else:
                        getattr(self.OperationsRig,meth)(Sel_list)
                if faceCheck  and not bodyCheck:
                    if 'visibility' in meth.lower()[:]:
                        getattr(self.OperationsRig,meth)(face,check=visiCheck)
                    elif 'mirrorpose' in meth.lower()[:]:
                        getattr(self.OperationsRig,meth)(face,self._toggle)
                    elif 'flippose' in meth.lower()[:]:
                        getattr(self.OperationsRig,meth)(face, keycycle)
                    else:
                        getattr(self.OperationsRig,meth)(face)
                if not faceCheck and bodyCheck:
                    if 'visibility' in meth.lower()[:]:
                        getattr(self.OperationsRig,meth)(body,check=visiCheck)
                    elif 'mirrorpose' in meth.lower()[:]:
                        getattr(self.OperationsRig,meth)(body,self._toggle)
                    elif 'flippose' in meth.lower()[:]:
                        getattr(self.OperationsRig,meth)(body, keycycle)
                    else:
                        getattr(self.OperationsRig,meth)(body)
                if faceCheck and bodyCheck:
                    face.extend(body)
                    if 'visibility' in meth.lower()[:]:
                        getattr(self.OperationsRig,meth)(face,check=visiCheck)
                    elif 'mirrorpose' in meth.lower()[:]:
                        getattr(self.OperationsRig,meth)(face,self._toggle)
                    elif 'flippose' in meth.lower()[:]:
                        getattr(self.OperationsRig,meth)(face, keycycle)
                    else:
                        getattr(self.OperationsRig,meth)(face)
# --------------------------------------------------------------------------------------------------#

class CustomCrossWidget(qg.QFrame):
    penTick = qg.QPen(qg.QColor(35,180,93), 1, qc.Qt.SolidLine)
    def __init__(self):
        super(CustomCrossWidget, self).__init__()
        self.setFrameStyle(qg.QFrame.Raised)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
        painter = qg.QPainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height()
        width = option.rect.width()

        painter.setRenderHint(qg.QPainter.Antialiasing)
        line_path = qg.QPainterPath()
        #------------------- ----------#
        offset_y = 10
        offset_x = 20

        line_path.moveTo( x + offset_x, (height / 2 ))
        line_path.lineTo( width - offset_x, (height / 2 ))
        line_path.moveTo((width / 2), y + offset_y)
        line_path.lineTo( (width / 2), height - offset_y)

        self.penTick.setCapStyle(qc.Qt.RoundCap)
        painter.setPen(self.penTick)
        painter.drawPath(line_path)

