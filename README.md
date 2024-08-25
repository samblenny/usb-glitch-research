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


### Install Espressif Port Build Dependencies

This is the procedure to set up CircuitPython ESP32-S3 build on Debian
Bookworm. These are distilled from the
[Building CircuitPython Learn Guide](https://learn.adafruit.com/building-circuitpython),
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
   page to install ESP-IDF and python packages.

    ```
    $ cd ~/code/circuitpython/ports/espressif/
    $ sudo apt install ninja-build python-is-python3 python3-pip
    $ ./esp-idf/install.sh
    ```

   Note that the export.sh script creates and activates a Python virtual
   environment (venv), but it does not change the shell prompt to indicate that
   a venv is active.

5. Install Python packages into the ESP-IDF virtual environment (venv):

    ```
    $ cd ~/code/circuitpython/ports/espressif
    $ source esp-idf/export.sh
    $ pip3 install --upgrade -r ../../requirements-dev.txt
    $ pip3 install --upgrade -r ../../requirements-doc.txt
    $ exit
    ```

6. Re-run esp-idf/install.sh to downgrade setuptools version from 73.0.1 to
   71.0.0 (there is an esp-idf requirements file in `~/.espressif/` that
   wants v71):

    ```
    $ cd ~/code/circuitpython/ports/espressif
    $ ./esp-idf/install.sh
    ```

    If I don't run the install script again after running pip, then attempting
    to run `make` will gives this error about the setuptools version:

    ```
    $ make BOARD=adafruit_feather_esp32s3_tft
    ...
    The following Python requirements are not satisfied:
    Requirement 'setuptools<71.0.1,>=21' was not met. Installed version: 73.0.1
    To install the missing packages, please run "install.sh"
    Diagnostic information:
        IDF_PYTHON_ENV_PATH: $HOME/.espressif/python_env/idf5.3_py3.11_env
        Python interpreter used: $HOME/.espressif/python_env/idf5.3_py3.11_env/bin/python
    Constraint file: $HOME/.espressif/espidf.constraints.v5.3.txt
    Requirement files:
     - $HOME/code/circuitpython/ports/espressif/esp-idf/tools/requirements/requirements.core.txt
    ...
    ```


### Build and Flash Feather TFT ESP32-S3 Firmware

The Makefile build procedure for Espressif boards requires the ESP-IDF tools,
and the ESP-IDF tools require that you source the
ports/espressif/esp-idf/export.sh script before running make.


1. Activate the ESP-IDF virtual environment (venv):

    ```
    $ cd ~/code/circuitpython/ports/espressif
    $ source esp-idf/export.sh
    ```

2. Build a normal Feather TFT ESP32-S3 firmware image with make:

    ```
    $ make BOARD=adafruit_feather_esp32s3_tft
    ```

3. Flash `ports/espressif/build-adafruit_feather_esp32s3_tft/firmware.bin` to
   your Feather TFT ESP32-S3 dev board using the
   [Adafruit ESPTool](https://adafruit.github.io/Adafruit_WebSerial_ESPTool/)
   in a Chromium-based browser. To put the board in the right bootloader mode
   for use with ESPTool, hold down the board's BOOT button while pressing its
   RESET button.
