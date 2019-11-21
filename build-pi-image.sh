#!/bin/bash

# Ensure we're running in the directory of the top-level repo
cd "$(dirname "${BASH_SOURCE[0]}")"
pushd .


# Start with a pristine pi-gen repo
SUBMOD=pi-gen
git submodule init
git submodule update
cd $SUBMOD
[ "$(basename $PWD)" = "$SUBMOD" ] || exit 1
git clean -fdx


# Mediate bug on 64-bit hosts https://github.com/RPi-Distro/pi-gen/issues/271
sed -i 's|FROM debian|FROM i386/debian|' Dockerfile


# Add config and select our custom build stage
touch stage{3,4,5}/SKIP
touch stage{4,5}/SKIP_IMAGES
rm stage2/EXPORT_IMAGE
cp -a ../config ../stage2b .


# Build with the allowance to build it again
read -p "Keep docker container after build (requires manual clean-up)? [y/N]: " KEEP
[ "$KEEP" = "y" ] && CLEAN=1 || CLEAN=0
CONTINUE=1 PRESERVE_CONTAINER=$CLEAN ./build-docker.sh


echo "If your image was build successfully, it will be in the deploy folder."
