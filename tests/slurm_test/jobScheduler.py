#!/usr/bin/env python

import os
import numpy as np
def mkdir_p(dir):
    '''make a directory (dir) if it doesn't exist'''
    if not os.path.exists(dir):
        os.mkdir(dir)
    

job_directory = "/gpfs/exfel/data/user/guestt/spb_model/tests/slurm_test/"
log_dir = "/gpfs/exfel/data/user/guestt/spb_model/logs/slurm_test/"
data_dir = os.path.join(job_directory, "/data/")

# Make top level directories
mkdir_p(job_directory)
mkdir_p(data_dir)

var = np.linspace(0,20)

for v in var:
    v = int(v)
    job_file = os.path.join(job_directory,"%s.job" %v)
    lizard_data = data_dir


    with open(job_file, "w+") as fh:
        
        fh.writelines("#!/bin/bash\n")
        fh.writelines("#SBATCH --partition=exfel \n")

        fh.writelines("#SBATCH --job-name=%s.job\n" % v)
        fh.writelines("#SBATCH --chdir {} \n".format(job_directory))
        fh.writelines("#SBATCH --nodes=1\n ")
        fh.writelines("#SBATCH --output={}{}.out\n".format(log_dir, v))
        fh.writelines("#SBATCH --error={}{}.err\n".format(log_dir, v))
        fh.writelines("#SBATCH --time=14-00:00\n")
        fh.writelines("#SBATCH --mail-type=ALL\n")
        fh.writelines("#SBATCH --mail-user=trey.guest@desy.de\n")
        fh.writelines("python /gpfs/exfel/data/user/guestt/spb_model/tests/slurm_test/testArgArray.py %s\n" %v)
        
    fh.close()
    os.system("sbatch %s" %job_file)
