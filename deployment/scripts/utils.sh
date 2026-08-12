#####################
# File manipulation #
#####################

# creates a directory only if it does not
# already exist
#
# $1 -> the name of the directory
new_dir() {
    if [ ! -d "$1" ]; then
        mkdir "$1"
    fi
}

# creates a file only if it does not
# already exist
#
# $1 -> the name of the file
new_file() {
    if [ ! -f "$1" ]; then
        touch "$1"
    fi
}

# remove a file only if it exists
#
# $1 -> the file
rmv() {
    if [ -e "$1" ]; then
        rm -rf "$1"
    fi
}

# copies a file to the specified location
# only if not already present
#
# $1 -> the name of file
# $2 -> the name of the destination
cpy() {
    local file_name="$(echo "$1" | sed "s|.*/||g")"
    if [ ! -e "file_name" ]; then
        cp -r "$1" "$2"
    fi
}


#############
# I/O usage #
#############

# makes it so that the user needs to enter something
# for the script to continue
user_info_wait() {
    print "Press any key to continue..." "read"
    read_var none
}

# prints the given string to the terminal. Only
# acts as a wrapper if more complex printing is needed in the future.
#
# $1 -> the content to print
# $2 -> the type of the content (error, read, default)
#           - error:   an error message
#           - read:    a message that requires user input
#           - default: a normal message
print() {
    local content=$1
    local type=$2

    case $type in
        "error")
            echo "$content" >&2
            ;;

        "read")
            echo -n "$content"
            ;;
        *)
            echo "$content"
            ;;
    esac
}

# reads a line of input from the terminal, and stores
# it in the variable with the given name. Acts as a wrapper
# for fancier display techniques and exiting
#
# $1 -> the name of the variable to store the input in
read_var() {
    local var_name="$1"
    local var_value=""

    # read with built in error handling
    read -r var_value || panic_clean

    # trick to store the variable value into the
    # given name - it won't technically crash if you
    # pass an incorrect variable name
    printf -v "$var_name" "%s" "$var_value"

    clear
}

################
# Compartments #
################

start_block() {
    clear

    print "=== $SCRIPT_NAME v$VERSION ==="
    print
    print
}

start_aws_block() {
    start_block

    print "AWS S3 storage options"
    print
}
