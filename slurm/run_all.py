#!/usr/bin/env python
#
# Copyright (C) 2018 Vanessa Sochat.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pickle
import json
import sys
import os

scratch = os.environ['SCRATCH']

if len(sys.argv) > 1:
    container = sys.argv[1]
else:
    # We pulled the container here
    container = os.path.join(scratch, 'zenodo-ml', 'zenodo-ml')

# The container must exist
if not os.path.exists(container):
    print('Container not found at %s' %container)
    print('singularity pull docker://vanessa/zenodo-ml')
    sys.exit(1)

# The database must exist
database = os.path.abspath('../records.pkl')
if not os.path.exists(database):
    print('Database not found at %s' %database)
    sys.exit(1)

print('Loading Zenodo Hits Database!')
hits = pickle.load(open(database, 'rb'))

# Here is the output data folder base
output_data = os.path.join(scratch, 'WORK', 'zenodo-ml')
here = os.getcwd()
jobs = '%s/jobs' %here

os.system('mkdir -p %s' %output_data)
os.system('mkdir -p %s' %jobs)

# Do the comparison with the rest
zenodo_ids = list(hits.keys())

print('%s zenodo ids are found to process!' %len(zenodo_ids)) 

# This is a general script to submit the job files
with open('run_jobs.sh', 'w') as run_jobs:
    run_jobs.writelines('#!/bin/bash\n')
    for zid in zenodo_ids:
        run_jobs.writelines('sbatch -p russpold %s/run_%s.sh\n' %(jobs, zid))

# Write a bash file to submit jobs
for zid in zenodo_ids:
    with open('jobs/run_%s.sh' %zid, 'w') as filey:
        filey.writelines('#!/bin/bash\n')
        outfolder = os.path.join(output_data, str(zid))
        print ("Processing Zenodo ID %s" %(zid))
        # Write job to file
        filey.writelines("#SBATCH --job-name=zenodo-ml_%s\n" %(zid))
        filey.writelines("#SBATCH --output=%s/jobs/zenodo-ml-%s.out\n" %(here,zid))
        filey.writelines("#SBATCH --error=%s/jobs/zenodo-ml-%s.err\n" %(here,zid))
        filey.writelines("#SBATCH --time=360:00\n")
        filey.writelines("#SBATCH --mem=8000\n")
        filey.writelines('ml singularity\n')
        args = "%s %s %s" %(zid, outfolder, database)
        filey.writelines('PYTHONPATH= singularity exec --bind %s:/code %s /opt/conda/bin/python /code/run.py %s' %(here, container, args))
