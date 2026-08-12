#!/bin/bash

#######################
# Docker dependencies #
#######################

grab_docker() {
    if [ "$(docker_is_installed)" = "0" ]; then
        start_block
        print "Grabbing docker..."
        sleep 1
        source "${SCRIPTS}/docker.sh"
    fi
}

##########################
# Running the containers #
##########################

run_containers() {
    if [ "$(deploy_files_are_present)" = "0" ]; then
        config_err
    fi

    docker compose up -d
}

#####################
# Certificate setup #
#####################

retrieve_certificates() {
    start_block
    print "Setting up certificates..."

    if [ "$PROTOCOL_CHOICE" = "https" ]; then
        # set up certificates or reuse them from cache
        if [ "$(certificate_files_are_present)" = "1" ] &&
           [ "$(certificates_are_valid)" = "1" ]; then
            print "Reusing certificates..."
            cpy .cache/conf ./data/certbot
        else
            print "Recreating certificates..."
            source "${SCRIPTS}/certificate.sh"
            add_certificates_to_cache
        fi
    fi
}

###################
# Setup functions #
###################

init() {
    # retrieve all input
    if [ "$(config_files_are_present)" = "0" ]; then
        start_block
        print "Populating environment..."
        get_all_choices
        create_deployment_config
    else
        print "Config already set. Continuing..."
    fi

    # build files if need
    if [ "$(build_files_are_present)" = "0" ]; then
        start_block
        print "Building necessary files..."
        set_up_deployment_environment
    else
        print "Build already present. Continuing..."
    fi
}

build() {
    build_backend
    build_frontend
    pull_dependencies
    retrieve_certificates
}

deploy() {
    start_block

    print "Sucessfully finished deployment setup!"
    print "|"
    print "|"
    print "Run app? [y/N]: " "read"
    read_var choice
    if [ "$choice" = "y" ]; then
        run_containers
    fi

    # cache the environment, since the script
    # was successful
    add_script_env_to_cache
}
