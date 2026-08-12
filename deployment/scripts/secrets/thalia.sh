#!/bin/bash

########################################
# Remote Thalia OAuth access utilities #
########################################

########
# Urls #
########

# retrieves the (staging) thalia login url
#
# ret -> the url
get_login_url() {
    echo "$THALIA_BASE_URI/user/account/login/"
}

# retrieves the (staging) thalia oauth app
# creation rul
#
# ret -> the url
get_add_url() {
    echo "$THALIA_BASE_URI/admin/oauth2_provider/application/add/"
}

# retrieves the (staging) thalia oauth app
# view url
#
# ret -> the url
get_select_url() {
    echo "$THALIA_BASE_URI/admin/oauth2_provider/application/"
}

# retrieves the (staging) thalia login app
# view url
#
# ret -> the url
get_remove_url() {
    echo "$THALIA_BASE_URI/admin/oauth2_provider/application/"
}

###########
# Globals #
###########

login_attempts=0

cookies=cookies.txt
csrf_token=""

user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
curl_bin="curl -s -c $cookies -b $cookies -A "$user_agent""

########
# CSRF #
########

# grabs the cookies of the login page and parses
# them for the csrf token, if found, sets the token
get_csrf() {
    if [ "$(file_is_present cookies.txt)" = "0" ]; then
        $curl_bin -e "$(get_login_url)" -L "$(get_login_url)" >/dev/null
    fi

    csrf_token="$(grep csrftoken $cookies | sed 's/^.*csrftoken\s*//')"
}

##################
# Login attempts #
##################

# exits if the login attempts exceed 3
check_login_attempts() {
    if [[ $login_attempts -gt "3" ]]; then
        print "Too many attempts! Exiting..." "error"
        clean_cookies
        exit 1
    fi
}

# tries the given credentials, and if they fail
# retries the credential login step
#
# $1 -> username
# $2 -> password
try_credentials() {
    local username="$1"
    local password="$2"

    # post credentials
    print "Entering credentials..."
    credentials_page="$($curl_bin \
                        -e "$(get_login_url)" \
                        -H "X-CSRFToken: $csrf_token" \
                        -X POST \
                        --data-urlencode "csrfmiddlewaretoken=$csrf_token" \
                        --data-urlencode "rate_limited_login_view-current_step=auth" \
                        --data-urlencode "auth-username=$username" \
                        --data-urlencode "auth-password=$password" \
                        -L $(get_login_url))"

    # test whether the login succeeded
    if [ "$(echo $credentials_page | grep "Invalid username or password.")" != "" ] ||
       [ "$username" = "" ] ||
       [ "$password" = "" ];
    then
        print "Invalid credentials! Try again..."
        login_attempts=$(( login_attempts + 1 ))
        credential_login
    fi
}

# tries the given token, and if it fails
# retries the token login step
#
# $1 -> OTP token
try_token() {
    local otp_token="$1"

    # post token
    token_page="$($curl_bin \
                -e "$(get_login_url)" \
                -H "X-CSRFToken: $csrf_token" \
                -X POST \
                --data-urlencode "csrfmiddlewaretoken=$csrf_token" \
                --data-urlencode "rate_limited_login_view-current_step=token" \
                --data-urlencode "token-otp_token=$otp_token" \
                --data-urlencode "Login=Login" \
                $(get_login_url))"

    # test whether the login succeeded
    if [ "$(echo $token_page | grep "Invalid token")" != "" ] ||
       [ "${#otp_token}" != "6" ];
    then
        print "Invalid token! Try again..."
        login_attempts=$(( login_attempts + 1 ))
        token_login
    fi
}

##############
# User input #
##############

# retrieves the login credentials and attempts
# to post them; these can be provided or retrieved via input
#
# $1 -> the username (optional)
# $2 -> the user password (optional)
credential_login() {
    local username="$1"
    local password="$2"

    check_login_attempts
    if [ "$username" = "" ] ||
       [ "$password" = "" ];
    then
        print "Login with Thalia"
        print "username: " "read"
        read_var username

        start_block
        print "Login with Thalia"
        print "password: " "read"
        stty -echo
        read_var password
        stty echo
        print
    fi

    get_csrf
    try_credentials $username $password
}

# retrieves the otp token and attempts
# to post it
token_login() {
    local otp_token=""

    check_login_attempts
    start_block
    print "Login with Thalia"
    print "Enter OTP token: " "read"
    read_var otp_token

    get_csrf
    try_token $otp_token
}

######################
# Thalia app actions #
######################

# returns the id of the specified oauth app
#
# !! you must login first
#
# $1 -> the name of the app
get_oauth_app_id() {
    # retrieve the view page
    get_csrf
    local apps="$($curl_bin \
    -e "$(get_login_url)" \
    -H "X-CSRFToken: $csrf_token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "csrfmiddlewaretoken=$csrf_token" \
    -L $(get_select_url))"

    # grab the id from the page
    local app_id="$(echo "$apps" | grep -oP 'value="\K[0-9]+(?="[^>]*aria-label="Select this object for an action - '${app_name}'")')"

    echo "$app_id"
}

# adds an oauth application to the (staging)
# thalia website
#
# !! you must login first
#
# $1 -> the app name
# $2 -> the client id
# $3 -> the client secret
add_thalia_oauth_app() {
    start_block

    local app_name="$1"
    local oauth_client_id="$2"
    local oauth_client_secret="$3"
    local redirect_uri="$PROTOCOL_CHOICE://$DOMAIN_NAME/login/thalia/callback"

    # post the details to the app creation page
    print "Adding application with name $app_name..."
    get_csrf
    $curl_bin \
    -e "$(get_login_url)" \
    -H "X-CSRFToken: $csrf_token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "csrfmiddlewaretoken=$csrf_token" \
    --data-urlencode "client_id=$oauth_client_id" \
    --data-urlencode "client_secret=$oauth_client_secret" \
    --data-urlencode "hash_client_secret=on" \
    --data-urlencode "redirect_uris=$redirect_uri" \
    --data-urlencode "client_type=confidential" \
    --data-urlencode "authorization_grant_type=authorization-code" \
    --data-urlencode "name=$app_name" \
    --data-urlencode "_save=Save" \
    -X POST \
    $(get_add_url) >/dev/null
}

# removes an oauth app from the (staging)
# thalia website
#
# !! you must login first
#
# $1 -> the id of the app to remove
rmv_thalia_oauth_app() {
    start_block

    local app_id="$1"

    # select the app on the page, and the delete action,
    # then post
    print "Removing app with id $app_id"
    get_csrf
    $curl_bin \
    -e "$(get_login_url)" \
    -H "X-CSRFToken: $csrf_token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "csrfmiddlewaretoken=$csrf_token" \
    --data-urlencode "action=delete_selected" \
    --data-urlencode "_selected_action=$app_id" \
    --data-urlencode "post=yes" \
    -X POST \
    -L "$(get_remove_url)" >/dev/null
}
