#!/usr/bin/expect

set APOC_USERNAME [lindex $argv 0]
set APOC_PASSPHRASE [lindex $argv 1];
set APOC_PASSWORD [lindex $argv 2];
set APOC_PRIVATE_KEY [lindex $argv 3];

set GIT_BRANCH [lindex $argv 4];
set PROJECT_NAME [lindex $argv 5];
set NEPTUNE_API_TOKEN [lindex $argv 6];

spawn ssh -i $APOC_PRIVATE_KEY $APOC_USERNAME@login.hpc.qmul.ac.uk \
 "
 cd $PROJECT_NAME; \
 git pull; \
 git checkout $GIT_BRANCH; \
 git pull; \
 cd ../; \

 source ../../../../../etc/bashrc; \
 rm myenvs; \
 echo NEPTUNE_API_TOKEN=$NEPTUNE_API_TOKEN > myenvs; \
 apptainer build --force gaig-pipeline.sif $PROJECT_NAME/apptainer/gaig-pipeline.def; \
 qsub $PROJECT_NAME/scripts/submit_job.sh;
 "
expect "Enter passphrase for key '$APOC_PRIVATE_KEY':"
send "$APOC_PASSPHRASE\r"
expect "$APOC_USERNAME@login.hpc.qmul.ac.uk's password"
send "$APOC_PASSWORD\r"
interact
