#!/bin/bash

#########################
# Command documentation #
#########################

display_basic_help() {
    start_block

    print "List of options:"
    print ""
    print "  -> '' (no-option):       run existing deployment;"
    print "  -> -h | --help:          display script options;"
    print "  -> -r | --reset_setup:   reset environment and run (more options);"
    print "  -> -c | --clean_setup:   clean environment (more options);"
    print "  -> -q | --quit:          exit current deployment;"
    print "  -> -b | --rebuild:       rebuild the containers and run;"
    exit
}
