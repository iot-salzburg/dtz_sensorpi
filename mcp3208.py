#!/usr/bin/env python3
"""
Analog input module for the raspberry pi and MCP3208.
"""
import RPi.GPIO as GPIO  # import the GPIO to use the Pins

class MCP3208:
    def __init__(self, clockpin, mosipin, misopin, cspin):
        self.clockpin = clockpin
        self.mosipin = mosipin
        self.misopin = misopin
        self.cspin = cspin
        

    def read_adc(self, adcnum):
        '''returns channel in voltage'''
        if ((adcnum > 7) or (adcnum < 0)):
              return -1
        GPIO.output(self.cspin, True)

        GPIO.output(self.clockpin, False)  # start clock low
        GPIO.output(self.cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
              if (commandout & 0x80):
                      GPIO.output(self.mosipin, True)
              else:
                      GPIO.output(self.mosipin, False)
              commandout <<= 1
              GPIO.output(self.clockpin, True)
              GPIO.output(self.clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(14):
              GPIO.output(self.clockpin, True)
              GPIO.output(self.clockpin, False)
              adcout <<= 1
              if (GPIO.input(self.misopin)):
                      adcout |= 0x1

        GPIO.output(self.cspin, True)

        adcout >>= 1       # first bit is 'null' so drop it
        return adcout # output in bitsdef

