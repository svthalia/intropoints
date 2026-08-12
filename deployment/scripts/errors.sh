#!/bin/bash

##################
# General errors #
##################

unimplemented_err() {
    print "Unimplemented" "error"
    exit 1
}

arg_err() {
    print "Invalid argument! Exiting..." "error"
    exit 1
}

invalid_dir_err() {
    print "The working directory does not contain the repository!" "error"
    print "|" "error"
    print "|" "error"
    print "Try to follow the structure:" "error"
    print "  -> WORK_DIR/REPOSITORY" "error"
    exit 1
}

config_err() {
    print "No config to deploy!" "error"
    print "|" "error"
    print "|" "error"
    print "Maybe used improperly? Use -h to see options." "error"
    exit 1
}

################
# Extra errors #
################

panic_err() {
    print "How did we get here?" "error"
    exit 1
}
