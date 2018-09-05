try:
    import maya.cmds as cmds
    import pymel.core as pm
    import os
    from HitchAnimationModule.Widgets import spliter
    from HitchAnimationModule.Widgets import button
    from HitchAnimationModule.Widgets import label
    from HitchAnimationModule.Tools.Tweener import Tweener
    from HitchAnimationModule.Tools.FBX_Exporter import FBX_UI
    reload(FBX_UI)
    reload(Tweener)

except:
    pass
############
from PySide import QtCore as qc
from PySide import QtGui as qg
from functools import partial
#----------------------------------------------------------------------------------------------------------#
HEADERPIXMAP = os.path.join(pm.internalVar(usd=1), 'HitchAnimationModule', 'Icons', 'hitchNameUIHeaderNoBackground.png')
# ---------------------------------------------------------------------------------------------------------#


class LeftPanel(qg.QFrame):
    def __init__(self):
        super(LeftPanel, self).__init__()
        self.setStyleSheet(""" background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 1.2 ,
                                 fx: 0.5 , fy: 0.5, stop: 0 rgba(53, 57, 60,255), stop: 0.7 rgba(25,15,05,50), stop: 1.1 rgba(33, 34, 36, 255));""")

        self.setObjectName('LeftPanelClass')
        self.setFrameStyle(qg.QFrame.Panel | qg.QFrame.Raised)
        self.setLayout(qg.QVBoxLayout())
        self.setContentsMargins(1, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setFixedWidth(200)
        ##################################
        ######### Pixmap header ##########
        #
        prePixmapSpacer = qg.QSpacerItem(0, 20)
        self.layout().addSpacerItem(prePixmapSpacer)

        headerLabel = qg.QLabel()
        headerLabel.setStyleSheet("background-color: transparent;")
        headerLabel.setFixedWidth(200)

        headerlabel_lyt = qg.QVBoxLayout()
        headerlabel_lyt.setAlignment(qc.Qt.AlignHCenter | qc.Qt.AlignVCenter)
        headerlabel_lyt.setContentsMargins(0, 0, 0, 0)
        headerlabel_lyt.addWidget(headerLabel)
        headerlabel_lyt.setAlignment(qc.Qt.AlignTop)
        self.layout().addLayout(headerlabel_lyt)

        headerPixmap = qg.QPixmap(HEADERPIXMAP)
        myScaledPixmap = headerPixmap.scaled(headerLabel.width(), headerLabel.height(), qc.Qt.KeepAspectRatio)
        headerLabel.setPixmap(myScaledPixmap)

        ###############################
        # Buttons:
        #
        buttonsLayout = qg.QVBoxLayout()
        buttonsLayout.addSpacing(50)
        self.channelBox_btn = button.Customflat_btn('Channel box')
        buttonsLayout.setAlignment(qc.Qt.AlignTop)
        buttonsLayout.addWidget(self.channelBox_btn)
        self.layout().addLayout(buttonsLayout)

        AnimationEditor_btn = button.Customflat_btn('Graph Editor')
        buttonsLayout.addWidget(AnimationEditor_btn)
        AnimationEditor_btn.setObjectName('graphEditor')

        dopeSheetEditor_btn = button.Customflat_btn('Dope Sheet')
        buttonsLayout.addWidget(dopeSheetEditor_btn)
        dopeSheetEditor_btn.setObjectName('dopeSheetPanel')

        ############# SPACING #############################
        buttonsLayout.addSpacing(50)

        playAnim_btn = button.Customflat_btn('Play Animation')
        playAnim_btn.setObjectName('play_Button')
        buttonsLayout.addWidget(playAnim_btn)

        rewindAnim_btn = button.Customflat_btn('Rewind Animation')
        rewindAnim_btn.setObjectName('rewind_Button')

        buttonsLayout.addWidget(rewindAnim_btn)

        midSpacer = qg.QSpacerItem(self.width(), 150)
        buttonsLayout.addSpacerItem(midSpacer)

        utils_lb = label.CustomClearLabel('Animation Tools')
        buttonsLayout.addWidget(utils_lb)

        proShaper_btn = button.Customflat_btn('Pro Shaper')
        proShaper_btn.setObjectName('shaper')
        animTweener_btn = button.Customflat_btn('Curve Tweener')
        animTweener_btn.setObjectName('tweener')

        export_fbx_btn = button.Customflat_btn('FBX Exporter')
        export_fbx_btn.setObjectName('FBX_Exporter')

        buttonsLayout.addWidget(proShaper_btn)
        buttonsLayout.addWidget(animTweener_btn)
        buttonsLayout.addWidget(export_fbx_btn)

        endSpacer = qg.QSpacerItem(self.width(), 400)
        buttonsLayout.addSpacerItem(endSpacer)

        #### Splitter ####
        splitter_lyt = spliter.SplitterLayout(content=(10, 1, 10, 1))
        self.layout().addLayout(splitter_lyt)

        #############################################
        # Connect Signals
        #
        self.channelBox_btn.clicked.connect(self.OpenChannelBox)
        AnimationEditor_btn.clicked.connect(self.launchPanelEditor)
        dopeSheetEditor_btn.clicked.connect(self.launchPanelEditor)
        animTweener_btn.clicked.connect(self.openTools)
        proShaper_btn.clicked.connect(self.openTools)
        export_fbx_btn.clicked.connect(self.openTools)

        playAnim_btn.clicked.connect(self.time_line_operations)
        rewindAnim_btn.clicked.connect(self.time_line_operations)

    # ------------------------------------------------------------------------------#
    def time_line_operations(self):
        checker = self.sender().objectName()
        if 'play' in checker:
            cmds.play(forward=True)
        if 'rewind' in checker:
            cmds.currentTime(int(cmds.playbackOptions(minTime=True)))

    def OpenChannelBox(self):
        MainUI = self.window()
        child = MainUI.findChildren(qg.QWidget, 'ViewportClass')[0]
        child.labelAnimationConnect(button=self.channelBox_btn)

    def launchPanelEditor(self):
        # print(self.sender().objectName())
        sender = self.sender().objectName()
        for panel in cmds.getPanel(sty="%s" % (sender)) or []:
            cmds.scriptedPanel(panel, e=True, to=True)

    def openTools(self):
        sender = self.sender()
        if sender.objectName() == 'tweener':
            Tweener.tweenerRun()

        if sender.objectName() == 'shaper':
            from HitchAnimationModule.Tools.ProShaperFolder import proShaper
            reload(proShaper)
            proShaper.interCreate()

        if sender.objectName() == 'FBX_Exporter':
            FBX_UI.FBX_Run()

    # ---------------------------------------------------------#
