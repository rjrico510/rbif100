#!/bin/bash
# mastermind (minimal version)

function make_code() {
    INIT_RESULT=( "1" "2" "3" "4" "5" "6" "7" "8" )
    ANSWER=($(shuf -e "${INIT_RESULT[@]}"))
}


# make code
make_code

echo "ANSWER"
printf "%s" "${ANSWER[@]}"
echo

# iterate 5 times
WIN=0
for ITER in {1..5}; do
    # - guess sequence (8 chars)
    echo "Round $ITER: input integers 1-8 in random order separated by spaces"
    read -a GUESS

    # - return 8 chars (Y=match, N=no match)
    N_MATCHES=0
    RESULT=()
    for I in {0..7}; do
        echo "I: $I guess: ${GUESS[$I]} answer: ${ANSWER[$I]}"
        if [ "${GUESS[$I]}" = "${ANSWER[$I]}" ]; then
            RESULT+=("Y")
            ((N_MATCHES++))
        else
            RESULT+=("N")
      fi
    done
    printf "%s" "${RESULT[@]}"
    echo

    # - break on success; set success flag
    if ((N_MATCHES == 8)); then
        WIN=1
        break
    fi
done
# print win/lose at end
if ((WIN == 1)); then
    echo "you win!"
else
    echo "you lose!"
fi