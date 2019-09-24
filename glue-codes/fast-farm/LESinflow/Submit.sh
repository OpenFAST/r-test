#! /bin/bash
#SBATCH --time 4:00:00
#SBATCH -A isda
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=36
#SBATCH --job-name case5_FF

module purge
module load comp-intel mkl


/home/kshaler/OpenFASTv2/OpenFAST/build/glue-codes/fast-farm/openfast-farm case5-YZforWT1.fstf > output.txt
