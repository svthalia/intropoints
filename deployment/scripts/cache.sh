#!/bin/bash

#######################
#  Retrieve cache env #
#######################

# reuses the previous script environment
source_script_env() {
    if [ "$(file_is_present $SCRIPT_ENV)" = "1" ]; then
        source $SCRIPT_ENV
    fi
}

###################
#  Populate cache #
###################

# adds the necessary certificate files to the
# cache for reuse
add_certificates_to_cache() {
    rmv ./.cache/conf
    cpy ./data/certbot/conf ./.cache
}

# adds the some of the current script variables
# to the cache for future reuse
add_script_env_to_cache() {
    rmv $SCRIPT_ENV
    new_file $SCRIPT_ENV

    echo "# Script env file"                >> $SCRIPT_ENV
    echo                                    >> $SCRIPT_ENV
    echo "DOMAIN_NAME=$DOMAIN_NAME"         >> $SCRIPT_ENV
    echo "PROTOCOL_CHOICE=$PROTOCOL_CHOICE" >> $SCRIPT_ENV
    echo "THALIA_BASE_URI=$THALIA_BASE_URI" >> $SCRIPT_ENV
}

# adds the necessary thalia oauth secrets to a
# sepparate environment
add_thalia_oauth_to_cache() {
    rmv $OAUTH_ENV
    new_file $OAUTH_ENV

    echo "# OAuth env file"                           >> $OAUTH_ENV
    echo                                              >> $OAUTH_ENV
    echo "THALIA_APP_ID=$THALIA_APP_ID"               >> $OAUTH_ENV
    echo "THALIA_APP_DOMAIN_NAME=$DOMAIN_NAME"        >> $OAUTH_ENV
    echo "THALIA_CLIENT_ID=$THALIA_CLIENT_ID"         >> $OAUTH_ENV
    echo "THALIA_CLIENT_SECRET=$THALIA_CLIENT_SECRET" >> $OAUTH_ENV
}

# adds the storage options and secretes to the cache
add_storage_options_to_cache() {
    rmv $STORAGE_ENV
    new_file $STORAGE_ENV

    if [ "$STORAGE" = "s3" ]; then
        echo "# S3 storage env file"                        >> $STORAGE_ENV
        echo                                                >> $STORAGE_ENV
        echo "PREVIOUS_STORAGE=$STORAGE"                    >> $STORAGE_ENV
        echo "AWS_BUCKET_NAME=$AWS_BUCKET_NAME"             >> $STORAGE_ENV
        echo "AWS_REGION_NAME=$AWS_REGION_NAME"             >> $STORAGE_ENV
        echo "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID"         >> $STORAGE_ENV
        echo "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY" >> $STORAGE_ENV
        echo "AWS_DEFAULT_ACL=$AWS_DEFAULT_ACL"             >> $STORAGE_ENV
        return
    fi
}
