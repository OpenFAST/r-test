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

import sys
import os
import subprocess

def exitWithInputError():
  print("ERROR: Invalid arguments given: {}.\nUSAGE: python3 compileDISCON.py compiler_type[gnu,intel] arch_type[32/64]".format(sys.argv))
  sys.exit(1)

if len(sys.argv) != 3:
  exitWithInputError()

# parse the directory of this script if used in the call
# move into it to run make
if os.path.sep in sys.argv[0]:
  splitpath = sys.argv[0].split(os.path.sep)
  os.chdir(os.path.sep.join(splitpath[0:len(splitpath)-1]))

compilerInput = sys.argv[1]
if compilerInput.lower() != "intel" and compilerInput.lower() != "gnu":
  exitWithInputError()
compiler = compilerInput.lower()

archType = sys.argv[2]
if archType != "32" and archType != "64":
  exitWithInputError()

makebase = os.path.join("makefile_DISCON")
for ext in ["", "_ITI", "_OC3"]:
    makefile = makebase+ext
    if not os.path.isfile(makefile):
      print("ERROR: The DISCON makefile, {}, does not exist.".format(makefile))
      sys.exit(1)

    make_command = "make -f {} COMPILER={} BUILD=RELEASE BITS={} > {}.log".format(makefile, compiler, archType, makefile)
    return_code = subprocess.call(make_command, shell=True)
    print("-- `make` for DISCON{} finished with return code: {}".format(ext, return_code))
