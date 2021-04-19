#!/bin/bash -e

#mkdir -p "${ROOTFS_DIR}/etc/systemd/system/basic.target.wants"
#ln -fsv /lib/systemd/system/climateclock.service "${ROOTFS_DIR}/etc/systemd/system/basic.target.wants/climateclock.service"


# Load up on goods
cp -a files/clock "${ROOTFS_DIR}/home/${FIRST_USER_NAME}"


APP_DIR=/home/${FIRST_USER_NAME}/clock
PY_VER=3.9.4
on_chroot << EOF
    cd ${APP_DIR}

    [ -d rpi-rgb-led-matrix ] || git clone https://github.com/hzeller/rpi-rgb-led-matrix

    echo "Installing python requirements"
    python3 -mvenv venv
    ln -sf venv/bin/activate
    . ./activate
    pip install -r requirements.txt
    
    echo "Installing LED matrix library"
    cd rpi-rgb-led-matrix
    make install-python HARDWARE_DESC=adafruit-hat-pwm PYTHON=${APP_DIR}/venv/bin/python
    cd -
        
    echo "Resetting permissions"
    chown -Rv 1000:1000 .
EOF


# Create the service
cat >"${ROOTFS_DIR}/lib/systemd/system/climateclock.service" <<EOF
[Unit]
Description=ClimateClock

[Service]
Type=simple
Restart=always
RestartSec=1s
ExecStart=/home/${FIRST_USER_NAME}/clock/climateclock.py
WorkingDirectory=/home/${FIRST_USER_NAME}/clock

[Install]
WantedBy=basic.target
EOF

# Setup within the environment
on_chroot << EOF
    # Give user sudo access once they've logged in
    if [ -e /etc/sudoers.d/010_pi-nopasswd ]; then 
        sed -i 's|^pi|'${FIRST_USER_NAME}'|' /etc/sudoers.d/010_pi-nopasswd
        mv /etc/sudoers.d/010_{pi,${FIRST_USER_NAME}}-nopasswd
    fi

    # Reduce DHCP timeout so system boots faster
    echo "timeout 5" >> /etc/dhcpcd.conf
    
    # Services
    systemctl enable climateclock
    systemctl disable man-db.timer
    systemctl disable avahi-daemon.service
    systemctl disable triggerhappy.service
    systemctl disable hciuart.service
EOF


# Hardware configuration
# Replicate the steps for configuring the RTC from rgb-matrix.sh here:
# https://github.com/adafruit/Raspberry-Pi-Installer-Scripts/blob/master/rgb-matrix.sh
on_chroot << 'EOF'
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

    echo "Configuring Hardware..."

    # I believe the net effect of this command (on a fresh system) is to:
    #   * Add "i2c-dev" to /etc/modules
    #   * Add "dtparam=i2c_arm" to /boot/config.txt
    # /usr/bin/raspi-config nonint do_i2c 0
    reconfig /etc/modules "^i2c-dev$" "i2c-dev" || true
    reconfig /boot/config.txt "^dtparam=i2c_arm$" "dtparam=i2c_arm" || true

    # Fix hwclock-set
    sed -i '/systemd/,+2 s|^|#|' /lib/udev/hwclock-set
    sed -i '/systz/ s|^|#|' /lib/udev/hwclock-set

    # Do additional RTC setup for DS1307
    reconfig /boot/config.txt "^.*dtoverlay=i2c-rtc.*$" "dtoverlay=i2c-rtc,ds1307" || true

    # Disable sound ('easy way' -- kernel module not blacklisted)
    reconfig /boot/config.txt "^.*dtparam=audio.*$" "dtparam=audio=off" || true

    echo "Done"
EOF

