#!/bin/bash

#                                             #
# /----------/ Deployment script /----------/ #
#                                             #

# This is the main deployment script that handles automatically
# deploying the Scavenger Hunt Website on a Ubuntu Distribution.
#
# Provides basic functionality for setting up the server directory
# and running the server over different protocols such as:
#   - HTTP;
#   - HTTP(s);
#
# Provides automatic OAuth app creation with Thalia, and local
# OAuth app coupling.
#
# Provides automatic certificate creating and renewal (HTTPs).
#
# Provides caching secrets for faster deployment times under
# development
#
# NOTE: this might need to be translated to another language in the future,
#       but for now bash was the easiest one to set up. If you are working on this
#       and have the time, I would suggest translating it to either C++ or Python.

##########
# Patent #
##########

SCRIPT_NAME="Scavenger Hunt Website Deployment Script"
VERSION="1.6.7"

######################
# Saved environments #
######################

SCRIPT_STATE_ENV="./.cache/.script_state.sh"
SCRIPT_ENV="./.cache/.script_env.sh"
OAUTH_ENV="./.cache/.oauth_env.sh"
STORAGE_ENV="./.cache/.storage_env.sh"

######################
# Deployment Globals #
######################

DOMAIN_NAME=""
DEPLOYMENT=""
PROTOCOL_CHOICE=""
STORAGE=""

DJANGO_SECRET_KEY=""
POSTGRES_PASSWORD=""

THALIA_BASE_URI=""
THALIA_APP_ID=""
THALIA_APP_DOMAIN_NAME=""

THALIA_CLIENT_ID=""
THALIA_CLIENT_SECRET=""

DJANGO_CLIENT_ID=""
DJANGO_CLIENT_SECRET=""

ADMIN_NAME="admin"
ADMIN_PASSWORD="test"

REPO="Scavenger-Hunt-Website"
SCRIPTS="${REPO}/deployment/scripts"

####################
# External scripts #
####################

source "${SCRIPTS}/errors.sh"
source "${SCRIPTS}/help.sh"

source "${SCRIPTS}/clean.sh"
source "${SCRIPTS}/environment.sh"

source "${SCRIPTS}/cache.sh"

source "${SCRIPTS}/validate.sh"
source "${SCRIPTS}/input.sh"
source "${SCRIPTS}/run.sh"

source "${SCRIPTS}/secrets/oauth.sh"
source "${SCRIPTS}/secrets/thalia.sh"
source "${SCRIPTS}/secrets/local.sh"

source "${SCRIPTS}/rebuild.sh"
source "${SCRIPTS}/build.sh"

source "${SCRIPTS}/utils.sh"
source_script_env

##################
# Option handles #
##################

# sets up the entire deployment then tries to run it
#
# !! if everything is already present, just runs the deployment
handle_setup() {
    if [ "$(deploy_files_are_present)" = "1" ]; then
        start_block

        echo "Deployment files already present! Running..."
        run_containers
        exit
    fi

    init
    build
    deploy
}

# rebuilds the containers and environment
handle_rebuild() {
    start_block
    print "Rebuilding containers..."
    sleep 1

    # these need to be in order because of dependencies
    rebuild_deployment_config
    rebuild_database
    rebuild_backend
    rebuild_frontend
    rebuild_proxy
    deploy
}

# displays the help text
handle_help()  { display_basic_help; exit; }

# stops the containers
handle_quit()  {
    start_block
    print "Stopping containers..."
    docker compose stop; exit;
}

# tries to clean all the relevant parts of the environment;
# most of them need to be specified
handle_clean() {
    # ensures safe clean
    start_block
    print "Stopping execution..."
    if [ "$(config_files_are_present)" = "1" ]; then
        docker compose down
    fi

    # clean containers
    start_block
    print "Remove containers?"
    print "|"
    print "This removes all the lingering containers from any other"
    print "previous execution of the script."
    print "|"
    print "Choice [y/N]: " "read"
    read_var choice
    if [ "$choice" = "y" ]; then
        rmv_all_containers
    fi

    # clean container data
    start_block
    print "Remove docker container cache?"
    print "|"
    print "This completely removes all stored data for every container,"
    print "and ensures a clean build."
    print "|"
    print "Choice [y/N]: " "read"
    read_var choice
    if [ "$choice" = "y" ]; then
        clean_all_container_data
    fi

    # clean .cache
    start_block
    print "Clean script build cache?"
    print "|"
    print "This makes it so that every secret, previous script configuration"
    print "and certificate information is cleaned."
    print "|"
    print "Choice: [y/N]: " "read"
    read_var choice
    if [ "$choice" = "y" ]; then
        clean_cache
    fi

    # clean build environment
    if [ "$(file_is_present ./docker-compose.yaml)" = "1" ]; then
        clean_build
        clean_env
    fi

    exit
}

# tries to reset specific parts of the environment
#
# !! note, some parts are tied to each-other, so if
# !! one is removed, so is the other
handle_reset() {
    # keeping track whether to reinitialize
    # the environment or not
    local reinit=""

    # clean container cache files alongside
    # build data
    start_block
    print "Reset docker container cache?"
    print "|"
    print "This completely removes all stored data for every container,"
    print "and ensures a clean build."
    print "|"
    print "Choice [y/N]: " "read"
    read_var choice
    if [ "$choice" = "y" ]; then
        start_block
        print "Cleaning docker cache..."
        clean_all_container_data
        clean_build
        reinit=1
    fi

    # clean config and global envrionment and reset
    # container data (because secrets change)
    start_block
    print "Reset config & environment?"
    print "|"
    print "This removes all configuration files, and the variable environment."
    print "|"
    print "Choice [y/N]: " "read"
    read_var choice
    if [ "$choice" = "y" ]; then
        clean_env
        reinit=1
    fi

    # clean .cache
    start_block
    print "Reset secrets & script cache?"
    print "|"
    print "This makes it so that every secret, previous script configuration"
    print "and certificate information is cleaned."
    print "|"
    print "Choice [y/N]: " "read"
    read_var choice
    if [ "$choice" = "y" ]; then
        clean_cache
    fi

    # if any integral part is missing,
    # reinitialize the whole deployment
    if [ "$reinit" = "1" ]; then
        init
        build
        deploy
    fi
}



####################
# Argument parsing #
####################

# parse the given script options
parse_options() {
    # handle no arguments
    #
    # try to intialize the deployment procedure,
    # or run the containers.
    if [ "$#" = "0" ]; then
        handle_setup
    fi

    local opt_string=":qhcrb"

    while getopts ${opt_string} opt; do
        case ${opt} in
            "b") handle_rebuild ;;
            "r") handle_reset   ;;
            "c") handle_clean   ;;
            "h") handle_help    ;;
            "q") handle_quit    ;;
            *)   arg_err        ;;
        esac
    done

    return
}



#########
# Traps #
#########

check_success() {
    EXIT_STATUS="$?"
    if [ "$EXIT_STATUS" = "0" ]; then
        start_block
        print "Finish up..."
        sleep 2
        clear
        exit
    else
        print "The script was interrupted;"
        print "Exiting in order to prevent faults!"
        print
        print "If the current version is corrupted try the '-c' option"
    fi
}

# exit in case of any error
set -e

# handle abrupt exits
trap check_success EXIT

# clean everything if interrupted
#
# !! this is for my peace of mind


#############
# Arguments #
#############

# translate options for easier parsing
TRANSLATED=""
while (( $# )); do
  case "$1" in
    "--help")              TRANSLATED+=("-h"); shift ;;
    "--build")             TRANSLATED+=("-b"); shift ;;
    "--reset-setup")       TRANSLATED+=("-r"); shift ;;
    "--clean-setup")       TRANSLATED+=("-c"); shift ;;
    "--quit")              TRANSLATED+=("-q"); shift ;;

    "--")                  TRANSLATED+=("--"); shift; TRANSLATED+=("$@"); set -- ;;
    *)                     TRANSLATED+=("$1"); shift ;;
  esac
done
set -- "${TRANSLATED[@]}"



##############
# Entrypoint #
##############

# check running directory
if [ "$(running_in_valid_directory)" = "0" ]; then
    invalid_dir_err
fi

# install docker if not present
if [ "$(docker_is_installed)" = "0" ]; then
    echo "Docker not found! Installing docker..."
    source "${SCRIPTS}/docker.sh"
fi

# parse options (and execute them if necessary)
parse_options $@
