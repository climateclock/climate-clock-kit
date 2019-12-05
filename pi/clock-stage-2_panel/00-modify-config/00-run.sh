#!/bin/bash -e

on_chroot << EOF
    echo "Adapting config for 2 panels..."
    sed -i '/chain_length/ s/[0-9]\+/2/' /home/${FIRST_USER_NAME}/climate-clock-kit/clock/config.py
EOF
