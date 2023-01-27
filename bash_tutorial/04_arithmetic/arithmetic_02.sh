#!/bin/bash
TODAY=$(date +%F)
echo "${TODAY}"
TOMORROW=$(date +%F -d "${TODAY} +$1 day")
echo "${TOMORROW}"