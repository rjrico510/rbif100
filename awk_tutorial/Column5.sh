#!/bin/sh -x
awk '{print $'"${1:-1}"'}'
