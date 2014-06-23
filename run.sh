#!/bin/bash
if [ "$1" = "-t" ]; then
    python src/man2.py -d -g testdir/gallery
else
    gnome-terminal -e 'bash -c "./run.sh -t ; bash"'
fi
