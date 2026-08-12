#!/bin/bash

#################
# Configuration #
#################

# trims the main config such that https options are removed
set_up_config_for_http() {
    sed -i "/# HTTPS/d" ./docker-compose.yaml
}

# trims the main config such that cloud storage options are removed
set_up_config_for_local_storage() {
    sed -i "/# AWS/d" ./docker-compose.yaml
}

# copies up the deployment configuration
create_deployment_config() {
    cpy "${REPO}/deployment/docker-compose.yaml" ./

    if [ "$PROTOCOL_CHOICE" = "http" ]; then
        set_up_config_for_http
    fi

    if [ "$STORAGE" = "local" ]; then
        set_up_config_for_local_storage
     fi
}

####################
# Base environment #
####################

# copies the necessary folders and configs
create_base_docker_environment() {
    # remove scripts
    rmv ./data/deploy.sh
    rmv ./data/scripts

    # copy all necessary data
    cpy "${REPO}/deployment/data" ./

    # setup necessary directories
    new_dir ./data/share
    new_dir ./data/share/static
    new_dir ./data/share/media

    new_dir ./data/database
    new_dir ./data/database/dat

    new_dir ./.cache

}

########################
# Variable environment #
########################

# creates the environment for the required globals;
# uses all marked globals in "deploy.sh";
create_global_var_environment() {
    # create the .env file
    new_file .env

    # initialize .env file
    print "# Docker Compose Environment Variables"        >> .env
    print                                                 >> .env

    print                                                 >> .env
    print "PROTOCOL=$PROTOCOL_CHOICE"                     >> .env

    print                                                 >> .env
    print "DOMAIN_NAME=$DOMAIN_NAME"                      >> .env
    print "ALLOWED_HOST=$DOMAIN_NAME"                     >> .env

    print "DJANGO_OAUTH_APP_ID=$DJANGO_CLIENT_ID"         >> .env
    print "DJANGO_OAUTH_APP_SECRET=$DJANGO_CLIENT_SECRET" >> .env

    print                                                 >> .env
    print "THALIA_BASE_URI=$THALIA_BASE_URI"              >> .env
    print "THALIA_OAUTH_APP_ID=$THALIA_CLIENT_ID"         >> .env
    print "THALIA_OAUTH_APP_SECRET=$THALIA_CLIENT_SECRET" >> .env

    print                                                 >> .env
    print "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"          >> .env
    print "DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY"          >> .env

    print                                                 >> .env
    print "STORAGE=$(echo "$STORAGE" | tr a-z A-Z)"       >> .env

    if [ "$STORAGE" = "s3" ]; then
        print                                                 >> .env
        print "# AWS S3 storage options"                      >> .env
        print                                                 >> .env
        print "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID"          >> .env
        print "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY"  >> .env
        print "AWS_BUCKET_NAME=$AWS_BUCKET_NAME"              >> .env
        print "AWS_S3_REGION_NAME=$AWS_REGION_NAME"           >> .env
        print "AWS_DEFAULT_ACL=$AWS_DEFAULT_ACL"              >> .env
    fi
}

########################
# Protocol environment #
########################

# makes sure all the certificate directories and files ar
# present
set_up_https_environment() {
    # remove unnecessary proxy config
    rmv ./data/proxy/conf.d/shw-proxy-http.conf
    sed -i "s|\[DOMAIN NAME\]|$DOMAIN_NAME|g" ./data/proxy/conf.d/shw-proxy-https.conf

    # set up certbot environment
    new_dir ./data/certbot
    new_dir ./data/certbot/www
    new_dir ./data/certbot/conf
}

# ensure that http is prioritized
set_up_http_environment() {
    # remove unnecessary proxy config
    rmv ./data/proxy/conf.d/shw-proxy-https.conf

    # remove unnecessary compose data
    sed -i "/# HTTPS/d" ./docker-compose.yaml
    sed -i "s|\[DOMAIN NAME\]|_|g" ./data/proxy/conf.d/shw-proxy-http.conf
}

########################
# Deployment specifics #
########################

# sets the necessary globals for dev
set_up_environment_for_dev() {
    THALIA_BASE_URI="https://staging.thalia.nu"

    # Dev always uses local storage
    STORAGE="local"
}

# sets the necessary globals for prod;
#   - generates minor secrets and credentials
set_up_environment_for_prod() {
    # TODO!
    #   - For now we only have access to the staging website,
    #     change to "https://thalia.nu" during production
    THALIA_BASE_URI="https://staging.thalia.nu"

    PROTOCOL_CHOICE="https"
}

#######################
# Environment Secrets #
#######################

# sets the necessary secrets or sources them from the cache
#
# !!
# !! TODO! this needs to be split up so bad, but I do not have the
# !!       energy for that anymore
# !!
# !!       to be fair, I have no idea how to split this more than I have,
# !!       since I am using return statements to manage flow, but I also want
# !!       to print messages - somebody smarter than me needs to do this...
# !!
set_up_environment_secrets() {
    # local secrets
    DJANGO_SECRET_KEY="$(gen_secret 40)"
    POSTGRES_PASSWORD="$(gen_secret 40)"

    DJANGO_CLIENT_ID="$(gen_secret 40)"
    DJANGO_CLIENT_SECRET="$(gen_secret 100)"

    # external secrets
    if [ "$(file_is_present $OAUTH_ENV)" = "1" ]; then
        print "Checking cache..."
        source "$OAUTH_ENV"
        if [ "$(oauth_app_is_valid)" = "0" ] &&
           [ "$THALIA_APP_ID" != "manual" ];
        then
            print "Secrets are registered for a different domain name!"
            clean_oauth_env
        else
            print "Reusing secrets from cache!"
            return
        fi
    fi

    # manual management of external secrets;
    # if specified
    print "Create Thalia OAuth app manually? [y/N]: " "read"
    read_var choice
    if [ "$choice" = "y" ]; then
        print "Create the Thalia OAuth app under the name $DOMAIN_NAME;"
        print "Then, enter the following here"
        print "Enter client ID: " "read"
        read_var thalia_app_id
        print "Enter client secret: " "read"
        read_var thalia_app_secret

        # flag the app as being manually managed
        # and store the secrets
        THALIA_APP_ID=manual
        add_thalia_oauth_to_cache

        print
        print "!! If mistyped, edit them in .env; mainly:"
        print "!! THALIA_APP_ID"
        print "!! THALIA_APP_SECRET"
        print "!! But first, wait for the script to finish. Then rebuild."
        print
        user_info_wait

        return
    fi

    # generate oauth secrets and register them if not
    # valid nor present
    start_block
    print "Generating new Thalia OAuth secrets..."
    THALIA_CLIENT_ID="$(gen_secret 40)"
    THALIA_CLIENT_SECRET="$(gen_secret 128)"
    create_thalia_oauth_app
}

#####################
# Environment Setup #
#####################

# sets up the whole deployment environment
set_up_deployment_environment() {
    # base files
    create_base_docker_environment

    # choose variables based on deployment choice
    if [ "$DEPLOYMENT" = "prod" ]; then
        set_up_environment_for_prod
        set_up_https_environment
    else
        set_up_environment_for_dev
        if [ "$PROTOCOL_CHOICE" = "https" ]; then
            set_up_https_environment
        else
            set_up_http_environment
        fi
    fi

    # commit to the environment and
    # set up secrets
    set_up_environment_secrets
    create_global_var_environment
}
