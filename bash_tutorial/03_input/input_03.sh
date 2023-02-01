#!/bin/bash
# get 3rd column of a file from stdin
echo "column 3"
cat /dev/stdin | cut -f3 -d' '