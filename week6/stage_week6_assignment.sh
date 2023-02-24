#!/bin/bash -xe
# stage assignment
SRC=assignment
DEST=/home/ricor/week6
rm -rf "${DEST}"
mkdir "${DEST}"
cd ${SRC}
cp -rL . "${DEST}"
gunzip "${DEST}"/*.gz
cd -