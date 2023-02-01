#!/bin/bash
# tic tac toe
# very clunky version

function draw_board() {
    echo
    echo "${board["11"]}|${board["12"]}|${board["13"]}"
    echo "------"
    echo "${board["21"]}|${board["22"]}|${board["23"]}"
    echo "------"
    echo "${board["31"]}|${board["32"]}|${board["33"]}"
    echo
}

function winner() {
    WIN_RESULT=0
    if [ "${board["11"]}" = "$SYMBOL" ] && [ "${board["12"]}" = "$SYMBOL" ] && [ "${board["13"]}" = "$SYMBOL" ]; then
        WIN_RESULT=1
    elif [ "${board["21"]}" = "$SYMBOL" ] && [ "${board["22"]}" = "$SYMBOL" ] && [ "${board["23"]}" = "$SYMBOL" ]; then
        WIN_RESULT=1
    elif [ "${board["31"]}" = "$SYMBOL" ] && [ "${board["32"]}" = "$SYMBOL" ] && [ "${board["33"]}" = "$SYMBOL" ]; then
        WIN_RESULT=1
    elif [ "${board["11"]}" = "$SYMBOL" ] && [ "${board["21"]}" = "$SYMBOL" ] && [ "${board["31"]}" = "$SYMBOL" ]; then
        WIN_RESULT=1
    elif [ "${board["12"]}" = "$SYMBOL" ] && [ "${board["22"]}" = "$SYMBOL" ] && [ "${board["32"]}" = "$SYMBOL" ]; then
        WIN_RESULT=1
    elif [ "${board["13"]}" = "$SYMBOL" ] && [ "${board["23"]}" = "$SYMBOL" ] && [ "${board["33"]}" = "$SYMBOL" ]; then
        WIN_RESULT=1
    elif [ "${board["11"]}" = "$SYMBOL" ] && [ "${board["22"]}" = "$SYMBOL" ] && [ "${board["33"]}" = "$SYMBOL" ]; then
        WIN_RESULT=1
    elif [ "${board["13"]}" = "$SYMBOL" ] && [ "${board["22"]}" = "$SYMBOL" ] && [ "${board["31"]}" = "$SYMBOL" ]; then
        WIN_RESULT=1
    fi
    return $WIN_RESULT
}

# initialize the board
declare -A board
board["11"]=" "
board["12"]=" "
board["13"]=" "
board["21"]=" "
board["22"]=" "
board["23"]=" "
board["31"]=" "
board["32"]=" "
board["33"]=" "

WIN=0
for I in {1..9}; do
    draw_board
    PROCEED=0
    until ((PROCEED == 1)); do
        if ((I % 2 == 1)); then # player turn
            SYMBOL="X"

        else
            SYMBOL="O"
        fi
        echo "$SYMBOL turn - enter a position (2 chars, rowcol)"
        read -r INPUT
        if [ "${board[$INPUT]}" = " " ]; then
            board[$INPUT]=$SYMBOL
            PROCEED=1
        fi
    done

    winner
    WIN=$?
    echo "Winner? $WIN"
    if ((WIN == 1)); then
        echo "$SYMBOL wins!"
        break
    fi

done

draw_board
if ((WIN == 0)); then
    echo "draw"
fi