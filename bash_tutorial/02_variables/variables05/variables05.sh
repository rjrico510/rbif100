#!/bin/bash
# copy file & prepend date
cp $1 "$(date +"%Y-%m-%d")_$1"