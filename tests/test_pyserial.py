import sys
import serial


def main():
    print(sys.version)  # check python version
    print(serial.__version__)  # check pyserial version


if __name__ == '__main__':
    main()