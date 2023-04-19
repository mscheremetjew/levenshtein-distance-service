include ./make/print.lib.mk
include ./make/dynamic-recipe.lib.mk

#------------------------------
# dynamic recipes
#
# marked with # dynamic
# A named recipe (eg. manage) will set CMD, and call it
# if it's the last recipe being called (eg. make manage).
# A recipe caught by .DEFAULT will add the recipe name
# (eg. changepassword) to a list of ARGS, and call CMD with
# the list of ARGS if it's the last recipe being called
# (eg. make manage changepassword youruser).
#
# NOTE: don't create any recipes with the same name as any
#       dynamic recipe args (eg. changepassword)
#------------------------------

#------------------------------
# vars
#------------------------------

SHELL := /bin/bash
CMD := ""
POS_ARGS := ""
ARGS := ""
SSH_AUTH_SOCK_RSA_MOUNT_VOLUMES = -v ~/.ssh/id_rsa:/id_rsa:ro -v ~/.ssh/id_rsa.pub:/id_rsa.pub:ro
SSH_AUTH_SOCK_ED25519_MOUNT_VOLUMES = -v ~/.ssh/id_ed25519:/id_ed25519:ro -v ~/.ssh/id_ed25519.pub:/id_ed25519.pub:ro
DOCKER_RUN_ARGS_FOR_SSH_AUTH_SOCK_RSA := --entrypoint= --rm --tty --interactive --env SSH_AUTH_SOCK=/run/host-services/ssh-auth.sock -v /run/host-services/ssh-auth.sock:/run/host-services/ssh-auth.sock ${SSH_AUTH_SOCK_RSA_MOUNT_VOLUMES}
DOCKER_RUN_ARGS_FOR_SSH_AUTH_SOCK_ED25519 := --entrypoint= --rm --tty --interactive --env SSH_AUTH_SOCK=/run/host-services/ssh-auth.sock -v /run/host-services/ssh-auth.sock:/run/host-services/ssh-auth.sock ${SSH_AUTH_SOCK_ED25519_MOUNT_VOLUMES}
SERVICE_TAG :=mscheremetjew/levenshtein-distance-service

#------------------------------
# helpers
#------------------------------

COMMA := ,

#------------------------------
# help
#------------------------------

.PHONY: help
help:
	$(call print_h1,"AVAILABLE","OPTIONS")
	$(call print_space)
	$(call print_h2,"code")
	$(call print_options,"lint","Run code lint checks.")
	$(call print_options,"format","Automatically format code where possible.")
	$(call print_space)
	$(call print_h2,"dependency")
	$(call print_options,"pip-compile-rsa","Compile requirements.txt from requirements.in without upgrading the packages and build the images using RSA SSH key.")
	$(call print_options,"pip-compile-ed-25519","Compile requirements.txt from requirements.in without upgrading the packages and build the images with ed-25519 SSH key.")
	$(call print_space)
	$(call print_h2,"test")
	$(call print_options,"pytest","Run all pytests (takes args additional via ARGS=\"...\" eg. \`\`make pytest ARGS=\"entertainment/tests/ --reuse-db\"\`\` or \`\`make pytest ARGS=\"-m \'mark1 and not mark2\'\"\`\`).")
	$(call print_options,"pytest-h","Show pytest help")
	$(call print_space)
	$(call print_h2,"dynamic recipes")
	$(call print_h3,"accepts any number of additional positional args as well as --args via ARGS=\"...\"")

#------------------------------
# code
#------------------------------

.PHONY: lint
lint: build-services
	$(call print_h1,"LINTING","CODE")
	@docker-compose run --rm --entrypoint=sh distance_calculator -c "flake8"
	@docker-compose run --rm --entrypoint=sh distance_calculator -c "isort --recursive --check-only"
	@docker-compose run --rm --entrypoint=sh distance_calculator -c "black --check ./"
	$(call print_h1,"LINTING","COMPLETE")

.PHONY: format
format: build-services
	$(call print_h1,"FORMATTING","CODE")
	@docker-compose run --rm --entrypoint=sh distance_calculator -c "isort --recursive --apply"
	@docker-compose run --rm --entrypoint=sh distance_calculator -c "black ./"
	$(call print_h1,"FORMATTING","COMPLETE")

#------------------------------
# docker helpers
#------------------------------

# runs docker compose with the provided args,
# and prints out the full command being run
define dockercompose
	$(call print,"docker-compose $(1)")
	@docker-compose $(1)
endef

# checks for 'local' command and if local config file exists,
# and if so runs docker-compose using the local file,
# if not prints a warning and runs with default config.
define dockercomposelocal
	@$(eval TARGETING_LOCAL := $(if $(filter-out local,$(lastword $(MAKECMDGOALS))),,""))
	@$(eval LOCAL_FILE_EXISTS := $(if $(wildcard $(FILE_PATH_DOCKER_COMPOSE_LOCAL)),"",))
	@$(eval DOCKER_COMPOSE_FILE_ARG := $(if $(and $(TARGETING_LOCAL),$(LOCAL_FILE_EXISTS)),"-f $(FILE_PATH_DOCKER_COMPOSE_LOCAL) ",))
	@$(if $(TARGETING_LOCAL),$(if $(LOCAL_FILE_EXISTS),,$(call print_warning,"Local config missing$(COMMA) please create: $(FILE_PATH_DOCKER_COMPOSE_LOCAL)$(COMMA) using default...")),)
	$(call dockercompose,"$(DOCKER_COMPOSE_FILE_ARG)$(1)")
endef

define build-services
	$(call print_h1,"BUILDING","IMAGES","FROM","SCRATCH")
	@docker build --ssh default -t $(SERVICE_TAG) -f Dockerfile .
	$(call print_h1,"IMAGES","BUILT","FROM","SCRATCH")
endef

#------------------------------
# docker
#------------------------------

.PHONY: build-services
build-services:
	$(call build-services)

.PHONY: up
up: build-services
	$(call print_h1,"LAUNCHING","ALL","DOCKER","CONTAINERS")
	$(call dockercomposelocal,"up -d")

.PHONY: buildup
buildup: build-services
	$(call print_h1,"REBUILDING","AND","LAUNCHING","ALL DOCKER CONTAINERS")
	$(call dockercomposelocal,"up --build")

#------------------------------
# utility
#------------------------------

.PHONY: shell-distance_calculator
shell-distance_calculator:
	$(call print_h1,"ENTERING","SHELL")
	@docker-compose exec distance_calculator /bin/bash

#------------------------------
# dependency
#------------------------------

.PHONY: pip-compile-rsa pip-compile-ed-25519

pip-compile-rsa: build-services
	$(call print_h1,"COMPILING","REQUIREMENTS")
	@-docker run $(DOCKER_RUN_ARGS_FOR_SSH_AUTH_SOCK_RSA) -v ${PWD}:/var/levenshtein-distance-service/ $(SERVICE_TAG) sh -c "ssh-add /id_rsa && pip-compile --no-header --output-file=app/requirements.txt"
	$(call build-services)
	$(call print_h1,"REQUIREMENTS","COMPILED")

pip-compile-ed-25519: build-services
	$(call print_h1,"COMPILING","REQUIREMENTS")
	@-docker run $(DOCKER_RUN_ARGS_FOR_SSH_AUTH_SOCK_ED25519) -v ${PWD}:/var/levenshtein-distance-service/ $(SERVICE_TAG) sh -c "ssh-add /id_ed25519 && pip-compile --no-header --output-file=app/requirements.txt"
	$(call build-services)
	$(call print_h1,"REQUIREMENTS","COMPILED")

#------------------------------
# Q&A
#------------------------------

.PHONY: pytest
pytest:
	$(call print_h1,"RUNNING","PYTEST","TESTS")
	@$(eval CMD := "docker-compose run --rm --entrypoint=sh distance_calculator -c 'pytest -vv'")
	$(call run_if_last,${CMD} ${POS_ARGS} ${ARGS})

.PHONY: pytest-h
pytest-h:
	$(call print_h1,"SHOWING","PYTEST","HELP")
	@docker-compose run --rm --entrypoint=sh distance_calculator -c "pytest --help"

#------------------------------
# dynamic functionality
#------------------------------

# adds recipe name (eg. changepassword) to POS_ARGS, calls CMD with ARGS and POS_ARGS if last
.DEFAULT:
	@$(eval POS_ARGS += $@)
	@$(eval ARGS += $(ARGS))
	$(call run_if_last,${CMD} ${ARGS} ${POS_ARGS})