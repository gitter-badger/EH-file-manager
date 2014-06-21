#!/bin/bash
if [ "$1" = "-t" ]; then
    python src/man2.py -d -g ./testdir/gallery --nogui
else
	gnome-terminal -e 'bash -c "./run_nogui.sh -t ; bash"'
fi
