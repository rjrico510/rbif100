#!/bin/bash
echo "$@"
printf "%s\0" "$@" | xargs -0 -t -n 1 -I {} ./variables06.sh {}