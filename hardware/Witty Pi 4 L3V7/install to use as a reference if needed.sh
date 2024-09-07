[ -z $BASH ] && { exec bash "$0" "$@" || exit; }
#!/bin/bash
# file: install.sh
#
# This script will install required software for Witty Pi.
# It is recommended to run it in your home directory.
#

# check if sudo is used
if [ "$(id -u)" != 0 ]; then
  echo 'Sorry, you need to run this script with sudo'
  exit 1
fi

# target directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/wittypi"

# error counter
ERR=0

# config file
if [ "$(lsb_release -si)" == "Ubuntu" ]; then
  # Ubuntu
  BOOT_CONFIG_FILE="/boot/firmware/usercfg.txt"
else
  # Raspberry Pi OS ("$(lsb_release -si)" == "Debian") and others
  if [ -e /boot/firmware/config.txt ] ; then
    BOOT_CONFIG_FILE="/boot/firmware/config.txt"
  else
    BOOT_CONFIG_FILE="/boot/config.txt"
  fi
fi

echo '================================================================================'
echo '|                                                                              |'
echo '|                   Witty Pi Software Installation Script                      |'
echo '|                                                                              |'
echo '================================================================================'

# enable I2C on Raspberry Pi
echo '>>> Enable I2C'
if grep -q 'i2c-bcm2708' /etc/modules; then
  echo 'Seems i2c-bcm2708 module already exists, skip this step.'
else
  echo 'i2c-bcm2708' >> /etc/modules
fi
if grep -q 'i2c-dev' /etc/modules; then
  echo 'Seems i2c-dev module already exists, skip this step.'
else
  echo 'i2c-dev' >> /etc/modules
fi

i2c1=$(grep 'dtparam=i2c1=on' ${BOOT_CONFIG_FILE})
i2c1=$(echo -e "$i2c1" | sed -e 's/^[[:space:]]*//')
if [[ -z "$i2c1" || "$i2c1" == "#"* ]]; then
  echo 'dtparam=i2c1=on' >> ${BOOT_CONFIG_FILE}
else
  echo 'Seems i2c1 parameter already set, skip this step.'
fi

i2c_arm=$(grep 'dtparam=i2c_arm=on' ${BOOT_CONFIG_FILE})
i2c_arm=$(echo -e "$i2c_arm" | sed -e 's/^[[:space:]]*//')
if [[ -z "$i2c_arm" || "$i2c_arm" == "#"* ]]; then
  echo 'dtparam=i2c_arm=on' >> ${BOOT_CONFIG_FILE}
else
  echo 'Seems i2c_arm parameter already set, skip this step.'
fi

miniuart=$(grep 'dtoverlay=miniuart-bt' ${BOOT_CONFIG_FILE})
miniuart=$(echo -e "$miniuart" | sed -e 's/^[[:space:]]*//')
if [[ -z "$miniuart" || "$miniuart" == "#"* ]]; then
  echo 'dtoverlay=miniuart-bt' >> ${BOOT_CONFIG_FILE}
else
  echo 'Seems setting Bluetooth to use mini-UART is done already, skip this step.'
fi

if [ -f /etc/modprobe.d/raspi-blacklist.conf ]; then
  sed -i 's/^blacklist spi-bcm2708/#blacklist spi-bcm2708/' /etc/modprobe.d/raspi-blacklist.conf
  sed -i 's/^blacklist i2c-bcm2708/#blacklist i2c-bcm2708/' /etc/modprobe.d/raspi-blacklist.conf
else
  echo 'File raspi-blacklist.conf does not exist, skip this step.'
fi

# install i2c-tools
echo '>>> Install i2c-tools'
if hash i2cget 2>/dev/null; then
  echo 'Seems i2c-tools is installed already, skip this step.'
else
  apt install -y i2c-tools || ((ERR++))
fi

# make sure en_GB.UTF-8 locale is installed
echo '>>> Make sure en_GB.UTF-8 locale is installed'
locale_commentout=$(sed -n 's/\(#\).*en_GB.UTF-8 UTF-8/1/p' /etc/locale.gen)
if [[ $locale_commentout -ne 1 ]]; then
  echo 'Seems en_GB.UTF-8 locale has been installed, skip this step.'
else
  sed -i.bak 's/^.*\(en_GB.UTF-8[[:blank:]]\+UTF-8\)/\1/' /etc/locale.gen
  locale-gen
fi

# install wiringPi
if hash gpio 2>/dev/null; then
  echo 'Seems wiringPi has been installed, skip this step.'
else
  os=$(lsb_release -r | grep 'Release:' | sed 's/Release:\s*//')
  if [ $os -le 10 ]; then
    apt install -y wiringpi || ((ERR++))
  elif [ $os -eq 11 ]; then
    wget https://github.com/WiringPi/WiringPi/releases/download/3.2/wiringpi_3.2-bullseye_armhf.deb -O wiringpi.deb || ((ERR++))
    apt install -y ./wiringpi.deb || ((ERR++))
    rm wiringpi.deb
  else
    arch=$(dpkg --print-architecture)
    if [ "$arch" == "arm64" ]; then
      wget https://github.com/WiringPi/WiringPi/releases/download/3.2/wiringpi_3.2_arm64.deb -O wiringpi.deb || ((ERR++))
    else
      wget https://github.com/WiringPi/WiringPi/releases/download/3.2/wiringpi_3.2_armhf.deb -O wiringpi.deb || ((ERR++))
    fi
    apt install -y ./wiringpi.deb || ((ERR++))
    rm wiringpi.deb
  fi
fi

# install wittyPi
if [ $ERR -eq 0 ]; then
  echo '>>> Install wittypi'
  if [ -d "wittypi" ]; then
    echo 'Seems wittypi is installed already, skip this step.'
  else
    wget https://www.uugear.com/repo/WittyPi4/LATEST -O wittyPi.zip || ((ERR++))
    unzip wittyPi.zip -d wittypi || ((ERR++))
    cd wittypi
    chmod +x wittyPi.sh
    chmod +x daemon.sh
    chmod +x runScript.sh
    chmod +x beforeScript.sh
    chmod +x afterStartup.sh
    chmod +x beforeShutdown.sh
    sed -e "s#/home/pi/wittypi#$DIR#g" init.sh >/etc/init.d/wittypi
    chmod +x /etc/init.d/wittypi
    update-rc.d wittypi defaults || ((ERR++))
    touch wittyPi.log
    touch schedule.log
    cd ..
    chown -R $SUDO_USER:$(id -g -n $SUDO_USER) wittypi || ((ERR++))
    sleep 2
    rm wittyPi.zip
  fi
fi

# install UUGear Web Interface
curl https://www.uugear.com/repo/UWI/installUWI.sh | bash

echo
if [ $ERR -eq 0 ]; then
  echo '>>> All done. Please reboot your Pi :-)'
else
  echo '>>> Something went wrong. Please check the messages above :-('
fi
