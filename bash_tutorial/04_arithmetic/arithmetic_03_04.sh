#!/bin/bash
# generate a random number between LOWER and UPPER (inclusive)
LOWER=${1:-0}
UPPER=${2:-100}
# add 1 for mod; set baseline
# e.g. for 10-45, get 0-35 and add 10
UPPERMOD=$((UPPER - LOWER + 1))
RESULT=$((RANDOM % UPPERMOD + LOWER))
echo "${RESULT}"