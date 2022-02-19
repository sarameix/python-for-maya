"""

What Can This Program Do?
- This program creates FK Controllers for all selected joints.

"""

# Import Maya Commands
from maya import cmds

# Creating List of Bind Joints
jntList = cmds.ls( sl=True )

# Storing Length of Joint List
jntCount = len(jntList)

# Looping Through Joint List
for index in range(0, jntCount):
    
    # Putting Current Joint into Variable
    jnt = jntList[index]
    
    # Creating and Positioning Controller
    ctrl = cmds.circle(name = 'FK_Joint' + str(index) + '_Ctrl', r=3)[0]
    grp = cmds.group(ctrl, name = 'FK_Joint' + str(index) + '_Group')
    parentConst = cmds.parentConstraint(jnt, grp, mo=False)
    cmds.delete(parentConst)
    
    # Rotating Controllers Properly
    currentRotation = cmds.getAttr(grp + '.rotateY')
    cmds.setAttr(grp + '.rotateY', currentRotation + 90)
    
    # Creating Constraint
    cmds.parentConstraint(ctrl, jnt, mo=True)    
    
    # Parenting Under Previous if Joint is Not Top of Chain
    if index > 0:
        cmds.parent(grp, 'FK_Joint' + str(index - 1) + '_Ctrl')