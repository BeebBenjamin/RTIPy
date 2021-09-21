#!/usr/bin/python3

import argparse
import logging.config
import os
import time
import serial
import sys
import yaml

from serial import SerialException
from typing import Dict
from typing import List, Optional

log_config: Dict = yaml.load(open('logging.yml', 'r'), Loader=yaml.FullLoader)
log = logging.getLogger("__name__")


def get_serial_port() -> Optional[str]:
    """
    Returns the Arduino serial port address on either Linux of MacOS, returns None for other unsupported systems
    :return:
    """
    if sys.platform == "linux":
        return "/dev/" + os.popen("dmesg | egrep ttyACM | cut -f3 -d: | tail -n1").read().strip()
    elif sys.platform == "darwin":
        return "/dev/cu.usbmodem1411"

    return None


def convert_string_to_number(string) -> Optional[int]:
    """
    Takes a string and tries to convert it into an int as a check for input parameter formatting
    :param string: string containing the calibration command sequence
    :return:
    """
    try:
        return int(string)
    except ValueError as error:
        raise error


def light_led(serial_connection: str) -> bool:
    """
    Takes a serial device address and attempts to send a string command to the Arduino to light one LED in the dome for
    60 seconds so a camera can be set up with the correct exposure and aperture etc.
    :param serial_connection: string containing the serial address of the Arduino connected to the USB port
    :return:
    """
    try:
        ser = serial.Serial(serial_connection, 9600, timeout=5)
        time.sleep(2)
        ser.write(b'L,0')
        time.sleep(2)
        log.info('Lighting LED for 60 seconds to allow for camera focusing!')
    except SerialException as error:
        log.error('Having trouble connecting, exiting with the following error %s', error)
        raise error

    return True


def calibrate_led(serial_connection: str, calibration: str) -> bool:
    """
    Takes a serial device address and calibration string and attempts to send a string command to the Arduino to light
    one LED in the dome for a specific amount of time (can also be used to set up a camera).  The calibration string
    needs to be a series of comma delimited integers.
    :param serial_connection: string containing the serial address of the Arduino connected to the USB port
    :param calibration: string containing 3 comma delimited integers containing the x, y, coordinates of the LED you
    wish to light up followed by how many seconds you wish to light it for e.g. 3,0,20.
    :return:
    """
    try:
        ser = serial.Serial(serial_connection, 9600, timeout=5)
        time.sleep(2)
        ser.write(f'T, {bytes(calibration,"utf-8")}')
        time.sleep(2)
        calibration_split: List = calibration.split()
        log.info('Turning on an LED at address x: %s, y: %s, for %s seconds!',
                 calibration_split[0], calibration_split[1], calibration_split[2])
    except SerialException as error:
        log.error('Having trouble connecting, exiting with the following error %s', error)
        raise error

    return True


def start_capture(serial_connection: str) -> bool:
    """
    Takes a serial device address and loads a configuration defined in a yaml file, the configuration is then converted
    into a command sequence which is then sent to the Arduino to instruct it to capture a sequence of images in the
    dome and what range of LEDS to use.  It is possible to set the wait inbetween photos, and also the start and end
    range of the LEDS you wish to use.
    :param serial_connection: string containing the serial address of the Arduino connected to the USB port
    :return:
    """
    setup: Dict = yaml.load(open('setup.yml', 'r'), Loader=yaml.FullLoader).get('setup')
    delay_before: str = setup.get('delay_before')
    delay_after: str = setup.get('delay_after')
    start_row: str = setup.get('start_row')
    end_row: str = setup.get('end_row')
    start_column: str = setup.get('start_column')
    end_column: str = setup.get('end_column')
    max_leds: str = setup.get('max_leds')

    command_sequence: str = f"C, {delay_before},{delay_after},{start_row},{end_row},{start_column},{end_column},{max_leds}"
    command_sequence: bytes = bytes(command_sequence, 'utf-8')

    try:
        ser = serial.Serial(serial_connection, 9600, timeout=5)
        time.sleep(2)
        ser.write(command_sequence)
        time.sleep(2)
        log.info("Starting capture sequence in 5 seconds, to cancel simply press the reset button on the Arduino"
                 "Capture can take 5-10 minutes to complete!")
    except SerialException as error:
        log.error('Having trouble connecting, exiting with the following error %s', error)
        raise error

    return True


def main(arguments) -> bool:
    """
    Takes arguments from argparse and runs either light_led, calibrate_led, or capture based on your choice.
    :param arguments: Arguments parsed out of argparse, this should only ever contain one of the mutually exclusive
    group, so it is not possible to run calibration at the same time as capture.
    :return:
    """
    serial_name: str = get_serial_port()

    if serial_name is None:
        log.error("System operating system is not supported for this program")
        return False

    if arguments.light:
        light: bool = light_led(serial_name)

        if not light:
            return False
        return True

    elif arguments.calibrate:
        calibration: str = arguments.calibrate
        calibrate: bool = calibrate_led(serial_name, calibration)

        if not calibrate:
            return False
        return True

    capture: bool = start_capture(serial_name)

    if not capture:
        return False
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Python terminal application to make operating the RTI dome simpler')
    arg_group = parser.add_mutually_exclusive_group(required=True)
    arg_group.add_argument('-l', '--light', action='store_true', help='Set up the camera by turning on a light')
    arg_group.add_argument('-c', '--calibrate', type=str, help='Enter the address of the LED and how long you would '
                                                               'like it to be activated for (in seconds), each variable'
                                                               'needs to be delimited by commas starting with '
                                                               'x, y, time e.g. 3,0,20')
    arg_group.add_argument('-s', '--start', action='store_true', help='Start capture of the RTI dome once camera and '
                                                                      'LEDS are set up')
    args = parser.parse_args()

    if args.calibrate:
        led_split = args.calibrate.split(',')
        if len(led_split) == 3:
            for item in led_split:
                try:
                    convert_string_to_number(item)
                except ValueError:
                    log.error("One or more values given in the parameter is not an integer! Please try again!")
                    sys.exit(1)
        else:
            log.error("Not enough variables to pass along to the Arduino!  Please specify three exactly delimited"
                      "by a comma and try again!")

    try:
        success = main(args)
    except BaseException:
        log.error("Unhandled exception in rti_pi", exc_info=True)
        raise

    if success:
        sys.exit()
    else:
        sys.exit(1)