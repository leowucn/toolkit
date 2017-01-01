# Import the os module, for the os.walk function
import os
import shutil


def refresh_folder(directory):
	if os.path.exists(directory):
		shutil.rmtree(directory)
	os.makedirs(directory)

# Set the directory you want to start from
root_dir = '.'
absolute_path = os.getcwd()

for dirName, subdirList, fileList in os.walk(root_dir):
	if len(dirName) > 3:
		if dirName[-3:] == 'log':
			refresh_folder(os.path.join(absolute_path, dirName[2:]))
