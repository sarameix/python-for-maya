"""

What Can This Program Do?
- This program copies all transforms on the controllers of the left side of a facial rig to the right side.
- The results is a mirrored expression on a character's face.

"""

for ctrl in ['_TopLip_Ctrl', '_BottomLip_Ctrl', '_CornerMouth_Ctrl', '_Cheek_Ctrl', '_Nostril_Ctrl', '_InnerEyebrow_Ctrl', '_MidEyebrow_Ctrl', '_OuterEyebrow_Ctrl', '_EyebrowArea_Ctrl', '_UpperEye_Ctrl', '_LowerEye_Ctrl']:
    if 'Eye_' in ctrl:
        transforms = ['.translate']
        axes = 'Y'
    else:
        transforms = ['.translate', '.rotate']
        axes = 'XYZ'
    for transform in transforms:
        for axis in axes:
            current = cmds.getAttr('L' + ctrl + transform + axis)
            cmds.setAttr('R' + ctrl + transform + axis, current)
