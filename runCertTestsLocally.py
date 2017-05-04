"""
    This script runs all of the CertTest cases to create a local 'gold standard'
    set of solutions.

    Usage: python runCertTestsLocally.py openfast_executable
     - openfast_executable is an optional argument pointing to the openfast executable of choice.
     - if not openfast_executable is given, an attempt will be made to search for one in $PATH

    Examples:
    $ python runCertTestsLocally.py
    $ python runCertTestsLocally.py openfast
    $ python runCertTestsLocally.py /openfast/install/bin/openfast
"""

import os
import sys
import shutil
import subprocess

def exitWithError(error):
    print error
    sys.exit(1)

# if no openfast executable was given, search in path
if len(sys.argv) == 1:
    try:
        devnull = open(os.devnull, 'w')
        subprocess.call("openfast", stdout=devnull)
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            exitWithError("{}: openfast".format(e))
        else:
            raise
    else:
        executable = "openfast"
        print "Using openfast executable found in path"

# verify that the given executable exists and can be run
elif len(sys.argv) == 2:
    executable = sys.argv[1]
    try:
        devnull = open(os.devnull, 'w')
        subprocess.call(executable, stdout=devnull)
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            exitWithError("{}: {}".format(e, executable))
        else:
            raise

# unhandled arguments so bail
else:
    exitWithError("Invalid arguments given: {}\n".format(" ".join(sys.argv)) +
    "Usage: python runCertTestsLocally.py openfast_executable")

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
    command = "{} {}.fst > {}.log".format(executable, caseName, caseName)
    print "'{}' - running".format(command)
    return_code = subprocess.call(command, shell=True)
    print "'{}' - finished with exit code {}".format(command, return_code)
