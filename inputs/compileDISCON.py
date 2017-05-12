import sys
import os
import subprocess

def exitWithInputError():
  print("ERROR: Invalid arguments.\nUSAGE: python compileDISCON.py compiler_type[gnu,intel] build_type[debug,release]")
  sys.exit(1)

if len(sys.argv) != 3:
  exitWithInputError()

compilerInput = sys.argv[1]
if compilerInput.lower() != "intel" and compilerInput.lower() != "gnu":
  exitWithInputError()
compiler = compilerInput.lower()

buildInput = sys.argv[2]
if buildInput.upper() != "DEBUG" and buildInput.upper() != "RELEASE":
  exitWithInputError()
build = buildInput.upper()

makebase = "makefile_DISCON"
for ext in ["", "_ITI", "_OC3"]:
    makefile = makebase+ext
    if not os.path.isfile(makefile):
      print("ERROR: The DISCON makefile, {}, does not exist.".format(makefile))
      sys.exit(1)

    make_command = "make -f {} COMPILER={} BUILD={} &> {}.log".format(makefile, compiler, build, makefile)
    return_code = subprocess.call(make_command, shell=True)
    print("Finished running `make` command for DISCON{} with return code: {}".format(ext, return_code))
