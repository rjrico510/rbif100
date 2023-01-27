#!/bin/bash
# print the larger of 2 inputs
if [ "$1" -gt "$2" ]; then
  echo "$1"
else
  echo "$2"
fi