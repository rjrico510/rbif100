#!/bin/bash
# add 1 day to the date
TODAY=$(date +%F)
echo "${TODAY}"
TOMORROW=$(date +%F -d "${TODAY} +$1 day")
echo "${TOMORROW}"