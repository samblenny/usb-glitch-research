# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
#
# Gamepad driver for XInput compatible USB wired gamepad with MAX421E.
#
# The button names used here match the Nintendo SNES style button
# cluster layout, but the USB IDs and protocol match the Xbox 360 USB
# wired controller. This is meant to work with widely available USB
# wired xinput compatible gamepads for the retrogaming market. In
# particular, I tested this package using my 8BitDo SN30 Pro USB wired
# gamepad.
#
# CAUTION: If you try to use a USB adapter with a wireless xinput
# compatible gamepad, it probably won't work with this driver in its
# current form. In my testing, compared to wired gamepads, USB wireless
# adapters have extra delays and errors that require retries and
# low-level error handling. I haven't been able to get a USB wireless
# gamepad adapter working yet in CircuitPython yet.
#
from time import sleep
from struct import unpack
from sys import stdout
from usb import core
from usb.core import USBError, USBTimeoutError

# Gamepad button bitmask constants
UP     = 0x0001  # dpad: Up
DOWN   = 0x0002  # dpad: Down
LEFT   = 0x0004  # dpad: Left
RIGHT  = 0x0008  # dpad: Right
START  = 0x0010
SELECT = 0x0020
L      = 0x0100  # Left shoulder button
R      = 0x0200  # Right shoulder button
B      = 0x1000  # button cluster: bottom button (Nintendo B, Xbox A)
A      = 0x2000  # button cluster: right button  (Nintendo A, Xbox B)
Y      = 0x4000  # button cluster: left button   (Nintendo Y, Xbox X)
X      = 0x8000  # button cluster: top button    (Nintendo X, Xbox Y)

class XInputGamepad:
    def __init__(self):
        # Variable to hold the gamepad's usb.core.Device object
        self.device = None

    def find_and_configure(self, retries=25):
        # Connect to a USB wired Xbox 360 style gamepad (vid:pid=045e:028e)
        #
        # retries: max number of attempts to find device (100ms retry interval)
        #
        # Returns: True = success, False = device not found or config failed
        # Exceptions: may raise usb.core.USBError or usb.core.USBTimeoutError
        #
        for _ in range(retries):
            device = core.find(idVendor=0x045e, idProduct=0x028e)
            if device:
                sleep(0.1)
                self._configure(device)  # may raise usb.core.USBError
                return True              # end retry loop
            else:
                sleep(0.1)
        # Reaching this point means no matching USB gamepad was found
        self._reset()
        return False

    def _configure(self, device):
        # Prepare USB gamepad for use (set configuration, drain buffer, etc)
        # Exceptions: may raise usb.core.USBError or usb.core.USBTimeoutError
        interface = 0
        timeout_ms = 5
        try:
            # Make sure CircuitPython core is not claiming the device
            if device.is_kernel_driver_active(interface):
                device.detach_kernel_driver(interface)
            # Make sure that configuration is set
            device.set_configuration()
        except USBError as e:
            print("[E1]: '%s', %s, '%s'" % (e, type(e), e.errno))
            self._reset()
            raise e
        # Initial reads may give old data, so drain gamepad's buffer. This
        # may raise an exception (with no string description nor errno!)
        # when buffer is already empty. If that happens, ignore it.
        try:
            sleep(0.1)
            buf = bytearray(64)
            for _ in range(8):
                __ = device.read(0x81, buf, timeout=timeout_ms)
        except USBError as e:
            if e.errno is None:
                pass  # this is okay
            else:
                print("[E2]: '%s', %s, '%s'" % (e, type(e), e.errno))
                self._reset()
                raise e
        # All good, so save reference to device object
        self.device = device

    def poll(self):
        # Generator function for polling gamepad for button changes
        #
        # Returns: an iterator that yields the button state, which is
        # either None (temporary error condition) or an integer bitfield with
        # the current button state. (see gamepad button bitmask constants
        # defined at the top of this file)
        # Exceptions: may raise usb.core.USBError or usb.core.USBTimeoutError
        #
        # Usage:
        #     prev = 0
        #     for buttons = gamepad.poll():
        #         if (buttons is not None) and (prev != buttons):
        #             # (do stuff to handle the changed button state)
        #             prev = buttons
        #
        # Expected endpoint 0x81 report format:
        #  bytes 0,1:    prefix that doesn't change      [ignored]
        #  bytes 2,3:    button bitfield for dpad, ABXY, etc (uint16)
        #  byte  4:      L2 left trigger (analog uint8)  [ignored]
        #  byte  5:      R2 right trigger (analog uint8) [ignored]
        #  bytes 6,7:    LX left stick X axis (int16)    [ignored]
        #  bytes 8,9:    LY left stick Y axis (int16)    [ignored]
        #  bytes 10,11:  RX right stick X axis (int16)   [ignored]
        #  bytes 12,13:  RY right stick Y axis (int16)   [ignored]
        #  bytes 14..19: ???, but they don't change
        #
        if self.device is None:
            # caller is trying to poll when gamepad is not connected
            return
        # Cache functions and object references as local variables to avoid
        # spending VM time on dictionary lookups. This is a technique commonly
        # used for MicroPython performance optimization.
        read_ = self.device.read
        unpack_ = unpack
        prev = 0
        buf = bytearray(64)
        err_count = 0
        MAX_ERRORS = 99
        ms = 10
        endpoint = 0x81
        # This generator loop uses yield instead of return. The point of this
        # is to make USB IO faster by keeping local variables alive in the
        # original stack frame (particularly the bytearray) so we can spend
        # less Python VM time on dictionary lookups and heap allocations.
        # Docs: https://docs.python.org/3/glossary.html#term-generator
        while True:
            try:
                # Poll gamepad endpoint
                try:
                    n = read_(endpoint, buf, timeout=ms)
                except USBTimeoutError:
                    # Immediately retry if first read timed out
                    n = read_(endpoint, buf, timeout=ms)
                # Only bytes 2 and 3 are interesting (ignore sticks/triggers)
                (buttons,) = unpack_('<H', buf[2:4])
                yield buttons
            except USBTimeoutError as e:
                # Log USB timeouts
                stdout.write(b"[E3 timeout]\n")
                yield None
            except USBError as e:
                # Handle other USB errors
                stdout.write("[E4]: '%s', %s, '%s'\n" % (e, type(e), e.errno))
                err_count += 1
                if err_count > MAX_ERRORS:
                    # Stop loop if there were too many errors in a row
                    self._reset()
                    raise e
                else:
                    # yield for error if the error counter is still small
                    yield None
            else:
                # reset error counter if device.read() didn't raise exception
                err_count = 0

    def device_info_str(self):
        # Return string describing gamepad device (or lack thereof)
        d = self.device
        if d is None:
            return "[Gamepad not connected]"
        (v, pi, pr, m) = (d.idVendor, d.idProduct, d.product, d.manufacturer)
        if (v is None) or (pi is None):
            # Sometimes the usb.core or Max3421E will return 0000:0000 for
            # reasons that I do not understand
            return "[bad vid:pid]: vid=%s, pid=%s, prod='%s', mfg='%s'" % (
                v, pi, pr, m)
        else:
            return "Connect: %04x:%04x prod='%s' mfg='%s'" % (v, pi, pr, m)

    def _reset(self):
        # Reset USB device and gamepad button polling state
        self.device = None
