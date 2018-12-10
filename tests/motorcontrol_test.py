#!/usr/bin/env python3

import unittest
from spoolbot import motorcontrol as control
import os
import sys
from Adafruit_MotorHAT import Adafruit_MotorHAT
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestMotorControl(unittest.TestCase):
    """Test the creation and use of a MotorController object"""

    def setUp(self):
        """Set up the motor controller"""

        self.mc = control.MotorController()
        self.mc.add_drive_motor()

    def tearDown(self):
        self.motorHAT = Adafruit_MotorHAT(addr=0x60)
        self.motorHAT.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        self.motorHAT.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        self.motorHAT.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        self.motorHAT.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

    def test_drive_forward(self):
        """Tests output of calling drive_forward"""
