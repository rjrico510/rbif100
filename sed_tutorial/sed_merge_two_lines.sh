#!/bin/sh
sed '=' $1 | \
sed '{
	N
	s/\n/ /
}'