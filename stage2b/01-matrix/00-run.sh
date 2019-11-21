#!/bin/bash -e

#rm -f "${ROOTFS_DIR}/etc/systemd/system/dhcpcd.service.d/wait.conf"
on_chroot << EOF
    cd "/home/${FIRST_USER_NAME}"

    [ -d rpi-rgb-led-matrix ] || git clone https://github.com/hzeller/rpi-rgb-led-matrix
    cd rpi-rgb-led-matrix
    git checkout e3dd56dcc0408862f39cccc47c1d9dea1b0fb2d2

    make build-python HARDWARE_DESC=adafruit-hat USER_DEFINES="-DDISABLE_HARDWARE_PULSES" PYTHON=/usr/bin/python3
    make install-python HARDWARE_DESC=adafruit-hat USER_DEFINES="-DDISABLE_HARDWARE_PULSES" PYTHON=/usr/bin/python3
EOF
