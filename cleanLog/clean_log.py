# Import the os module, for the os.walk function
import os
import shutil

def refreshFolder(directory):
	if os.path.exists(directory):
		shutil.rmtree(directory)
	os.makedirs(directory)

# Set the directory you want to start from
rootDir = '.'
absolute_path = os.getcwd()

for dirName, subdirList, fileList in os.walk(rootDir):
	if len(dirName) > 3:
		if dirName[-3:] == 'log':
			refreshFolder(os.path.join(absolute_path, dirName[2:]))