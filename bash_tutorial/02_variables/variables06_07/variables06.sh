#!/bin/bash
# see: https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html
# copy file and insert date between base name & extension
filename=$1
cp "${filename}" "$(basename "${filename%.*}")"_"$(date +"%Y-%m-%d")"."${filename##*.}"