## Introduction

RTIPy is a Python and Arduino project designed to power a low complexity, affordable, and portable micro Reflectance
Transformation Imaging (RTI) dome for use in fieldwork.  The RTI dome was commissioned by Dr Abigail Desmond and 
designed and built by Mr Richard Benjamin Allen at Palaeopi Ltd and funded by the Ashmolean Museum, Oxford.

## Installation

The project depends on an external Arduino library to drive the Lolshield. Download and install the LoLshield library 
into your Arduino IDE, the project can be found here: https://github.com/jprodgers/LoLshield

Use the Arduino IDE to upload the code from the `arduino/rti_py` directory to the Ardunio Uno in the usual way.

To install the Python script needed to communicate with the Arduino board first install `Python 3.6` and `pipenv` as
per your computer's OS.

**N.B.** Only Linux or MacOS are currently supported by this project.

Then open up a terminal, navigate to the local GitHub repository, and install the required Python packages as follows:

```bash
pipenv install
```

## Changing the Setup File
The project includes a configurable `setup.yml` file, here one can change the various system variables that the
project uses for photography timings e.g. delays required for different exposures; the number of LEDs in use and the
'bounds' of the LEDs e.g. the number and address of the columns and rows used in your setup.  The file itself contains
additional helpful comments that can tell you what each setting does.

## Bill Of Materials
1 * Pre-wired 5mm Infra-red 5v LED
1 * LoLshield
Several strips of 2.54 mm un-shrouded pin headers cut into pairs (total of 72 pins in pairs of 2 e.g. 31 pairs)
1 * Arduino Uno + USB cable
1 * 3D printed dome
72 * Dual pin jumper wire with "Dupont" connectors, you can buy them [here](https://shop.pimoroni.com/products/dual-pin-jumper-wire)
72 * Pre-wired 5mm clear 5v LED with "Dupont" connectors

## Build Instructions
1. Build the Lolshield (assemble as per it's instructions).  However, if the board comes with its own LEDs don't 
solder them to the board, because we are going to attach our own headers. 

2. Cut up the 2.54mm pin headers into pairs and solder these in rows as in the following image:

**insert picture here**

2. Solder a header pair to analogue pin A0 and to a ground pin for the IR LED as follows:

**insert picture here**

3. Attach the Lolshield to the Arduino Uno by pushing it into place like many of the available Arduino shields.

4. Connect the jumper leads to the pre-wired white light LEDs and link them up to the headers on the Lolshield, making
sure that the polarity is correct.  Next connect up the pre-wired IR LED to analogue pins A0 and ground.

5. Insert the white light LEDs into the holes of the 3D printed dome, use blue-tack or something similar to secure them
if the fittings are loose.

6. Plug the Arduino into a USB port on your computer to power the device; you will need to use serial over USB to
also send instructions to the device.

7. Set up your camera as you usually would for RTI and position it over the hole in the top of the dome, use a
cloth to cover the dome if you wish.  [See Basic Usage](#Basic Usage) for how to pilot the dome using the computer terminal. 

## 3D Printed Files
There is a 3D printable dome in the project files, this can be printed using many types of 3D printer or material. 
For best results the model should be re-sized/calibrated so that the LED holes are not too loose upon printing.

## RTI Spheres
We found that 5mm steel balls extracted from roller bearings make excellent RTI Spheres for macro photography.  These
can be superglued to [Lego studs with holes](https://www.brickowl.com/catalog/lego-white-plate-1-x-1-round-with-open-stud-28626-85861)
and their height can easily be adjusted by adding Lego plates to the bottom of the stud.

## Camera Compatibility
The Arduino code is designed to work with Nikon DSLRs with IR trigger capability.  These have unfortunately been
phased out of the most recent models.  If you want to make it work with different camera makes (or more modern Nikons), 
you will need to change the IR pulse code accordingly or find another method of triggering the camera.

## Basic Usage
# Turning on a light for adjusting camera focus and exposure
Open a terminal and change directory to the place where you downloaded the RTIPy repository.  Activate the pipenv 
environment previously installed during [Installation](#Installation) by typing in the following command into the 
terminal and press enter:

```bash
pipenv shell
```
Next type the following command into the terminal and press enter:

```bash
python rti_py.py -l
```

A single LED should light up inside which will allow you to adjust the camera exposure and the timings in the `setup.yml`
file accordingly.

# Adjusting the angle of individual LEDs
If you notice that a particular LED needs adjusting (probably during post processing) it is possible to follow the LED
back to the board, find its column and row address and instruct the board to light it; this should allow you to adjust 
the angle with the blue tack if it is a particularly loose fit.  To do so type the something like following command into 
the terminal and press enter, where the numbers following mean column, row, and duration in seconds:

```bash
python rti_py.py -c 3,0,20
```

A single LED should light up inside which will allow you to adjust its angle shining onto the target object or use it
to calibrate the camera as per the `-l` command.

# Triggering Capture
To trigger the capture sequence, activate the IR release mode on your Nikon camera in the menu and make sure it can "see"
the IR trigger LED.  Next type the following command into the terminal and press enter:

```bash
python rti_py.py -s
```

Remember that if you require different delays for different camera exposures, these can be adjusted using the `setup.yml`
config file.