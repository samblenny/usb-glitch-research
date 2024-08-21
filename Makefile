# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny

.PHONY: bundle sync tty clean

bundle:
	@mkdir -p build
	python3 bundle_builder.py

# Sync current code and libraries to CIRCUITPY drive on Debian
sync: bundle
	rsync -rcvO 'build/usb-glitch-research/CircuitPython 9.x/' /media/${USER}/CIRCUITPY
	sync

# Debian CircuitPython USB serial console (may need dialout group perms)
usbtty:
	screen -fn /dev/serial/by-id/usb-Adafruit_Feather_ESP32-S3_TFT* 115200

# Debian Tigard UART (may need udev rule and/or plugdev group perms)
tigard:
	screen -fn /dev/serial/by-id/usb-*Tigard_V1.1*-if00-port0 115200

clean:
	rm -rf build
