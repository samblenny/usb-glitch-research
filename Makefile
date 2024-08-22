# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny

.PHONY: bundle sync tty clean mount umount

# Path to CIRCUITPY on Debian
D_CPY=/media/CIRCUITPY

# Relative path to project bundle's install source directory
BUNDLE_SRC=build/usb-glitch-research/CircuitPython\ 9.x/

# Build project bundle zip file.
# The bundle builder script downloads a copy of the full CircuitPython library
# bundle using curl and the URL configured in ./bundle_manifest.cfg. On Debian,
# you might need to do `sudo apt install curl` before using this.
bundle:
	@mkdir -p build
	python3 bundle_builder.py

# Mount CIRCUITPY from Debian command line (works over ssh).
# You might need to do `sudo apt install pmount` before using this.
mount:
	@if [ ! -d ${D_CPY} ] ; then \
		pmount `readlink -f /dev/disk/by-label/CIRCUITPY` CIRCUITPY; else \
		echo "${D_CPY} was already mounted"; fi

# Unmount CIRCUITPY from Debian command line.
# You might need to do `sudo apt install pmount` before using this.
umount:
	@if [ -d ${D_CPY} ] ; then pumount CIRCUITPY; else \
		echo "${D_CPY} wasn't mounted"; fi

# Sync current code and libraries to CIRCUITPY drive on Debian.
# You might need to do `sudo apt install rsync` before using this.
sync: bundle
	@if [ -d ${D_CPY} ] ; then \
		rsync -rcvO ${BUNDLE_SRC} ${D_CPY}; else \
		echo "${D_CPY} does not exist"; \
		sync; fi

# Open terminal emulator for CircuitPython USB serial console on Debian.
# You might need to do `sudo apt install screen` before using this.
# You might need to add yourself to the dialout group before using this.
# The serial port device name glob below ("/dev/...*") will probably break if
# you have more than one Adafruit dev board plugged in at the same time.
tty:
	screen -fn /dev/serial/by-id/usb-Adafruit_* 115200

# Open terminal emulator for Tigard UART on Debian.
# You might need to do `sudo apt install screen` before using this.
# You might need to add Tigard udev rules to get plugdev group perms to
# access the serial port device.
tigard:
	screen -fn /dev/serial/by-id/usb-*Tigard_V1.1*-if00-port0 115200

clean:
	rm -rf build
