#!/bin/bash
#$ -pe smp 1
#$ -l h_vmem=1G
#$ -l h_rt=1:0:0
#$ -cwd
#$ -j y
#$ -o job_results

module load python/3.8.5

# Replace the following line with a program or command
apptainer run --env-file myenvs --env "RUN_NAME=$RUN_NAME,START_ID=$START_ID,END_ID=$END_ID" containers/aggregate_data.sif
