#!/bin/bash -e

# Copy the clock script to the user's home directory
echo "Adding climateclock script to ${FIRST_USER_NAME}'s home directory..."
install -v -o 1000 -g 1000 files/climateclock.py "${ROOTFS_DIR}/home/${FIRST_USER_NAME}/climateclock.py"


# Produce a systemd service and enable it for the multi-user target
echo "Adding climateclock systemd service..."
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
ln -fsv /etc/systemd/system/climateclock.service "${ROOTFS_DIR}/etc/systemd/system/multi-user.target.wants/climateclock.service"


# Build and install the python library from within the emulated target system
# NOTE: It's not clear why some binaries need full paths in this environment
on_chroot << EOF
    echo "Adding rpi-rgb-led-matrix python library..."
    cd "/home/${FIRST_USER_NAME}"

    [ -d rpi-rgb-led-matrix ] || git clone https://github.com/hzeller/rpi-rgb-led-matrix
    chown -R 1000:1000 rpi-rgb-led-matrix
    cd rpi-rgb-led-matrix
    git checkout e3dd56dcc0408862f39cccc47c1d9dea1b0fb2d2

    make build-python HARDWARE_DESC=adafruit-hat USER_DEFINES="-DDISABLE_HARDWARE_PULSES" PYTHON=/usr/bin/python3
    make install-python HARDWARE_DESC=adafruit-hat USER_DEFINES="-DDISABLE_HARDWARE_PULSES" PYTHON=/usr/bin/python3
EOF

# Replicate the steps for configuring the RTC from rgb-matrix.sh here:
# https://github.com/adafruit/Raspberry-Pi-Installer-Scripts/blob/master/rgb-matrix.sh
on_chroot << EOF
    echo "Configuring realtime clock..."

    # I believe the net effect of this command (on a fresh system) is to:
    #   * Add "i2c-dev" to /etc/modules
    #   * Add "dtparam=i2c_arm" to /boot/config.txt
    /usr/bin/raspi-config nonint do_i2c 0

    # Do additional RTC setup for DS1307
    printf "\n# For RGB Matrix HAT RTC\n" >> /boot/config.txt
    printf "dtoverlay=i2c-rtc,ds1307\n" >> /boot/config.txt

    # Comment out line which causes hwclock-set to exit when systemd is running
    sed -i '/if \[ -e \/run\/systemd\/system \] ; then/,+2 s/^#*/#/' /lib/udev/hwclock-set
EOF
