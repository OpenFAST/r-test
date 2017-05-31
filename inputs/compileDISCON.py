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
  print("ERROR: Invalid arguments given: {}.\nUSAGE: python3 compileDISCON.py".format(sys.argv))
  sys.exit(1)

def exitWithReturnCode(return_code):
  print("-- Finished with return code: {}".format(return_code))
  sys.exit(return_code)

if len(sys.argv) != 1:
  exitWithInputError()

# parse the directory of this script if used in the call
# move into it to run make
if os.path.sep in sys.argv[0]:
  splitpath = sys.argv[0].split(os.path.sep)
  os.chdir(os.path.sep.join(splitpath[0:len(splitpath)-1]))
parentDir = os.getcwd()

sourcebase = os.path.join("5MW_Baseline", "ServoData", "DISCON")
for ext in ["", "_ITI", "_OC3"]:

  sourcedir = os.path.join(parentDir, sourcebase + ext)
  if not os.path.isdir(sourcedir):
    print("ERROR: The DISCON source directory, {}, does not exist.".format(sourcedir))
    sys.exit(1)

  os.chdir(sourcedir)

  cmake_command = "cmake ."
  return_code = subprocess.call(cmake_command, shell=True)
  if return_code != 0:
    print("-- Finished DISCON{} with return code: {}".format(ext, return_code))
    continue

  make_command = "make"
  return_code = subprocess.call(make_command, shell=True)
  if return_code != 0:
    print("-- Finished DISCON{} with return code: {}".format(ext, return_code))
    continue

  install_command = "make install"
  return_code = subprocess.call(install_command, shell=True)

  os.chdir(parentDir)

  print("-- Finished DISCON{} with return code: {}".format(ext, return_code))
