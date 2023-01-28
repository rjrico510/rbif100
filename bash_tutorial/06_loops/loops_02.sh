#!/bin/bash
# for each item in a directory
# if file, list size
# if dir, list # elements
if [ -d "$1" ]; then
    for f in "$1"/*; do
        echo "$f"
        if [ -d "$f" ]; then
            echo "dir: # entries: $(ls -l "$f" | wc -l)" 
        elif [ -e "$f" ]; then
            echo "file: size: $(ls -l "$f" | awk '{print $5}')" 
        fi
    done
fi