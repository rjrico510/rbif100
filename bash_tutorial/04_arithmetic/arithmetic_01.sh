#!/bin/bash
# multiply 2 numbers using let, expr and double-parentheses
let "A_LET = $1 * $2"
echo "let: ${A_LET}"
A_EXPR=$( expr $1 \* $2 )
echo "expr: ${A_EXPR}"
A_PAREN=$(( $1 * $2 ))
echo "paren: ${A_PAREN}"
