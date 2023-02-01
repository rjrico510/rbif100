#!/bin/bash
# print message for each day of the week
DAY=$(echo "$1" | tr '[:upper:]' '[:lower:]')
echo "$DAY"

case $DAY in
    "sunday")
        echo "End of weekend"
        ;;
    "monday")
        echo "Ugh"
        ;;
    "tuesday")
        echo "2/5 of the way there"
        ;;
    "wednesday")
        echo "Hump day"
        ;;
    "thursday")
        echo "Thunder day"
        ;;
    "friday")
        echo "TGIF"
        ;;
    "saturday")
        echo "Happy weekend"
        ;;
    *)
        echo "Not a day!"
        ;;
esac