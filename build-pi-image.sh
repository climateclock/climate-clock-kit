#!/bin/bash

# Ensure we're running in the directory of the top-level repo
cd "$(dirname "${BASH_SOURCE[0]}")"


# Start with a pristine pi-gen repo
SUBMOD=pi-gen
git submodule init
git submodule update
cd $SUBMOD
[ "$(basename $PWD)" = "$SUBMOD" ] || exit 1
git clean -fdx

# Add config, build stage, and remove stage2 (raspbian-lite) image generation
cp -a ../{config,clock-build-stage} .
rm stage2/EXPORT_{IMAGE,NOOBS}


# Remove build-breaking fake-hwclock from stage2 and image generation
sed -i 's/fake-hwclock\s//' stage2/01-sys-tweaks/00-packages
sed -i '/-x.*fake-hwclock/,+2d' export-image/04-finalise/01-run.sh

# Workaround for 64-bit hosts https://github.com/RPi-Distro/pi-gen/issues/271
sed -i 's|FROM debian|FROM i386/debian|' Dockerfile


# Build or resume partial build
read -p "Keep docker container after build (requires manual clean-up)? [y/N]: " KEEP
[ "$KEEP" = "y" ] && CLEAN=1 || CLEAN=0
CONTINUE=1 PRESERVE_CONTAINER=$CLEAN ./build-docker.sh
echo "If your image was built successfully, it will be in the deploy folder."

