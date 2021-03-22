#!/bin/bash

# Ensure we're running commands from the directory containing this script
cd "$(dirname "${BASH_SOURCE[0]}")"


# Get a password
if ! grep -q "^\s*FIRST_USER_PASS=.\+" config; then
    echo -en "Enter a linux password for the system build built."\
             "\nDO NOT use any characters with special significance in bash syntax: "
    read PASSWORD
    echo "FIRST_USER_PASS='${PASSWORD}'" >>config
fi


# Start with a pristine pi-gen repo
git submodule init
git submodule update
cd pi-gen
[ "$(basename $PWD)" = "pi-gen" ] || exit 1
echo "Cleaning pi-gen repo..."
git clean -fdx


# Add config, build stage, and remove stage2 (raspbian-lite) image generation
cp -a ../{config,clock-stage} .
rm stage2/EXPORT_{IMAGE,NOOBS} 2>/dev/null


# Remove build-breaking fake-hwclock from stage2 and image generation
sed -i 's/fake-hwclock\s//' stage2/01-sys-tweaks/00-packages
sed -i '/-x.*fake-hwclock/,+2d' export-image/04-finalise/01-run.sh


# Workaround for 64-bit hosts https://github.com/RPi-Distro/pi-gen/issues/271
sed -i 's|FROM debian|FROM i386/debian|' Dockerfile


# Build or resume partial build
read -p "Keep docker container after build (requires manual clean-up)? [y/N]: " KEEP
[ "$KEEP" = "y" ] && CLEAN=1 || CLEAN=0
CONTINUE=1 PRESERVE_CONTAINER=$CLEAN ./build-docker.sh
echo "If your image was built successfully, it will be in ${PWD}/deploy."

