import maya.cmds as cmds
import maya.OpenMaya as om
from collections import OrderedDict
#----------------------------------------------------------------------------------------------------------------------------------------------#
def Hitch_L_LegSnap(prefix=''):
    #################
    ikfkValue = cmds.getAttr(prefix + "Leg_l_Attributes.IK_1_FK_0")
    fkNeutral = (42.6 + 43.6)
    ikLength = cmds.getAttr(prefix + "Hitch_lowerleg_l_IK_JNT.translateX") + cmds.getAttr(prefix + "Hitch_leg_end_l_IK_JNT.translateX")
    fkStretch = max((ikLength - fkNeutral ) / 2,0)
    ################################################################
    fk_procs = OrderedDict()
    ik_procs = OrderedDict()

    fk_procs = {prefix + 'Hitch_upperleg_l_FK_Ctrl':prefix + 'Hitch_upperleg_l_IK_JNT',
                prefix + 'Hitch_lowerleg_l_FK_Ctrl':prefix + 'Hitch_lowerleg_l_IK_JNT'}

    ik_procs = {prefix + 'Hitch_l_foot_IK_Ctrl':prefix + 'Hitch_l_foot_FK_Ctrl',
                prefix + 'Hitch_l_leg_PV_Ctrl':prefix + 'l_leg_PV_FK_ref'}

    ik_foot = [prefix + 'Hitch_l_heel_IK_Ctrl',prefix + 'Hitch_l_toesTip_IK_Ctrl',prefix + 'Hitch_l_ball_IK_Ctrl',prefix + 'Hitch_l_tillOut_Ctrl',prefix + 'Hitch_l_tillIn_Ctrl']

    ####################################
    if ikfkValue == 0: # SWITCHING TO IK
        for ik, fk in ik_procs.items():
            fk_pos = cmds.xform(fk, q=True, ws=True, m=True)
            cmds.xform(ik, ws=True, m=fk_pos)

        # foot ctrls
        for ctrl in ik_foot:
            cmds.xform(ctrl, ro = [0,0,0], t = [0,0,0])

        attr = cmds.listAttr(prefix + "Foot_l_IK_Animation_Values",  v=1, k=1)
        for att in attr:
            cmds.setAttr(prefix + "Foot_l_IK_Animation_Values.{}".format(att), 0 )

        # toes rot
        fk_toes_rot = cmds.xform(prefix + 'Hitch_l_toes_FK_Ctrl', q=True, ws=True, ro=True)
        cmds.xform(prefix + 'Hitch_l_toes_IK_Ctrl', ws=True, ro=fk_toes_rot)

        cmds.setAttr(prefix + "Leg_l_Attributes.IK_1_FK_0", 1)
        om.MGlobal.displayInfo(" You are now in IK system ")

    #####################################
    if ikfkValue == 1: # SWITCHING TO FK
        cmds.setAttr(prefix + "Leg_l_Attributes.FK_Stretch", fkStretch)

        for key, val in fk_procs.items():
            ik_rot = cmds.xform(val,q=True, ws=True, ro=True)
            cmds.xform(key, ws=True, ro = ik_rot)

        ik_foot = cmds.xform(prefix + 'Hitch_l_foot_IK_Ctrl', q=True, ws=True, m=True)
        cmds.xform(prefix + 'Hitch_l_foot_FK_Ctrl', ws=True, m=ik_foot)

        ik_toes_rot = cmds.xform(prefix + 'Hitch_l_toes_IK_Ctrl', q=True, ws=True, ro=True)
        cmds.xform(prefix + 'Hitch_l_toes_FK_Ctrl', ws=True, ro=ik_toes_rot)

        cmds.setAttr(prefix + "Leg_l_Attributes.IK_1_FK_0", 0)
        om.MGlobal.displayInfo(" You are now in FK system ")

#----------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------#
def Hitch_R_LegSnap(prefix=''):
    #################
    ikfkValue = cmds.getAttr(prefix + "Leg_r_Attributes.IK_1_FK_0")
    fkNeutral = (42.6 + 43.6)
    ikLength = cmds.getAttr(prefix + "Hitch_lowerleg_r_IK_JNT.translateX") + cmds.getAttr(prefix + "Hitch_leg_end_r_IK_JNT.translateX")
    fkStretch = max((ikLength - fkNeutral ) / 2,0)
    ################################################################
    fk_procs = OrderedDict()
    ik_procs = OrderedDict()

    fk_procs = {prefix + 'Hitch_upperleg_r_FK_Ctrl':prefix + 'Hitch_upperleg_r_IK_JNT',
                prefix + 'Hitch_lowerleg_r_FK_Ctrl':prefix + 'Hitch_lowerleg_r_IK_JNT'}

    ik_procs = {prefix + 'Hitch_r_foot_IK_Ctrl':prefix + 'Hitch_r_foot_FK_Ctrl',
                prefix + 'Hitch_r_leg_PV_Ctrl':prefix + 'r_leg_PV_FK_ref'}

    ik_foot = [prefix + 'Hitch_r_heel_IK_Ctrl',prefix + 'Hitch_r_toesTip_IK_Ctrl',prefix + 'Hitch_r_ball_IK_Ctrl',prefix + 'Hitch_r_tillOut_Ctrl',prefix + 'Hitch_r_tillIn_Ctrl']

    ####################################
    if ikfkValue == 0: # SWITCHING TO IK
        for ik, fk in ik_procs.items():
            fk_pos = cmds.xform(fk, q=True, ws=True, m=True)
            cmds.xform(ik, ws=True, m=fk_pos)

        # foot ctrls
        for ctrl in ik_foot:
            cmds.xform(ctrl, ro = [0,0,0], t = [0,0,0])

        attr = cmds.listAttr(prefix + "Foot_r_IK_Animation_Values",  v=1, k=1)
        for att in attr:
            cmds.setAttr(prefix + "Foot_r_IK_Animation_Values.{}".format(att), 0 )

        # toes rot
        fk_toes_rot = cmds.xform(prefix + 'Hitch_r_toes_FK_Ctrl', q=True, ws=True, ro=True)
        cmds.xform(prefix + 'Hitch_r_toes_IK_Ctrl', ws=True, ro=fk_toes_rot)

        cmds.setAttr(prefix + "Leg_r_Attributes.IK_1_FK_0", 1)
        om.MGlobal.displayInfo(" You are now in IK system ")

    #####################################
    if ikfkValue == 1: # SWITCHING TO FK
        cmds.setAttr(prefix + "Leg_r_Attributes.FK_Stretch", fkStretch)

        for key, val in fk_procs.items():
            ik_rot = cmds.xform(val,q=True, ws=True, ro=True)
            cmds.xform(key, ws=True, ro = ik_rot)

        ik_foot = cmds.xform(prefix + 'Hitch_r_foot_IK_Ctrl', q=True, ws=True, m=True)
        cmds.xform(prefix + 'Hitch_r_foot_FK_Ctrl', ws=True, m=ik_foot)

        ik_toes_rot = cmds.xform(prefix + 'Hitch_r_toes_IK_Ctrl', q=True, ws=True, ro=True)
        cmds.xform(prefix + 'Hitch_r_toes_FK_Ctrl', ws=True, ro=ik_toes_rot)

        cmds.setAttr(prefix + "Leg_r_Attributes.IK_1_FK_0", 0)
        om.MGlobal.displayInfo(" You are now in FK system ")

#----------------------------------------------------------------------------------------------------------------------------------------------#
def Hitch_R_arm_Snap(prefix=''):
    
    ikfkValue = cmds.getAttr(prefix +"Arm_r_Attributes.IK_1_FK_0")
    fkNeutral = (25.267 + 28.608)
    ikLength = cmds.getAttr(prefix +"Hitch_lowerarm_r_IK.tx") + cmds.getAttr(prefix +"hitch_arm_end_r_IK.tx")
    fkStretch = max((ikLength - fkNeutral ) / 2,0)
    auto_clav_value = cmds.getAttr(prefix + 'Arm_r_Attributes.Auto_Clavicle')
    
    # FK to IK
    if ikfkValue == 0:
        if auto_clav_value == 1:
            channel = ['rx','ry','rz']
            for ch in channel:
                val = cmds.getAttr(prefix + '{}.{}'.format('Hitch_r_clavicle_FK_ctrl_Auto', ch))
                cmds.setAttr(prefix + '{}.{}'.format('Hitch_r_clavicle_FK_Ctrl', ch), val)

            cmds.setAttr(prefix + 'Arm_r_Attributes.Auto_Clavicle',0)
                             
        clav_ik_pos = cmds.xform(prefix +"Hitch_r_clavicle_FK_Ctrl", q=1, ws=1, ro=1)
        cmds.xform(prefix +"hitch_clavicle_r_IK_Ctrl", ws=1, ro=clav_ik_pos)        
        
        pv_pos = cmds.xform(prefix +"Hitch_r_arm_PV_FKRef", q=1, ws=1, m=1)
        cmds.xform(prefix +"Hitch_r_arm_PV_Ctrl", ws=1, m=pv_pos)
        
        hand_pos = cmds.xform(prefix +"Hitch_r_hand_FK_Ctrl", q=1, ws=1, m=1)
        cmds.xform(prefix +"Hitch_r_hand_IK_Ctrl", ws=1, m=hand_pos)        
                        
        cmds.setAttr(prefix +"Arm_r_Attributes.IK_1_FK_0", 1)
        om.MGlobal.displayInfo(" You are now in IK system ")

    # IK to FK
    if ikfkValue == 1:
        cmds.setAttr(prefix +"Arm_r_Attributes.FK_Stretch", fkStretch)
        
        clav_pos = cmds.xform(prefix +"hitch_clavicle_r_IK_Ctrl", q=1, ws=1, ro=1)
        cmds.xform(prefix +"Hitch_r_clavicle_FK_Ctrl", ws=1, ro=clav_pos) 
            
        upper_rot = cmds.xform(prefix +"Hitch_upperarm_r_IK", q=1, ws=1, ro=1)
        cmds.xform(prefix +"Hitch_r_upperarm_FK_Ctrl", ws=1, ro=upper_rot)        

        lower_rot = cmds.xform(prefix +"Hitch_lowerarm_r_IK", q=1, ws=1, ro=1)
        cmds.xform(prefix +"Hitch_r_lowerarm_FK_Ctrl", ws=1, ro=lower_rot)          
        
        matrix = cmds.xform(prefix +"Hitch_r_hand_IK_Ctrl", q=1, ws=1, m=1)
        cmds.xform(prefix +"Hitch_r_hand_FK_Ctrl", ws=1, m=matrix)  
          
        cmds.setAttr(prefix +"Arm_r_Attributes.IK_1_FK_0", 0)
        om.MGlobal.displayInfo(" You are now in FK system ")
#----------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------#
def Hitch_L_arm_Snap(prefix=''):

    ikfkValue = cmds.getAttr(prefix +"Arm_l_Attributes.IK_1_FK_0")
    fkNeutral = (25.267 + 28.608)
    ikLength = cmds.getAttr(prefix +"Hitch_lowerarm_l_IK.tx") + cmds.getAttr(prefix +"hitch_arm_end_l_IK.tx")
    fkStretch = max((ikLength - fkNeutral ) / 2,0)
    print ('FKS: %s / FKN: %s   -    IKS: %s' %(fkStretch,fkNeutral, ikLength))
    auto_clav_value = cmds.getAttr(prefix + 'Arm_l_Attributes.Auto_Clavicle')
    
    # FK to IK
    if ikfkValue == 0:
        if auto_clav_value == 1:
            channel = ['rx','ry','rz']
            for ch in channel:
                val = cmds.getAttr(prefix + '{}.{}'.format('Hitch_l_clavicle_FK_ctrl_Auto', ch))
                cmds.setAttr(prefix + '{}.{}'.format('Hitch_l_clavicle_FK_Ctrl', ch), val)

            cmds.setAttr(prefix + 'Arm_l_Attributes.Auto_Clavicle',0)
                             
        clav_ik_pos = cmds.xform(prefix +"Hitch_l_clavicle_FK_Ctrl", q=1, ws=1, ro=1)
        cmds.xform(prefix +"hitch_clavicle_l_IK_Ctrl", ws=1, ro=clav_ik_pos)        
        
        pv_pos = cmds.xform(prefix +"Hitch_l_arm_PV_FKRef", q=1, ws=1, m=1)
        cmds.xform(prefix +"Hitch_l_arm_PV_Ctrl", ws=1, m=pv_pos)        
        
        hand_pos = cmds.xform(prefix +"Hitch_l_hand_FK_Ctrl", q=1, ws=1, m=1)
        cmds.xform(prefix +"Hitch_l_hand_IK_Ctrl", ws=1, m=hand_pos)   
                             
        cmds.setAttr(prefix +"Arm_l_Attributes.IK_1_FK_0", 1)
        om.MGlobal.displayInfo(" You are now in IK system ")

    # IK to FK
    if ikfkValue == 1:       
        cmds.setAttr(prefix +"Arm_l_Attributes.FK_Stretch", fkStretch) 
        
        clav_pos = cmds.xform(prefix +"hitch_clavicle_l_IK_Ctrl", q=1, ws=1, ro=1)
        cmds.xform(prefix +"Hitch_l_clavicle_FK_Ctrl", ws=1, ro=clav_pos) 
            
        upper_rot = cmds.xform(prefix +"Hitch_upperarm_l_IK", q=1, ws=1, ro=1)
        cmds.xform(prefix +"Hitch_l_upperarm_FK_Ctrl", ws=1, ro=upper_rot)        

        lower_rot = cmds.xform(prefix +"Hitch_lowerarm_l_IK", q=1, ws=1, ro=1)
        cmds.xform(prefix +"Hitch_l_lowerarm_FK_Ctrl", ws=1, ro=lower_rot)          
        
        matrix = cmds.xform(prefix +"Hitch_l_hand_IK_Ctrl", q=1, ws=1, m=1)
        cmds.xform(prefix +"Hitch_l_hand_FK_Ctrl", ws=1, m=matrix)  
               
        cmds.setAttr(prefix +"Arm_l_Attributes.IK_1_FK_0", 0)
        om.MGlobal.displayInfo(" You are now in FK system ")
#----------------------------------------------------------------------------------------------------------------------------------------------#


#----------------------------------------------------------------------------------------------------------------------------------------------#

if __name__ == '__main__':
    #Hitch_R_LegSnap()
    #Hitch_L_LegSnap()
    #Hitch_R_arm_Snap()
    Hitch_L_arm_Snap()
