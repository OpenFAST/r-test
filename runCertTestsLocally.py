"""
    This script runs all of the CertTest cases to create a local 'gold standard'
    set of solutions.
"""

import os
import sys
import shutil
import subprocess

# if the local output directory already exists, bail for two reasons
# 1. don't silenty overwrite previous outputs
# 2. the python filesystem methods arent robust enough to do something like 'cp * .'
localDirectory = "outputs-local"
if os.path.exists(localDirectory):
    print "The local output directory, {}, already exists.".format(localDirectory)
    sys.exit(1)

# get the input files from /inputs
shutil.copytree("inputs", "{}".format(localDirectory))

# run through each case
os.chdir("{}".format(localDirectory))
num = [str(i).zfill(2) for i in range(1,3)]
for n in num:
    caseName = "Test{}".format(n)
    command = "openfast {}.fst > {}.log".format(caseName, caseName)
    print "'{}' - running".format(command)
    return_code = subprocess.call(command, shell=True)
    print "'{}' - finished with exit code {}".format(command, return_code)
