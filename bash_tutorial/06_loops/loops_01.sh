#!/bin/bash
# while and for loop for checking even/odd
COUNTER=1
while [ $COUNTER -le 10 ]; do
    if ((COUNTER % 2 == 0)); then
        echo "$COUNTER: even"
    else
        echo "$COUNTER: odd"
    fi
    ((COUNTER++))
done

for COUNTER in {1..10}; do
    if ((COUNTER % 2 == 0)); then
        echo "$COUNTER: even"
    else
        echo "$COUNTER: odd"
    fi
    ((COUNTER++))
done