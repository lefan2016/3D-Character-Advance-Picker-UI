# -*- coding: utf-8 -*-
try:
    from HitchAnimationModule.LogicData import refreshUI
    import maya.cmds as cmds
except:
    pass
import book
import os
import json
import pprint
from PySide import QtGui as qg
from contextlib import contextmanager
#------------------------------------------------------------------------------------#
# GLOBALS:

DIRECTORY = os.path.join(cmds.internalVar(usd=1), 'HitchAnimationModule', 'StoredData')
#------------------------------------------------------------------------------------#


@contextmanager
def delete_callbacks():

    scene = refreshUI.resetScene()
    # Get the instances of the classes witch contains callbacks
    channelBox = scene.findSceneChilds(qg.QFrame, 'ChannelBoxColt')[0]

    for item in channelBox.callBacks_ids:
        # print(item)
        # print(item[-1].length())

        # om.MMessage.removeCallback(item[0])
        call = om.MMessage.removeCallbacks(item[-1])

        method = item[1]
        channelBox.disconnect(channelBox, qc.SIGNAL('destroyed()'), method)

    # clean the arrays after delete everything inside .....
    channelBox.ids_array.clear()  # callback id array

    if len(channelBox.callBacks_ids) < 1000:
        channelBox.callBacks_ids = []

    yield

    # just continues the proceess, other  methods will createm back again ..
    getattr(channelBox, 'refresDisplay')()

#------------------------------------------------------------------------------------#


def createDirectory(dir=DIRECTORY):
    # Creates the directory to save the controls created #
    if not os.path.exists(dir):
        os.mkdir(dir)


def rawDicData(data):
    attDict = data
    for key, val in attDict.items():
        for ks in val.keys():
            if ks == 'node':
                del val[ks]

    return attDict


class PoserLibrary(dict):
    def __init__(self):
        mainDict = {}

        # child finder helper !!!
        #
        self.scene = refreshUI.resetScene()
        topPanel = self.scene.findSceneChilds(qg.QFrame, 'topFrame')[0]
        self.lineEdit = topPanel.nameSpace_le

    ##################################################################################################
    def save(self, name, camera, head=False, body=False, dir=DIRECTORY, screenShot=True, **info):
        createDirectory(dir)
        infoFile = os.path.join(dir, '%s.json' % name)
        info['name'] = name
        #####################
        #   Here is where i store the json data for the bookmarks over controls #########################   < --------- HERE !!
        #
        Saved = {}
        cleanData = {}

        if head:
            cleanData = rawDicData(book.getValueData('HEAD'))

        if body:
            cleanData = rawDicData(book.getValueData('BODY'))

        info['data'] = cleanData
        if screenShot:
            info['screenShot'] = self.saveScreenshot(name, camera, directory=dir)

        with open(infoFile, 'w') as f:
            json.dump(info, f, indent=4)

        Saved[name] = info
        return Saved

    ################ SCREENSHOT SYSTEM ##########################
    def saveScreenshot(self, name, camera, directory=DIRECTORY):
        path = os.path.join(directory, '%s.jpg' % name)
        if not os.path.exists(directory):
            os.mkdir(directory)

        time = cmds.currentTime(q=True)
        cmds.modelEditor('modelPanel4', edit=True, grid=False, displayTextures=True, rnm='base_OpenGL_Renderer',
                         displayAppearance="smoothShaded", allObjects=False, polymeshes=True, camera=camera)
        cmds.setAttr('defaultRenderGlobals.imageFormat', 8)
        cmds.playblast(editorPanelName='modelPanel4', completeFilename=path, forceOverwrite=True,
                       format='image', width=500, height=500,
                       showOrnaments=False, startTime=time, endTime=time, viewer=False)
        cmds.modelEditor('modelPanel4', edit=True, allObjects=True, camera='persp')
        return path
        #########################################################################

    def find(self, dir=DIRECTORY):
        self.clear()
        if not os.path.exists(dir):
            return
        datos = {}
        ownDict = {}

        files = os.listdir(dir)
        mayaFiles = [f for f in files if f.endswith('.json')]
        for file in mayaFiles:
            name, ext = os.path.splitext(file)
            path = os.path.join(dir, file)
            infoFile = '%s.json' % name
            if infoFile in files:
                infoFile = os.path.join(dir, infoFile)

                with open(infoFile, 'r') as f:
                    ownDict = json.load(f)
                    # pprint.pprint(info)

            else:
                ownDict = {}
                #print ('No File Found')

            screenShot = '%s.jpg' % name
            if screenShot in files:
                ownDict['screenShot'] = os.path.join(dir, screenShot)

            ownDict['name'] = name
            ownDict['path'] = path
            datos[name] = ownDict

        # pprint.pprint(datos)
        return datos

    def load(self, name):
        path = self[name]['path']
        with open(path, 'r') as f:
            info = json.load(f)
            # pprint.pprint(info)

            with delete_callbacks():
                self.LoadPose(info)

    #################################################################################

    def LoadPose(self, data):
        for key, val in data.items():
            pass
            #print('clave: %s valor: %s' %(key,val))

        if not self.lineEdit.isReadOnly():
            controls = data['data']

            for ctrl, dat in controls.items():
                dumb = ''
                if ':' in ctrl:
                    dumb = ctrl.split(':')[-1]

                else:
                    dumb = ctrl

                attrs = dat.get('attributes')
                shapes = dat.get('shapes')

                for ch, val in attrs.items():
                    formato = '{}.{}'.format(dumb, ch)
                    if cmds.getAttr(formato, se=True):
                        cmds.setAttr(formato, val)

                if len(shapes) > 0:
                    for shp, atts in shapes.items():
                        shape = shp.split('|')[-1]
                        if ':' in shape:
                            shape = shape.split(':')[-1]

                        else:
                            shape = shape

                        for ch, val in atts.items():
                            formato = '{}.{}'.format(shape, ch)
                            if cmds.getAttr(formato, se=True):
                                cmds.setAttr(formato, val)

        # if name space active
        #
        if self.lineEdit.isReadOnly():
            name = self.lineEdit.text() + ':'

            controls = data['data']
            for ctrl, dat in controls.items():
                attrs = dat.get('attributes')
                shapes = dat.get('shapes')

                if ':' in ctrl:
                    ctrl = name + ctrl.split(':')[-1]

                else:
                    ctrl = name + ctrl

                for ch, val in attrs.items():
                    formato = '{}.{}'.format(ctrl, ch)
                    if cmds.getAttr(formato, se=True):
                        cmds.setAttr(formato, val)

                if len(shapes) > 0:
                    for shp, atts in shapes.items():
                        shape = shp.split('|')[-1]

                        if ':' in shape:
                            shape = name + shape.split(':')[-1]

                        else:
                            shape = name + shape

                        for ch, val in atts.items():
                            formato = '{}.{}'.format(shape, ch)
                            if cmds.getAttr(formato, se=True):
                                cmds.setAttr(formato, val)

    ###################################################################################################

    def deleteBookmark(self, lista, dir=DIRECTORY):
        for item in lista:
            name = item.text()
            files = os.listdir(dir)
            JsonFile = [f for f in files if f == name + '.json'][0]
            path = os.path.join(dir, JsonFile)
            info = {}

            with open(path, 'r') as f:
                info = json.load(f)
                # pprint.pprint(info)

            screenShot = info.get('screenShot')
            os.remove(screenShot)
            listWidget = item.listWidget()
            row = item.listWidget().row(item)
            print(row)
            listWidget.takeItem(row)
            os.remove(path)
            del(item)

###########################################################################################################################################
