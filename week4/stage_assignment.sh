#!/bin/bash -xe
# stage assignment
SRC=assignment
DEST=/home/ricor/week4
rm -rf "${DEST}"
mkdir "${DEST}"
cd ${SRC}
cp -rL . "${DEST}"
cd -