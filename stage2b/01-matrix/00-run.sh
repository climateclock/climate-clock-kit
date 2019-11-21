#!/bin/bash -e

cp files/climateclock.py "${ROOTFS_DIR}/home/${FIRST_USER_NAME}/climateclock.py"

cat >"${ROOTFS_DIR}/etc/systemd/system/climateclock.service" <<EOF
[Unit]
Description=CLIMATECLOCK LED Matrix driver

[Service]
Type=simple
Restart=always
ExecStart=/home/${FIRST_USER_NAME}/climateclock.py

[Install]
WantedBy=multi-user.target
EOF

ln -sv /etc/systemd/system/climateclock.service "${ROOTFS_DIR}/etc/systemd/system/multi-user.target.wants/climateclock.service"


on_chroot << EOF
    cd "/home/${FIRST_USER_NAME}"

    [ -d rpi-rgb-led-matrix ] || git clone https://github.com/hzeller/rpi-rgb-led-matrix
    cd rpi-rgb-led-matrix
    git checkout e3dd56dcc0408862f39cccc47c1d9dea1b0fb2d2

    make build-python HARDWARE_DESC=adafruit-hat USER_DEFINES="-DDISABLE_HARDWARE_PULSES" PYTHON=/usr/bin/python3
    make install-python HARDWARE_DESC=adafruit-hat USER_DEFINES="-DDISABLE_HARDWARE_PULSES" PYTHON=/usr/bin/python3
EOF
