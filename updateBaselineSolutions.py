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

    Usage: python updateBaselineSolutions.py input_case_list source_solution_parent target_solution_parent system_name compiler_id
    input_case_list - a text file listing all the cases to copy
    source_solution_parent - the location to copy the files from. this is the parent directory of the cases; for example, `openfast/build/reg_tests/openfast`
    target_solution_parent - the location to copy the files to. this is the parent directory of the target cases; for example, `openfast/reg_tests/r-test/openfast`

    Example: python updateBaselineSolutions.py caselist.txt source/solution/parent target/solution/parent
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
if len(sys.argv) != 4:
    exitWithError("Invalid arguments: {}\n".format(" ".join(sys.argv)) +
    "Usage: python updateBaselineSolutions.py caselist.txt local/solution/parent baseline/solution/parent")

with open(sys.argv[1]) as listfile:
    content = listfile.readlines()

# allow comments with '#'
casenames = [x.rstrip("\n\r").strip() for x in content if "#" not in x]
# allow empty lines
casenames = [x for x in casenames if len(x.strip()) > 0]

sourceParent = sys.argv[2]
targetParent = sys.argv[3]

for case in casenames:
    # verify source directory exists. if not, bail
    if not os.path.isdir(sourceParent):
        exitWithDirNotFound(sourceParent)

    # verify destination directory exists. if not, make it
    destinationDir = os.path.join(targetParent, case)
    if not os.path.isdir(destinationDir):
        os.makedirs(destinationDir)

    caseDir = os.path.join(sourceParent, case)
    sourceFiles = os.listdir(caseDir)
    if "linear" in case.lower():
        targetExtensions = [".lin"]
    else:
        targetExtensions = [".out", ".outb", ".sum"]
    
    targetExtensions += [".log"]
    targetFiles = [s for s in sourceFiles for t in targetExtensions if t in s]

    for f in targetFiles:
        shutil.copyfile(os.path.join(caseDir, f), os.path.join(destinationDir,f))
