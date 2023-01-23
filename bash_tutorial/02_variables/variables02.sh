#!/bin/bash
# get random word
cat /usr/share/dict/words | sed -n "${RANDOM}p"