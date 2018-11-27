#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This programm measures the temp and humidity based on a DHT Sensor,
as well as several currents based on a yhdc sensor and a MCP3208.
Eventually the data is sent periodically, either once per second or
minute, depending if a threshold is exceeded."""

import os
import time  # import the module called "time"
import datetime
import pytz
import math
import logging
import psutil
import Adafruit_DHT
from socket import gethostname
import paho.mqtt.publish as publish

import RPi.GPIO as GPIO  # import the GPIO to use the Pins
from mcp3208 import MCP3208

### Path in which the data is saved
##path = os.path.dirname(os.path.realpath(__file__))

# Set configs for the current measurement:
# set the sample rate (number of measurements per seconds) and its duration
sample_rate = 1000  # 1000 Sample per second
read_intervall = 0.2  # 200 ms
QUANTILE = 0.95

mqtt_broker = "il081"
SEND_IDLE = 60  # send every .. s if below a threshold
SEND_ACTIVE = 10 # send every .. s if over a threshold
THRESHOLD = 0.01  # Threshold for sending currents in A

# initialize MCP 3208 with its resolution and pins:
channels = [0,1]  #TODO: install channels 3 and 4 # measure channels on output 0,1
# 1: Panda
# 2: Prusa
# 3: PiXtend
# 4: Misc.

# MCP 3208 has a resolution of 12 bits, that means there are 2^12 states
# starting with state 0
resolution = 4095

 # set pins to connect the MCP 3208 to the rpi
CLK = 10  # Clock
MISO = 9  # Master (rpi) in, Slave (MCP) out
MOSI = 11  # Master out, Slace in
CS = 7  # Chip Select (Master (rpi) can activate Slaves with this)


def measure_current(channel):
    # inserting in numpy arrays is faster
    voltages = [0.0] * int(sample_rate * read_intervall)

    # for each channel in channels, measure a 100 ms
    # intervall with very high sample rate.
    # read_adc returns an integer between 0 and 2^12-1 = 4095
    # (0 means 0 V, 4095 means 5 V)
    # We need to scale this raw integer like this:
    for i in range(len(voltages)):
        voltages[i] = mcp3208.read_adc(channel)
        # wait 1/sample_rate seconds
        time.sleep(1/sample_rate)

    voltage = sorted(voltages)[int(QUANTILE*len(voltages))]
    voltage = voltage / resolution * 5
    # Correction for reading the 0.95 percentile
    # math.sin(math.pi/2 - (1-0.95)/2*2*math.pi)
    voltage = voltage / 0.9876883405951378
    # Convert from peak voltage to effective current
    current = voltage * 5 / math.sqrt(2)

    return current


def check_hardware():
    """Check the hardware connection. The first reads are frequently 0,
    so there are made multiple reads on channel 0 and the maximum value
    is evaluated."""
    x = 0
    for i in range(10):
        x = max(x, mcp3208.read_adc(channels[i%len(channels)]))
        time.sleep(0)

    if x == 0:
        return "Warning: Hardware might not connected"

    humidity, temperature = Adafruit_DHT.read_retry(11, 4,
                                        retries=15,delay_seconds=2)
    if temperature is None or temperature > 1000:
        return "Warning: DHT-Sensor not connected"
    return "Hardware Check successful"


if __name__ == "__main__":
    host = gethostname()

    filename = datetime.datetime.now().replace(microsecond=0).replace(
          tzinfo=pytz.timezone('Europe/Vienna')).isoformat()

    print("Started measurement: {} on host {}".format(filename, host))

    # initialize the GPIOs (General Purpose Input and Output)
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # set the pins as output or input
    GPIO.setup(CLK, GPIO.OUT)
    GPIO.setup(MOSI, GPIO.OUT)
    GPIO.setup(MISO, GPIO.IN)
    GPIO.setup(CS, GPIO.OUT)

    # Init mcp3208 instance
    mcp3208 = MCP3208(clockpin=CLK, mosipin=MOSI, misopin=MISO, cspin=CS)

    hardware_status = check_hardware()
    print(hardware_status)

    c = 0  # Start with zero, because the first msgs should contain all data
    while True:
        starttime = time.time()
        msgs = list()
        # The function measure_voltage will be executed (called) with the argument
        # "channels" which was defined on at the top of the code.
        currents = [measure_current(channel) for channel in channels]

        # Send everything after SEND_IDLE time
        if (c % (SEND_IDLE/SEND_ACTIVE)) == 0:
            c = 1
            # Adding DHT values to msgs
            humidity, temperature = Adafruit_DHT.read_retry(11, 4,
                                        retries=15,delay_seconds=2)
            if humidity is not None:
                msg = ("{0}/humidity".format(host), humidity, 0, False)
                msgs.append(msg)
            if temperature is not None:
                msg = ("{0}/temperature".format(host), temperature, 0, False)
                msgs.append(msg)
            for i, current in enumerate(currents):
                msg = ("{0}/current{1}".format(host,i), current, 0, False)
                msgs.append(msg)

        # Send higher currents if active
        else:
            c += 1
            for i, current in enumerate(currents):
                if current > THRESHOLD:
                    msg = ("{0}/current{1}".format(host,i), current, 0, False)
                    msgs.append(msg)

        if msgs != list():
            print()
            print(starttime)
        #print(currents)
        [print(msg) for msg in msgs]

        try:
            publish.multiple(msgs, hostname=mqtt_broker)
        except Exception as e:
            print("Cannot publish message, keep trying: ", e)

        # Wait the reals SEND_ACTIVE time
        while(time.time() < starttime + SEND_ACTIVE - 0.0005):
            time.sleep(0.001)

