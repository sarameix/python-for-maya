"""

The batchRename function takes one parameter: a string.
It renames all selected objects with the given string.

The batchReplace function takes two parameters: an old string and a new string.
It replaces the old string in the name of all selected objects with the new string.

The addSuffix function adds a suffix to the name of all the following objects in the scene based on type:
    1. Poly Geo: __MESH
    2. Nurbs: __NURB
    3. Lights: __LIGHT
    4. Locators: __LOC

All other functions are help functions that assist batchRename, batchReplace, and addSuffix.

"""

# Importing Modules
from maya import cmds

# Gets List of Selected Objects
def checkSelection():
    objList = cmds.ls(sl=1)
    if len(objList) < 1:
        cmds.error("Please select an object.")
    return objList

# Checks Type of Given Object
def checkType(obj):
    shapeNode = cmds.listRelatives(obj, shapes=True)
    objType = cmds.nodeType(shapeNode)
    return objType

# Renames All Selected Objects with String
def batchRename(phrase):
	objList = checkSelection()
	indexNum = 1
	for obj in objList:
		cmds.rename(obj, phrase + str(indexNum))
		indexNum += 1

# Replaces Old String with New String in Selected Objects
def batchReplace(oldPhrase, newPhrase):
	objList = checkSelection()
	for obj in objList:
		if oldPhrase in obj:
			newName = obj.replace(oldPhrase, newPhrase)
			cmds.rename(obj, newName)

# Adds Suffix to Object Name Based on Type
def addSuffix():
    cmds.select(all=True, hierarchy=True)
    objList = checkSelection()
    cmds.select(clear=True)
    for obj in objList:
        if ("Shape" not in obj) and (checkType(obj) != None):
            if (checkType(obj) == "mesh"):
                cmds.rename(obj, obj + "__MESH")
            elif (checkType(obj) == "nurbsCurve"):
                cmds.rename(obj, obj + "__NURB")
            elif ("Light" in checkType(obj)):
                cmds.rename(obj, obj + "__LIGHT")
            elif (checkType(obj) == "locator"):
                cmds.rename(obj, obj + "__LOC")
            else:
                cmds.rename(obj, obj)
