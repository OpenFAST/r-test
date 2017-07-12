#
# Copyright 2017 National Renewable Energy Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
    This program copies locally generated solutions into the appropriate machine - compiler
    specific directory to update the baseline solutions.

    Usage: python updateBaselineSolutions.py source_directory target_directory system_name compiler_id
    Example: python updateBaselineSolutions.py local/solution/TestName target/solution/TestName [Darwin,Linux,Windows] [Intel,GNU]
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

### Verify input arguments
if len(sys.argv) != 5:
    exitWithError("Invalid arguments: {}\n".format(" ".join(sys.argv)) +
    "Usage: python updateBaselineSolutions.py local/solution/TestName target/solution/TestName [Darwin,Linux,Windows] [Intel,GNU]")

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
    shutil.copyfile(os.path.join(sourceDir,f), os.path.join(destinationDir,f))
