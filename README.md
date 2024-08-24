<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: Copyright 2024 Sam Blenny -->
# USB Glitch Research

Notes on tracking down CircuitPython USB stack glitches


## Hardware


### Parts

- Adafruit ESP32-S3 TFT Feather - 4MB Flash, 2MB PSRAM
  ([product page](https://www.adafruit.com/product/5483),
  [learn guide](https://learn.adafruit.com/adafruit-esp32-s3-tft-feather))

- Adafruit USB Host FeatherWing with MAX3421E
  ([product page](https://www.adafruit.com/product/5858),
  [learn guide](https://learn.adafruit.com/adafruit-usb-host-featherwing-with-max3421e))

- Adafruit FeatherWing Tripler
  ([product page](https://www.adafruit.com/product/3417))

- 8BitDo SN30 Pro USB gamepad
  ([product page](https://www.8bitdo.com/sn30-pro-usb-gamepad/))

- 8BitDo USB Wireless Adapter 2
  ([product page](https://www.8bitdo.com/usb-wireless-adapter-2/))

- 8BitDo 8BitDo Ultimate Controller with Charging Dock
  ([product page](https://www.8bitdo.com/ultimate-bluetooth-controller/))

- Tigard FT2232H USB UART adapter
  ([1bitsquared](https://1bitsquared.com/products/tigar),
  [crowdsupply](https://www.crowdsupply.com/securinghw/tigard))

- Tamiya Universal Plate Set #70157
  (3mm thick, 160x60mm ABS plates with 3mm holes on 5mm grid)

- M2.5 Nylon Standoff Set
  (misc. M2.5 machine screws, standoffs, and nuts)


### Pinouts

| TFT feather | USB Host | ST7789 TFT |
| ----------- | -------- | ---------- |
|  SCK        |  SCK     |            |
|  MOSI       |  MOSI    |            |
|  MISO       |  MISO    |            |
|  D9         |  IRQ     |            |
|  D10        |  CS      |            |
|  TFT_CS     |          |  CS        |
|  TFT_DC     |          |  DC        |


## Building CircuitPython for ESP32-S3

This is the procedure to set up CircuitPython ESP32-S3 build on Debian
Bookworm. These are distilled from the
[Building CircuitPython](https://learn.adafruit.com/building-circuitpython),
and various related documentation that the guide links to. When the notes below
refer to sections of "the learn guide", that means the Building CircuitPython
learn guide.

1. Clone adafruit/circuitpython (or your own fork of the circuitpython repo):

    ```
    $ cd ~/code
    $ git clone https://github.com/adafruit/circuitpython.git
    ```

2. Follow instructions from the learn guide's
   [Linux Setup](https://learn.adafruit.com/building-circuitpython/linux)
   page to install build dependency packages:

    ```
    $ sudo apt install build-essential git git-lfs gettext cmake python3-venv
    ```

3. Follow instructions from the learn guide's
   [Build CircuitPython](https://learn.adafruit.com/building-circuitpython/build-circuitpython)
   section to fetch submodules for the Espressif port:

    ```
    $ cd ~/code/circuitpython/ports/espressif
    $ make fetch-port-submodules
    ```

4. Follow instructions from the learn guide's
   [Espressif Builds](https://learn.adafruit.com/building-circuitpython/espressif-build)
   page to install ESP-IDF, which is needed to build for ESP32-S3 boards. Some
   of these steps come from the
   [ports/espressif/README.rst](https://github.com/adafruit/circuitpython/blob/main/ports/espressif/README.rst)
   file which the Expressif Builds learn guide page links to.

    ```
    $ cd ~/code/circuitpython/ports/espressif/
    $ ./esp-idf/install.sh
    ```

... (TODO: install esp-idf, etc)
