# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny

.PHONY: bundle sync tty clean mount umount

# Path to CIRCUITPY on Debian
D_CPY=/media/CIRCUITPY

# Relative path to project bundle's install source directory
BUNDLE_SRC=build/usb-glitch-research/CircuitPython\ 9.x/

# Build project bundle zip file
bundle:
	@mkdir -p build
	python3 bundle_builder.py

# Mount CIRCUITPY from Debian command line (works over ssh)
# you might need to do `sudo apt install pmount` before using this
mount:
	@if [ ! -d ${D_CPY} ] ; then \
		pmount `readlink -f /dev/disk/by-label/CIRCUITPY` CIRCUITPY; else \
		echo "${D_CPY} was already mounted"; fi

# Unmount CIRCUITPY from Debian command line
umount:
	@if [ -d ${D_CPY} ] ; then pumount CIRCUITPY; else \
		echo "${D_CPY} wasn't mounted"; fi

# Sync current code and libraries to CIRCUITPY drive on Debian
sync: bundle
	@if [ -d ${D_CPY} ] ; then \
		rsync -rcvO ${BUNDLE_SRC} ${D_CPY}; else \
		echo "${D_CPY} does not exist"; \
		sync; fi

# Debian CircuitPython USB serial console (may need dialout group perms)
# This assumes you have only one Adafruit dev board plugged in
usbtty:
	screen -fn /dev/serial/by-id/usb-Adafruit_* 115200

# Debian Tigard UART (may need udev rule and/or plugdev group perms)
tigard:
	screen -fn /dev/serial/by-id/usb-*Tigard_V1.1*-if00-port0 115200

clean:
	rm -rf build
