GIT_BRANCH = main
PROJECT_NAME = monte_carlo_graph_search

#APOCRITA
AP_PRIVATE_KEY_PATH = ~/Apocrita/apocrita.ssh
APOCRITA_USER = acw549

.PHONE: apocrita_login
apocrita_login:
	sudo expect ./scripts/apocrita_login.sh \
	${APOCRITA_USER} ${APOCRITA_PASSPHRASE} ${APOCRITA_USER_PASSWORD} ${AP_PRIVATE_KEY_PATH}

.PHONY: apocrita_clone_repo
apocrita_clone_repo:
	sudo expect ./scripts/apocrita_clone_repo.sh \
	${APOCRITA_USER} ${APOCRITA_PASSPHRASE} ${APOCRITA_USER_PASSWORD} ${AP_PRIVATE_KEY_PATH} \
 	${GIT_BRANCH} ${GITHUB_USER} ${GITHUB_TOKEN} ${PROJECT_NAME}

.PHONY: apocrita_build_and_run
apocrita_build_and_run:
	sudo expect ./scripts/apocrita_build_and_run.sh \
 	${APOCRITA_USER} ${APOCRITA_PASSPHRASE} ${APOCRITA_USER_PASSWORD} ${AP_PRIVATE_KEY_PATH} \
 	${GIT_BRANCH} ${PROJECT_NAME} ${NEPTUNE_API_TOKEN}

.PHONY: apocrita_pg_build_and_run
apocrita_build_and_run:
	sudo expect ./scripts/apocrita_build_and_run_playground.sh \
 	${APOCRITA_USER} ${APOCRITA_PASSPHRASE} ${APOCRITA_USER_PASSWORD} ${AP_PRIVATE_KEY_PATH} \
 	${GIT_BRANCH} ${PROJECT_NAME} ${NEPTUNE_API_TOKEN}
