"""

What Can This Program Do?
- This program creates a full body rig for a biped character.
- This program takes three parameters: the root joint of the bind skeleton chain, the spine curve, and the mesh of the character.
- It uses this selection input and UI input for controller radius to create a full rig for the entire body.
- The center controllers of the setup will be the generic dark blue, with the root controller being yellow.
- The left controllers of the setup will be blue, and right controllers will be red.

Notes for Prior Joint Creation:
- The spine should have 5 joints.
- The head and neck should have 3 joints.
- The arms should have 11 joints each.
- The legs should have 9 joints each.


"""


# ***** IMPORTING MODULES *****


from maya import cmds


# ***** FUNCTION DEFINITIONS *****


# **** SPINE CREATION ****


# *** Function for Creating Lists Based on Selection ***
def checkSelection():
    	objList = cmds.ls(sl=1)
    	if len(objList) < 1:
        	cmds.error("Please select an object.")
    	return objList
    	
# *** Duplicating Chest Joints from Bind Chain for Later Use ***
def getSpineJoints(rad, rootJnt, spineCurve):
    
    # Creating Bind Joint Chain
    for obj in cmds.listRelatives(rootJnt):
        if ('Spine' in obj) or ('spine' in obj):
            Bbase = obj
        else:
            pelvisJnt = obj
    Bchain = cmds.listRelatives(Bbase, ad=True, type='joint')
    Bchain.reverse()
    Bchain.insert(0, Bbase)
    
    # Creating IK Spine Joint Chain  
    spineChain = cmds.duplicate(Bchain, name='Spine_Chain', renameChildren=True)
    sChest = spineChain[4]
    chestChildren = cmds.listRelatives(sChest)
    for child in chestChildren:
        cmds.delete(child)
    cmds.parent(spineChain[0], world=True)
    
    # Renaming Spine Joint Chain
    newSpineChain = []
    for i in range(0, 5):
        if i == 4:
            name = 'IK_Chest_j'
        else:
            name = 'IK_Spine_' + str((i+1)) + '_j'
        cmds.rename(spineChain[i], name)
        newSpineChain.append(name)
        
    # Hiding IK Chains
    cmds.hide(newSpineChain[0])
    
    # Returning Necessary Items
    return rootJnt, pelvisJnt, Bchain, newSpineChain, spineCurve
    
# *** Creating IK Spline, Curve, and Driver Joints ***
def createChestSpline(rad, rootJnt, spineCurve):
    rootJnt, pelvisJnt, Bchain, IKchain, spineCurve = getSpineJoints(rad, rootJnt, spineCurve)
    
    # Creating IK Spline
    spineIK = cmds.ikHandle(sj=IKchain[0], ee=IKchain[-1], sol='ikSplineSolver', c=spineCurve, ccv=False, pcv=False)[0]
    cmds.rename(spineIK, 'Spine_IKhandle')
    spineIK = 'Spine_IKhandle'
    cmds.hide(spineIK)
    
    # Getting Top and Bottom Positions
    cmds.select(clear=True)
    bottomPos = []
    topPos = []
    duplicateJnt = cmds.duplicate(IKchain[-1])[0]
    cmds.parent(duplicateJnt, world=True)
    for axis in 'XYZ':
        bottomPos.append(cmds.getAttr(IKchain[0] + '.translate' + axis))
        topPos.append(cmds.getAttr(duplicateJnt + '.translate' + axis))
    cmds.delete(duplicateJnt)
    
    # Making Top and Bottom Joints
    bottomDriver = cmds.joint(p=bottomPos, name='baseSpine_j')
    cmds.select(clear=True)
    topDriver = cmds.joint(p=topPos, name='Chest_j')
    cmds.select(clear=True)
    cmds.parent(topDriver, bottomDriver)
    
    # Making Middle Joint
    midPos = []
    for i in range(0,3):
        pos = ((bottomPos[i] + topPos[i])/2)
        midPos.append(pos)
    midDriver = cmds.joint(p=midPos, name='midSpine_j')
    cmds.parent(midDriver, bottomDriver)
    cmds.parent(topDriver, midDriver)
    
    # Skinning Driver Joints to Curve
    driverChain = [bottomDriver, midDriver, topDriver]
    cmds.skinCluster(driverChain, spineCurve, mi=2, name='SpineCurve_SkinCluster')
    
    # Painting Curve Weights
    cmds.skinPercent('SpineCurve_SkinCluster', spineCurve + '.cv[0]', transformValue=[(bottomDriver, 1.0)])
    cmds.skinPercent('SpineCurve_SkinCluster', spineCurve + '.cv[1]', transformValue=[(bottomDriver, 1.0)])
    cmds.skinPercent('SpineCurve_SkinCluster', spineCurve + '.cv[2]', transformValue=[(bottomDriver, 0.5), (midDriver, 0.5)])
    cmds.skinPercent('SpineCurve_SkinCluster', spineCurve + '.cv[3]', transformValue=[(midDriver, 1.0)])
    cmds.skinPercent('SpineCurve_SkinCluster', spineCurve + '.cv[4]', transformValue=[(midDriver, 0.5), (topDriver, 0.5)])
    cmds.skinPercent('SpineCurve_SkinCluster', spineCurve + '.cv[5]', transformValue=[(topDriver, 1.0)])
    cmds.skinPercent('SpineCurve_SkinCluster', spineCurve + '.cv[6]', transformValue=[(topDriver, 1.0)])
    
    return rootJnt, pelvisJnt, Bchain, IKchain, driverChain, spineCurve, spineIK
    
# *** Creating and Implementing Chest Controllers ***    
def createChestControllers(rad, rootJnt, spineCurve):
    rootJnt, pelvisJnt, Bchain, IKchain, driverChain, spineCurve, spineIK = createChestSpline(rad, rootJnt, spineCurve)
    
    # Creating and Positioning Chest Controllers
    baseSpineGrp = 0
    names = ['baseSpine', 'midSpine', 'Chest']
    for i in range(0,3):
        
        # Determining Controller Radius
        if i == 0:
            newRad = rad + 3
        elif i == 1:
            newRad = rad + 5
        else:
            newRad = rad + 7
        
        # Positioning Controllers
        spineCtrl = cmds.circle(name = names[i] + '_Ctrl', r=newRad)[0]
        spineGrp = cmds.group(spineCtrl, name = names[i] + '__Offset')
        pointConst = cmds.pointConstraint(driverChain[i], spineGrp)
        cmds.delete(pointConst)
        currentX = cmds.getAttr(spineGrp + '.rotateX')
        cmds.setAttr(spineGrp + '.rotateX', currentX + 90)
        
        # Storing Base Spine Group for Later
        if i == 0:
            baseSpineGrp = spineGrp
        
    # Creating Controller Hierarchy
    cmds.parent(names[2] + '__Offset', names[1] + '_Ctrl')
    cmds.parent(names[1] + '__Offset', names[0] + '_Ctrl')
    for i in range(0,3):
        cmds.parent(names[i] + '_j', names[i] + '_Ctrl')
        
    # Parenting Spine Controllers to Bind
    for i in range(0,4):
        cmds.parentConstraint(IKchain[i], Bchain[i], mo=True)
    cmds.parentConstraint('Chest_Ctrl', Bchain[4], mo=True)
    
    # Hiding Driving Joints
    for jnt in driverChain:
        cmds.hide(jnt)
    
    # Returning Items
    return rootJnt, pelvisJnt, Bchain, IKchain, driverChain, spineCurve, spineIK, baseSpineGrp
    
# *** Creating Controls for and Connecting Spine to Root and Pelvis 
def createRootAndPelvis(rad, rootJnt, spineCurve):
    rootJnt, pelvisJnt, Bchain, IKchain, driverChain, spineCurve, spineIK, baseSpineGrp = createChestControllers(rad, rootJnt, spineCurve)
    
    # Positioning Root Control
    rootRad = rad + 10
    rootCtrl = cmds.circle(name = 'Root_Ctrl', r=rootRad)[0]
    cmds.color(rootCtrl, rgb=[1,1,0])
    rootGrp = cmds.group(rootCtrl, name = 'Root__Offset')
    pointConst = cmds.pointConstraint(rootJnt, rootGrp)
    cmds.delete(pointConst)
    currentX = cmds.getAttr(rootGrp + '.rotateX')
    cmds.setAttr(rootGrp + '.rotateX', currentX + 90)
    
    # Moving Root Control Up fron Pelvis
    cmds.select(rootCtrl + '.cv[0:7]')
    cmds.move(0, rad/2, 0, r=True)
    cmds.select(clear=True)
    
    # Positioning Pelvis Control
    pelvisRad = rad + 6
    pelvisCtrl = cmds.circle(name = 'Pelvis_Ctrl', r=pelvisRad)[0]
    pelvisGrp = cmds.group(pelvisCtrl, name = 'Pelvis__Offset')
    pointConst = cmds.pointConstraint(pelvisJnt, pelvisGrp)
    cmds.delete(pointConst)
    currentX = cmds.getAttr(pelvisGrp + '.rotateX')
    cmds.setAttr(pelvisGrp + '.rotateX', currentX + 90)
    
    # Implementing Controllers
    cmds.parent(baseSpineGrp, rootCtrl)
    cmds.parent(pelvisGrp, rootCtrl)
    cmds.parentConstraint(rootCtrl, rootJnt, mo=True)
    cmds.parentConstraint(pelvisCtrl, pelvisJnt, mo=True)
    
    return rootJnt, pelvisJnt, Bchain, IKchain, driverChain, spineCurve, spineIK, baseSpineGrp
    
# *** Setting Up Advanced Twist on Spine IK Handle ***
def setSpineAdvancedTwist(rad, rootJnt, spineCurve):
    rootJnt, pelvisJnt, Bchain, IKchain, driverChain, spineCurve, spineIK, baseSpineGrp = createRootAndPelvis(rad, rootJnt, spineCurve)
    
    # Enabling and Setting Up Advanced Twist
    cmds.setAttr(spineIK + '.dTwistControlEnable', 1)
    cmds.setAttr(spineIK + '.dWorldUpType', 4)
    cmds.setAttr(spineIK + '.dWorldUpAxis', 4)
    cmds.connectAttr('Pelvis_Ctrl.worldMatrix[0]', spineIK + '.dWorldUpMatrix', f=True)
    cmds.connectAttr('Chest_Ctrl.worldMatrix[0]', spineIK + '.dWorldUpMatrixEnd', f=True)
    
    # Returning Necessary Items
    return Bchain
    
    
# **** CREATING HEAD AND NECK ****
    
    
# *** Getting Necessary Joint Chains for Neck ***
def getNeckJoints(rad, neckJnt, chestBchain, mesh):
    
    # Creating Bind Joint Chain
    Bchain = cmds.listRelatives(neckJnt, ad=True, type='joint')
    Bchain.reverse()
    Bchain.insert(0, neckJnt)

    # Creating IK Joint Chain
    IKchain = cmds.duplicate(Bchain, name='Neck_Chain', renameChildren=True)
    cmds.parent(IKchain[0], world=True)
    names = ['IK_Neck1_j', 'IK_Neck2_j', 'IK_Head_j']
    newIKchain = []
    for i in range(0,3):
        cmds.rename(IKchain[i], names[i])
        newIKchain.append(names[i])
    
    # Hiding IK Chain
    cmds.hide(newIKchain[0])
    
    # Returning Items
    return Bchain, newIKchain

# *** Creating IK Spline Curve and Driving Joints ***
def createNeckSpline(rad, neckJnt, chestBchain, mesh):
    Bchain, IKchain = getNeckJoints(rad, neckJnt, chestBchain, mesh)
    
    # Creating Neck IK Spline Handle
    neckIK, neckEffector, neckCurve = cmds.ikHandle(sj=IKchain[0], ee=IKchain[-1], sol='ikSplineSolver')
    cmds.rename(neckCurve, 'neckCurve')
    neckCurve = 'neckCurve'
    cmds.rename(neckIK, 'Neck_IKhandle')
    neckIK = 'Neck_IKhandle'
    cmds.hide(neckIK)
    
    # Getting Top and Bottom Positions
    cmds.select(clear=True)
    bottomPos = []
    topPos = []
    duplicateJnt = cmds.duplicate(IKchain[-1])[0]
    cmds.parent(duplicateJnt, world=True)
    for axis in 'XYZ':
        bottomPos.append(cmds.getAttr(IKchain[0] + '.translate' + axis))
        topPos.append(cmds.getAttr(duplicateJnt + '.translate' + axis))
    cmds.delete(duplicateJnt)
    
    # Making Top and Bottom Joints
    bottomDriver = cmds.joint(p=bottomPos, name='Neck_j')
    cmds.select(clear=True)
    topDriver = cmds.joint(p=topPos, name='Head_j')
    cmds.select(clear=True)
    cmds.parent(topDriver, bottomDriver)
    cmds.select(clear=True)
    
    # Skinning Driver Joints to Curve
    driverChain = [bottomDriver, topDriver]
    cmds.skinCluster(driverChain, neckCurve, mi=2, name='NeckCurve_SkinCluster')
    cmds.hide(driverChain[0])
    
    # Painting Curve Weights
    cmds.skinPercent('NeckCurve_SkinCluster', neckCurve + '.cv[0]', transformValue=[(bottomDriver, 1.0)])
    cmds.skinPercent('NeckCurve_SkinCluster', neckCurve + '.cv[1]', transformValue=[(bottomDriver, 1.0)])
    cmds.skinPercent('NeckCurve_SkinCluster', neckCurve + '.cv[2]', transformValue=[(topDriver, 1.0)])
    cmds.skinPercent('NeckCurve_SkinCluster', neckCurve + '.cv[3]', transformValue=[(topDriver, 1.0)])
    
    # Returning Items
    return Bchain, IKchain, driverChain, neckCurve, neckIK
    
# *** Creating and Implementing Neck Controllers ***
def createNeckControllers(rad, neckJnt, chestBchain, mesh):
    Bchain, IKchain, driverChain, neckCurve, neckIK = createNeckSpline(rad, neckJnt, chestBchain, mesh)
    
    # Positioning Controllers
    names = ['Neck', 'Head']
    for i in range(0,2):
        neckCtrl = cmds.circle(name = names[i] + '_Ctrl', r=rad+3)[0]
        neckGrp = cmds.group(neckCtrl, name = names[i] + '__Offset')
        pointConst = cmds.pointConstraint(driverChain[i], neckGrp)
        cmds.delete(pointConst)
        currentX = cmds.getAttr(neckGrp + '.rotateX')
        cmds.setAttr(neckGrp + '.rotateX', currentX + 90)
        
    # Fixing Head Control Positioning
    bbox = cmds.xform(mesh, bb=True, query=True)
    for i in range(0,8):
        cmds.select('Head_Ctrl.cv[' + str(i) + ']') 
        cmds.move(bbox[4], moveY=True, absolute=True)
        cmds.select(clear=True)
        
    # Creating Controller Hierarchy
    cmds.parent(names[1] + '__Offset', names[0] + '_Ctrl')
    for i in range(0,2):
        cmds.parent(names[i] + '_j', names[i] + '_Ctrl')

    # Parenting Spine Controllers to Bind
    for i in range(0,2):
        cmds.parentConstraint(IKchain[i], Bchain[i], mo=True)
    cmds.parentConstraint('Head_Ctrl', Bchain[2], mo=True)

    # Hiding Driving Joints
    for jnt in driverChain:
        cmds.hide(jnt)
        
    # Returning Items
    return Bchain, IKchain, driverChain, neckCurve, neckIK
    
# *** Setting Up Advanced Twist on Spine IK Handle ***
def setNeckAdvancedTwist(rad, neckJnt, chestBchain, mesh):
    Bchain, IKchain, driverChain, neckCurve, neckIK = createNeckControllers(rad, neckJnt, chestBchain, mesh)
    
    # Enabling and Setting Up Advanced Twist
    cmds.setAttr(neckIK + '.dTwistControlEnable', 1)
    cmds.setAttr(neckIK + '.dWorldUpType', 4)
    cmds.setAttr(neckIK + '.dWorldUpAxis', 4)
    cmds.connectAttr('Neck_Ctrl.worldMatrix[0]', neckIK + '.dWorldUpMatrix', f=True)
    cmds.connectAttr('Head_Ctrl.worldMatrix[0]', neckIK + '.dWorldUpMatrixEnd', f=True)
    
    # Returning Items
    return Bchain, IKchain, driverChain, neckCurve, neckIK

def createHeadAim(rad, neckJnt, chestBchain, mesh):
    Bchain, IKchain, driverChain, neckCurve, neckIK = setNeckAdvancedTwist(rad, neckJnt, chestBchain, mesh)
    
    # Creating Head Aim Control
    aimCtrl = cmds.circle(name = 'Aim_Ctrl', r=rad)[0]
    aimGrp = cmds.group(aimCtrl, name = 'Aim__Offset')
    pointConst = cmds.pointConstraint('Head__Offset', aimGrp)
    cmds.delete(pointConst)
    
    # Positioning Aim Control and Setting Constraint
    currentZ = cmds.getAttr(aimGrp + '.translateZ')
    cmds.setAttr(aimGrp + '.translateZ', currentZ + (rad * 12))
    #aimConst = cmds.aimConstraint(aimCtrl, 'Head__Offset', wut='scene', aimVector=[1,0,0], upVector=[0,1,0])
    
    # Creating Head Aim Attribute
    cmds.addAttr(aimCtrl, longName='Head_Aim', attributeType='float', defaultValue=0.0, minValue=0.0, maxValue=1.0, keyable=True)
    #cmds.connectAttr(aimCtrl + '.Head_Aim', 'Head__Offset_aimConstraint1.Aim_CtrlW0')
    
    # Returning Necessary Items
    return 'Neck__Offset', 'Chest_Ctrl'
    
    
# **** CREATING ARMS ****


# *** Creating Lists of Joint Chains ***
def createArmChainLists(size, side, limb, topJoint):
    
    # Creating Bind Joint Chain  
    Btop = topJoint
    Bchain = cmds.listRelatives(Btop, ad=True, type='joint')
    Bchain.reverse()
    Bchain.insert(0, Btop)
    
    # Creating List of Joint Names
    if (limb == 'Arm'):
        jntNames = ['Shoulder', 'Elbow', 'Wrist']
    else:
        jntNames = ['Hip', 'Knee', 'Ankle']
    
    # Creating and Renaming IK Joint Chain    
    IKchain = cmds.duplicate(Bchain, name='IK_Chain', renameChildren=True)
    cmds.delete(IKchain[size])
    cmds.parent(IKchain[0], world=True)
    newIKchain = []
    baseIKchain = []
    for i in range(0, size):
        cmds.rename(IKchain[i], side + '_' + limb + '_IK_' + str((i+1)) + '_j')
        newIKchain.append(side + '_' + limb + '_IK_' + str((i+1)) + '_j')
    
    # Creating IK Base Joint Chain
    baseIKchain = cmds.duplicate(newIKchain, name='IK_Base_', renameChildren=True)
    for i in range(0, size):
        if i == ((size-1)/2):
            cmds.parent('IK_Base_' + str(((size-1)/2)), 'IK_Base_')
        if i == (size-1):
            cmds.parent('IK_Base_' + str((size-1)), 'IK_Base_' + str(((size-1)/2)))
    cmds.delete('IK_Base_' + str(1))
    cmds.delete('IK_Base_' + str(((size-1)/2)+1))
    
    # Renaming IK Base Joint Chain
    newBaseIKchain = []
    for i in range(0,3):
        if i == 0:
            cmds.rename('IK_Base_', side + '_' + limb + '_IK_Base_' + str((i+1)) + '_j')
        if i == 1:
            cmds.rename('IK_Base_' + str(((size-1)/2)), side + '_' + limb + '_IK_Base_' + str((i+1)) + '_j')
        if i == 2:
            cmds.rename('IK_Base_' + str((size-1)), side + '_' + limb + '_IK_Base_' + str((i+1)) + '_j')
        newBaseIKchain.append(side + '_' + limb + '_IK_Base_' + str((i+1)) + '_j')
    
    # Hiding IK Chains
    cmds.hide(newIKchain[0])
    cmds.hide(newBaseIKchain[0])

    # Creating FK Joint Chain  
    FKchain = cmds.duplicate(Bchain, name='FK_Chain', renameChildren=True)
    cmds.delete(FKchain[size])
    cmds.parent(FKchain[0], world=True)
    newFKchain = []
    for i in range(0, size):
        cmds.rename(FKchain[i], side + '_' + limb + '_FK_' + str((i+1)) + '_j')
        newFKchain.append(side + '_' + limb + '_FK_' + str((i+1)) + '_j')
    cmds.hide(newFKchain[0])
    
    # Adding Last Joint to Chains
    size = size + 1
    veryBottomIKjnt = cmds.duplicate(Bchain[size-1], name=side+'_'+limb+'_IK_'+str(size)+'_j', rc=True)[0]
    cmds.delete(cmds.listRelatives(veryBottomIKjnt))
    cmds.parent(veryBottomIKjnt, world=True)
    veryBottomFKjnt = cmds.duplicate(veryBottomIKjnt, name=side+'_'+limb+'_FK_'+str(size)+'_j')[0]
    cmds.parent(veryBottomIKjnt, side+'_'+limb+'_IK_'+str(size-1)+'_j')
    cmds.parent(veryBottomFKjnt, side+'_'+limb+'_FK_'+str(size-1)+'_j')
    newIKchain.append(veryBottomIKjnt)
    newFKchain.append(veryBottomFKjnt)
    
    return newIKchain, newBaseIKchain, newFKchain, Bchain

# *** Creating the Switch Controller ***
def createArmSwitchController(rad, size, side, limb, topJoint):
    IKchain, baseIKchain, FKchain, Bchain = createArmChainLists(size, side, limb, topJoint)
    
    # Determining Switch Radius
    if rad == 1:
        switchRad = 1
    else:
        switchRad = rad-2
    
    # Creating Switch and Group
    switchCtrl = cmds.circle(nr=(0,1,0), r=switchRad, name=side + '_' + limb + '_Switch_Ctrl')[0]
    switchCtrlGroup = cmds.group(switchCtrl, name=switchCtrl + '__Offset')
    
    # Coloring Control Based on Side
    if side == 'L':
        cmds.color(switchCtrl, rgb=(0, 0, 1))
    else:
        cmds.color(switchCtrl, rgb=(1, 0, 0))
    
    # Adding Attribeutes to the Switch
    cmds.addAttr(switchCtrl, longName='IK_Blend', attributeType='float', defaultValue=1.0, minValue=0.0, maxValue=1.0, keyable=True)
    cmds.addAttr(switchCtrl, longName='IK_Visibility', attributeType='short', defaultValue=1, minValue=0, maxValue=1, keyable=True)
    cmds.addAttr(switchCtrl, longName='FK_Visibility', attributeType='short', defaultValue=1, minValue=0, maxValue=1, keyable=True)
    
    # Moving Switch Above End of Chain
    wristIndex = size
    parentConst = cmds.parentConstraint(Bchain[wristIndex], switchCtrlGroup)
    cmds.delete(parentConst)
    
    # Adjusting Switch Position Based on Limb Type
    if limb == 'Arm':
        currentX = cmds.getAttr(switchCtrlGroup + '.translateX')
        if side == 'L':
            cmds.setAttr(switchCtrlGroup + '.translateX', currentX + rad)
        else:
            cmds.setAttr(switchCtrlGroup + '.translateX', currentX - rad)
    else:
        currentX = cmds.getAttr(switchCtrlGroup + '.translateX')
        if side == 'L':
            cmds.setAttr(switchCtrlGroup + '.translateX', currentX + (rad*4))
        else:
            cmds.setAttr(switchCtrlGroup + '.translateX', currentX - (rad*4))
        cmds.setAttr(switchCtrlGroup + '.translateY', cmds.getAttr(switchCtrlGroup + '.translateY') + (rad*4))
        currentRot = cmds.getAttr(switchCtrlGroup + '.rotateX')
        cmds.setAttr(switchCtrlGroup + '.rotateX', currentRot + 90)
    newParentConst = cmds.parentConstraint(Bchain[wristIndex], switchCtrlGroup, mo=True)
    
    return IKchain, baseIKchain, FKchain, Bchain, switchCtrl

# *** Creating Controllers for IK and FK Joint Chains ***
def createArmJointControllers(rad, size, side, limb, topJoint):
    IKchain, baseIKchain, FKchain, Bchain, switchCtrl = createArmSwitchController(rad, size, side, limb, topJoint)
    
    # *** FK CONTROLS ***
    
    # Selecting Control Rotation Axis Based on Limb Type
    if limb == "Arm":
        axis = 'Y'
    else:
        axis = 'X'
    
    # Creating FK Controllers and Groups
    for i in range(0, size+1):
        
        # Determining Controller Size
        if i == 0:
            FKctrl = cmds.circle(name = FKchain[i] + '_Ctrl', r=rad+3, degree=1)[0]
        elif i == ((size-1)/2):
            FKctrl = cmds.circle(name = FKchain[i] + '_Ctrl', r=rad+3, degree=1)[0]
        elif i == size:
            FKctrl = cmds.circle(name = FKchain[i] + '_Ctrl', r=rad+3, degree=1)[0]
        else:
            FKctrl = cmds.circle(name = FKchain[i] + '_Ctrl', r=rad, degree=1)[0]
        
        # Determining Controller Color
        if side == 'L':
            cmds.color(FKctrl, rgb=(0, 0, 1))
        else:
            cmds.color(FKctrl, rgb=(1, 0, 0))
        
        # Positioning Each Controller        
        FKctrlGroup = cmds.group(FKctrl, name=FKctrl + '__Offset')
        parentConst = cmds.parentConstraint(FKchain[i], FKctrlGroup)
        cmds.delete(parentConst)
        
        currentCtrlRot = cmds.getAttr(FKctrlGroup + '.rotate' + axis)
        cmds.setAttr(FKctrlGroup + '.rotateY', currentCtrlRot + 90)
    
    # Creating Chain of FK Controllers and Groups
    for i in range(0, size+1):
        if i != 0:
            cmds.parent(FKchain[i] + '_Ctrl__Offset', FKchain[i-1] + '_Ctrl')
            
    # Constraining Corresponding Controls
    for i in range(0, size+1):
        if i == 0:
            cmds.parentConstraint(FKchain[i] + '_Ctrl', FKchain[i], mo=True)
        else:
            cmds.orientConstraint(FKchain[i] + '_Ctrl', FKchain[i], mo=True)
        
    # *** IK CONTROLS ***
    
    # Naming IK Controls Based on Limb Type
    if limb == "Arm":
        top = "Shoulder"
        bottom = "Wrist"
    else:
        top = "Hip"
        bottom = "Ankle"
    
    # Creating IK Handle and Controls for End of IK Chain
    IKhand = cmds.ikHandle(sj=baseIKchain[0], ee=baseIKchain[-1])[0]
    IKbottomCtrl = cmds.circle(name = side + '_IK_' + bottom + '_Ctrl', r=rad+2)[0]
    cmds.setAttr(IKbottomCtrl+'.rotateY', 90)
    cmds.makeIdentity(IKbottomCtrl, apply=True)
    cmds.select(IKbottomCtrl+'.cv[0:7]')
    cmds.rotate(90.0, 0, 0)
    cmds.select(clear=True)
    if side == 'L':
        cmds.color(IKbottomCtrl, rgb=(0, 0, 1))
    else:
        cmds.color(IKbottomCtrl, rgb=(1, 0, 0))
    cmds.addAttr(IKbottomCtrl, longName='Twist', attributeType='float', defaultValue=0.0, keyable=True)
    
    # Creating Controls for Top of IK Chain
    IKbottomCtrlGroup = cmds.group(IKbottomCtrl, name=IKbottomCtrl + '__Offset')
    IKtopCtrl = cmds.circle(name = side + '_IK_' + top + '_Ctrl', r=rad+2)[0]
    if side == 'L':
        cmds.color(IKtopCtrl, rgb=(0, 0, 1))
    else:
        cmds.color(IKtopCtrl, rgb=(1, 0, 0))
    IKtopCtrlGroup = cmds.group(IKtopCtrl, name=IKtopCtrl + '__Offset')
    
    # Positioning and Implementing Base IK Bottom Control 
    cmds.parent(IKbottomCtrlGroup, IKchain[-1])
    for trans in ['.translate', '.rotate']:
        for axis in 'XYZ':
            cmds.setAttr(IKbottomCtrlGroup + trans + axis, 0)
    cmds.parent(IKbottomCtrlGroup, world=True)
   
    cmds.pointConstraint(IKbottomCtrl, IKhand, mo=True)
    cmds.orientConstraint(IKbottomCtrl, baseIKchain[-1], mo=True)
    cmds.connectAttr(IKbottomCtrl + '.Twist', IKhand + '.twist', f=True)
    cmds.hide(IKhand)
    
    # Positioning and Implementing IK Top Control 
    parentConst = cmds.parentConstraint(IKchain[0], IKtopCtrlGroup)
    cmds.delete(parentConst)
    
    currentCtrlRot = cmds.getAttr(IKtopCtrlGroup + '.rotateY')
    cmds.setAttr(IKtopCtrlGroup + '.rotateY', currentCtrlRot + 90)
    
    cmds.pointConstraint(IKtopCtrl, baseIKchain[0], mo=True)
    
    # Parenting Base IK to IK Chain
    cmds.parentConstraint(baseIKchain[0], IKchain[0], sr=['x'], mo=True)
    cmds.parentConstraint(baseIKchain[1], IKchain[((size-1)/2)], mo=True)
    cmds.parentConstraint(baseIKchain[2], IKchain[size], mo=True)
    cmds.hide(baseIKchain[0])
    
    # Creating Proper Rotation if Arm Limb
    if limb == 'Arm':
        
        # *** UPPER ARM ROTATION ***
        
        # Creating Node and Connecting Base IK Shoulder
        upperMultDivNode = cmds.shadingNode('multiplyDivide', asUtility=True)
        cmds.connectAttr(baseIKchain[0]+'.rotateX', upperMultDivNode+'.input1X', force=True)
        cmds.setAttr(upperMultDivNode+'.input2X', 1.0/((size-1)/2.0))
        
        # Outputting Multiplied Number to Upper IK Arm Rotations
        for i in range(0, ((size-1)/2)):
            cmds.connectAttr(upperMultDivNode+'.outputX', IKchain[i]+'.rotateX', force=True) 
        
        # *** LOWER ARM ROTATION ***
        
        # Creating Proper Outliner Structure for Wrist
        cmds.parent(IKchain[-1], IKchain[((size-1)/2)])
        wristJnt = IKchain[-1]
        wristExtractJnt = cmds.duplicate(wristJnt, name=side+'_'+limb+'_WristExtractor_j')[0]
        handJnt = cmds.duplicate(wristJnt, name=side+'_'+limb+'_Hand_j')[0]
        if side == 'L':
            cmds.setAttr(handJnt+'.translateX', cmds.getAttr(handJnt+'.translateX')+5)
        else:
            cmds.setAttr(handJnt+'.translateX', cmds.getAttr(handJnt+'.translateX')-5)
        cmds.parent(handJnt, wristJnt)
        
        # Setting Up Wrist Extractor Calculations
        if side == 'L':
            cmds.aimConstraint(handJnt, wristExtractJnt, wut='none', aim=[1.0,0.0,0.0], u=[0.0,1.0,0.0])
        else:
            cmds.aimConstraint(handJnt, wristExtractJnt, wut='none', aim=[-1.0,0.0,0.0], u=[0.0,1.0,0.0])
        wristLoc = cmds.spaceLocator(name=side+'_IK_Wrist_Loc')[0]
        
        # Setting Up Wrist Locator to Inherit Calculations
        parentConst = cmds.parentConstraint(wristJnt, wristLoc)
        cmds.delete(parentConst)
        cmds.parent(wristLoc, wristJnt)
        cmds.orientConstraint(wristJnt, wristExtractJnt, wristLoc)
        
        # Transferring Calculation to Forearm Joints
        lowerMultDivNode01 = cmds.shadingNode('multiplyDivide', asUtility=True)
        cmds.connectAttr(wristLoc+'.rotateX', lowerMultDivNode01+'.input1X', force=True)
        cmds.setAttr(lowerMultDivNode01+'.input2X', -(10.0*(1.0/((size-1)/2.0))))
        lowerMultDivNode02 = cmds.shadingNode('multiplyDivide', asUtility=True)
        cmds.connectAttr(lowerMultDivNode01+'.outputX', lowerMultDivNode02+'.input1X')
        cmds.setAttr(lowerMultDivNode02+'.input2X', 1.0/((size-1)/2.0))
        
        # Outputting Multiplied Number to Lower IK Arm Rotations
        for i in range(((size-1)/2)+1, size):
            cmds.connectAttr(lowerMultDivNode02+'.outputX', IKchain[i]+'.rotateX', force=True) 
    
    # Connecting Controls to Visibility Attributes in Switch
    cmds.connectAttr(switchCtrl + '.FK_Visibility', FKchain[0] + '_Ctrl__Offset.visibility', f=True)
    cmds.connectAttr(switchCtrl + '.IK_Visibility', IKbottomCtrlGroup + '.visibility', f=True)
    cmds.connectAttr(switchCtrl + '.IK_Visibility', IKtopCtrlGroup + '.visibility', f=True)
    
    # Creating Controls for Fingers if Limb is Arm
    if limb == 'Arm':
        fingersGrp = createFingerCtrls(Bchain, switchCtrl, rad, size, side, topJoint)
    
    # Organizing Everything into Groups
    FKgroup = cmds.group(FKchain[0] + '_Ctrl__Offset', FKchain[0], name=side + '_FK_Arm__Group')
    IKjntGroup = cmds.group(IKchain[0], baseIKchain[0], name = side + '_IK_Arm_Joint__Group')
    IKgroup = cmds.group(IKbottomCtrlGroup, IKtopCtrlGroup, IKhand, IKjntGroup, name=side + '_IK_Arm__Group')
    
    return IKchain, baseIKchain, FKchain, Bchain, switchCtrl

# *** Creating Controls for Fingers ***
def createFingerCtrls(Bchain, switchCtrl, rad, size, side, topJoint):
    
    # Creating Empty Group to Put Finger Controls in Later
    fingersGrp = cmds.group(empty=True, name=side + '_Fingers_Group')
    parentConstr = cmds.parentConstraint(Bchain[size], fingersGrp)
    cmds.delete(parentConstr)
    
    # Creating Attributes for SDKs
    cmds.addAttr(switchCtrl, longName='_____________', attributeType='short', defaultValue=0, keyable=True)
    for fName in ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']:
        cmds.addAttr(switchCtrl, longName=fName + '_Curl', attributeType='float', defaultValue=0.0, keyable=True)
    for fName in ['Index', 'Middle', 'Ring', 'Pinky']:
        cmds.addAttr(switchCtrl, longName=fName + '_Spread', attributeType='float', defaultValue=0.0, keyable=True)
         
    # Creating Lists of Knuckles for Each Finger
    fingerList = cmds.listRelatives(Bchain[size])
    for finger in fingerList:
        if 'thumb' in finger.lower():
            jntNum = 3
        else:
            jntNum = 4
        
        knuckleList = cmds.listRelatives(finger, ad=True, type='joint')
        knuckleList.append(finger)
        knuckleList.reverse()
        for knuckle in knuckleList:
            knuckle.replace('_jB', '')
        
        for i in range(0, jntNum):
            # Creating Control for Each Knuckle
            if ('thumb' in finger.lower()) and (i == 0):
                knuckleCtrl = cmds.circle(name = knuckleList[i] + '_Ctrl', r=rad/2.5, degree=1)[0]
            else:
                knuckleCtrl = cmds.circle(name = knuckleList[i] + '_Ctrl', r=rad/4.0, degree=1)[0]
            
            # Determining Color of Control Based on Side
            if side == 'L':
                cmds.color(knuckleCtrl, rgb=(0, 0, 1))
            else:
                cmds.color(knuckleCtrl, rgb=(1, 0, 0))        
        
            # Positioning Each Controller        
            knuckleSDK = cmds.group(knuckleCtrl, name=knuckleCtrl + '__SDK')
            knuckleOffset = cmds.group(knuckleSDK, name=knuckleCtrl + '__Offset')
            parentConst = cmds.parentConstraint(knuckleList[i], knuckleOffset)
            cmds.delete(parentConst)
        
            currentCtrlRot = cmds.getAttr(knuckleOffset + '.rotateY')
            cmds.setAttr(knuckleOffset + '.rotateY', currentCtrlRot + 90)
    
        # Creating Chain of Knuckle Controllers and Groups
        for i in range(0, jntNum):
            if i != 0:
                cmds.parent(knuckleList[i] + '_Ctrl__Offset', knuckleList[i-1] + '_Ctrl')
            
        # Constraining Corresponding Controls
        for i in range(0, jntNum):
            if i == 0:
                cmds.parentConstraint(knuckleList[i] + '_Ctrl', knuckleList[i], mo=True)
            else:
                cmds.orientConstraint(knuckleList[i] + '_Ctrl', knuckleList[i], mo=True)               

        # Connecting SDK Groups to Attributes           
        for i in range(1, jntNum):
            if jntNum == 3:
                cmds.connectAttr(switchCtrl + '.Thumb_Curl', knuckleList[i] + '_Ctrl__SDK.rotateY',)
            else:
                for fName in ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']:
                    if fName.lower() in knuckleList[i].lower():
                        cmds.connectAttr(switchCtrl + '.' + fName + '_Curl', knuckleList[i] + '_Ctrl__SDK.rotateX')
                        cmds.connectAttr(switchCtrl + '.' + fName + '_Spread', knuckleList[i] + '_Ctrl__SDK.rotateY')
                        
        # Adding Everything to Fingers Group
        cmds.parent(knuckleList[0] + '_Ctrl__Offset', fingersGrp)
        
    # Making Fingers Follow the Arm
    cmds.parentConstraint(cmds.listRelatives(switchCtrl, parent=True)[0], fingersGrp, mo=True)
    
    return fingersGrp

# *** Creating Parent Constraints and SDKs for the Switch ***
def parentAndKeyArmJoints(rad, size, side, limb, topJoint):
    IKchain, baseIKchain, FKchain, Bchain, switchCtrl = createArmJointControllers(rad, size, side, limb, topJoint)
    
    for i in range(0, len(IKchain)):
        
        # Parenting Corresponding Joints
        IKconstr = cmds.parentConstraint(IKchain[i], Bchain[i], mo=True)
        IKattr = IKconstr[0] + '.' + IKchain[i] + 'W0'
        FKconstr = cmds.parentConstraint(FKchain[i], Bchain[i], mo=True)
        FKattr = FKconstr[0] +'.' + FKchain[i] + 'W1'
        
        # Setting FK SDK
        cmds.setAttr(switchCtrl + '.IK_Blend', 0)
        cmds.setAttr(IKattr, 0)
        cmds.setAttr(FKattr, 1)
        cmds.setDrivenKeyframe(IKattr, cd = switchCtrl + '.IK_Blend')
        cmds.setDrivenKeyframe(FKattr, cd = switchCtrl + '.IK_Blend')
        
        # Setting IK SDK
        cmds.setAttr(switchCtrl + '.IK_Blend', 1)
        cmds.setAttr(IKattr, 1)
        cmds.setAttr(FKattr, 0)
        cmds.setDrivenKeyframe(IKattr, cd = switchCtrl + '.IK_Blend')
        cmds.setDrivenKeyframe(FKattr, cd = switchCtrl + '.IK_Blend')

    cmds.hide(IKchain[0])
    cmds.hide(FKchain[0])
    
    return IKchain, FKchain, Bchain, switchCtrl
    
# *** Creating Functioning Clavicle
def createClavicleCtrl(rad, size, side, limb, clavicleJnt, topJoint):
    IKchain, FKchain, Bchain, switchCtrl = parentAndKeyArmJoints(rad, size, side, limb, topJoint)
    
    # Creating Clavicle Control and Group
    clavicleCtrl = cmds.circle(name = side + '_Clavicle_Ctrl', r=rad)[0]
    clavicleGrp = cmds.group(clavicleCtrl, name = side + '_Clavicle__Offset')
    
    # Determining Controller Color
    if side == 'L':
        cmds.color(clavicleCtrl, rgb=(0, 0, 1))
    else:
        cmds.color(clavicleCtrl, rgb=(1, 0, 0))
        
    # Positioning Controller
    parentConst = cmds.parentConstraint(clavicleJnt, clavicleGrp)
    cmds.delete(parentConst)
    clavicleEnd = cmds.listRelatives(clavicleJnt)[0]
    
    # Rotating Clavicle Control
    offsetRotY = cmds.getAttr(clavicleGrp + '.rotateY')
    newRotY = offsetRotY + 90
    cmds.setAttr(clavicleGrp + '.rotateY', newRotY)
    
    # Getting New Clavicle Position
    endDuplicate = cmds.duplicate(clavicleEnd)[0]
    cmds.parent(endDuplicate, world=True)
    clavDuplicate = cmds.duplicate(clavicleJnt)[0]
    cmds.parent(clavDuplicate, world=True)
    ctrlX = (cmds.getAttr(endDuplicate + '.translateX') - cmds.getAttr(clavDuplicate + '.translateX')) / 2
    ctrlY = (cmds.getAttr(endDuplicate + '.translateY') - cmds.getAttr(clavDuplicate + '.translateY'))
    ctrlZ = (cmds.getAttr(endDuplicate + '.translateZ') - cmds.getAttr(clavDuplicate + '.translateZ'))
    cmds.delete(endDuplicate)
    cmds.delete(clavDuplicate)
    
    # Setting New Rotation
    cmds.select(clavicleCtrl + '.cv[0:7]')
    cmds.move(ctrlX, ctrlY, ctrlZ, r=True)
    cmds.select(clear=True)
    
    # Creating Constraints
    orientConst = cmds.orientConstraint(clavicleCtrl, clavicleJnt, mo=True)
    FKparentConst = cmds.parentConstraint(clavicleCtrl, side + '_' + limb + '_FK_1_j_Ctrl__Offset', mo=True)
    IKparentConst = cmds.parentConstraint(clavicleCtrl, side + '_IK_Shoulder_Ctrl__Offset', mo=True)
    
    # Returning Necessary Items
    return clavicleGrp


# **** CREATING FOOT ****


# ** Creating Lists of Joint Chains ***
def createLegChainLists(size, side, limb, topJoint):

    # Creating Bind Joint Chain  
    Btop = topJoint
    Bchain = cmds.listRelatives(Btop, ad=True, type='joint')
    Bchain.reverse()
    Bchain.insert(0, Btop)
    
    # Creating List of Joint Names
    jntNames = ['Hip', 'Knee', 'Ankle']
    
    # Creating and Renaming IK Joint Chain    
    IKchain = cmds.duplicate(Bchain, name='IK_Chain', renameChildren=True)
    IKfootJnt = IKchain[size]
    cmds.parent(IKfootJnt, world=True)
    cmds.parent(IKchain[0], world=True)
    newIKchain = []
    baseIKchain = []
    for i in range(0, size):
        cmds.rename(IKchain[i], side + '_' + limb + '_IK_' + str((i+1)) + '_j')
        newIKchain.append(side + '_' + limb + '_IK_' + str((i+1)) + '_j')

    # Creating IK Base Joint Chain
    baseIKchain = cmds.duplicate(newIKchain, name='IK_Base_', renameChildren=True)
    for i in range(0, size):
        if i == ((size-1)/2):
            cmds.parent('IK_Base_' + str(((size-1)/2)), 'IK_Base_')
        if i == (size-1):
            cmds.parent('IK_Base_' + str((size-1)), 'IK_Base_' + str(((size-1)/2)))
    cmds.delete('IK_Base_' + str(1))
    cmds.delete('IK_Base_' + str(((size-1)/2)+1))
    
    # Renaming IK Base Joint Chain
    newBaseIKchain = []
    for i in range(0,3):
        if i == 0:
            cmds.rename('IK_Base_', side + '_' + limb + '_IK_Base_' + str((i+1)) + '_j')
        if i == 1:
            cmds.rename('IK_Base_' + str(((size-1)/2)), side + '_' + limb + '_IK_Base_' + str((i+1)) + '_j')
        if i == 2:
            cmds.rename('IK_Base_' + str((size-1)), side + '_' + limb + '_IK_Base_' + str((i+1)) + '_j')
        newBaseIKchain.append(side + '_' + limb + '_IK_Base_' + str((i+1)) + '_j')
    
    # Hiding IK Chains
    cmds.hide(newIKchain[0])
    cmds.hide(newBaseIKchain[0])
    cmds.hide(IKfootJnt)
    
    # Creating FK Joint Chain  
    FKchain = cmds.duplicate(Bchain, name='FK_Chain', renameChildren=True)
    cmds.parent(FKchain[0], world=True)
    newFKchain = []
    for i in range(0, size+2):
        cmds.rename(FKchain[i], side + '_' + limb + '_FK_' + str((i+1)) + '_j')
        newFKchain.append(side + '_' + limb + '_FK_' + str((i+1)) + '_j')
    cmds.hide(newFKchain[0])
    
    return newIKchain, newBaseIKchain, newFKchain, Bchain, IKfootJnt

# *** Creating the Switch Controller ***
def createLegSwitchController(rad, size, side, limb, topJoint):
    IKchain, baseIKchain, FKchain, Bchain, IKfootJnt = createLegChainLists(size, side, limb, topJoint)
    
    # Determining Switch Radius
    if rad == 1:
        switchRad = 1
    else:
        switchRad = rad-2
    
    # Creating Switch and Group
    switchCtrl = cmds.circle(nr=(0,1,0), r=switchRad, name=side + '_' + limb + '_Switch_Ctrl')[0]
    switchCtrlGroup = cmds.group(switchCtrl, name=switchCtrl + '__Offset')
    
    # Coloring Control Based on Side
    if side == 'L':
        cmds.color(switchCtrl, rgb=(0, 0, 1))
    else:
        cmds.color(switchCtrl, rgb=(1, 0, 0))
    
    # Adding Attribeutes to the Switch
    cmds.addAttr(switchCtrl, longName='IK_Blend', attributeType='float', defaultValue=1.0, minValue=0.0, maxValue=1.0, keyable=True)
    cmds.addAttr(switchCtrl, longName='IK_Visibility', attributeType='short', defaultValue=1, minValue=0, maxValue=1, keyable=True)
    cmds.addAttr(switchCtrl, longName='FK_Visibility', attributeType='short', defaultValue=1, minValue=0, maxValue=1, keyable=True)
    
    # Moving Switch Above End of Chain
    ankleIndex = size
    parentConst = cmds.parentConstraint(Bchain[ankleIndex], switchCtrlGroup)
    cmds.delete(parentConst)
    
    # Adjusting Switch Position
    cmds.setAttr(switchCtrlGroup + '.rotateX', 90)
    cmds.setAttr(switchCtrlGroup + '.rotateY', 0)
    cmds.setAttr(switchCtrlGroup + '.rotateZ', 0)
    currentX = cmds.getAttr(switchCtrlGroup + '.translateX')
    if side == 'L':
        cmds.setAttr(switchCtrlGroup + '.translateX', currentX + (rad*2))
    else:
        cmds.setAttr(switchCtrlGroup + '.translateX', currentX - (rad*2))
    currentY = cmds.getAttr(switchCtrlGroup + '.translateY')
    cmds.setAttr(switchCtrlGroup + '.translateY', currentY + rad)
    
    # Parenting Switch to Follow Ankle
    newParentConst = cmds.parentConstraint(Bchain[ankleIndex], switchCtrlGroup, mo=True)
    
    return IKchain, baseIKchain, FKchain, Bchain, IKfootJnt, switchCtrl

# *** Creating Controllers for IK and FK Joint Chains ***
def createLegJointControllers(rad, size, side, limb, topJoint):
    IKchain, baseIKchain, FKchain, Bchain, IKfootJnt, switchCtrl = createLegSwitchController(rad, size, side, limb, topJoint)
    
    # *** FK CONTROLS ***
    
    # Selecting Control Rotation Axis Based on Limb Type
    if limb == "Arm":
        axis = 'Y'
    else:
        axis = 'X'
    
    # Creating FK Controllers and Groups
    for i in range(0, (size+2)):
        
        # Determining Controller Size
        if i == 0:
            FKctrl = cmds.circle(name = FKchain[i] + '_Ctrl', r=rad+3, degree=1)[0]
        elif i == ((size-1)/2):
            FKctrl = cmds.circle(name = FKchain[i] + '_Ctrl', r=rad+3, degree=1)[0]
        elif i == size:
            FKctrl = cmds.circle(name = FKchain[i] + '_Ctrl', r=rad+3, degree=1)[0]
        else:
            FKctrl = cmds.circle(name = FKchain[i] + '_Ctrl', r=rad, degree=1)[0]
        
        # Determining Controller Color
        if side == 'L':
            cmds.color(FKctrl, rgb=(0, 0, 1))
        else:
            cmds.color(FKctrl, rgb=(1, 0, 0))
        
        # Positioning Each Controller        
        FKctrlGroup = cmds.group(FKctrl, name=FKctrl + '__Offset')
        parentConst = cmds.parentConstraint(FKchain[i], FKctrlGroup)
        cmds.delete(parentConst)
        
        currentCtrlRot = cmds.getAttr(FKctrlGroup + '.rotateZ')
        if (i == size) or (i == (size-1)):
            cmds.setAttr(FKctrlGroup + '.rotateZ', currentCtrlRot + 90)
        elif i == (size+1):
            cmds.setAttr(FKctrlGroup + '.rotateZ', currentCtrlRot + 90)
        else:
            cmds.setAttr(FKctrlGroup + '.rotateZ', currentCtrlRot + 90)
    
    # Creating Chain of FK Controllers and Groups
    for i in range(0, size+2):
        if i != 0:
            cmds.parent(FKchain[i] + '_Ctrl__Offset', FKchain[i-1] + '_Ctrl')
            
    # Constraining Corresponding Controls
    for i in range(0, size+2):
        if i == 0:
            cmds.parentConstraint(FKchain[i] + '_Ctrl', FKchain[i], mo=True)
        else:
            cmds.orientConstraint(FKchain[i] + '_Ctrl', FKchain[i], mo=True)
        
    # *** IK CONTROLS ***
    
    # Creating Naming Convens
    top = "Hip"
    bottom = "Ankle"
    
    # Creating IK Handle and Controls for End of IK Chain
    IKhand = cmds.ikHandle(sj=baseIKchain[0], ee=baseIKchain[-1])[0]
    IKbottomCtrl = cmds.circle(name = side + '_IK_' + bottom + '_Ctrl', r=rad+2)[0]
    cmds.setAttr(IKbottomCtrl+'.rotateY', 90)
    cmds.makeIdentity(IKbottomCtrl, apply=True)
    cmds.select(IKbottomCtrl+'.cv[0:7]')
    cmds.rotate(90.0, 0, 0)
    cmds.select(clear=True)
    if side == 'L':
        cmds.color(IKbottomCtrl, rgb=(0, 0, 1))
    else:
        cmds.color(IKbottomCtrl, rgb=(1, 0, 0))
    cmds.addAttr(IKbottomCtrl, longName='Twist', attributeType='float', defaultValue=0.0, keyable=True)
    
    # Creating Controls for Top of IK Chain
    IKbottomCtrlGroup = cmds.group(IKbottomCtrl, name=IKbottomCtrl + '__Offset')
    IKtopCtrl = cmds.circle(name = side + '_IK_' + top + '_Ctrl', r=rad+2)[0]
    if side == 'L':
        cmds.color(IKtopCtrl, rgb=(0, 0, 1))
    else:
        cmds.color(IKtopCtrl, rgb=(1, 0, 0))
    IKtopCtrlGroup = cmds.group(IKtopCtrl, name=IKtopCtrl + '__Offset')
    
    # Positioning and Implementing Base IK Bottom Control 
    cmds.parent(IKbottomCtrlGroup, IKchain[-1])
    for trans in ['.translate', '.rotate']:
        for axis in 'XYZ':
            cmds.setAttr(IKbottomCtrlGroup + trans + axis, 0)
    cmds.parent(IKbottomCtrlGroup, world=True)
    cmds.connectAttr(IKbottomCtrl + '.Twist', IKhand + '.twist', f=True)
    cmds.hide(IKhand)
    
    # Creating Rotation Distribution for Upper Leg
    upperMultDivNode = cmds.shadingNode('multiplyDivide', asUtility=True)
    cmds.connectAttr(baseIKchain[0]+'.rotateX', upperMultDivNode+'.input1X', force=True)
    cmds.setAttr(upperMultDivNode+'.input2X', 1.0/((size-1)/2.0))
        
    # Outputting Multiplied Number to Upper Arm Rotations
    for i in range(0, ((size-1)/2)):
        cmds.connectAttr(upperMultDivNode+'.outputX', IKchain[i]+'.rotateX', force=True) 
    
    # Positioning and Implementing IK Top Control 
    parentConst = cmds.parentConstraint(IKchain[0], IKtopCtrlGroup)
    cmds.delete(parentConst)    
    currentCtrlRot = cmds.getAttr(IKtopCtrlGroup + '.rotateZ')
    cmds.setAttr(IKtopCtrlGroup + '.rotateZ', currentCtrlRot + 90)
    cmds.pointConstraint(IKtopCtrl, baseIKchain[0], mo=True)
    
    # Parenting Base IK to IK Chain
    cmds.parentConstraint(baseIKchain[0], IKchain[0], sr=['x'], mo=True)
    cmds.parentConstraint(baseIKchain[1], IKchain[((size-1)/2)], mo=True)
    cmds.parentConstraint(baseIKchain[2], IKchain[size-1], mo=True)
    cmds.hide(baseIKchain[0])
    
    # Connecting Controls to Visibility Attributes in Switch
    cmds.connectAttr(switchCtrl + '.FK_Visibility', FKchain[0] + '_Ctrl__Offset.visibility', f=True)
    cmds.connectAttr(switchCtrl + '.IK_Visibility', IKbottomCtrlGroup + '.visibility', f=True)
    cmds.connectAttr(switchCtrl + '.IK_Visibility', IKtopCtrlGroup + '.visibility', f=True)
    
    # Organizing Everything into Groups
    FKgroup = cmds.group(FKchain[0] + '_Ctrl__Offset', FKchain[0], name=side + '_FK_Leg__Group')
    IKjntGroup = cmds.group(IKchain[0], baseIKchain[0], name=side + '_IK_Leg_Joint__Group')
    IKgroup = cmds.group(IKbottomCtrlGroup, IKtopCtrlGroup, IKjntGroup, name=side + '_IK_Leg__Group')
    cmds.parent(IKhand, IKbottomCtrl)
    
    # Returning Necessary Items
    return IKchain, baseIKchain, FKchain, Bchain, IKfootJnt, IKhand, switchCtrl

# *** Parenting IK and FK Leg Chains and Setting Up SDKs ***
def parentAndKeyLegJoints(rad, size, side, limb, topJoint):
    IKchain, baseIKchain, FKchain, Bchain, IKfootJnt, IKhand, switchCtrl = createLegJointControllers(rad, size, side, limb, topJoint)
    
    for i in range(0, len(FKchain)):
        
        # Setting IK Joint to Parent
        if i == size:
            ikJnt = IKfootJnt
        elif i == (size+1):
            ikJnt = cmds.listRelatives(IKfootJnt)[0]
        else:
            ikJnt = IKchain[i]
        
        # Parenting Corresponding Joints
        IKconstr = cmds.parentConstraint(ikJnt, Bchain[i], mo=True)
        IKattr = IKconstr[0] + '.' + ikJnt + 'W0'
        FKconstr = cmds.parentConstraint(FKchain[i], Bchain[i], mo=True)
        FKattr = FKconstr[0] +'.' + FKchain[i] + 'W1'
        
        # Setting FK SDK
        cmds.setAttr(switchCtrl + '.IK_Blend', 0)
        cmds.setAttr(IKattr, 0)
        cmds.setAttr(FKattr, 1)
        cmds.setDrivenKeyframe(IKattr, cd = switchCtrl + '.IK_Blend')
        cmds.setDrivenKeyframe(FKattr, cd = switchCtrl + '.IK_Blend')
        
        # Setting IK SDK
        cmds.setAttr(switchCtrl + '.IK_Blend', 1)
        cmds.setAttr(IKattr, 1)
        cmds.setAttr(FKattr, 0)
        cmds.setDrivenKeyframe(IKattr, cd = switchCtrl + '.IK_Blend')
        cmds.setDrivenKeyframe(FKattr, cd = switchCtrl + '.IK_Blend')

    return IKchain, FKchain, Bchain, IKfootJnt, IKhand, switchCtrl

# *** Creating Preset Sliders on Foot Control Using Locators ***
def createFootControls(rad, size, side, limb, heelLoc, tippyToeLoc, outerToesLoc, innerToesLoc, ballLoc, topJoint):  
    IKchain, FKchain, Bchain, IKfootJnt, ikHand, switchCtrl = parentAndKeyLegJoints(rad, size, side, limb, topJoint)
    
    # Defining Joints and Chain for IK Foot
    IKfootChain = []
    IKfootChain.append(IKfootJnt)
    IKballJnt = cmds.listRelatives(IKfootJnt)[0]
    IKfootChain.append(IKballJnt)
    IKtoesJnt = cmds.listRelatives(IKballJnt)[0]
    IKfootChain.append(IKtoesJnt)
    
    # Creating Locators to Place at Ball Joint
    parentConstr = cmds.parentConstraint(IKballJnt, ballLoc)
    cmds.delete(parentConstr)
    toesLoc  = cmds.duplicate(ballLoc, name = side + '_ToesLoc')
    grindLoc = cmds.duplicate(toesLoc, name = side + '_GrindLoc') 
    
    # Creating Duplicates of Locators
    heelChild = cmds.duplicate(heelLoc, name = side + '_HeelChild')
    tippyToeChild = cmds.duplicate(tippyToeLoc, name = side + '_TippyToeChild')
    grindChild = cmds.duplicate(grindLoc, name = side + '_GrindChild')
    outerToesChild = cmds.duplicate(outerToesLoc, name = side + '_OuterToesChild')
    innerToesChild = cmds.duplicate(innerToesLoc, name = side + '_InnerToesChild')
    ballChild = cmds.duplicate(ballLoc, name = side + '_BallChild')
    toesChild = cmds.duplicate(toesLoc, name = side + '_ToesChild')
    
    # Putting Children Under Parents
    cmds.parent(heelChild, heelLoc)
    cmds.parent(tippyToeChild, tippyToeLoc)
    cmds.parent(grindChild, grindLoc)
    cmds.parent(outerToesChild, outerToesLoc)
    cmds.parent(innerToesChild, innerToesLoc)
    cmds.parent(ballChild, ballLoc)
    cmds.parent(toesChild, toesLoc)
    
    # Creating Proper Chain of Locators and Joints
    cmds.parent(heelLoc, side + '_IK_' + 'Ankle_Ctrl')
    cmds.parent(tippyToeLoc, heelChild)
    cmds.parent(grindLoc, tippyToeChild)
    cmds.parent(outerToesLoc, grindChild)
    cmds.parent(innerToesLoc, outerToesChild)
    cmds.parent(ballLoc, innerToesChild)
    cmds.parent(toesLoc, innerToesChild)
    cmds.parent(ikHand, ballChild)
    
    # Setting up Constraints and ikHandles
    cmds.pointConstraint(IKchain[-1], IKfootJnt, mo=True)
    ballIK = cmds.ikHandle(name = side + '_Ball_IK_Handle', sj=IKfootJnt, ee=IKballJnt, sol='ikSCsolver')[0]
    toesIK = cmds.ikHandle(name = side + '_Toes_IK_Handle', sj=IKballJnt, ee=IKtoesJnt, sol='ikSCsolver')[0]
    cmds.hide(ballIK, toesIK)
    cmds.parent(ballIK, ballChild)
    cmds.parent(toesIK, toesChild)
    cmds.parent(IKfootChain[0], ballChild)
    
    # *** Adding Attributes to Foot Controller ***
    footCtrl = side + '_IK_Ankle_Ctrl'
    
    # Heel Roll
    cmds.addAttr(footCtrl, longName=side+'_Heel_Roll', attributeType='float', defaultValue=0.0, keyable=True)
    cmds.connectAttr(footCtrl + '.' + side + '_Heel_Roll', heelChild[0] + '.rotateX')
    
    # Ball Roll
    cmds.addAttr(footCtrl, longName=side+'_Ball_Roll', attributeType='float', defaultValue=0.0, keyable=True)
    cmds.connectAttr(footCtrl + '.' + side + '_Ball_Roll', ballChild[0] + '.rotateZ')
    
    # Tippy Toe
    cmds.addAttr(footCtrl, longName=side+'_Tippy_Toe', attributeType='float', defaultValue=0.0, keyable=True)
    cmds.connectAttr(footCtrl + '.' + side + '_Tippy_Toe', tippyToeChild[0] + '.rotateX')
    
    # Grind
    cmds.addAttr(footCtrl, longName=side+'_Grind', attributeType='float', defaultValue=0.0, keyable=True)
    cmds.connectAttr(footCtrl + '.' + side + '_Grind', grindChild[0] + '.rotateY')
    
    # Inner Toe
    cmds.addAttr(footCtrl, longName=side+'_Inner_Toe', attributeType='float', defaultValue=0.0, keyable=True)
    cmds.connectAttr(footCtrl + '.' + side + '_Inner_Toe', innerToesChild[0] + '.rotateZ')
    
    # Outer Toe
    cmds.addAttr(footCtrl, longName=side+'_Outer_Toe', attributeType='float', defaultValue=0.0, keyable=True)
    cmds.connectAttr(footCtrl + '.' + side + '_Outer_Toe', outerToesChild[0] + '.rotateZ')
    
    # Toes
    cmds.addAttr(footCtrl, longName=side+'_Toes', attributeType='float', defaultValue=0.0, keyable=True)
    cmds.connectAttr(footCtrl + '.' + side + '_Toes', toesChild[0] + '.rotateZ')
    
    # Hiding Locators
    cmds.hide(heelLoc)
    
    # Connecting to Rest of Body
    cmds.parentConstraint('Pelvis_Ctrl', side + '_IK_Hip_Ctrl__Offset', mo=True)
    cmds.parentConstraint('Pelvis_Ctrl', side + '_Leg_FK_1_j_Ctrl__Offset', mo=True)

    
# *** Doing Final Organization for Rig ***
def finalOrg(mesh, rootJnt, spineCurve, rigName):
    
    # * Creating Master Controller *
    bbox = cmds.xform(mesh, bb=True, query=True)
    xMin = bbox[2]
    xMax = bbox[5]
    masterRad = xMin - xMax
    masterCtrl = cmds.circle(name="Master_Ctrl", r=masterRad*1.5)[0]
    
    # * Rotating Master Control Into Place *
    cmds.select(masterCtrl + '.cv[0:7]')
    cmds.rotate(90, 0, 0)
    cmds.select(clear=True)
    
    # * Creating Final Groups *
    finalRig = cmds.group(masterCtrl, mesh, name=rigName)
    spineGrp = cmds.group('Spine_IKhandle', spineCurve, name='IK_Spine_Group')
    neckGrp = cmds.group(em=True, name='IK_Neck_Group')
    cmds.parent('Neck_IKhandle', 'neckCurve', neckGrp)
    switchGrp = cmds.group('L_Arm_Switch_Ctrl__Offset', 'R_Arm_Switch_Ctrl__Offset', 'L_Leg_Switch_Ctrl__Offset', 'R_Leg_Switch_Ctrl__Offset', name='Switch_Group')
    
    # * Grouping Rig Properly *
    cmds.parent(spineGrp, neckGrp, finalRig)
    cmds.parent('Root__Offset', 'Aim__Offset', rootJnt, 'IK_Spine_1_j', 'IK_Neck1_j', switchGrp, masterCtrl)
    cmds.parent('L_FK_Arm__Group', 'L_IK_Arm__Group', 'R_FK_Arm__Group', 'R_IK_Arm__Group', masterCtrl)
    cmds.parent('L_FK_Leg__Group', 'L_IK_Leg__Group', 'R_FK_Leg__Group', 'R_IK_Leg__Group', masterCtrl)
    cmds.parent('L_Fingers_Group', 'R_Fingers_Group', masterCtrl)
    
    # * Root Follower *
    
    # Creating Root Follower Groups
    L_Arm_RtFollow = cmds.group(em=True, name='L_IK_Arm_RootFollower')
    parentConst = cmds.parentConstraint('Root_Ctrl', L_Arm_RtFollow)
    cmds.delete(parentConst)
    L_Leg_RtFollow = cmds.duplicate(L_Arm_RtFollow, name='L_IK_Leg_RootFollower')
    R_Arm_RtFollow = cmds.duplicate(L_Arm_RtFollow, name='R_IK_Arm_RootFollower')
    R_Leg_RtFollow = cmds.duplicate(L_Arm_RtFollow, name='R_IK_Leg_RootFollower')
    
    # Adding Joints Under Groups
    cmds.parent('L_IK_Arm_Joint__Group', L_Arm_RtFollow)
    cmds.parent('L_IK_Leg_Joint__Group', L_Leg_RtFollow)
    cmds.parent('R_IK_Arm_Joint__Group', R_Arm_RtFollow)
    cmds.parent('R_IK_Leg_Joint__Group', R_Leg_RtFollow)
    
    # Parenting Root Follow Groups to Root
    cmds.parentConstraint('Root_Ctrl', L_Arm_RtFollow, mo=True)
    cmds.parentConstraint('Root_Ctrl', L_Leg_RtFollow, mo=True)
    cmds.parentConstraint('Root_Ctrl', R_Arm_RtFollow, mo=True)
    cmds.parentConstraint('Root_Ctrl', R_Leg_RtFollow, mo=True)
    
    # Moving Root Follow Groups Under Proper Group
    cmds.parent(L_Arm_RtFollow, 'L_IK_Arm__Group')
    cmds.parent(L_Leg_RtFollow, 'L_IK_Leg__Group')
    cmds.parent(R_Arm_RtFollow, 'R_IK_Arm__Group')
    cmds.parent('R_IK_Leg_RootFollower', 'R_IK_Leg__Group')
    
    
# ***** CREATING UI AND FUNCTIONS TO RUN AUTORIG *****

def showRigWindow():
    
    # Initial Window Creation
    name = "Biped_Auto_Rig"
    if cmds.window(name, query=True, exists=True):
        cmds.deleteUI(name)
    
    # Creating and Formatting Main Column
    cmds.windowPref(name, remove=True)
    cmds.window(name, title="Biped Auto Rig", widthHeight=(285,375))
    column = cmds.columnLayout(columnAttach=('left', 5), rowSpacing=10)
    cmds.text(label = "GARDEN CLUB STUDIOS: AUTO RIG")
    
    # Setting Up Rig Name Text Field
    cmds.text(label = "Rig Name:")
    cmds.textField("rigName")

    # Setting Up Joint Amount
    cmds.text("Spine Control Radius:")
    cmds.intField("spineRad", value=1)
    
    # Setting Up Control Size
    cmds.text("Head and Neck Control Radius:")
    cmds.intField("neckRad", value=1)

    # Setting Up Control Size
    cmds.text("Arm Control Radius:")
    cmds.intField("armRad", value=1)

    # Setting Up Control Size
    cmds.text("Leg Control Radius:")
    cmds.intField("legRad", value=1)
    
    # Creating Create and Close Buttons
    cmds.text("* Create Left Foot Locators Before Apply *")
    cmds.text("* Select Root, Spine Curve, and Mesh Before Apply *")
    cmds.columnLayout(adjustableColumn=True)
    cmds.rowLayout(numberOfColumns=3)
    cmds.button(label="Create Locators", command=createLocators)
    cmds.button(label="Apply", command=onApply)
    cmds.button(label="Close", command="cmds.deleteUI('{}')".format(name))
    
    # Finally Displaying Window
    cmds.showWindow()
    
# Locator Creation Function
def createLocators(*args):
    for preset in ['Ball', 'Heel', 'TippyToe', 'OuterToes', 'InnerToes']:
        cmds.spaceLocator(name= 'L_' + preset + 'Loc')

# Function to Create Rig
def onApply(*args):
    # ** Getting Items from User Selection **
    userSelectList = checkSelection()
    rootJnt = userSelectList[0]
    spineCurve = userSelectList[1]
    mesh = userSelectList[2]

    # ** Getting Variables from User **
    rigName = cmds.textField("rigName", query=True, text=True)
    spineRad = cmds.intField("spineRad", query=True, value=True)
    neckRad = cmds.intField("neckRad", query=True, value=True)
    armRad = cmds.intField("armRad", query=True, value=True)
    legRad = cmds.intField("legRad", query=True, value=True)
    print rigName
    
    # ** Getting Locators Mirrored Onto Right Side **
    for preset in ['Ball', 'Heel', 'TippyToe', 'OuterToes', 'InnerToes']:
        leftLoc = ('L_' + preset + 'Loc')
        rightLoc = cmds.duplicate(leftLoc, name= ('R_' + preset + 'Loc'))[0]
        currentX = cmds.getAttr(leftLoc + '.translateX')
        cmds.setAttr(rightLoc + '.translateX', (currentX * -1))

    # ** Creating Chest **
    chestBchain = setSpineAdvancedTwist(spineRad, rootJnt, spineCurve)

    # ** Getting Neck and Clavicle Joints **
    chestJnt = chestBchain[4]
    chestList = cmds.listRelatives(chestJnt)
    for child in chestList:
        if ('Neck' in child) or ('neck' in child):
            neckJnt = child
        if (('Clavicle' in child) or ('clavicle' in child)) and ('L' in child):
            LclavicleJnt = child
        if (('Clavicle' in child) or ('clavicle' in child)) and ('R' in child):
            RclavicleJnt = child

    # ** Getting Arm Joints **
    LarmJnt = cmds.listRelatives(cmds.listRelatives(LclavicleJnt)[0])[0]
    RarmJnt = cmds.listRelatives(cmds.listRelatives(RclavicleJnt)[0])[0]
            
    # ** Creating Head and Neck Rig **
    neckOffset, chestCtrl = createHeadAim(neckRad, neckJnt, chestBchain, mesh)
    cmds.parent(neckOffset, chestCtrl)

    # ** Creating Arm Rig **
    LclavicleGrp = createClavicleCtrl(armRad, 11, 'L', 'Arm', LclavicleJnt, LarmJnt)
    RclavicleGrp = createClavicleCtrl(armRad, 11, 'R', 'Arm', RclavicleJnt, RarmJnt)
    cmds.parent(LclavicleGrp, 'Chest_Ctrl')
    cmds.parent(RclavicleGrp, 'Chest_Ctrl')

    # ** Getting Joints for Leg Rig **
    rootList = cmds.listRelatives(rootJnt)
    for child in rootList:
        if 'Pelvis' in child or 'pelvis' in child:
            pelvisJnt = child
    pelvisList = cmds.listRelatives(pelvisJnt)
    for child in pelvisList:
        if 'L_' in child:
            LfootJnt = child
        if 'R_' in child:
            RfootJnt = child

    # ** Creating Leg Rig **
    createFootControls(legRad, 9, 'L', 'Leg', 'L_HeelLoc', 'L_TippyToeLoc', 'L_OuterToesLoc', 'L_InnerToesLoc', 'L_BallLoc', LfootJnt)
    createFootControls(legRad, 9, 'R', 'Leg', 'R_HeelLoc', 'R_TippyToeLoc', 'R_OuterToesLoc', 'R_InnerToesLoc', 'R_BallLoc', RfootJnt)
    cmds.hide(rootJnt, spineCurve)

    # ** Doing Final Organization **
    finalOrg(mesh, rootJnt, spineCurve, rigName)


# ***** FINALLY CREATING AUTORIG *****

showRigWindow()