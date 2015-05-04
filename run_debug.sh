#!/bin/bash
if [ "$1" = "-t" ]; then
    python -m ehfilemanager -d
else
    x-terminal-emulator -e "$0 -t"
fi
