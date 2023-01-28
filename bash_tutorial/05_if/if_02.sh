#!/bin/bash
# check if a file is executable or writeable
if [ -w "$1" ]; then
  echo "$1 is writeable"
fi

if [ -x "$1" ]; then
  echo "$1 is executable"
fi