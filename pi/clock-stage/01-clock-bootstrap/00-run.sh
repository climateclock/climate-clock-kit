#!/bin/bash -e


# Reduce DHCP timeout so system can boot faster
printf "\n# Faster booting when network isn't present\ntimeout 5\n" >>"${ROOTFS_DIR}/etc/dhcpcd.conf"


# Produce a systemd service and enable it for the multi-user target
echo "Adding climateclock systemd service..."
cat >"${ROOTFS_DIR}/lib/systemd/system/climateclock.service" <<EOF
[Unit]
Description=ClimateClock

[Service]
Type=simple
Restart=always
RestartSec=2s
ExecStart=/home/${FIRST_USER_NAME}/clock/climateclock.py
WorkingDirectory=/home/${FIRST_USER_NAME}/clock

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
git checkout dfc27c15c224a92496034a39512a274744879e86
make build-python HARDWARE_DESC=adafruit-hat-pwm PYTHON=/usr/bin/python3
make install-python HARDWARE_DESC=adafruit-hat-pwm PYTHON=/usr/bin/python3
EOF
chmod +x "${ROOTFS_DIR}/home/${FIRST_USER_NAME}/install_rgbmatrix.sh"


# Build and install the python library from within the emulated target system
# TODO: Use some kind of package
on_chroot << EOF
    echo "Adding rpi-rgb-led-matrix python library..."
    cd "/home/${FIRST_USER_NAME}"

    [ -d climate-clock-kit ] || git clone https://github.com/beautifultrouble/climate-clock-kit
    ln -sf climate-clock-kit/clock

    # Build the matrix library
    ./install_rgbmatrix.sh

    # Fix ownership of everything we've just created
    chown -R 1000:1000 *
EOF


# Replicate the steps for configuring the RTC from rgb-matrix.sh here:
# https://github.com/adafruit/Raspberry-Pi-Installer-Scripts/blob/master/rgb-matrix.sh
on_chroot << EOF
    reconfig() {
        grep $2 $1 >/dev/null
        if [ $? -eq 0 ]; then
            # Pattern found; replace in file
            sed -i "s/$2/$3/g" $1 >/dev/null
        else
            # Not found; append (silently)
            echo $3 | sudo tee -a $1 >/dev/null
        fi
    }

    echo "Configuring realtime clock..."

    # I believe the net effect of this command (on a fresh system) is to:
    #   * Add "i2c-dev" to /etc/modules
    #   * Add "dtparam=i2c_arm" to /boot/config.txt
    /usr/bin/raspi-config nonint do_i2c 0

    # Comment out line which causes hwclock-set to exit when systemd is running
    sed -i '/if \[ -e \/run\/systemd\/system \] ; then/,+2 s/^#*/#/' /lib/udev/hwclock-set

    echo "Configuring additional hardware..."

    # Do additional RTC setup for DS1307
    reconfig /boot/config.txt "^.*dtoverlay=i2c-rtc.*$" "dtoverlay=i2c-rtc,ds1307"
    # Disable sound ('easy way' -- kernel module not blacklisted)
    reconfig /boot/config.txt "^.*dtparam=audio.*$" "dtparam=audio=off"
EOF


