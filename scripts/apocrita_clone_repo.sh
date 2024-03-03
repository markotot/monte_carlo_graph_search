#!/usr/bin/expect

set APOC_USERNAME [lindex $argv 0]
set APOC_PASSPHRASE [lindex $argv 1];
set APOC_PASSWORD [lindex $argv 2];
set APOC_PRIVATE_KEY [lindex $argv 3];

set GIT_BRANCH [lindex $argv 4];
set GITHUB_USER [lindex $argv 5];
set GITHUB_TOKEN [lindex $argv 6];

set PROJECT_NAME [lindex $argv 7];

spawn ssh -i $APOC_PRIVATE_KEY $APOC_USERNAME@login.hpc.qmul.ac.uk \
"
  rm -r -f $PROJECT_NAME; \
  git clone -b $GIT_BRANCH https://$GITHUB_USER:$GITHUB_TOKEN@github.com/markotot/$PROJECT_NAME.git
"
expect "Enter passphrase for key '$APOC_PRIVATE_KEY':"
send "$APOC_PASSPHRASE\r"
expect "$APOC_USERNAME@login.hpc.qmul.ac.uk's password"
send "$APOC_PASSWORD\r"
expect EOF
