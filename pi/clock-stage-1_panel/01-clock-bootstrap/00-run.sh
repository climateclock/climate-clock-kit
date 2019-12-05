#!/bin/bash -e


# Reduce DHCP timeout so system can boot faster
printf "\n# Faster booting when network isn't present\ntimeout 5\n" >>"${ROOTFS_DIR}/etc/dhcpcd.conf"


# Produce a systemd service and enable it for the multi-user target
echo "Adding climateclock systemd service..."
cat >"${ROOTFS_DIR}/lib/systemd/system/climateclock.service" <<EOF
[Unit]
Description=CLIMATECLOCK automatic startup service

[Service]
Type=simple
Restart=always
ExecStart=/home/${FIRST_USER_NAME}/climateclock.py

[Install]
WantedBy=multi-user.target
EOF
ln -fsv /lib/systemd/system/climateclock.service "${ROOTFS_DIR}/etc/systemd/system/multi-user.target.wants/climateclock.service"


# Produce a build script for rpi-rgb-led-matrix
echo "Adding rpi-rgb-led-matrix build script..."
cat > "${ROOTFS_DIR}/home/${FIRST_USER_NAME}/install_rgbmatrix.sh" <<EOF
#!/bin/bash

cd "/home/${FIRST_USER_NAME}"
[ -d rpi-rgb-led-matrix ] || git clone https://github.com/hzeller/rpi-rgb-led-matrix
cd rpi-rgb-led-matrix
git checkout e3dd56dcc0408862f39cccc47c1d9dea1b0fb2d2
make build-python HARDWARE_DESC=adafruit-hat USER_DEFINES="-DDISABLE_HARDWARE_PULSES" PYTHON=/usr/bin/python3
make install-python HARDWARE_DESC=adafruit-hat USER_DEFINES="-DDISABLE_HARDWARE_PULSES" PYTHON=/usr/bin/python3
EOF
chmod +x "${ROOTFS_DIR}/home/${FIRST_USER_NAME}/install_rgbmatrix.sh"


# Build and install the python library from within the emulated target system
# TODO: Make this whole process repeatable for those who update their system python version
on_chroot << EOF
    echo "Adding rpi-rgb-led-matrix python library..."
    cd "/home/${FIRST_USER_NAME}"

    # Pull the climate-clock-kit repo and modify the shebang for a virtualenv
    [ -d climate-clock-kit ] || git clone https://github.com/beautifultrouble/climate-clock-kit
    ln -sf climate-clock-kit/clock/climateclock.py

    # Build the matrix library
    ./install_rgbmatrix.sh

    # Fix ownership of everything we've just created
    chown -R 1000:1000 *
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


