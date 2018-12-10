#!/usr/bin/env python3

from Adafruit_MotorHAT import Adafruit_MotorHAT

VERSION = "12.08.18"

FORWARD = Adafruit_MotorHAT.FORWARD
BACKWARD = Adafruit_MotorHAT.BACKWARD
RELEASE = Adafruit_MotorHAT.RELEASE

HAT_ADDRESS = 0x60

# Motor speed values
FWD_SPEED = 225
BWD_SPEED = 175
SPOOL_SPEED = 255
STOPPING_FACTOR = 0.70

TURN_OUTER = 175
TURN_INNER = 125

# Pin numbers
PIN_CW = 4
PIN_CCW = 17
PIN_FWD = 18
PIN_BWD = 27
PIN_LEFT = 22
PIN_RIGHT = 23

BTN_PINS = {PIN_CW: "btn_cw", PIN_CCW: "btn_ccw", PIN_FWD: "btn_fwd", PIN_BWD: "btn_bwd", PIN_LEFT: "btn_left",
            PIN_RIGHT: "btn_right"}

CYCLE_WAIT = 0.016666  # 1/60th of a second

PYGAME_SCREEN = [1, 1]

# DS4 button values
BTN_CW = 4
BTN_CCW = 5
# HAT 0
BTN_UP = (0, 1)
BTN_DWN = (0, -1)
BTN_LFT = (-1, 0)
BTN_RGT = (1, 0)

BTN_NUMS = {BTN_CW: "btn_cw", BTN_CCW: "btn_ccw", BTN_UP: "btn_fwd", BTN_DWN: "btn_bwd", BTN_LFT: "btn_left",
            BTN_RGT: "btn_right"}