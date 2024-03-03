#!/bin/bash
#$ -pe smp 1
#$ -l h_vmem=1G
#$ -l h_rt=5:0:0
#$ -cwd
#$ -j y
#$ -o job_results

module load python/3.8.5

# Replace the following line with a program or command
apptainer run --env-file myenvs --env "RUN_NAME=$RUN_NAME,SEED=$SGE_TASK_ID" containers/mcgs.sif
