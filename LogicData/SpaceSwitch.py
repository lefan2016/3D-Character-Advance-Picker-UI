import maya.cmds as cmds
import maya.OpenMaya as om

sel = cmds.ls(sl=True)

def spaceSwitch_operation(node):
    spaces = []
    for item in node:       
        attributes = cmds.listAttr(item,  k=True, se=True, c=True)
        if attributes is not None:

            check = [itm  for itm in attributes if cmds.attributeQuery(itm, node=item, enum=True)]           
            if len(check) > 0:
                attribute = check[0]
                values = cmds.attributeQuery(attribute, node=item, le=True)[0].split(':')
                
                for idx, att in enumerate(values):
                    spaces.append([item,idx,attribute,att])
                    #print("['{}','{}','{}','{}']".format(item,idx,attribute,att))

    return spaces
            
data = spaceSwitch_operation(sel)

print(data)
#---------------------------------------------------------------------------------------------------------------------#
# defe function for head isolate
def Space_matching(array): 
    # checker::::
    node = array[0]
    index = array[1]
    attribute = array[2]
    space = array[3]
    
    max = cmds.xform(node, q=True, m=True, ws=1)
    formato = '{}.{}'.format(node,attribute)
    cmds.setAttr(formato, int(index))
    cmds.xform(node, m=max, ws=1)
    om.MGlobal.displayInfo("Node: {} now working on '{}' space ".format(node, space))


# call function for head Isolate        

#----------------------------------------------------------------------------------------------------#
