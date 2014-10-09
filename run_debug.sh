#!/bin/bash
if [ "$1" = "-t" ]; then
    python src/main.py -d
else
    x-terminal-emulator -e "$0 -t"
fi
