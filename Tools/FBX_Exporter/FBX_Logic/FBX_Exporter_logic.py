import maya.cmds as cmds
import maya.mel as mel
import string
import maya.OpenMaya as om
import maya.OpenMayaUI as omUI
import pymel.core as pm
from contextlib import contextmanager
###############################
# GLOBALS :
#
melScriptPath = cmds.internalVar(usd=True) + "HitchAnimationModule/Tools/FBX_Exporter/FBX_Logic/SIP_FBXAnimationExporter_FBXOptions.mel"
mel.eval('source "%s"' %melScriptPath)

###############################

#---------------------------------------#
#Globals:

def undo_pm(func):
    def wrapper(*args, **kwargs):
        pm.undoInfo(openChunk=True)
        try:
            ret = func(*args, **kwargs)
        finally:
            pm.undoInfo(closeChunk=True)
        return ret
    return wrapper
# -----------------------------------------------------------------------------------------------------------------------------------------------------#

class FBX_ExporterClass(object):
    def __init__(self):
        super(FBX_ExporterClass, self).__init__()

        # Arrays to manage later on other procs like delete and whatever...
        self.node_originArray = []
        self.mesh_messageArray = []
        self.export_nodesArray = []
        self.current_character_data = []
        self.current_exportNodes = {}
        self.current_origin = None
        self.currentMainExportJoint = None
        self.current_meshes = []

    # ---------------------------------------------------------------------------#
    ########################################################################################################################################################
    #
    #                                                                                                   Low-level procs
    #
    ########################################################################################################################################################
    # TAG THE ORIGIN ATTR IN EXTRAA ATTR FOR EXPORT
    #

    def delete_all_data(self):
        for key, val in self.current_exportNodes.items():
            if cmds.objExists(val):
                cmds.delete(val)

            self.current_exportNodes = {}

        try:
            exportAttr = self.current_origin + '.origin'
            messageAttr = self.current_origin + '.exportNode'

            if cmds.objExists(exportAttr):
                cmds.deleteAttr(exportAttr)

            if cmds.objExists(messageAttr):
                cmds.deleteAttr(messageAttr)

            self.current_origin = None
            self.currentMainExportJoint = None

        except:
            pass


        #######################################################

    @undo_pm
    def tagForOrigin(self,node, characterName):
        attribute = node + '.origin'

        if cmds.objExists(attribute):
            try:
                cmds.deleteAttr(attribute)
                exportN = self.returnFBXExportNodes(node)

                cmds.delete(exportN)
            except:
                pass


        if cmds.objExists(node) and not cmds.objExists(attribute):
            cmds.addAttr(node, shortName = "org", longName = "origin", at = "bool")
            cmds.setAttr(attribute, True)

            self.current_origin = node
            exportNode = self.createFBXExportNode(characterName, 'animation')

            # 1 - export node - 2 - origin
            self.connectFBXExportNodeToOrigin(exportNode, node)

    ######################################################################################
    def makeVisible(self, node):
        cmds.setAttr(node + '.visibility', 1)
        try:
            cmds.setAttr(node + '.drawStyle', 1)
        except:
            pass

    # add attributes to the mesh so exporter can find them
    #
    def tagForMeshExport(self,mesh):
        attribute = mesh + '.exportMeshes'
        if cmds.objExists(mesh) and not cmds.objExists(attribute):
            cmds.addAttr(mesh, shortName = "xms", longName = "exportMeshes", at = "message")
            self.mesh_messageArray.append(attribute)


    # add attribute to the node so exporter can find export definitions
    # i could attach this to the node array and take just the node from the array
    def tagForExportNode(self, node):
        attribute = node + '.exportNode'
        if cmds.objExists(node) and not cmds.objExists(node + ".exportNode"):
            cmds.addAttr(node, shortName = "xnd", longName = "exportNode", at = "message")



    # Return the origin of the given namespace
    # i could just check it from the class array ...
    def returnOrigin(self,namespace=None):
        joints = []

        if namespace is not None:
            joints = cmds.ls((namespace + ":*"), type = "joint")
            
        else:
            joints = cmds.ls(type = "joint")

        if len(joints) > 0:
            for curJoint in joints:
                attribute = curJoint + ".origin"

                if cmds.objExists(attribute) and cmds.getAttr(attribute):
                    return curJoint

        # if fails return str ERROR i will check it later..
        return "ERROR"


    # Tag object for being garbage
    # If node is valid object and attribute does not exists, add deleteMe attribute
    def tagForGarbage(self,node):
        attribute = node + ".deleteMe"
        if cmds.objExists(node)and not cmds.objExists(attribute):
            cmds.addAttr(node, shortName = "del", longName = "deleteMe", at = "bool")
            cmds.setAttr(attribute, True)


    # Removes all nodes taged as garbage
    # List all transforms in the scene
    def clearGarbage(self):
        list = cmds.ls(tr=True)
        for cur in list:
            if cmds.objExists(cur + ".deleteMe"):
                cmds.delete(cur)


    #       Return the meshes connected to blendshape nodes
    #       Get a list of blendshape nodes
    #       Follow those connections to the mesh shape node
    #       Traverse up the hierarchy to find parent transform node
    #       character has a valid namespace, namespace does not have colon
    #       only exporting polygonal meshes
    def findMeshesWithBlendshapes(self,nameSpace=None):
        returnArray = []
        blendShapes = []

        if nameSpace is not None:
            blendShapes = cmds.ls((nameSpace + ":*" ), type = "blendShape")
        else:
            blendShapes = cmds.ls(type = "blendShape")

        for curBlendShape in blendShapes:
            downstreamNodes = cmds.listHistory(curBlendShape, future = True)

            for curNode in downstreamNodes:
                if cmds.objectType(curNode, isType = "mesh"):
                    parents = cmds.listRelatives(curNode, parent = True)
                    returnArray.append(parents[0])

        return returnArray

    ########################################################################################################################################################
    #
    #                                                                                           Export settings node procs
    #
    ########################################################################################################################################################

    #######################################
    # orginize the parent data into a generic categori parent-child for new joint chains creation
    #
    def create_export_joints_data(self):
        root_joints = self.current_character_data[1]
        current_origin = self.current_origin
        parent_child = []

        for joint in root_joints:
            #print joint
            if joint != current_origin:
                const = list(set([itm for itm in cmds.listConnections(joint) if cmds.objectType(itm, i='parentConstraint')]))
                try:
                    attr = list(set([itm for itm in cmds.listConnections(const[0]) if cmds.objectType(itm, i='joint')]))
                    for att in attr:
                        if att != joint:
                            parent_child.append([att,joint])
                except:
                    pass

        return parent_child

        ###############################################################################

    # Procces to find all root joints to tag in the rig
    # Only joints at top hier with skincluster are taking in count
    def get_nodes_in_proccess(self, rootCtrl):
        checkList= cmds.listRelatives(rootCtrl, allParents=True, f=True)[0].split('|')
        topNode = [itm for itm in checkList if itm  in cmds.ls(assemblies=True)]
        joints = []
        meshes = []
        meshesOnScreen = self.getFromScreen()
        #print meshesOnScreen

        if len(topNode) > 0:
            print('Root Character folder: %s' %topNode[0])
            childs = cmds.listRelatives(topNode[0], ad=True )
            for itm in childs:
                try:
                    if cmds.objectType(itm , isType='joint'):
                        par = cmds.listRelatives(itm, p=True)
                        if cmds.objectType(par , isType= 'transform'):
                            connection = list(set([item for item in cmds.listConnections(itm, d=True) if 'skinCluster' in item]))
                            if len(connection) > 0:
                                joints.append(itm)

                    item = [itm]
                    this = [i for i in item if i in meshesOnScreen  ]
                    if len(this) > 0:
                        meshes.append(this[0])


                except:
                    pass

        toPop = []
        for jnt in joints:
            if not jnt.endswith('Ctrl') and not jnt.endswith('ctrl') and not jnt.endswith('control') and not jnt.endswith('Control'):
                if not jnt[-1].isdigit():
                    toPop.append(jnt)

        for jnt,po in [(jnt, po) for jnt in toPop for po in toPop]:
            childCheck = cmds.listRelatives(jnt, ad=True)
            for item in childCheck:
                if po == item:
                    try:
                        toPop.remove(po)
                    except:
                        pass

        rootJoints = toPop

        print('Root Joints Found: {}'.format(rootJoints))
        print('Geometry List found %s'%meshes)
        om.MGlobal.displayWarning('ATTENTION: To Get all Meshes on Screen the Character Meshes to Export Must be FULLY VISIBLE AND NOT TEMPLATE OR REFERENCE in The Viewport' )

        self.current_character_data = [topNode , rootJoints, meshes]
        self.node_originArray = rootJoints
        self.current_meshes = meshes

        return topNode , rootJoints, meshes


    ################################################################
    # gets all the geometry in scene to compare it after in the above process
    def getFromScreen(self):
        lista = []
        view = omUI.M3dView.active3dView()
        this = om.MGlobal.selectFromScreen( 0, 0, view.portWidth(), view.portHeight(), om.MGlobal.kReplaceList)
        sel = pm.ls(sl=True)
        pm.select(clear=True)

        for itm in sel:
            node = pm.PyNode(itm)
            if isinstance(node.getShape(), pm.nodetypes.Mesh):
                lista.append(node.name())

        return lista


    def get_Meshes_to_Export(self):
        data = self.current_meshes
        temp_set = set()

        for mesh in data:
            attrs =  pm.listHistory(mesh, ha = True)
            for att in attrs:
                node = pm.PyNode(att)
                if isinstance(node, pm.nodetypes.SkinCluster):
                    temp_set.add(node.name())


        skins = list(temp_set)
        array = []
        export_grp = pm.group(name='ExportMeshes_group', em=True)
        self.tagForGarbage(export_grp.name())

        for mesh in data:
            attrs =  pm.listHistory(mesh, ha = True)
            for att, sk in [(att, sk) for att in attrs for sk in skins]:
                if att == sk:
                    duplicate = pm.duplicate(mesh, name = str(mesh)+'_export')[0]
                    if pm.objExists(duplicate.name()[:-1]):
                        name = duplicate.name()[:-1]
                        pm.delete(duplicate)
                        try:
                            pm.parent(name, export_grp)
                        except:
                            pass

                        array.append([name,sk])

                    else:
                        pm.parent(duplicate, export_grp)
                        array.append([duplicate.name(),att.name()])

        returned = []
        for item in array:
            # ITEM[0] = mesh , ITEM[1] = SKINCLUSTER
            returned.append(item[0])

            source = "_".join(item[0].split('_')[:-1])
            skin = [itm for itm in cmds.listHistory(source) if 'skinCluster' in itm][0]
            jntList  = [itm for itm in cmds.skinCluster(skin,q=1,inf=1)]


            # primero checkea por el wrap si lo encuentra, los copia o bakea en skinC ..
            wraps = self.findWrapDeformer(source)
            if wraps:
                self.copySkinCluster(wraps, item[0])

            # query el skin si ya lo hay, lo salta ..
            evaluation = mel.eval('findRelatedSkinCluster '+item[0])

            if not evaluation:

                skinCl = cmds.skinCluster(jntList,item[0],bm=0, name = item[0] + '_SC_export' )[0]
                copyWeights = cmds.copySkinWeights(ss=skin,ds=skinCl,noMirror=True)
                cmds.select(clear=True)
                #print ('{} -   {}   -  {}'.format(jntList, skin, item[0]))



        self.connectFBXExportNodeToMeshes(self.current_exportNodes['model'], returned)
        return returned



    # create the export node to store our export settings
    # create an empty transform node
    # we will send it to SIP_AddFBXNodeAttrs to add the needed attributes
    @undo_pm
    def createFBXExportNode(self, characterName, types):
        exportName = ''
        if ':' in characterName:
            exportName = characterName + ":_{}_FBXExportNode".format(types)
        else:
            exportName = characterName + "_{}_FBXExportNode".format(types)

        if cmds.objExists(exportName):
            return

        fbxExportNode = cmds.group(em = True, name = exportName)
        self.addFBXNodeAttrs(fbxExportNode)
        cmds.setAttr(fbxExportNode + ".export", 1)
        self.export_nodesArray.append(fbxExportNode)
        self.current_exportNodes[types] = fbxExportNode
        cmds.select(clear=True)
        #cmds.setAttr(fbxExportNode + '.hiddenInOutliner', 1)

        return fbxExportNode

    ###############################################################################
    # intentar obtener mejor la data de los skin desde los root
    #
    def findWrapDeformer(self,node):
        wrap = [itm for itm in pm.listHistory(node, f=True) if isinstance(itm, pm.nodetypes.Wrap)]

        if wrap:
            # hago un query del source del wrap deformer para encontrar la malla principal
            connect = [itm for itm in pm.listConnections(wrap, d=False, s=True, t='mesh') if itm != node]
            for item in connect:
                evaluation = mel.eval('findRelatedSkinCluster '+str(item.name()))
                if evaluation:
                    # retornara
                    # node source | node destin | skin related |
                    #print node, item, evaluation
                    #print type(node), type(item), type(evaluation)
                    return [node, item, evaluation]

    ###############################################################################
    # copia el skin desde el wrap function si hace match
    #
    def copySkinCluster(self, data, newNode):
        evaluation = mel.eval('findRelatedSkinCluster '+newNode)
        if evaluation:
            return

        # node source | node destin | skin related |  newNode el duplicadod e la mesh
        source = data[0] # primero
        dest = data[1].name()   #segunda
        skinCluster = data[2] #skin

        jntList  = [itm for itm in cmds.skinCluster(dest,q=True,inf=True)]

        skinCl = cmds.skinCluster(jntList,newNode,bm=0)
        copyWeights = cmds.copySkinWeights(ss=skinCluster,ds=skinCl[0],noMirror=True)
        cmds.select(clear=True)

        ###############################################################################

    # to add the attribute to the export node to store our export settings
    #PROCEDURE       for each attribute we want to add, check if it exists
    #                if it doesn't exist, add
    @undo_pm
    def addFBXNodeAttrs(self, fbxExportNode):

        if not cmds.attributeQuery("export", node=fbxExportNode, exists=True):
            cmds.addAttr(fbxExportNode, longName='export', at="bool")

        if not cmds.attributeQuery("moveToOrigin", node=fbxExportNode, exists=True):
            cmds.addAttr(fbxExportNode, longName='moveToOrigin', at="bool")

        if not cmds.attributeQuery("zeroOrigin", node=fbxExportNode, exists=True):
            cmds.addAttr(fbxExportNode, longName='zeroOrigin', at="bool")

        if not cmds.attributeQuery("exportName", node=fbxExportNode, exists=True):
            cmds.addAttr(fbxExportNode, longName='exportName', dt="string")

        if not cmds.attributeQuery("useSubRange", node=fbxExportNode, exists=True):
            cmds.addAttr(fbxExportNode, longName='useSubRange', at="bool")

        if not cmds.attributeQuery("startFrame", node=fbxExportNode, exists=True):
            cmds.addAttr(fbxExportNode, longName='startFrame', at="float")

        if not cmds.attributeQuery("endFrame", node=fbxExportNode, exists=True):
            cmds.addAttr(fbxExportNode, longName='endFrame', at="float")

        if not cmds.attributeQuery("exportMeshes", node=fbxExportNode, exists=True):
            cmds.addAttr(fbxExportNode, longName='exportMeshes', at="message")

        if not cmds.attributeQuery("exportNode", node=fbxExportNode, exists=True):
            cmds.addAttr(fbxExportNode, shortName = "xnd", longName='exportNode', at="message")

        if not cmds.attributeQuery("animLayers", node=fbxExportNode, exists=True):
            cmds.addAttr(fbxExportNode, longName='animLayers', dt="string")


    #PURPOSE        Return all export nodes connected to given origin
    #PROCEDURE      if origin is valid and has the exportNode attribute,
    #               return list of export nodes connected to it
    #PRESUMPTIONS   Only export nodes are connected to exportNode attribute
    def returnFBXExportNodes(self, origin):
        exportNodeList=[]
        attribute = origin + ".exportNode"
        if cmds.objExists(origin + ".exportNode"):
            exportNodeList = cmds.listConnections(origin + ".exportNode" ,source = False, destination = True)

        return exportNodeList[0]


    #     Connect the fbx export node to the origin
    #     check if attribute exist and nodes are valid
    #     if they are, connect attributes
    @undo_pm
    def connectFBXExportNodeToOrigin(self, exportNode, origin):
        attribute = origin + ".exportNode"
        exportAttr = exportNode + ".exportNode"

        if not cmds.objExists(attribute):
            self.tagForExportNode(origin)

        elif not cmds.objExists(exportAttr):
            self.addFBXNodeAttrs(exportNode)

        if cmds.objExists(origin) and cmds.objExists(exportNode):
            cmds.connectAttr(attribute, exportAttr, f=True)


    # delete given export node
    # if object exists, delete
    def deleteFBXExportNode(self):
        for node in self.export_nodesArray:
            if cmds.objExists(node):
                cmds.delete(node)

    ########################################################################################################################################################
    #
    #                                                                                                     Model export procs
    #
    ########################################################################################################################################################

    #    To connect meshes to the export node so the exporter can find them
    #    check to make sure meshes and exportNode is valid, check for attribute "exportMeshes"
    #    if no attribute, add it. then connect attributes
    #   exportNode is a exportNode, and meshes is a list of transform nodes for polygon meshes
    @undo_pm
    def connectFBXExportNodeToMeshes(self,exportNode, meshes):
        #print(exportNode, meshes)
        if cmds.objExists(exportNode):
            if not cmds.objExists(exportNode + ".exportMeshes"):
                self.addFBXNodeAttrs(exportNode)
            for curMesh in meshes:
                if cmds.objExists(curMesh):
                    if not cmds.objExists(curMesh + ".exportMeshes"):
                        self.tagForMeshExport(curMesh)
                    try:
                        cmds.connectAttr(exportNode + ".exportMeshes", curMesh + ".exportMeshes", force = True)
                    except:
                        pass

    # to disconnect the message attribute between export node and mesh
    # iterate through list of meshes and if mesh exists, disconnect
    # that node and mesh are connected via exportMeshes message attr
    @undo_pm
    def disconnectFBXExportNodeFromMeshes(self,exportNode, meshes):
        if cmds.objExists(exportNode):
            for curMesh in meshes:
                if cmds.objExists(curMesh):
                    cmds.disconnectAttr(exportNode + ".exportMeshes", curMesh + ".exportMeshes")

    # return a list of all meshes connected to the export node
    # listConnections to exportMeshes attribute
    # exportMeshes attribute is used to connect to export meshes, exportMeshes is valid
    def returnConnectedMeshes(self,exportNode):
        meshes = cmds.listConnections((exportNode + ".exportMeshes"), source = False, destination = True)
        return meshes



    ########################################################################################################################################################
    #
    #                                                                                                   Animation export procs
    #
    ########################################################################################################################################################

    #  To copy the bind skeleton and connect the copy to the original bind
    #  duplicate hierarchy
    #  delete everything that is not a joint
    #  unlock all the joints
    #  connect the translates, rotates, and scales
    #  parent copy to the world
    #  add deleteMe attr
    #  No joints are children of anything but other joints
    @undo_pm
    def copyAndConnectSkeleton(self,origin):
        preffix = ''
        _origin = ''
        nameSpace = False

        if ':' in origin[:]:
            preffix = origin.split(':')[0] + ':'
            nameSpace = True
            #print preffix

        else:
            preffix = ''


        joints = self.create_export_joints_data()
        joints.append(['world',origin])
        new_skells = []
        joints.reverse()

        self.currentMainExportJoint = '_'.join(origin.split('_')[:-1]) + '_export'


        if origin != "ERROR" and cmds.objExists(origin):
            # joint[0] = padre , joint[1] = hijo
            for idx, joint in enumerate(joints):
                #print joint
                dupHierarchy = cmds.duplicate(joint[1], renameChildren=True)
                dup_root = dupHierarchy[0]
                cmds.parent(dup_root, world = True)

                new_skel = []
                if nameSpace:
                    new_skel = self.createSkelleton(dup_root, preffix)

                else:
                    new_skel = self.createSkelleton(dup_root)


                self.tagForGarbage(new_skel[0])

                if joint[0] == 'world':
                    try:
                        cmds.parent(new_skel[0], world = True)
                    except:
                        pass
                else:
                    newParent = '_'.join(joint[0].split('_')[:-1])
                    par = newParent + '_export'
                    cmds.parent(new_skel[0], par)


                self.unlockJointTransforms(new_skel[0])

                matchJoints = self.match_joints(new_skel,joint[1])
                attributes = ['translate','rotate','scale']

                for item in matchJoints:
                    try:
                        cmds.setAttr(item[1] + '.segmentScaleCompensate', 0)
                        self.unlockAttributes(item[1])
                    except:
                        pass

                    for attr in attributes:
                        for ch in 'XYZ':
                            source_attr = '{}.{}{}'.format(item[0],attr,ch)
                            destin_attr = '{}.{}{}'.format(item[1],attr,ch)
                            cmds.connectAttr(source_attr, destin_attr, force=True)

                # transform group fix

                trans = pm.PyNode(new_skel[0]).getParent()
                if not isinstance(trans, pm.nodetypes.Joint):
                    try:
                        #print trans.getParent().name()
                        cmds.delete(cmds.pointConstraint(trans.getParent().name(),trans.name()))
                    except:
                        pass

                    #############
                new_skells.append(new_skel)
        ########
        cmds.select(clear=True)
        cmds.select(self.currentMainExportJoint)
        cmds.select(hi=True)
        joints = cmds.ls(sl=True)
        cmds.select(clear=True)
        for jnt in joints:
            self.unlockAttributes(jnt)


        return new_skells

    ############################################################################
    #
    #
    @undo_pm
    def createSkelleton(self,object, preffix=''):
        # select hier to get all nodes in it ...
        pm.select(object)
        pm.select(hi=True)

        selection = pm.ls(sl=True, fl=True, l=True)
        pm.delete(cn=True)

        parent = selection[0]

        # iterate over the list got it from selection ..
        for itm in selection:
            node = pm.PyNode(itm)
            if isinstance(node, pm.nodetypes.PoseReader):
                par = node.getParent()
                pm.delete(par)
            elif isinstance(node, pm.nodetypes.Locator):
                pm.delete(node)

        ######################
        # Clean the selection
        pm.select(clear=True)

        returned_jnt = []
        pm.select(parent)
        pm.select(hi=True)
        joints = cmds.ls(sl=True)

        for jnt in joints:
            suffix = 'export'
            splited = jnt.split('_')[:-1]
            newName = preffix + '_'.join(splited) + '_' + suffix
            try:
                cmds.rename(jnt, newName)
            except:
                pass

            returned_jnt.append(newName)

        for idx,itm in  enumerate(returned_jnt):
            if not itm.endswith('export'):
                cmds.delete(itm)
                poped = returned_jnt.pop(idx)
                del(poped)

        ################
        cmds.select(clear=True)

        return returned_jnt
        ####################################################

    ################################Y#######################################################
    # match the export joints with the rig ones
    #
    def match_joints(self, jointlist, origin):
        joints_to = []
        origin_suff = origin.split('_')[-1]
        namespace = ''

        if ':' in origin[:]:
            namespace = origin.split(':')[0] + ':'
        else:
            namespace = namespace

        for jnt in jointlist:
            splited = jnt.split('_')[:-1]
            joined = '_'.join(splited)
            try:
                rig_jnt = cmds.ls('{}{}_{}'.format(namespace,joined,origin_suff))
                joints_to.append([rig_jnt[0], jnt])
            except:
                pass

        return joints_to

    #########################################################################################
    @undo_pm
    def unlockAttributes(self, node):
        for ch in 'trs':
            for att in 'xyz':
                name = '{}.{}{}'.format(node,ch,att)
                try:
                    cmds.setAttr(name, lock=False)

                except:
                    pass
        try:
            cmds.setAttr(node + '.visibility', lock=False)
        except: pass


    ###########################################################
    @undo_pm
    def unlockJointTransforms(self,root):
        hierarchy = cmds.listRelatives(root, ad=True, f=True)
        hierarchy.append(root)

        for current in hierarchy:
            for ch in 'trs':
                for att in 'xyz':
                    name = '{}.{}{}'.format(current,ch,att)
                    try:
                        cmds.setAttr(name, lock=False)
                    except:
                        pass


    #               Translate export skeleton to origin. May or may not kill origin animation depending on input
    #               bake the animation onto our origin
    #               create an animLayer
    #               animLayer will either be additive or overrride depending on parameter we pass
    #               add deleteMe attr to animLayer
    #               move to origin
    #               origin is valid, end frame is greater than start frame, zeroOrigin is boolean
    @undo_pm
    def transformToOrigin(self,origin, startFrame, endFrame, zeroOrigin):
        cmds.bakeResults(origin, t = (startFrame, endFrame), at= ["rx","ry","rz","tx","ty","tz","sx","sy","sz"], hi="none")

        cmds.select(clear = True)
        cmds.select(origin)

        newAnimLayer = ""

        if zeroOrigin:
            #kills origin animation
            newAnimLayer = cmds.animLayer(aso=True, mute = False, solo = False, override = True, passthrough = True, lock = False)
            cmds.setAttr (newAnimLayer + ".rotationAccumulationMode", 0)
            cmds.setAttr (newAnimLayer + ".scaleAccumulationMode", 1)
        else:
            #shifts origin animation
            newAnimLayer = cmds.animLayer(aso=True, mute = False, solo = False, override = False, passthrough = False, lock = False)

        self.tagForGarbage(newAnimLayer)

        #turn anim layer on
        cmds.animLayer(newAnimLayer, edit = True, weight = 1)
        cmds.setKeyframe(newAnimLayer + ".weight")

        #move origin animation to world origin
        cmds.setAttr(origin + ".translate", 0,0,0)
        cmds.setAttr(origin + ".rotate", 0,0,0)
        cmds.setKeyframe(origin, al=newAnimLayer, t=startFrame)

        ###############################################################################

    ########################################################################################################################################################
    #
    #                                                                                                        AnimLayers procs
    #
    ########################################################################################################################################################

    #               Record the animLayer settings used in animation and store in
    #               the exportNode as a string
    #               List all the animLayers. Query their mute and solo attributes.
    #               List them in one single string
    #               Uses ; as sentinal value to split seperate animLayers
    #               Uses , as sentinal value to split seperate fields for animLayer
    #               Uses = as sentinal value to split seperate attrs from thier values in field

    def setAnimLayerSettings(self, exportNode): # THIS IS THE RECORD BUTTON IN THEE UI

        if not cmds.attributeQuery("animLayers", node=exportNode, exists=True):
            self.addFBXNodeAttrs(exportNode)

        animLayers = cmds.ls(type = "animLayer")

        animLayerCommandStr = ""

        for curLayer in animLayers:
            mute = cmds.animLayer(curLayer, query = True, mute = True)
            solo = cmds.animLayer(curLayer, query = True, solo = True)
            animLayerCommandStr += (curLayer + ", mute = " + str(mute) + ", solo = " + str(solo) + ";")

        cmds.setAttr(exportNode + ".animLayers", animLayerCommandStr, type = "string")


    #               Set the animLayers based on the string value in the exportNode
    #               Use pre-defined sentinal values to split the string for seperate animLayers
    #               And parse out the attributes and their values, then set
    #               Uses ; as sentinal value to split seperate animLayers
    #               Uses , as sentinal value to split seperate fields for animLayer
    #               Uses = as sentinal value to split seperate attrs from thier values in field
    #               order is Layer, mute, solo
    def setAnimLayersFromSettings(self, exportNode):  # THIS IS THE PREVIEW BUTTON

        if cmds.objExists(exportNode)and cmds.objExists(exportNode + ".animLayers"):
            animLayersRootString = cmds.getAttr(exportNode + ".animLayers", asString = True)

            if animLayersRootString:
                animLayerEntries = animLayersRootString.split(";")

                for curEntry in animLayerEntries:
                    if curEntry:
                        fields = curEntry.split(",")

                        animLayerField = fields[0]
                        curMuteField = fields[1]
                        curSoloField = fields[2]

                        muteFieldStr = curMuteField.split(" = ")
                        soloFieldStr = curMuteField.split(" = ")

                        #convert strings to bool values
                        muteFieldBool = True
                        soloFieldBool = True

                        if muteFieldStr[1] != "True":
                            muteFieldBool = False

                        if soloFieldStr[1] != "True":
                            soloFieldBool = False

                        cmds.animLayer(animLayerField, edit = True, mute = muteFieldBool, solo = soloFieldBool)


    #################################################################
    def clearAnimLayerSettings(self, exportNode): # THIS IS THE CLEAR BUTTON ....
        cmds.setAttr(exportNode + ".animLayers", "", type = "string")


    ########################################################################################################################################################
    #
    #                                                                                                           Export procs
    #
    ########################################################################################################################################################

    ######################################################################################
    # EXPORT MAIN PROCESS
    #
    @undo_pm
    def back_to_name(self,origin):
        pm.select(origin)
        pm.select(hi=True)
        sel = pm.ls(sl=True, l=True)
        pm.select(clear=True)

        main = []

        for idx,obj in enumerate(sel):
            node = pm.PyNode(obj)
            splited = obj.split('_')[:-1]
            joined = '_'.join(splited) + '_Bind'
            
            newName = joined
            if ':' in joined[:]:
                newName = joined.split(':')[1:][0]

            else:
                newName = joined
                
            #print newName
            pm.rename(node, newName)
            self.makeVisible(node.name())
            if idx == 0:
                main.append(node)
    
        pm.select(main[0])
        pm.select(hi=True)
        print(main[0])


    ########################################################################################
    def exportFBX(self,exportNode):
        #curWorkspace = cmds.workspace(q=True, rd=True)
        fileName = cmds.getAttr(exportNode + ".exportName")

        if fileName:
            newFBX =  fileName
            cmds.file(newFBX, force = True, type = 'FBX export', pr=True, es=True)
        else:
            cmds.warning("No Valid Export Filename for Export Node " + exportNode + "\n")

    ########################################################################################


    ########################################################################################
    # EXPORT ANIMATION
    #

    def exportFBXAnimation(self, exportNode, characterName=None):

        self.clearGarbage()
        characters = []

        if characterName is not None:
            characters.append(characterName)
        else:
            characters.append(None)


        for curCharacter in characters:
            origin = self.current_origin
   

            exportNodes = []

            if exportNode:
                exportNodes.append(exportNode)
            else:
                exportNodes = self.current_exportNodes['animation']
                 

            for curExportNode in exportNodes:
                test = self.returnConnectedMeshes(curExportNode)
                
                
                if cmds.getAttr(curExportNode + ".export") and origin != "ERROR" and not test:
                    
                    exportRig = self.copyAndConnectSkeleton(origin)
                    startFrame = cmds.playbackOptions(query=True, minTime=1)
                    endFrame = cmds.playbackOptions(query=True, maxTime=1)

                    subAnimCheck = cmds.getAttr(curExportNode + ".useSubRange")

                    if subAnimCheck:
                        startFrame = cmds.getAttr(curExportNode + ".startFrame")
                        endFrame = cmds.getAttr(curExportNode + ".endFrame")
                        print('framessss')

                    if cmds.getAttr(curExportNode + ".moveToOrigin"):
                        newOrigin = cmds.listConnections(origin + ".translateX", source = False, d = True)
                        zeroOriginFlag = cmds.getAttr(curExportNode + ".zeroOrigin")
                        self.transformToOrigin(newOrigin[0], startFrame, endFrame, zeroOriginFlag)

                    cmds.select(clear = True)
                    self.back_to_name(exportRig[0])

                    self.setAnimLayersFromSettings(curExportNode)

                    #print(curExportNode)
                
                    mel.eval("SIP_SetFBXExportOptions_animation(" + str(startFrame) + "," + str(endFrame) + ")")

                    
                    # HERE IS WHERE I CALL THE EXPORT COMAND
                    self.exportFBX(curExportNode)
                    print ('Exported!!!!!!!')
                #print(curExportNode)
                ######### CLEAN THE GARBAGE AFTER THE EXPORT
                self.clearGarbage()
                ###
       
    #########################################################################################
    # EXPORT CHARACTER
    # the mesh ......
    @contextmanager
    def breakSkeleton(self, origin, hierchy, meshes):
        parentNode = cmds.listRelatives(origin, parent=True, fullPath = True)
        roots = self.current_character_data[1]
        parents = {}

        # store the normal parent for each root and save it
        for root in roots:
            parent = cmds.listRelatives(root, parent=True, fullPath = True)[0]
            parents[parent] = root

        # esta es la herarquia q obtengo desde un methodo la q use para export aimation
        for bound in hierchy:
            if ':' in origin[:]:
                cmds.group( bound[1], parent=bound[0])
                
            
            else:
                
                cmds.parent(bound[1], bound[0])


        # parent the root main joint to thw world to export
        if parentNode:
            cmds.parent(origin, world = True)


        cmds.select(clear = True)
        cmds.select(origin, add = True)
        cmds.select(hi = True)
        jointsHierchy = cmds.ls(sl=True)
        cmds.select(meshes, add = True)

        for jnt in jointsHierchy:
            try:
                cmds.setAttr(jnt + '.segmentScaleCompensate', 0)
            except:
                pass

        # YYYYIIIIEEEEEELLLDDD !!!!!!!!!!!!!!!!!!!!!!
        yield

        # REPARENT EVERYTHING AGAIN !!
        cmds.select(clear=True)

        for jnt in jointsHierchy:
            try:
                cmds.setAttr(jnt + '.segmentScaleCompensate', 1)
            except:
                pass

        for key, val in parents.items():
            try:
                cmds.parent(val, key)
            except:
                pass

        if parentNode:
            try:
                # TRY JUST IN CASE THE ROOT TO ITS PARENT
                cmds.parent(origin, parentNode[0])
            except:
                pass


    #####################################################################
    # FBX EXPORT CHARACTER
    #
    @undo_pm
    def exportFBXCharacter(self, exportNode):
        origin = self.returnOrigin("")
        self.get_Meshes_to_Export()
        hierchy = self.create_export_joints_data()

        exportNodes = []

        if exportNode:
            exportNodes.append(exportNode)
        else:
            exportNodes = self.returnFBXExportNodes(origin)

        for curExportNode in exportNodes:
            if cmds.getAttr(curExportNode + ".export"):
                mel.eval("SIP_SetFBXExportOptions_model()")
                meshes = self.returnConnectedMeshes(curExportNode)

                with self.breakSkeleton(self.current_origin, hierchy, meshes ):
                    self.exportFBX(curExportNode)

        # DELETE THE GARBAGE AFTER EXPORT...
        self.clearGarbage()
        cmds.select(clear=True)



#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################

if __name__ == '__main__':

    exp = FBX_ExporterClass()
    # 1 - from mainControl sel will find the root folder and root joints
    sel = cmds.ls(sl=True)
    nodes = exp.get_nodes_in_proccess('nestor:Hitch_global_Ground_Ctrl')
    origin = nodes[1][0]
    ######exp.get_Meshes_to_Export()
    #print(origin)
    # 2 - will tag the selected joint as origin with the follow process
    exp.tagForOrigin(origin, nodes[0][0])
    #################exportRig = exp.copyAndConnectSkeleton(origin)
    #exp.tagForExportNode(origin)
    # 3 - Create export node
    # returns a string

    #print(exportNode)
    # 4 - connect to skeleton
    #exp.copyAndConnectSkeleton(origin)
    # 5 -  call export
    #exp.exportFBXAnimation(exp.current_exportNodes['animation'], 'nestor:')
    #exp.exportFBXAnimation(exp.current_exportNodes['animation'], 'nestor:')
    # 6 - export mesh caracheter
    #exp.exportFBXCharacter(exportNode)





