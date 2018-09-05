# -*- coding: utf-8 -*-
from __future__                   import division
import random
import shutil
import errno
import os
import json
import pymel.all
import collections
import copy
import shiboken        as shi
import PySide.QtCore   as qc
import PySide.QtGui    as qg
import maya.cmds       as cmds
import pymel.core      as pm
import maya.OpenMaya   as om
import maya.OpenMayaUI as mui
from math                         import log
from functools                    import partial
from HitchAnimationModule.Tools.ProShaperFolder.widgets       import spliter
from HitchAnimationModule.Tools.ProShaperFolder.widgets       import button
from HitchAnimationModule.Tools.ProShaperFolder.widgets       import checkBox
from HitchAnimationModule.Tools.ProShaperFolder.widgets       import label
from HitchAnimationModule.Tools.ProShaperFolder.widgets       import slider
from HitchAnimationModule.Tools.ProShaperFolder.widgets       import lineEdit
from HitchAnimationModule.Tools.ProShaperFolder.utils.generic import undo_pm
from maya.app.general.mayaMixin   import MayaQWidgetDockableMixin as dockable
from maya.app.general.mayaMixin   import MayaQDockWidget as mayaDock
#------------------------------------------------------------------------------------------------------------------------------#
# Some global vars
START      = 'start'
END        = 'end'
CACHE      = 'cache'
NODE       = 'node'
interDialog = None
#---------------------------------------------------------------------------------#
windowTitle  = "ProShaper xX"
windowObject = "PreShaperPro"
#---------------------------------------------------------------------------------#
TEMPFILEDIR = os.path.join(pm.internalVar(userScriptDir=True) ,"HitchAnimationModule","Tools","ProShaperFolder","tempData","TEMP")
#---------------------------------------------------------------------------------#
STYLESHEET = os.path.join(pm.internalVar(usd=1) , 'HitchAnimationModule',"Tools","ProShaperFolder","styleSheets","scheme.txt")
#---------------------------------------------------------------------------------#
# delete proces that i created for delet childs of dock
def deleteFromGlobal():
    mayaMainWindowPtr = mui.MQtUtil.mainWindow()
    mayaMainWindow = shi.wrapInstance(long(mayaMainWindowPtr), qg.QMainWindow) # Important that it's QMainWindow, and not QWidget
    # Go through main window's children to find any previous instances
    for obj in mayaMainWindow.children():
        if type( obj ) == mayaDock:
            if obj.widget().objectName() == "PreShaperPro":
                print obj
                print obj.widget().objectName()
                mayaMainWindow.removeDockWidget(obj)
                obj.setParent(None)
                obj.deleteLater()
                del(obj)
                global interDialog
                interDialog = None
#---------------------------------------------------------------------------------#
class ProShaper(dockable,qg.QDialog):
    def __init__(self,dockWidget=None,dockName=None):
        qg.QDialog.__init__(self)

        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.dock_widget = dockWidget
        self.dock_name = dockName

        self.setWindowTitle(windowTitle)
        self.setObjectName(windowObject)
        self.setFixedWidth(314)
        self.setMinimumHeight(500)

        self.setLayout(qg.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        self.layout().addSpacerItem(qg.QSpacerItem(1,1,qg.QSizePolicy.Expanding))
        self.layout().setAlignment(qc.Qt.AlignVCenter | qc.Qt.AlignHCenter )

        style_sheet_file = STYLESHEET

        with open(style_sheet_file,'r') as styleSheet:
            data = str(styleSheet.read())
            self.setStyleSheet(data)

        scroll_area = qg.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFocusPolicy(qc.Qt.NoFocus)
        scroll_area.setContentsMargins(0,0,0,0)
        scroll_area.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.layout().addWidget(scroll_area)

        main_widget = qg.QWidget()
        main_widget.setObjectName('ProShaper')
        main_layout = qg.QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(10)
        main_layout.setAlignment(qc.Qt.AlignTop)
        main_widget.setLayout(main_layout)
        scroll_area.setWidget(main_widget)

        self.interpolateLayout = qg.QVBoxLayout()
        self.interpolateLayout.setContentsMargins(0,0,0,0)
        self.interpolateLayout.setSpacing(0.5)
        self.interpolateLayout.setAlignment(qc.Qt.AlignTop)
        main_layout.addLayout(self.interpolateLayout)

        new_widget = InterpolateWidget()
        new_widget.hideCloseButton()
        self.interpolateLayout.addWidget(new_widget)

        button_layout = qg.QHBoxLayout()
        button_layout.setContentsMargins(0,0,0,0)
        button_layout.setSpacing(0)
        button_layout.setAlignment(qc.Qt.AlignRight)
        main_layout.addLayout(button_layout)

        add_button = button.CustomButton(' New ... ')
        button_layout.addWidget(add_button)

        self._extraInterpWidgetList = []
        self._extraInterpWidgetList.append(new_widget)
        self.mainCounter = 0
        #-----------------------#
        add_button.clicked.connect(self.addTool)
        self.rejected.connect(self.close)

        self._callBackID = om.MEventMessage.addEventCallback('SceneOpened',self.clearAll)
        delCallBack = partial(om.MMessage.removeCallback,self._callBackID)
        self.destroyed.connect(delCallBack)
#---------------------------------------------------------------------------------#
    def closeEvent(self,event):
        qg.QDialog.closeEvent(self,event)
        self._deleteDataTemp()
        deleteFromGlobal()
        global interDialog
        interDialog = None
#---------------------------------------------------------------------------------#
    def _deleteDataTemp(self):
        shutil.rmtree(TEMPFILEDIR, ignore_errors=True, onerror=None)
        print "\nAll Temp Data Removed\n"
#---------------------------------------------------------------------------------#
    def addTool(self):
        new_widget = InterpolateWidget()
        self.interpolateLayout.addWidget(new_widget)
        self._extraInterpWidgetList.append(new_widget)
        self.connect(new_widget, qc.SIGNAL('CLOSE'), lambda x: self.removeTool(new_widget))
        new_widget.setFixedHeight(0)
        new_widget._animateExpand(True)
        self.mainCounter += 1

    def removeTool(self,interpWidget):
        print('Removing......')
        self.connect(interpWidget,qc.SIGNAL('DELETE'),lambda x: self._delete(interpWidget))
        self._extraInterpWidgetList.remove(interpWidget)
        interpWidget._animateExpand(False)

    def _delete(self,interpWidget):
        print('Deleting......')
        self.interpolateLayout.removeWidget(interpWidget)
        interpWidget._animation = None
        interpWidget.deleteLater()
#---------------------------------------------------------------------------------#
    def clearAll(self,*args):
        for interpWidget in self._extraInterpWidgetList:
            interpWidget.clearItems()
#---------------------------------------------------------------------------------#
    def close(self):
        if self.dock_widget:
            cmds.deleteUI( 'MayaWindow|'+self.dock_name.objectName() )
        else:
            qg.QDialog.close(self)
        self.dock_widget = self.dock_name = None
        print ("Global Dock UI to None")
#---------------------------------------------------------------------------------#
class InterpolateWidget(qg.QFrame):
    def __init__(self):
        qg.QFrame.__init__(self)

        self.randomNum = str(random.randrange(99*99))
        self.Name = '{}_{}'.format('Frame_',str(random.randrange(999)))
        self.setObjectName(self.Name)

        self.setFrameStyle(qg.QFrame.Panel | qg.QFrame.Raised)

        self.setLayout(qg.QVBoxLayout())
        self.layout().setContentsMargins(0,1,1,0)
        self.layout().setSpacing(0)
        self.setFixedHeight(200)
        self.layout().setAlignment(qc.Qt.AlignVCenter | qc.Qt.AlignHCenter )

        main_widget = qg.QWidget()
        main_widgetLayout = qg.QVBoxLayout()
        main_widget.setLayout(main_widgetLayout)
        main_widgetLayout.setContentsMargins(1,1,1,1)
        main_widgetLayout.setAlignment(qc.Qt.AlignVCenter | qc.Qt.AlignHCenter )
        main_widgetLayout.setSpacing(6)
        main_widget.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)
        main_widget.setFixedHeight(200)
        main_widget.setFixedWidth(290)

        graphics_scene = qg.QGraphicsScene()
        graphics_view  = qg.QGraphicsView()
        graphics_view.cacheMode()
        graphics_view.setCacheMode(qg.QGraphicsItem.  DeviceCoordinateCache)
        graphics_view.setOptimizationFlags(qg.QGraphicsView.DontSavePainterState)
        graphics_view.setScene(graphics_scene)
        graphics_view.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        graphics_view.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        graphics_view.setFocusPolicy(qc.Qt.NoFocus)
        graphics_view.setStyleSheet("QGraphicsView {border-style: none;}")
        graphics_view.setSizePolicy(qg.QSizePolicy.Minimum,qg.QSizePolicy.Minimum)
        self.layout().addWidget(graphics_view)
        self.main_widgetProxy = graphics_scene.addWidget(main_widget)
        main_widget.setParent(graphics_view)

        title_layout  = qg.QHBoxLayout()
        splitter_01Layout = qg.QHBoxLayout()
        select_layout = qg.QHBoxLayout()
        button_layout = qg.QHBoxLayout()
        slider_layout = qg.QHBoxLayout()
        check_layout  = qg.QHBoxLayout()
        lastHBoxLayout = qg.QHBoxLayout()
        keyButtonLayout = qg.QHBoxLayout()
        lastItemsLayout = qg.QVBoxLayout()

        lastItemsLayout.setSpacing(0)
        lastItemsLayout.addSpacing(2)
        lastHBoxLayout.addSpacing(50)
        lastHBoxLayout.setAlignment(qc.Qt.AlignRight | qc.Qt.AlignBottom )
        lastItemsLayout.setAlignment(qc.Qt.AlignVCenter | qc.Qt.AlignHCenter )

        main_widgetLayout.addLayout(title_layout)
        main_widgetLayout.addLayout(splitter_01Layout)
        main_widgetLayout.addLayout(select_layout)
        main_widgetLayout.addLayout(button_layout)
        main_widgetLayout.addLayout(slider_layout)
        lastItemsLayout.addLayout(check_layout)
        lastHBoxLayout.addLayout(lastItemsLayout)
        lastHBoxLayout.addSpacerItem(qg.QSpacerItem(1,1,qg.QSizePolicy.Expanding))
        lastHBoxLayout.addLayout(keyButtonLayout)
        main_widgetLayout.addLayout(lastHBoxLayout)
        main_widgetLayout.addLayout(spliter.SplitterLayout())

        title_le = lineEdit.CustomLineEdit()
        title_le.setPlaceholderMessage(' Untitled -')
        title_layout.addWidget(title_le)
        self.close_btn = button.CloseButton('X')

        self.close_btn.setObjectName('roundedButton')
        title_layout.setAlignment(qc.Qt.AlignVCenter | qc.Qt.AlignHCenter )
        title_layout.setSpacing(2)
        title_layout.addWidget(self.close_btn)


        splitterTop = spliter.Splitter(color=(35,180,93))
        splitter_01Layout.addWidget(splitterTop)

        store_items = button.CustomButton('Store items')
        self.clear_items = button.CustomButton('Clear items')

        select_layout.setAlignment(qc.Qt.AlignVCenter | qc.Qt.AlignHCenter )
        select_layout.setSpacing(6)
        select_layout.addWidget(store_items)
        select_layout.addWidget(self.clear_items)

        self.store_start_btn = button.CustomButton('Store Start')
        self.reset_item_btn  = button.CustomButton('Reset')
        self.store_end_btn   = button.CustomButton('Store End')

        button_layout.setAlignment(qc.Qt.AlignVCenter | qc.Qt.AlignHCenter )
        button_layout.setSpacing(6)
        button_layout.addWidget(self.store_start_btn)
        button_layout.addWidget(self.reset_item_btn)
        button_layout.addWidget(self.store_end_btn)

        self.start_lb = label.CustomLabel('Start')
        self.slider = slider.CustomSlider()
        self.slider.setFixedHeight(22)
        self.slider.setRange(0,49)
        self.end_lb = label.CustomLabel('End')

        slider_layout.setSpacing(5)
        slider_layout.addWidget(self.start_lb)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.end_lb)

        self.transformCheckbox = checkBox.CustomCheck('Transform')
        self.attributesCheckbox = checkBox.CustomCheck('UD Attributes')
        self.transformCheckbox.setCheckState(qc.Qt.Checked)
        self.keyButton = button.KeyButton('K')
        keyButtonLayout.setAlignment(qc.Qt.AlignRight | qc.Qt.AlignBottom )
        keyButtonLayout.addWidget(self.keyButton)
        self.keyButton.setEnabled(False)

        check_layout.setAlignment(qc.Qt.AlignVCenter | qc.Qt.AlignHCenter )
        check_layout.setSpacing(15)
        check_layout.addWidget(self.transformCheckbox)
        check_layout.addWidget(self.attributesCheckbox)

        self.items        = collections.OrderedDict({})
        self.slider_down  = False
        self._animation   = None
        self.glow_value   = 0
        self._tempFiles   = []
        self.fullDict     = collections.OrderedDict({})
        self.jsonStored   = collections.OrderedDict({})
        self.neutralAttrs = collections.OrderedDict({})
        self._tempSignal  = False
        self.StoredSignal = False
        self._buttonCounter = 0
        self.keyCounter     = 0
        self.resetCounter   = 0
#------------------------------------------------------------------------------------------#
        self.close_btn.clicked.connect(self.closeWidgetUI)

        store_items.clicked.connect(self.storeItems)
        self.clear_items.clicked.connect(self.clearItems)
        self.clear_items.clicked.connect(lambda: self.resetGlowValue())

        self.store_start_btn.clicked.connect(self.storeStart)
        self.store_start_btn.clicked.connect(self.countPress)
        self.store_end_btn.clicked.connect(self.storeEnd)
        self.reset_item_btn.clicked.connect(self.resetAttributes)

        self.slider.valueChanged.connect(self.setLinearInterpolation)
        self.slider.valueChanged.connect(self.setLabelGlow)

        self.slider.sliderReleased.connect(self._endSliderUndo)

        self.keyButton.clicked.connect(self.setKeyFrame)
        self.close_btn.clicked.connect(self.tempDelOnClose)

        self.enableButtons(False)

#------------------------------------------------------------------------------------------------------------------------------#
    def countPress(self):
        if self.StoredSignal == True and self.keyCounter != 0:
            self._buttonCounter += 1
        print self._buttonCounter

#------------------------------------------------------------------------------------------------------------------------------#
    def createTemps(self,name=None,attDict=None,random=None):

        for key,val in attDict.items():
            for clave in val.keys():
                if clave == CACHE:
                    del val[clave]
                if clave == NODE:
                    del val[clave]

        #---------------------------------------------#

        rootDir   = TEMPFILEDIR
        filePath  = os.path.join(rootDir,"{}_{}{}".format(name,random,'.json'))
        jsonData = json.dumps(collections.OrderedDict(attDict), sort_keys=True, ensure_ascii=True, indent = 1 )

        if not os.path.exists(rootDir):
            try:
                os.makedirs(rootDir)
                with open(filePath, "w") as f:
                     f.write(jsonData)
                #print " Directory Created at {}".format(rootDir)
                # Store the temp files on a list for delete later
                self.tempFilesDelete(filePath)

            except OSError as exc:
                if exc.errno != errnoEEXIST:
                    raise

        else:
            with open(filePath, "w") as f:
                f.write(jsonData)
                f.close()
                #print "Data was successfully written to {0}".format(filePath)
                # Store the temp files on a list for delete later
                self.tempFilesDelete(filePath)


        self.jsonStored = filePath

        return filePath

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def tempFilesDelete(self,path):
        self._tempFiles.append(path)

#-------------------------------------------------------------------------#
    def rawDicData(self,data):

        attDict = data

        for key,val in attDict.items():
            if val == NODE:
                del attDict[val]
            for clave in val.keys():
                if clave == CACHE:
                    del val[clave]

        return attDict
#-------------------------------------------------------------------------#
    def _SIGNAL(self,filePath=False):
        if filePath:
            self._tempSignal = True

#-------------------------------------------------------------------------#
    def readJsonFile(self,fileName):
        try:
          with open(fileName, 'r') as jsonFile:
              return json.load(jsonFile)
        except:
            cmds.error("Could not read {0}".format(fileName))

#-------------------------------------------------------------------------#
    def tempDelOnClose(self):
        for x in self._tempFiles:
            os.remove(x)

        del self._tempFiles[:]

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def getBaseAttrs(self):
        att = ['sx','sy','sz']
        self.fullDict
        tempDict = collections.defaultdict(dict)

        for name, item_dict in self.fullDict.items():
            start = item_dict[START]
            for key,val in start.items():
                if key not in att:
                    tempDict[name][key] = 0
                else:
                    tempDict[name][key] = 1


        return dict(tempDict)
#-------------------------------------------------------------------------#
    @undo_pm
    def setKeyFrame(self):
        fullDict = dict(self.fullDict.items())
        copyDict = copy.deepcopy(fullDict)
        mainData = self.rawDicData(copyDict)
        oldData  = dict(self.readJsonFile(self.jsonStored).items())
        baseData = dict(self.getBaseAttrs().items())
        #-------------------------------------------------------#

        nap = mainData.values()

        for x in nap:
            for z in x.keys():
                if z == NODE:
                    del x[z]

        #--------------------------------------#
        newData = mainData

        def getAttributeChange(mainKey,oldDat,newDat):

            formData = collections.defaultdict(dict)

            for (oldKey,oldVal),(newKey,newVlr) in zip(sorted(oldDat.items()),sorted(newDat.items())):

                oldStart = oldVal[mainKey]
                newStart = newVlr[mainKey]
                print "\n{} --------------- ".format(newKey)
                for (key,val), (clave,valor) in zip(oldStart.items(), newStart.items()):
                    oldVal = "{:.3f}".format(val)
                    newVal = "{:.3f}".format(valor)

                    print "{} : {:>7} < - oldVal - - newVal - > {:>7}".format(clave,oldVal,newVal)
                    if float(newVal) != float(oldVal):
                        formData[newKey][clave] = float(newVal)

            self._SIGNAL(True)

            return dict(formData)
        #-------------------------------------------------------------------------#

        def start_end_compare(dictionary,signal=False):

            formData = collections.defaultdict(dict)
            crashData = collections.defaultdict(dict)


            for keys,val in dictionary.items():
                start = val['start']
                end = val['end']

                for (key,val), (clave,valor) in zip(start.items(), end.items()):
                    oldVal = "{:.3f}".format(val)
                    newVal = "{:.3f}".format(valor)

                    #print "{} : {:>7} < - START - - END - > {:>7}".format(clave,oldVal,newVal)

                    if signal:
                        if float(newVal) != float(oldVal):
                            crashData[keys][clave] = float(oldVal)


                    if not signal:
                        if float(newVal) != float(oldVal):
                            formData[keys][clave] = float(newVal)


            self._SIGNAL(True)

            if not signal:
                return dict(formData)

            else:
                return dict(crashData)
        #-------------------------------------------------------------------------#
        def setKeyframesNow():
            if self.slider.value() == 0:
                 if self._buttonCounter == 0 and self.keyCounter <= 1:

                    calculo = start_end_compare(newData,True)
                    for key,val in calculo.items():
                        for clave,valor in val.items():
                            #formated = "{}.{} at {}".format(key,clave,valor)
                            pm.setKeyframe(key, v=valor, at=clave )

                    self.createTemps(self.Name,newData,self.randomNum)
                    self.keyCounter += 1

                 else:
                     compareAttr = getAttributeChange(START,oldData,newData)

                     for key,val in compareAttr.items():
                        for clave,valor in val.items():
                            pm.setKeyframe(key, v=valor, at=clave )

                     calculo = start_end_compare(newData)

                     for key,val in calculo.items():
                        time = pm.findKeyframe(key, timeSlider=True, which="last" )
                        for clave,valor in val.items():
                            pm.setKeyframe(key, v=valor, at=clave , t=time )

                     self.createTemps(self.Name,newData,self.randomNum)
                     self.keyCounter += 1

                 om.MGlobal.displayInfo("# Start Keyframe Values Set - - ")
                 self.keyButton.setEnabled(False)

            elif self.slider.value() == 49:
                 if self._buttonCounter == 0 and self.keyCounter <= 1:

                     calculo = start_end_compare(newData)
                     for key,val in calculo.items():
                         for clave,valor in val.items():
                             #formated = "{}.{} at {}".format(key,clave,valor)
                             pm.setKeyframe(key, v=valor, at=clave )

                     self.createTemps(self.Name,newData,self.randomNum)
                     self.keyCounter += 1

                 else:
                     compareAttr = getAttributeChange(END,oldData,newData)
                     self.keyCounter += 1

                     for key,val in compareAttr.items():
                        for clave,valor in val.items():
                            pm.setKeyframe(key, v=valor, at=clave )

                     calculo = start_end_compare(newData,True)

                     for key,val in calculo.items():
                        time = pm.findKeyframe(key, timeSlider=True, which="first" )
                        for clave,valor in val.items():
                            pm.setKeyframe(key, v=valor, at=clave , t=time )

                     self.createTemps(self.Name,newData,self.randomNum)

                 om.MGlobal.displayInfo(" # End Keyframe Values Set - - ")
                 self.keyButton.setEnabled(False)

            else:
                om.MGlobal.displayWarning("You must set the slider at start or end position in order to keyframe values")

        setKeyframesNow()

        #-------------------------------------------------------------------------#

#-----------------------------------------------------------------------------------------------------------------------------------------------#
    def setLabelGlow(self,value):
        self.glow_value = int(float(value) / self.slider.maximum() * 100)
        self.start_lb.setGlowValue(100 - self.glow_value)
        self.end_lb.setGlowValue(self.glow_value)

    def resetGlowValue(self):
        self.start_lb.glow_index = 0
        self.start_lb.setGlowValue(0)
        self.end_lb.setGlowValue(0)

#--------------------------------------------------------------------------------------------------------------------------------------------#
    def _animateExpand(self,value):

        opacityAnim = qc.QPropertyAnimation(self.main_widgetProxy, "opacity")
        opacityAnim.setStartValue(int(not(value)));
        opacityAnim.setEndValue(int(value))
        opacityAnim.setDuration(200)
        opacityAnimCurve = qc.QEasingCurve()
        if value:
            opacityAnimCurve.setType(qc.QEasingCurve.InQuad)

        else:
            opacityAnimCurve.setType(qc.QEasingCurve.OutQuad)


        #####
        size_anim = qc.QPropertyAnimation(self,"geometry")

        geometry = self.geometry()
        width = geometry.width()
        x,y,_,_ = geometry.getCoords()

        size_start = qc.QRect(x,y,width, int(not(value) * 200))
        size_end   = qc.QRect(x,y,width, int(value) * 200)

        size_anim.setStartValue(size_start)
        size_anim.setEndValue(size_end)
        size_anim.setDuration(150)

        size_animCurve = qc.QEasingCurve()

        if value:
            size_animCurve.setType(qc.QEasingCurve.InQuad)

        else:
            size_animCurve.setType(qc.QEasingCurve.OutQuad)

        size_anim.setEasingCurve(size_animCurve)

        self._animation = qc.QSequentialAnimationGroup()

        if value:
            self.main_widgetProxy.setOpacity(0.05)
            self._animation.addAnimation(size_anim)
            self._animation.addAnimation(opacityAnim)
        else:
            self.main_widgetProxy.setOpacity(1)
            self._animation.addAnimation(opacityAnim)
            self._animation.addAnimation(size_anim)

        size_anim.valueChanged.connect(self._forceResize)
        self._animation.finished.connect(self._animation.clear)

        if not value:
            self._animation.finished.connect(self.deleteWidgetUI)

        self._animation.start(qc.QAbstractAnimation.DeleteWhenStopped)


    def _forceResize(self,new_height):
        self.setFixedHeight(new_height.height())

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def _startSliderUndo(self):
        pm.undoInfo(openChunk=True)


    def _endSliderUndo(self):
        pm.undoInfo(closeChunk=True)
        self.slider_down = False
#------------------------------------------------------------------------------------------#
    def storeItems(self):
        selection = pm.ls(sl=True,fl=True, tr=True)

        if not selection:
            return

        self.items = {}
        for node in selection:
            self.items[node.name()] = {NODE:node, START:{},END:{},CACHE:{}}

        self.enableButtons(True)


    def clearItems(self):
        self.items = {}
        print '\nDictionary %s is empty\n'%self.items
        self.enableButtons(False)
        self.slider.setValue(0)
        self._buttonCounter = 0
        self.StoredSignal = False
        self.keyButton.setEnabled(False)
        self.keyCounter = 0
#---------------------------------------------------------------------------------#
    def _getVals(self,key,value):
        tempDict = copy.deepcopy(self.items)
        for name, item_dict in tempDict.items():
            node = item_dict[NODE]

            if not node.exists():
                del(self.items[name])
                continue

            attrs = self.getAttributes(node)
            data = item_dict[key]

            for attr in attrs:
                data[attr] = node.attr(attr).get()

            #print "this is the item Dic %s"%item_dict
            self.fullDict = tempDict

        return self.fullDict
#---------------------------------------------------------------------------------#
    def enableButtons(self,value):
        self.store_start_btn.setEnabled(value)
        self.reset_item_btn.setEnabled(value)
        self.store_end_btn.setEnabled(value)
        self.transformCheckbox.setEnabled(value)
        self.attributesCheckbox.setEnabled(value)
        self.slider.setEnabled(value)
        self.start_lb.setEnabled(value)
        self.end_lb.setEnabled(value)

    def hideCloseButton(self,value=True):
        self.close_btn.setVisible(not(value))
#---------------------------------------------------------------------------------#
    def storeStart(self):
        if not self.items: return
        self._store(START,0)
        self._cache()
        self.setLabelGlow(0)

        if self._buttonCounter >= 1:
            self.keyButton.setEnabled(True)
    def storeEnd(self):
        if not self.items: return
        self._store(END,50)
        self._cache()
        self.setLabelGlow(49)
        if not self._tempSignal:
            self.createTemps(self.Name,self._getVals(END,50),self.randomNum)

        if self.resetCounter > 0:
            self.keyButton.setEnabled(True)

#---------------------------------------------------------------------------------#
    def _store(self,key,value):

        for name, item_dict in self.items.items():
            node = item_dict[NODE]

            if not node.exists():
                del(self.items[name])
                continue

            attrs = self.getAttributes(node)

            data = item_dict[key]


            for attr in attrs:
                data[attr] = node.attr(attr).get()

        self.fullDict = self.items

        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)

#---------------------------------------------------------------------------------#
    def _cache(self):
        for item_dict in self.items.values():
            node  = item_dict[NODE]
            start = item_dict[START]
            end   = item_dict[END]

            if not start or not end:
                item_dict[CACHE] = None
                continue

            attrs = list(set(start.keys()) and set(end.keys()))

            cache = item_dict[CACHE] = {}
            for attr in attrs:
                start_attr = start[attr]
                end_attr   = end[attr]

                if start_attr == end_attr:
                    cache[attr] = None
                else:
                    cache_values = cache[attr] = []
                    interval     = float(end_attr - start_attr) / 49.0
                    for index in range(50):
                        cache_values.append((interval * index) + start_attr)

#---------------------------------------------------------------------------------#
    def getAttributes(self,node):
        attrs = []

        if self.transformCheckbox.isChecked():
            for transform in 'trs':
                for axis in 'xyz':
                    channel = '{0}{1}'.format(transform, axis)
                    if node.attr(channel).isLocked(): continue
                    attrs.append(channel)


        if self.attributesCheckbox.isChecked():
            for attr in node.listAttr(ud=True):
                if attr.type() not in ('double','int'): continue
                if attr.isLocked(): continue

                attrs.append(attr.name().split('.')[-1])

        #print "from get attrs func --> %s"%attrs
        return attrs

#---------------------------------------------------------------------------------#
    @undo_pm
    def resetAttributes(self,*args):
        if not self.items: return

        for name, item_dict in self.items.items():
            node = item_dict[NODE]

            if not node.exists():
                del(self.items[name])
                continue

            start = item_dict[START]
            for key,val in start.items():
                formato = "{}.{} - {}".format(node,key,val)
                #print formato
                pm.setAttr(("{}.{}").format(node,key),val,e=True)


            self.slider.setValue(0)

        self.StoredSignal = True
        if self.StoredSignal:
            self.keyButton.setEnabled(True)

        self.resetCounter += 1
#---------------------------------------------------------------------------------#
    def setLinearInterpolation(self,value):
        if not self.items: return

        if not self.slider_down:
            self._startSliderUndo()
            self.slider_down = True

        for name, item_dict in self.items.items():
            node = item_dict[NODE]
            start = item_dict[START]

            if not node.exists():
                del(self.items[name])
                continue

            if not start or not item_dict[END]: continue

            cache = item_dict[CACHE]

            for attr in cache.keys():
                if cache[attr] == None: continue
                pm.setAttr(node.attr(attr),cache[attr][value])

#---------------------------------------------------------------------------------#
    def closeWidgetUI(self):
        print ('Extra Tool Closed')
        return self.emit(qc.SIGNAL('CLOSE'), self)

    def deleteWidgetUI(self):
            print ('UI Tool Deleted')
            return self.emit(qc.SIGNAL('DELETE'), self)

#---------------------------------------------------------------------------------#
def interCreate(docked=False):
    deleteFromGlobal()
    global interDialog
    if interDialog is None:
        interDialog = ProShaper()
        if docked:
            ptr = mui.MQtUtil.mainWindow()
            main_window = shi.wrapInstance(long(ptr), qg.QMainWindow)

            interDialog.setParent(main_window)
            size = interDialog.size()

            name = mui.MQtUtil.fullName(long(shi.getCppPointer(interDialog)[0]))
            dock = cmds.dockControl(
                    allowedArea =['right', 'left'],
                    floating    = not(docked),
                    content     = name,
                    width       = size.width(),
                    height      = size.height(),
                    label       = 'Interpolate It',
                    r           = True,
                    bgc         = (0.141,0.135,0.135),
                    ebg         = True,
                    ret         = False)

            """ from this is the process to delete the dock from maya window
            before create it again, this way will only appear once in dock panel """
            dockWidget = mui.MQtUtil.findControl(dock)
            dockName = shi.wrapInstance(long(dockWidget), qg.QWidget)
            interDialog.dock_widget = dockWidget
            interDialog.dock_name = dockName
            name = dockName.objectName()

            def changeName(name):
                intNum = int(name[-1])
                if intNum in range(1,10):
                    preNum = str(intNum - 1)
                    alpha = list(name)
                    alpha[-1] = preNum
                    newName = "".join(alpha)
                    print newName
                    return newName

            oldTool = changeName(name)
            stackDock = 'dockControl5'
            print stackDock

            if oldTool != stackDock[:]:
                try:
                    cmds.deleteUI( oldTool )
                    print ('DockControl -- > {} DELETED'.format(oldTool))
                except:
                    pass
            else:pass

        else:
            interDialog.show(dockable=True)

#---------------------------------------------------------------------------------#
def interDelete():
    deleteFromGlobal()
    global interDialog
    if interDialog:
        try:
            interDialog.close()
            interDialog.deleteTool()
        except:
            print '\n -- Nothing to Close -- \n'

        interDialog = None
#---------------------------------------------------------------------------------#
if __name__ == '__main__':
    interDelete()
    deleteFromGlobal()
    interCreate()
    print ('\nUI Created...\n')
