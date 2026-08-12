#!/bin/bash

##############################
# Global variable retrievers #
##############################

# sets the deployment choice
get_deployment_choice() {
    start_block

    print "Run the website in:"
    print " - Development [dev];"
    print " - Production  [prod];"
    print ""
    print "Choice [PROD]: " "read"
    read_var choice

    case $choice in
        "prod"|"") DEPLOYMENT=prod ;;
        "dev")     DEPLOYMENT=dev  ;;
        *)         arg_err         ;;
    esac
}

# sets the storage choice
get_storage_choice() {
    start_block

    print "File storage handler:"
    print " - Local  [local];"
    print " - AWS S3 [s3];"
    print ""
    print "Choice [LOCAL]: " "read"
    read_var choice

    case $choice in
        "local"|"") STORAGE="local" ;;
        "s3")       STORAGE="s3"    ;;
        *)          arg_err         ;;
    esac
}

# sets the admin name
get_admin_name() {
    start_block

    print "Admin name [admin]: " "read"
    read_var ADMIN_NAME

    if [ "$ADMIN_NAME" = "" ]; then
        ADMIN_NAME="admin"
    fi
}

# sets the admin password
get_admin_password() {
    start_block

    print "Admin password [shw]: " "read"
    read_var ADMIN_PASSWORD

    # TODO: add password validation - install libpwquality-tools
    #       then use pwscore; rating of at least 85!
    if [ "$ADMIN_PASSWORD" = "" ]; then
        ADMIN_PASSWORD="shw"
    fi
}

# sets up all the necessary admin credentials
get_admin_credentials() {
    start_block

    get_admin_name
    get_admin_password
}

# sets protocol choice
get_protocol_choice() {
    start_block

    print "Choose transport protocol [HTTP/https]: " "read"
    read_var choice

    case $choice in
        "https")   PROTOCOL_CHOICE="https" ;;
        "http"|"") PROTOCOL_CHOICE="http" ;;
        *)         arg_err ;;
    esac
}

# sets domain name
get_domain_name() {
    start_block

    print "Domain name [scavengerhunt.thalia.nu]: " "read"
    read_var DOMAIN_NAME

    if [ "$DOMAIN_NAME" = "" ]; then
        DOMAIN_NAME="scavengerhunt.thalia.nu"
    fi
}

####################################
# Cloud storage variable retrieves #
####################################

# AWS #

# retrieves the AWS S3 bucket name
get_aws_bucket_name() {
    start_aws_block

    print "Enter the S3 bucket name: " "read"
    read_var AWS_BUCKET_NAME
}

# retrieves the AWS S3 region name
get_aws_region_name() {
    start_aws_block

    print "Enter the S3 region name: " "read"
    read_var AWS_REGION_NAME
}

# retrieves the AWS access key ID
get_aws_access_key_id() {
    start_aws_block

    print "Enter the AWS access key ID: " "read"
    read_var AWS_ACCESS_KEY_ID
}

# retrieves the AWS secret access key
get_aws_secret_access_key() {
    start_aws_block

    print "Enter the AWS secret access key: " "read"
    read_var AWS_SECRET_ACCESS_KEY
}

# retrieves the AWS default ACL
get_aws_default_acl() {
    start_aws_block

    print "Enter the AWS default ACL [optional]: " "read"
    read_var AWS_DEFAULT_ACL

    if [ "$AWS_DEFAULT_ACL" = "" ]; then
        AWS_DEFAULT_ACL="DISABLED"
    fi
}

# retrieve all AWS credentials
get_aws_credentials() {
    if [ "$(file_is_present "$STORAGE_ENV")" = "1" ]; then
        source $STORAGE_ENV
    fi

    if [ "$PREVIOUS_STORAGE" = "s3" ]; then
        print "Reusing AWS credentials..."
        return
    fi

    get_aws_bucket_name
    get_aws_region_name
    get_aws_access_key_id
    get_aws_secret_access_key
    get_aws_default_acl

    add_storage_options_to_cache
}

############################
# Base variable retrievers #
############################

# sets all the choices that do not
# actively modify the deployment environment
get_base_choices() {
    get_domain_name
    get_deployment_choice

    if [ "$DEPLOYMENT" = "prod" ]; then
        get_admin_credentials
        get_storage_choice
    fi
}

##############
# Shorthands #
##############

get_rebuild_choices() {
    get_base_choices

    if [ "$STORAGE" = "s3" ]; then
        get_aws_credentials
    fi
}

# sets all choice variables
get_all_choices() {
    get_base_choices

    # read dev only
    if [ "$DEPLOYMENT" = "dev" ]; then
        get_protocol_choice
    fi

    if [ "$STORAGE" = "s3" ]; then
        get_aws_credentials
    fi
}
