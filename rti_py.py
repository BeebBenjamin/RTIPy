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
    :return:
    """
    if sys.platform == "linux":
        return "/dev/" + os.popen("dmesg | egrep ttyACM | cut -f3 -d: | tail -n1").read().strip()
    elif sys.platform == "darwin":
        return "/dev/cu.usbmodem1411"

    return None


def convert_string_to_number(string) -> Optional[int]:
    """
    :param string:
    :return:
    """
    try:
        return int(string)
    except ValueError as error:
        raise error


def light_led(serial_connection: str) -> bool:
    """

    :param serial_connection:
    :return:
    """
    try:
        ser = serial.Serial(serial_connection, 9600, timeout=5)
        time.sleep(2)
        ser.write('L,0')
        time.sleep(2)
        log.info('Lighting LED for 60 seconds to allow for camera focusing!')
    except SerialException as error:
        log.error('Having trouble connecting, exiting with the following error %s', error)
        raise error

    return True


def calibrate_led(serial_connection: str, calibration: str) -> bool:
    """
    :param serial_connection:
    :param calibration:
    :return:
    """
    try:
        ser = serial.Serial(serial_connection, 9600, timeout=5)
        time.sleep(2)
        ser.write(f'T, {calibration}')
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
    :param serial_connection:
    :return:
    """
    setup: Dict = yaml.load(open('setup.yml', 'r'), Loader=yaml.FullLoader)
    delay_before: str = setup.get('delay_before')
    delay_after: str = setup.get('delay_after')
    start_row: str = setup.get('start_row')
    end_row: str = setup.get('end_row')
    start_column: str = setup.get('start_column')
    end_column: str = setup.get('end_column')
    max_leds: str = setup.get('max_leds')

    command_sequence: str = f"C, {delay_before},{delay_after},{start_row},{end_row},{start_column},{end_column}," \
                            f"{max_leds}"

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
    
    :param arguments:
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
    arg_group = parser.add_mutually_exclusive_group()
    arg_group.add_argument('-l', '--light', action='store_true', help='Set up the camera by turning on a light')
    arg_group.add_argument('-c', '--calibrate', type=str, help='Enter the address of the LED and how long you would'
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
        log.error("Unhandled exception in indexer", exc_info=True)
        raise

    if success:
        sys.exit()
    else:
        sys.exit(1)
