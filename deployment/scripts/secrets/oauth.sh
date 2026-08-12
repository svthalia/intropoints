#!/bin/bash

#####################
# Secret generation #
#####################

# generates a variable length base62 secret
#
# $1  -> the length
# ret -> the secret
gen_secret() {
    echo "$(tr -dc "A-Za-z0-9" < /dev/urandom | head -c $1)"
}

######################
# Saved environments #
######################

# creates a thalia oauth application and
# stores its secrets and data in the .cache
#
# $1 -> (optional) username
# $2 -> (optional) password
create_thalia_oauth_app() {
    local username=$1
    local password=$2

    # login
    credential_login $username $password
    token_login

    add_thalia_oauth_app $DOMAIN_NAME $THALIA_CLIENT_ID $THALIA_CLIENT_SECRET

    # store the id
    THALIA_APP_ID=$(get_oauth_app_id $DOMAIN_NAME)
    clean_cookies

    # commit secrets to cache
    add_thalia_oauth_to_cache
}

# removes the stored thalia oauth app
#
# $1 -> (optional) username
# $2 -> (optional) password
remove_thalia_oauth_app() {
    local username=$1
    local password=$2

    credential_login $username $password
    token_login
    rmv_thalia_oauth_app $THALIA_APP_ID
    clean_cookies
}

# creates a local oauth app
#
# $1 -> the oauth client id
# $2 -> the oauth client secret
create_local_oauth_app() {
    add_local_oauth_app $DJANGO_CLIENT_ID $DJANGO_CLIENT_SECRET
}
