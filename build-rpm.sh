#!/bin/bash

set -u
set -e

MOCK="/usr/bin/mock -r epel-6-x86_64"
SRC_DIR=build/SOURCES
RPM_DIR=build/RPMS

mkdir -p ${SRC_DIR}
cp cloud-init* sources ${SRC_DIR}
wget https://github.com/platform9/cloud-init/releases/download/rel-pf9-0.7.4/pf9-cloud-init-0.7.4.tar.gz -O build/SOURCES/pf9-cloud-init-0.7.4.tar.gz

mkdir -p ${RPM_DIR}
${MOCK} --buildsrpm --sources ${SRC_DIR} --spec cloud-init.spec --resultdir ${RPM_DIR}
${MOCK} --rebuild --resultdir ${RPM_DIR} ${RPM_DIR}/*.src.rpm


