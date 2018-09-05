import maya.cmds       as cmds
import pymel.core      as pm
import maya.OpenMaya   as om
import pymel
from HitchAnimationModule.ControlList import ControlList; reload(ControlList)
from HitchAnimationModule.LogicData import refreshUI
from PySide import QtCore as qc
from PySide import QtGui as qg
##########################################
# Globals:
NODE  = 'node'
ATTRS = 'attributes'
SHAPE = 'shapes'
############################
# Global controls list
HEADCONTROLS = ControlList.FACECONTROLS
BODYCONTROLS = ControlList.BODYCONTROLS

##########################################################################
#
class BookMarkCreate(object):
    def __init__(self, controlsSelector=''):
        super(BookMarkCreate, self).__init__()
        #print (controlsSelector)
        self._controls = []
        self.items = {}

        if controlsSelector == 'HEAD':
            self._controls = HEADCONTROLS
        if controlsSelector == 'BODY':
            self._controls = BODYCONTROLS
                    #
        # child finder helper !!!
        #
        self.scene = refreshUI.resetScene()
        topPanel = self.scene.findSceneChilds(qg.QFrame, 'topFrame')[0]
        self.lineEdit = topPanel.nameSpace_le

    # ---------------------------------------------------------------------------------#
    # creates de dictionary for the process
    def storeItems(self):
        selection = self._controls
        if not selection:
            return

        if not self.lineEdit.isReadOnly():
            self.items = {}
            try:
                for obj in selection:
                    node = pm.PyNode(obj)
                    self.items[node.name()] = {NODE:node, ATTRS:{}, SHAPE:{} }

                return

            except:
                cmds.warning('Must set a Name Space to save Bookmarks')


        else:

            name = self.lineEdit.text()
            self.items = {}
            for obj in selection:
                formato = name + ':' + obj
                node = pm.PyNode(formato)
                self.items[node.name()] = {NODE:node, ATTRS:{}, SHAPE:{} }

            return

    #---------------------------------------------------------------------------------#
    # catch the proccess or start the operation , --- >> connect this to button!!!!!!
    def storeStart(self):
        self.storeItems()
        if not self.items:
            return
        self._store(ATTRS)
        return
    #---------------------------------------------------------------------------------#
    # Store Data into dictionary data types , gets the values of everything ...
    def _store(self,key):
        for name, item_dict in self.items.items():
            node = item_dict[NODE]
            if not node.exists():
                del(self.items[name])
                continue

            data = item_dict[key]
            shapes = self.getShape(node)
            shapesDic = {}

            for itm in shapes:
                tempDict = {}
                for att in self.getAttributes(itm):
                    tempDict[att] = itm.attr(att).get()
                shapesDic[itm.name()] = tempDict

            item_dict[SHAPE] = shapesDic
            attrs = self.getAttributes(node)

            for attr in attrs:
                data[attr] = node.attr(attr).get()

    ######################################################################
    # Get the shapes , if there are attributes or shapes intanced will get ti too
    def getShape(self,node):
        shapes = []
        node = pm.PyNode(node)
        nodeShape = node.getShape()
        if len(nodeShape.listAttr(ud=True)) > 0:
            shapes.append(nodeShape)
        locs =  [obj for obj in node.getShapes() if isinstance(obj,pymel.core.nodetypes.Locator)]
        if len(locs) > 0:
            for loc in locs:
                 shapes.append(loc)

        return shapes

    #########################################################################
    # gets the 'XYZ' or userDefined Attributes function.
    def getAttributes(self,node):
        attrs = []
        if isinstance(node, pymel.core.nodetypes.Transform):
            for transform in 'trs':
                for axis in 'xyz':
                    channel = '%s%s' %(transform, axis)
                    if node.attr(channel).isLocked(): continue
                    attrs.append(channel)

        if True:
            for attr in node.listAttr(ud=True):
                if attr.type() not in ('double', 'int'): continue
                if attr.isLocked(): continue

                attrs.append(attr.name().split('.')[-1])

        return attrs


def getValueData(CONTROLS=''):
    book = BookMarkCreate(CONTROLS)
    book.storeStart()
    return book.items


if __name__ == '__main__':
    print(getValueData())
