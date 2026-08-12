#########
# State #
#########

# this might not be the best idea,
# but I needed something fast
config_changed="0"

#####################
# Deployment config #
#####################

rebuild_deployment_config() {
    start_block

    print "Checking the deployment configuration..."

    if [ "$(docker_config_is_valid)" = "0" ]; then
        print "It seems like your current docker compose environment"
        print "is out of sync with the one in your repository."
        print
        print "In order for your changes to take effect, it needs to be"
        print "kept up to date. Wait for it to be updated..."
        print
        print "New input is needed!"
        user_info_wait

        clean_env
        print "Recreating deployment configuration..."
        get_rebuild_choices
        create_deployment_config
        print
        start_block
        print "The protocol choice cannot be overriden. If you want to change it"
        print "please use the '--reset', '-r' or '--clean' or '-c' options."
        user_info_wait

        set_up_environment_secrets
        create_global_var_environment

        config_changed="1"
    fi
}

#########
# Proxy #
#########

update_proxy() {
    start_block
    print "Updating proxy..."

    # load the proxy config file choice
    local proxy_config_file=""
    case $PROTOCOL_CHOICE in
        "http")
            proxy_config_file="data/proxy/conf.d/shw-proxy-http.conf"
            ;;
        "https")
            proxy_config_file="data/proxy/conf.d/shw-proxy-https.conf"
            ;;
        *)
            panic_err
            ;;
    esac

    # replace the placeholders
    cpy "$REPO/deployment/$proxy_config_file" "./$proxy_config_file"
    sed -i "s|\[DOMAIN NAME\]|$DOMAIN_NAME|g" "./$proxy_config_file"

    # recreate the container
    print "Updating proxy..."
    sudo docker compose up -d --force-recreate proxy
    print "Proxy up to date!"
    print "Downgrading proxy..."
    sudo docker compose down proxy
}

rebuild_proxy() {
    start_block
    print "Rebuilding proxy..."

    # ensure the container is running
    # sudo docker compose up -d proxy

    # remove the container after all the
    # operations are done
    sudo docker compose down proxy

    # ensure the base config mathces
    cpy $REPO/deployment/data/proxy/nginx.conf ./data/proxy/nginx.conf

    # check whether the proxy matches the one in the repo
    if [ "$(proxy_config_is_valid)" != "1" ]; then
        print "It seems like your current proxy is out of"
        print "sync with the one in your repository."
        print "Do you want to sync it? [Y/n]: " "read"
        read_var choice

        if [ "$choice" != "n" ]; then
            update_proxy
        fi
    fi
}

############
# Database #
############

rebuild_database() {
    start_block
    print "Rebuilding database..."

    # ensure the container is running
    docker compose up -d database

    # keep track of the new password in case the
    # environment has been updated
    #
    # this can be cached and then checked against,
    # but that's only if you want to change the password
    # manually
    if [ "$config_changed" = "1" ]; then
        docker exec -i database psql -U "django" -d \
            "postgres" -c "ALTER USER django WITH PASSWORD '$POSTGRES_PASSWORD';" > /dev/null
    fi

    # remove the container after operations are
    # completely done
    docker compose down database
}

###########
# Backend #
###########

resolve_migrations() {
    start_block

    # copy all previous migrations and
    # compress them
    print "Resolving migrations..."
    docker exec -i backend/ /bin/bash -c \
        "find . -path '*/migrations/*.py' \
         | tar -cvf migrations.tar -T -" > /dev/null
    docker cp backend:/app/website/migrations.tar ./$REPO/backend/resources/ > /dev/null

    # untrack previous migration index
    print "Resetting migration index..."
    docker exec -i database psql -U "django" -d \
        "postgres" -c "DELETE FROM django_migrations;" > /dev/null
}

rebuild_backend() {
    start_block
    print "Rebuilding backend..."

    # ensure no leftover migrations are
    # present during the build
    rmv ./$REPO/backend/resources/migrations.tar

    # ensure necessary containers are up
    docker compose up -d database
    docker compose up -d backend

    # try to save previous database migrations
    resolve_migrations

    # after all the operations are done, remove
    # the containers
    start_block
    print "Rebuilding backend..."
    docker compose down backend
    docker compose down database

    # rebuild the backend
    docker compose build backend

    # clean previous migrations from build
    rmv ./$REPO/backend/resources/migrations.tar
}

############
# Frontend #
############

rebuild_frontend() {
    start_block
    print "Rebuilding frontend..."

    # ensure the container is up
    # docker compose up -d frontend

    # remove the container after all operations
    # are done
    docker compose down frontend

    # rebuild the frontend
    docker compose build frontend
}
