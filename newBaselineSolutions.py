"""

"""

import sys
import os
import shutil

##### Helper functions
def exitWithError(error):
    print(error)
    sys.exit(1)

def exitWithDirNotFound(dir):
    exitWithError("Directory does not exist: {}\n".format(dir))

##### Main
sourceDir = sys.argv[1]
targetDir = sys.argv[2]
machine = sys.argv[3]
compiler = sys.argv[4]

destinationDir = os.path.join(targetDir, "{}-{}".format(machine, compiler))

# verify source directory exists. if not, bail
if not os.path.isdir(sourceDir):
    exitWithDirNotFound(sourceDir)

# verify destination directory exists. if not, make it
if not os.path.isdir(destinationDir):
    os.makedirs(destinationDir)

sourceFiles = os.listdir(sourceDir)
targetExtensions = [".out", ".outb", ".sum"]
targetFiles = [s for s in sourceFiles for t in targetExtensions if t in s]
for f in targetFiles:
    print f, os.path.join(sourceDir,f), os.path.join(destinationDir,f)
    shutil.copyfile(os.path.join(sourceDir,f), os.path.join(destinationDir,f))
