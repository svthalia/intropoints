#!/bin/bash

######################
# Container building #
######################

pull_database() {
    start_block

    print "Pulling database..."
    sudo docker compose up -d database
    printf "Waiting for database to be pulled"

    # wait until postgress is available
    while [[ ! "$(docker exec -i database/ 'pg_isready')" == *"accepting"* ]]; do
        printf "."
        sleep 0.3
    done
    print ""
    print "Database is ready!"
}


pull_backend() {
    start_block
    print "Pulling backend..."

    docker compose build backend
    docker compose up -d backend

    # wait until migrations are done
    #
    # apparently this is really sensitive,
    # so I will keep it to a second for now
    printf "Applying migrations"
    while [ "$(docker exec -i backend/ /bin/bash -c 'python manage.py showmigrations | grep 'no migrations'')" != "" ]; do
        printf "."
        sleep 1
    done
    print ""
    print "Backend container created!"
}


pull_frontend() {
    start_block
    print "Pulling frontend..."

    docker compose build frontend
}


pull_dependencies() {
    start_block

    grab_docker
    print "Pulling remaining dependencies..."
    docker compose pull
}

##############################
# Integrating the containers #
##############################

build_backend() {
    # remove any accidentally added migrations
    print "Sanitizing build..."
    cd "$REPO/backend/"
    rmv $REPO/backend/resources/migrations.tar
    source "./resources/rm_migrations.sh"
    cd "../../"

    # proceed with normal set up
    pull_database
    pull_backend

    start_block
    print "Creating local items..."
    create_django_super_user $ADMIN_NAME "admin@test.com" $ADMIN_PASSWORD
    create_local_oauth_app
}


build_frontend() {
    start_block

    print "Building frontend..."
    pull_frontend
}
