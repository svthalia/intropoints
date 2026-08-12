#!/bin/bash

######################
# Directory cleaning #
######################

clean_build() {
    rmv ./data
}

clean_env() {
    rmv .env
    rmv ./docker-compose.yaml
}

clean_oauth_env() {
    if [ "$(file_is_present $OAUTH_ENV)" = "1" ]; then
        start_block

        print "Previously generated Thalia OAuth app detected..."
        source $OAUTH_ENV

        if [ "$THALIA_APP_ID" = "manual" ]; then
            print "This app is manually managed - cannot remove it automatically!"
            return
        fi

        print "Remove Thalia OAuth app manually? [y/N]: " "read"
        read_var choice
        if [ "$choice" != "y" ]; then
            print "Removing thalia app connected to previous deployment..."
            print "You will need to re-enter your admin account credentials."
            print
            print "If interrupted, you will need to remove it manually; continue..."
            print
            user_info_wait
            remove_thalia_oauth_app
        fi

        rmv $oauth_env
    fi
}

clean_cache() {
    clean_oauth_env
    rmv .cache
}

######################
# Container cleaning #
######################

clean_all_container_data() {
    docker system prune -f -a
}

rmv_all_containers() {
    local containers="$(docker ps -a -q)"

    if [ "$containers" != "" ]; then
        docker rm -f "$containers"
    fi
}

####################
# Cookies cleaning #
####################

clean_cookies() {
    rmv cookies.txt
}

##################
# Fault cleaning #
##################

panic_clean() {
    clean_build
    clean_env
    clean_cookies
    exit 1
}
