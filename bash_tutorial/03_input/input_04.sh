#!/bin/bash
ls -l $1 | awk '{print $9 " " $5 " " $3}'