#!/bin/bash

hash docker 2>/dev/null || not_found=true 
if [[ $not_found ]]; then
    echo "Docker is not installed! Install docker first."
    exit 1
fi

if [ $# -eq 0 ]; then
    echo "Usage: $0 <path to dataset> [options]"
    exit 0
fi

if [[ $* == *--help* ]] || [[ $* == *-h* ]]; then
    docker run -ti --rm --entrypoint /app/run.py uav4geo/nodecm --help
fi

if [ -e $2 ]; then
    docker run -ti --rm --entrypoint /app/run.py -v $(realpath "$2"):/datasets uav4geo/nodecm "${@:2}"
else
    echo "$2 is not a directory"
fi

