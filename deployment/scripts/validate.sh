#!/bin/bash

#####################
# Required packages #
#####################

# ret -> 1 if yes; 0 if not
docker_is_installed() {
    if [ -x "$(command -v docker)" ]; then
        echo 1
        return
    fi

    echo 0
}

##################
# Required files #
##################

# $1 -> file name
#
# ret -> 1 if yes; 0 if not
file_is_present() {
    if [ ! -e "$1" ]; then
        echo 0
        return
    fi

    echo 1
}

# ret -> 1 if yes; 0 if no
certificate_files_are_present () {
    local params_dir=".cache/conf"
    local cert_dir=".cache/conf/live/$DOMAIN_NAME"

    res=$((
        $(file_is_present "$cert_dir/fullchain.pem") &
        $(file_is_present "$cert_dir/privkey.pem") &
        $(file_is_present "$params_dir/options-ssl-nginx.conf") &
        $(file_is_present "$params_dir/ssl-dhparams.pem")
    ))

    echo $res
}

# ret -> 1 if yes; 0 if no
config_files_are_present () {
    local res=$((
        $(file_is_present "docker-compose.yaml") &
        $(file_is_present ".env")
    ))

    echo $res
}

# ret -> 1 if yes; 0 if no
build_files_are_present() {
    local res=$((
        $(file_is_present "data") &
        $(file_is_present "data/proxy/nginx.conf") &
        $(file_is_present "data/proxy/conf.d")
    ))

    echo $res
}

# ret -> 1 if yes; 0 if no
deploy_files_are_present() {
    local res=$((
        $(build_files_are_present) &
        $(config_files_are_present)
    ))

    echo $res
}

########################
# Required directories #
########################

# ret -> 1 if yes; 0 if no
running_in_valid_directory() {
    local res=$((
        $(file_is_present "${REPO}/deployment/docker-compose.yaml") &
        $(file_is_present "${REPO}/deployment/data") &
        $(file_is_present "${REPO}/deployment/data/proxy/nginx.conf") &
        $(file_is_present "${REPO}/deployment/data/proxy/conf.d")
    ))

    echo $res
}

#############
# OAuth app #
#############

# ret -> 1 if yes; 0 if the stored app domain name does not match
oauth_app_is_valid() {
    if [ "$THALIA_APP_DOMAIN_NAME" = "$DOMAIN_NAME" ]; then
        echo 1
        return
    fi

    echo 0
}

################
# Certificates #
################

# ret -> 1 if yes; 0 if it needs renewal
certificates_are_valid() {
    local cert_file=".cache/conf/live/$DOMAIN_NAME/fullchain.pem"

    if [ "$(file_is_present $cert_file)" = "0" ]; then
        echo 0
        return
    fi

    if [ "$(openssl x509 -checkend 86400 -noout -in $cert_file)" = "Certificate will expire" ];
    then
        echo 0
        return
    fi

    echo 1
}

###############
# Environment #
###############

# ret -> 1 if yes; 0 if the environment has changed
docker_config_is_valid() {
    local base_config="$REPO/deployment/docker-compose.yaml"
    local current_config="./docker-compose.yaml"

    cpy "$base_config" "./comp.conf"
    base_config="./comp.conf"

    if [ "$PROTOCOL_CHOICE" = "http" ]; then
        sed -i "/# HTTPS/d" $base_config
    fi

    if [ "$STORAGE" = "local" ]; then
        sed -i "/# AWS/d" $base_config
    fi

    if [ "$(cmp $base_config $current_config)" != "" ]; then
        echo 0
    else
        echo 1
    fi

    rmv $base_config
}

#########
# Proxy #
#########

# ret -> 1 if yes; 0 if the proxy config is outdated
proxy_config_is_valid() {
    local base_config_path="$REPO/deployment/data/proxy/conf.d"
    local current_config=""
    local base_config="comp.conf"

    # copy the template to a reachable location
    case $PROTOCOL_CHOICE in
        "http")
            cpy "$base_config_path/shw-proxy-http.conf" "./$base_config"
            current_config="./data/proxy/conf.d/shw-proxy-http.conf"
            ;;

        "https")
            cpy "$base_config_path/shw-proxy-https.conf" "./$base_config"
            current_config="./data/proxy/conf.d/shw-proxy-https.conf"
            ;;
        *)
            panic_err
            ;;
    esac

    # replace placeholders
    sed -i "s|\[DOMAIN NAME\]|$DOMAIN_NAME|g" "./$base_config"

    # compare the two versions
    if [ "$(cmp $base_config $current_config)" != "" ]; then
        echo 0
    else
        echo 1
    fi

    rmv $base_config
}
