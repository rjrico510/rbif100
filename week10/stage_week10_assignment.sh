#!/bin/bash -xe
# stage assignment
SRC=assignment
DEST=/home/ricor/week10
rm -rf "${DEST}"
mkdir "${DEST}"
cd ${SRC}
cp -rL . "${DEST}"
cd -