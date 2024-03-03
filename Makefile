GIT_BRANCH = main
PROJECT_NAME = monte_carlo_graph_search

#APOCRITA
AP_PRIVATE_KEY_PATH = ~/Apocrita/apocrita.ssh
APOCRITA_USER = acw549

#EXPERIMENT CONFIG
START_SEED = 1
END_SEED = 100
RUN_NAME = "MCGS"

# Used to login to apocrita server
.SILENT: apocrita_login
apocrita_login:
	sudo expect ./scripts/apocrita_login.sh \
	${APOCRITA_USER} ${APOCRITA_PASSPHRASE} ${APOCRITA_USER_PASSWORD} ${AP_PRIVATE_KEY_PATH}

# Clones the repository from github to apocrita (use only once)
.SILENT: apocrita_clone_repo
apocrita_clone_repo:
	sudo expect ./scripts/apocrita_clone_repo.sh \
	${APOCRITA_USER} ${APOCRITA_PASSPHRASE} ${APOCRITA_USER_PASSWORD} ${AP_PRIVATE_KEY_PATH} \
 	${GIT_BRANCH} ${GITHUB_USER} ${GITHUB_TOKEN} ${PROJECT_NAME}

# Builds and runs the main.py on apocrita using apptainer
.SILENT: apocrita_build_and_run
apocrita_build_and_run:
	sudo expect ./scripts/apocrita_build_and_run.sh \
 	${APOCRITA_USER} ${APOCRITA_PASSPHRASE} ${APOCRITA_USER_PASSWORD} ${AP_PRIVATE_KEY_PATH} \
 	${GIT_BRANCH} ${PROJECT_NAME} ${NEPTUNE_API_TOKEN} ${START_SEED} ${END_SEED} ${RUN_NAME}

# Aggregates the results of the main.py on apocrita using apptainer
.SILENT: apocrita_aggregate
apocrita_aggregate:
	sudo expect ./scripts/apocrita_aggregate.sh \
 	${APOCRITA_USER} ${APOCRITA_PASSPHRASE} ${APOCRITA_USER_PASSWORD} ${AP_PRIVATE_KEY_PATH} \
 	${GIT_BRANCH} ${PROJECT_NAME} ${NEPTUNE_API_TOKEN} ${START_SEED} ${END_SEED} ${RUN_NAME}

# Builds sif files, runs experiments and aggregates the results of the main.py on apocrita using apptainer
 .SILENT: apocrita_build_and_run
apocrita_build_and_run:
	sudo expect ./scripts/apocrita_build_and_run_and_aggregate.sh \
 	${APOCRITA_USER} ${APOCRITA_PASSPHRASE} ${APOCRITA_USER_PASSWORD} ${AP_PRIVATE_KEY_PATH} \
 	${GIT_BRANCH} ${PROJECT_NAME} ${NEPTUNE_API_TOKEN} ${START_SEED} ${END_SEED} ${RUN_NAME}

.SILENT: apocrita_build
apocrita_build:
	sudo expect ./scripts/apocrita_build.sh \
 	${APOCRITA_USER} ${APOCRITA_PASSPHRASE} ${APOCRITA_USER_PASSWORD} ${AP_PRIVATE_KEY_PATH} \
 	${GIT_BRANCH} ${PROJECT_NAME} ${NEPTUNE_API_TOKEN}

# Builds and runs the main.py on apocrita using apptainer
.SILENT: apocrita_run
apocrita_run:
	sudo expect ./scripts/apocrita_run.sh \
 	${APOCRITA_USER} ${APOCRITA_PASSPHRASE} ${APOCRITA_USER_PASSWORD} ${AP_PRIVATE_KEY_PATH} \
 	${GIT_BRANCH} ${PROJECT_NAME} ${NEPTUNE_API_TOKEN} ${START_SEED} ${END_SEED} ${RUN_NAME}

.SILENT: apocrita_clean_runs
apocrita_clean_runs:
	sudo expect ./scripts/apocrita_clean.sh \
 	${APOCRITA_USER} ${APOCRITA_PASSPHRASE} ${APOCRITA_USER_PASSWORD} ${AP_PRIVATE_KEY_PATH} \
 	${GIT_BRANCH} ${PROJECT_NAME}

.PHONY: test
test:
	echo "git clone -b ${GIT_BRANCH} https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/markotot/${PROJECT_NAME}.git"
