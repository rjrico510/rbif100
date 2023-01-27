#!/bin/bash
# print filename, owner & size from ls -l
ls -l $1 | awk '{print $9 " " $5 " " $3}'