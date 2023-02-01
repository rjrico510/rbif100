#!/bin/sh
# this example is WRONG - s never occurs since d occurs 1st & deletes pattern space
sed -e '1 {
	d
	s/.*//
}'