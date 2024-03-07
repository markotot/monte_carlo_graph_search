#!/usr/bin/expect

set APOC_USERNAME [lindex $argv 0]
set APOC_PASSPHRASE [lindex $argv 1];
set APOC_PASSWORD [lindex $argv 2];
set APOC_PRIVATE_KEY [lindex $argv 3];

set GIT_BRANCH [lindex $argv 4];
set PROJECT_NAME [lindex $argv 5];
set NEPTUNE_API_TOKEN [lindex $argv 6];

set START_SEED [lindex $argv 7];
set END_SEED [lindex $argv 8];

set RUN_NAME [lindex $argv 9];


ECHO_CMD="echo Test ${RUN_NAME} ${GIT_BRANCH} ${PROJECT_NAME}"

spawn ssh -i $APOC_PRIVATE_KEY $APOC_USERNAME@login.hpc.qmul.ac.uk \
 "
  source ../../../../../etc/bashrc; \
  rm myenvs; \
  echo $ECHO_CMD; \
"
expect "Enter passphrase for key '$APOC_PRIVATE_KEY':"
send "$APOC_PASSPHRASE\r"
expect "$APOC_USERNAME@login.hpc.qmul.ac.uk's password"
send "$APOC_PASSWORD\r"
interact
