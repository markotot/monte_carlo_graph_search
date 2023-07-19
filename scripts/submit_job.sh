#!/bin/bash
#$ -pe smp 1
#$ -l h_vmem=1G
#$ -l h_rt=1:0:0
#$ -cwd
#$ -j y
#$ -N Example
#$ -m beas

module load python/3.8.5

# Replace the following line with a program or command
apptainer run --env-file myenvs apptainer.sif
