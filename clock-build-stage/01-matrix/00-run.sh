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
#  The PATH within this environment seems incorrect
on_chroot << EOF
    echo "Adding rpi-rgb-led-matrix python library..."
    cd "/home/${FIRST_USER_NAME}"

    [ -d rpi-rgb-led-matrix ] || git clone https://github.com/hzeller/rpi-rgb-led-matrix
    chown -R 1000:1000 rpi-rgb-led-matrix
    cd rpi-rgb-led-matrix
    git checkout e3dd56dcc0408862f39cccc47c1d9dea1b0fb2d2

    make build-python HARDWARE_DESC=adafruit-hat USER_DEFINES="-DDISABLE_HARDWARE_PULSES" PYTHON=/usr/bin/python3
    make install-python HARDWARE_DESC=adafruit-hat USER_DEFINES="-DDISABLE_HARDWARE_PULSES" PYTHON=/usr/bin/python3


    echo "Configuring realtime clock..."
    /usr/bin/raspi-config nonint do_i2c 0

    echo "# Enable HAT RTC" >> /boot/config.txt
    echo "dtoverlay=i2c-rtc,ds1307" >> /boot/config.txt

    update-rc.d -f fake-hwclock remove || true
    apt-get -y remove fake-hwclock
    sed -i '/if \[ -e \/run\/systemd\/system \] ; then/,+2 s/^#*/#/' /lib/udev/hwclock-set
EOF
