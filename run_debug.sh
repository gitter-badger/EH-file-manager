#!/bin/bash
if [ "$1" = "-t" ]; then
    python src/main.py -d
else
    gnome-terminal -e 'bash -c "./run_debug.sh -t ; bash"'
fi
