"""

What Can This Program Do?
- This script is a batch renamer that finds a string within a file name and 
replaces it with another string.
- On the command line, the user must provide the directory in which file names will be changed, the original string, and the new 
string.

Instructions:
- Start the program by using the following format:
	python batchRenamer.py directoryPath oldString newString 
- This is an example of how a Windows user would use this script:
	python batchRenamer.py D:\Documents\ old new
- This is an example of how a Mac user would use this script:
	python batchRenamer.py /Users/sarameixner/Documents old new

Notes:
-If an incorrect amount of command line arguments is entered, an error message will be printed indicating the proper format, and the program will end.

"""

# Importing Modules
import sys
from sys import argv
import os

# ***** SCRIPT BODY *****

# ** VARIABLE CREATION **

# Checking For Correct Amount of Arguments
if ( len(sys.argv) != 4 ):
	print( "Error: Invalid Arguments" )
	print( "Usage: python sam_w04_01.py directoryPath oldString newString" )
	sys.exit( 1 )

# Defining Variables Received on Command Line
script, directoryPath, oldString, newString = argv

# ** REPLACING STRINGS **

# Getting List of Files in Directory
fileList = os.listdir(directoryPath)

# Iterating through File List
for file in fileList:
	if oldString in file:
		# Making File Path for Old File Name
		oldFilePath = os.path.join(directoryPath, file)
		
		# Making Name for New File and Creating Path
		newFile = file.replace(oldString, newString)
		newFilePath = os.path.join(directoryPath, newFile)

		# Renaming File
		os.rename(oldFilePath, newFilePath)
