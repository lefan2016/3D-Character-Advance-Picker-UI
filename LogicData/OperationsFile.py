import maya.cmds       as cmds
import pymel.core      as pm
import maya.OpenMaya   as om
import pymel

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
#------------------------------------------------------------------------------------------------------------------------------#
class Operations(object):
    def __init__(self):
        super(Operations, self).__init__()
        variable = 'for testing pourposes'

    def getList(self,lista):
        centralControls = []
        left = []
        right = []
        for ctrl in lista:
            if '_r_' in ctrl:
                right.append(ctrl)
            elif '_l_' in ctrl:
                left.append(ctrl)
            else:
                centralControls.append(ctrl)

        mayor = max(left,right,key=len)
        menor = min(left,right,key=len)
        toDo  = []
        for itm in mayor:
            if '_r_' in itm:
                new = itm.replace('_r_','_l_')
                toDo.append([itm,new])

            elif '_l_' in itm:
                new = itm.replace('_l_','_r_')
                toDo.append([itm,new])

        return toDo , centralControls

    ############################?
    # Mirror the pose from left to right and vice versa
    #
    @undo_pm
    def mirrorPose(self,lista,left=True):
        if len(lista) == 0:
            om.MGlobal.displayWarning("# Select Objets in Scene ... - - ")
            return
        toDo, _ = self.getList(lista)
        attT = ['tx','ty','tz']
        attR = ['rx','ry','rz']
        #create the mirror function
        def mir(num):
            for ls in toDo:
                for att in attT:
                    try:
                        Trans = cmds.getAttr('{}.{}'.format(ls[num],att))
                        cmds.setAttr('{}.{}'.format(ls[int(not(num))],att),Trans)
                    except:
                        pass

                for att in attR:
                    try:
                        Rot = cmds.getAttr('{}.{}'.format(ls[num],att))
                        cmds.setAttr('{}.{}'.format(ls[int(not(num))],att),Rot)
                    except:
                        pass

        if left:
            mir(1)
        else:
            mir(0)
    #-------------------------------------------------------#
    # Flip the pose, and set a keyframes from one to other aswell, (this is for making cycles).
    #
    @undo_pm
    def flipPose(self,lista,keyframe=False):
        if len(lista) == 0:
            om.MGlobal.displayWarning("# Select Objets in Scene ... - - ")
            return

        toDo, CentralCtrl = self.getList(lista)
        attT = ['tx','ty','tz']
        attR = ['rx','ry','rz']

        def flip(ls):
            for att in attT:
                try:
                    TransR = cmds.getAttr('{}.{}'.format(ls[0],att))
                    TransL = cmds.getAttr('{}.{}'.format(ls[1],att))
                    cmds.setAttr('{}.{}'.format(ls[0],att),TransL)
                    cmds.setAttr('{}.{}'.format(ls[1],att),TransR)
                except:
                    pass

            for att in attR:
                try:
                    RotR = cmds.getAttr('{}.{}'.format(ls[0],att))
                    RotL = cmds.getAttr('{}.{}'.format(ls[1],att))
                    cmds.setAttr('{}.{}'.format(ls[0],att),RotL)
                    cmds.setAttr('{}.{}'.format(ls[1],att),RotR)
                except:
                    pass

        ###########################
        def flipCentral(central):
            for ctrl in central:
                for att in attT:
                    try:
                        if att != 'ty':
                            Trans = cmds.getAttr('{}.{}'.format(ctrl,att))
                            cmds.setAttr('{}.{}'.format(ctrl,att),Trans * - 1)
                    except:
                        pass

                for att in attR:
                    try:
                        if att != 'rx':
                            Rot = cmds.getAttr('{}.{}'.format(ctrl,att))
                            cmds.setAttr('{}.{}'.format(ctrl,att),Rot * - 1)
                    except:
                        pass

        #########################
        def flipKeys(lista):
            atts = lista[0]
            keyframe = lista[1]
            cur_time = cmds.currentTime(q=True)

            for ch in atts:
                source = cmds.getAttr(ch, time=keyframe)
                if '_r_' in ch:
                    dest = ch.replace('_r_','_l_')
                    cmds.setKeyframe(dest, t=(cur_time,cur_time),value=source)
                else:
                    dest = ch.replace('_l_','_r_')
                    cmds.setKeyframe(dest, t=(cur_time,cur_time),value=source)

        ###########################
        def flipCentralKeys(lista):
            atts = lista[0]
            keyframe = lista[1]
            cur_time = cmds.currentTime(q=True)

            for ch in atts:
                try:
                    source = cmds.getAttr(ch, time=keyframe)
                    cmds.setKeyframe(ch, t=(cur_time,cur_time) , value = source * (- 1))
                except:
                    pass

        ################################################################################
        # set up data:
        #
        if not keyframe:
            for ls in toDo:
                flip(ls)
            flipCentral(CentralCtrl)

        else:
            if len(toDo) > 0:
                for ls in toDo:
                    keys = self.findKeys(ls)
                    flip(ls)
                    for ex in keys:
                        flipKeys(ex)

            ## Central controls operation ##
            ##
            if len(CentralCtrl) > 0:
                centralKeys = self.findKeys(CentralCtrl)
                flipCentral(CentralCtrl)
                for data in centralKeys:
                    flipCentralKeys(data)

    #------------------------------------------------------------------------------------#
    # Search the keyframes in one site of the character to flip em all
    #

    def findKeys(self,lista):
        if len(lista) < 1:
            return

        data = []
        TRange = cmds.playbackOptions(q=1,max=True)
        frames = []
        for obj in lista:
            this = cmds.keyframe( obj, time=(0,TRange), query=True)
            if this != None:
                frames.append([obj,list(set(this))])
            else:
                frames.append([obj,this])

        for dts in frames:
            for item in dts:
                if isinstance(item , list):
                    for tm in item:
                        if tm != None:
                            curve = map(lambda itm: itm.split('_')[-1], cmds.keyframe( dts[0], time=(0,tm), query=True,name=True))
                            channels = map(lambda itm:'{}.{}'.format(dts[0],itm), curve)
                            data.append([channels,tm])
                else:
                    pass

        #print(data)
        return data

    ####################
    # Shape Visibility
    #
    @undo_pm
    def controlVisibility(self, lista, check):
        for itm in lista:
            node = pm.PyNode(itm)
            for shp in node.getShapes():
                try:
                    shp.visibility.set( check )
                except:
                    shp.lodVisibility.set( check )

    # -------------------------------------------------------------#
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

    @undo_pm
    def executeResetloop(self,sel):
        # Reset Attributes to default function.
        #
        def resetAttributes(node):
            attrs = self.getAttributes(node)
            for attr in attrs:
                default_value = pm.attributeQuery(attr, node=node, ld=True)[0]
                try:
                    node.attr(attr).set(default_value)
                    #print('node: {} - attr: {} - default: {}'.format(node,attr,default_value))
                except:
                    pass

        # loop through select items and set to default value transforms,shapes,extraShapes with Attributes.
        #
        for itm in sel:
            node = pm.PyNode(itm)
            resetAttributes(node)
            if node.getShape().listAttr(ud=True) > 0:
                resetAttributes(node.getShape())
            locs =  [obj for obj in node.getShapes() if isinstance(obj,pymel.core.nodetypes.Locator)]
            if len(locs) > 0:
                for loc in locs:
                     resetAttributes(loc)
    #--------------------------------------------------#
    @undo_pm
    def keyNotZero(self, items):
        for itm in items:
            node = pm.PyNode(itm)
            attrs = self.getAttributes(node)

            for att in attrs:
                long = pm.attributeQuery(att, node=node, longName=True )
                value = pm.getAttr(node + '.' + long)
                default= pm.attributeQuery(long, node=node, ld=True)[0]

                if float(value) != float(default):
                    object = '{}.{}'.format(node, long)
                    print('Attribute:{} - Default:{} - Now:{}'.format(object,default, value))
                    try:
                        pm.setKeyframe(node, attribute=long)
                    except:
                        pass

# --------------------------------------------------------------#

if __name__ == '__main__':
    SELECTION = cmds.ls(sl=True)
    op = Operations()
    #op.executeResetloop(SELECTION)
    #op.controlVisibility(BODYCONTROLS, True)
    #op.mirrorPose(lf=True,lista=FACECONTROLS)
    #op.mirrorPose(rt=True,lista=SELECTION)
    op.flipPose(lista=SELECTION, keyframe=True)
    #op.flipPose(lista=SELECTION)
    #op.keyNotZero(SELECTION)
