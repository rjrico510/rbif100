#!/bin/bash
# echo some params

echo "name: $0"
echo "variables: $@"
echo "number variables: $#"
echo "pid: $$"
echo "user: $USER"
echo "hostname: $HOSTNAME"
echo "random number: $RANDOM"
echo "seconds since script started: $SECONDS"
echo "line number: $LINENO"