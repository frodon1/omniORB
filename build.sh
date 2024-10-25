#!/bin/bash
set -euo pipefail
set -x

git reset --hard HEAD
git clean -df

export INSTALL_OMNIORB=$(pwd)/install
[ -d $INSTALL_OMNIORB ] && rm -rf $INSTALL_OMNIORB || true
[ -d build ] && rm -rf build || true
[ -d build_py ] && rm -rf build_py || true
mkdir -p build build_py

(cd build && ../omniORB/configure && make -j16 && DESTDIR=$INSTALL_OMNIORB make install)
(cd build_py && CPPFLAGS=-I${INSTALL_OMNIORB}/usr/local/include/omniORB4/internal ../omniORBpy/configure --with-omniorb=${INSTALL_OMNIORB}/usr/local && make -j16 && DESTDIR=${INSTALL_OMNIORB} make install)
