"""

What Can This Program Do?
- This script uses command line arguments to create a directory structure, in the
proper location, that will be used to organize projects.
- The proper usage of the script is by entering on the command line: 
     python directoryCreator.py directory name sequence shot

Instructions:
- Use argv and have the user provide the project directory, project name, 
sequence, and shot in the command line. 

Notes:
- Also prints out an error message, informs the user of the proper format, and 
ends the program if the wrong amount of arguments is entered.

"""

# Importing Modules
import os
import sys
from sys import argv

# Script Body

# Error Message for Invalid Arguments
if (( len(sys.argv) != 5 )):
	print("Error: Invalid Arguments")
	print("Usage: python sam_w02_01.py directory name sequence shot")
	sys.exit( 1 )

# Creating Variables for Directory Structure
script, prjRoot, prjName, prjSeq, prjShot = argv
shotFolders = ["from_client", "output", "PUB", "WIP"]
prodFolders = ["anim", "comp", "light", "track", "vfx"]

# Creating Function for Checking If Path Exists and Making Folders
def makeDir(newPath):
	if (os.path.exists(newPath)):
		print ("{0} already exists!".format(newPath))
	else:
		os.makedirs(newPath)

# Creating Folders Using Variables
for sFolder in shotFolders:
	# Adding Folders in prodFolder List for PUB and WIP
	if (( sFolder == "PUB" ) or ( sFolder == "WIP" )):
		for pFolder in prodFolders:
			newPath = os.path.join(prjRoot,prjName,prjSeq,prjShot)
			newPath = os.path.join(newPath,sFolder,pFolder)
			makeDir(newPath)
	# Creating Empty from_client and output Folders
	else:
		newPath = os.path.join(prjRoot,prjName,prjSeq,prjShot,sFolder)
		makeDir(newPath)
