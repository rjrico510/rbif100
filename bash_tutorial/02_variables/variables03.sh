#!/bin/bash
# get random word of N chars
echo $1
cat /usr/share/dict/words | grep -o -E ".{$1}" | sed -n "${RANDOM}p"