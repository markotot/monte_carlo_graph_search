#!/bin/bash
#$ -pe smp 1
#$ -l h_vmem=1G
#$ -l h_rt=5:0:0
#$ -cwd
#$ -j y
#$ -o job_results

module load python/3.8.5

# Replace the following line with a program or command
echo "RUN_NAME=$1,SEED=$SGE_TASK_ID"
echo "SecondParam=$2"
echo "ThirdParam=$3"
apptainer run --env-file myenvs --env "RUN_NAME=$1,SEED=$SGE_TASK_ID" mcgs.sif
