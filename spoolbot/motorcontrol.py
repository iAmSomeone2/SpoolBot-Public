#!/usr/bin/env python3

# Written by Brenden Davidson on Dec 3 2018.
# Version info found in constants file.

import constants
from Adafruit_MotorHAT import Adafruit_MotorHAT
from time import sleep

VERSION = constants.VERSION

# consts
_FWD_SPEED = constants.FWD_SPEED
_BWD_SPEED = constants.BWD_SPEED
_SPOOL_SPEED = constants.SPOOL_SPEED
_STOPPING_FACTOR = constants.STOPPING_FACTOR

# Rename movement for easier use
FORWARD = constants.FORWARD
BACKWARD = constants.BACKWARD
RELEASE = constants.RELEASE


def print_info():
    print("\nRaspberry Pi MotorHAT controller module for use on ME2011 robot.")
    print("Version " + VERSION + "\t\tWritten by Brenden Davidson")


class Motor:
    """Keeps track of info for individual motors to be used with the MotorHAT"""

    def __init__(self, motor_hat, name="motor", style="generic", index=1):
        """Creates a Motor object. 'name' is a string id, and 'index' is what header the motor is connected to."""

        self.name = name
        self.style = style
        self.index = index
        self.motor = motor_hat.getMotor(index)
        self.state = RELEASE


class DriveMotor(Motor):
    """Creates a DriveMotor object for use with the MotorHAT"""

    def __init__(self, motor_hat, side="left", name="drive_motor", index=1, trim=0):
        super().__init__(motor_hat, name=name, style="drive", index=index)
        self.side = side
        self.trim = trim


class SpoolMotor(Motor):
    """Creates a SpoolMotor object for use with the MotorHAT"""

    def __init__(self, motor_hat, name="spool_motor", index=3):
        super().__init__(motor_hat, name=name, style="spool", index=index)


class MotorController:
    """Manages all motors connected to the MotorHAT and provides methods for interacting with them"""

    def __init__(self, hat_addr=constants.HAT_ADDRESS, fwd_speed=_FWD_SPEED, bwd_speed=_BWD_SPEED, spool_speed=_SPOOL_SPEED):
        print_info()
        self._motor_hat = Adafruit_MotorHAT(addr=hat_addr)
        self.fwd_speed = fwd_speed
        self.bwd_speed = bwd_speed
        self.spool_speed = spool_speed
        self.motors = {1: None, 2: None, 3: None, 4: None}
        self.drive_motors = {1: None, 2: None, 3: None, 4: None}
        self.spool_motors = {1: None, 2: None, 3: None, 4: None}
        # This will be a dictionary containing all of the motor objects and their indexes

    def add_drive_motor(self, name="drive_motor", side="left", index=1, trim=0):
        """Creates a DriveMotor object and adds it to the motor controller."""

        drive_motor = DriveMotor(motor_hat=self._motor_hat, side=side, name=name, index=index, trim=trim)
        self.motors[index] = drive_motor
        self.drive_motors[index] = drive_motor

    def add_spool_motor(self, name="spool_motor", index=3):
        """Creates a DriveMotor object and adds it to the motor controller."""

        spool_motor = SpoolMotor(motor_hat=self._motor_hat, name=name, index=index)
        self.motors[index] = spool_motor
        self.spool_motors[index] = spool_motor

    def stop_all(self):
        """Stops all motors at the same time. Useful for testing."""
        # Get list of usable motors
        live_motors = []
        for drive_motor in self.drive_motors.values():
            if drive_motor is not None:
                live_motors.append(drive_motor)

        for motor in live_motors:
            motor.state = RELEASE
            motor.motor.run(RELEASE)

    # BEGIN DRIVE MOTOR FUNCTIONS #

    def drive_forward(self):
        """Uses all drive motors to move forward."""

        # Get list of usable motors
        live_motors = []
        for drive_motor in self.drive_motors.values():
            if drive_motor is not None:
                live_motors.append(drive_motor)

        # Set all correct attributes of all usable motors
        for motor in live_motors:
            trim = motor.trim
            motor.state = FORWARD
            motor.motor.setSpeed(self.fwd_speed + trim)
            motor.motor.run(motor.state)
            print(motor.name + " is moving forward.")

    def drive_backward(self):
        """Uses all drive motors to move backward."""

        # Get list of usable motors
        live_motors = []
        for drive_motor in self.drive_motors.values():
            if drive_motor is not None:
                live_motors.append(drive_motor)

        # Set all correct attributes of all usable motors
        for motor in live_motors:
            trim = motor.trim
            motor.state = BACKWARD
            motor.motor.setSpeed(self.bwd_speed + trim)
            motor.motor.run(motor.state)
            print(motor.name + " is moving backward.")

    def drive_stop(self):
        """Stops all drive motors gracefully, and returns a list of live motors."""

        # Get list of usable motors
        live_motors = []
        for drive_motor in self.drive_motors.values():
            if drive_motor is not None:
                live_motors.append(drive_motor)

        # Set all correct attributes of all usable motors
        motor = live_motors[0]
        current_speed = 100
        if motor.state == FORWARD:
            print("Current direction of " + motor.name + " is FORWARD")
            # Slow down from forward direction
            current_speed = self.fwd_speed
        elif motor.state == BACKWARD:
            print("Current direction of " + motor.name + " is BACKWARD")
            # Slow down from backward direction
            current_speed = self.bwd_speed
        elif motor.state == RELEASE:
            print("Current direction of " + motor.name + " is RELEASE")
            current_speed = 0

        while current_speed > 2:
            for motor in live_motors:
                trim = motor.trim
                motor.motor.setSpeed(current_speed)
                print(motor.name + " is at speed: " + str(current_speed))
            current_speed = int(current_speed * _STOPPING_FACTOR)
            if current_speed <= 2:
                current_speed = 0
            sleep(0.25)

        for motor in live_motors:
            motor.motor.run(RELEASE)

        return live_motors

    def drive_pivot_right(self):
        """Pivots the robot left from a stopped position."""

        # Stop the robot first.
        live_motors = self.drive_stop()

        # Get lists of all motors for each direction
        right_motors = []
        left_motors = []

        for motor in live_motors:
            if motor.side == "left":
                left_motors.append(motor)
            elif motor.side == "right":
                right_motors.append(motor)
            else:
                print(motor.name + " was not set as 'left' or 'right'. Omitting...")

        # Run the right motors forward and the left motors backward to pivot left
        for motor in left_motors:
            trim = motor.trim
            motor.state = BACKWARD
            motor.motor.setSpeed(self.bwd_speed + trim)
            motor.motor.run(motor.state)
            print(motor.name + " is moving backward.")

        for motor in right_motors:
            trim = motor.trim
            motor.state = FORWARD
            motor.motor.setSpeed(self.bwd_speed + trim)
            motor.motor.run(motor.state)
            print(motor.name + " is moving forward.")

    def drive_pivot_left(self):
        """Pivots the robot right from a stopped position."""

        # Stop the robot first.
        live_motors = self.drive_stop()

        # Get lists of all motors for each direction
        right_motors = []
        left_motors = []

        for motor in live_motors:
            if motor.side == "left":
                left_motors.append(motor)
            elif motor.side == "right":
                right_motors.append(motor)
            else:
                print(motor.name + " was not set as 'left' or 'right'. Omitting...")

        # Run the right motors forward and the left motors backward to pivot left
        for motor in right_motors:
            trim = motor.trim
            motor.state = BACKWARD
            motor.motor.setSpeed(self.bwd_speed + trim)
            motor.motor.run(motor.state)
            print(motor.name + " is moving backward.")

        for motor in left_motors:
            trim = motor.trim
            motor.state = FORWARD
            motor.motor.setSpeed(self.bwd_speed + trim)
            motor.motor.run(motor.state)
            print(motor.name + " is moving forward.")

    def check_same_direction(self, directions):
        """Returns 'True' if all of the directions are the same. 'False' otherwise."""

        direction = directions[0]

        for item in directions:
            if not item == direction:
                return False

        return True

    def drive_turn_left(self):
        """Turns right while the robot is in motion"""

        # Get lists of all motors for each direction
        right_motors = []
        left_motors = []
        motor_directions = []

        for motor in self.drive_motors.values():
            if motor is not None:
                if motor.side == "left":
                    left_motors.append(motor)
                    motor_directions.append(motor.state)
                elif motor.side == "right":
                    right_motors.append(motor)
                    motor_directions.append(motor.state)
                else:
                    print(motor.name + " was not set as 'left' or 'right'. Omitting...")

        # Double check that all motors are moving in the same direction.
        all_same = self.check_same_direction(motor_directions)

        # Skip the rest of the function if the robot is pivoting.
        if not all_same:
            print("Robot is currently pivoting. Can't do a drive turn right now.")
            return

        # Set appropriate speeds for the motors to allow a turn
        for motor in right_motors:
            trim = motor.trim
            motor.motor.setSpeed(self.fwd_speed + trim)
            motor.motor.run(motor.state)

        for motor in left_motors:
            trim = motor.trim
            motor.motor.setSpeed(self.bwd_speed + trim)
            motor.motor.run(motor.state)

    def drive_turn_right(self):
        """Turns right while the robot is in motion"""

        # TODO: Figure out why this is turning left

        # Get lists of all motors for each direction
        right_motors = []
        left_motors = []
        motor_directions = []

        for motor in self.drive_motors.values():
            if motor is not None:
                if motor.side == "left":
                    left_motors.append(motor)
                    motor_directions.append(motor.state)
                elif motor.side == "right":
                    right_motors.append(motor)
                    motor_directions.append(motor.state)
                else:
                    print(motor.name + " was not set as 'left' or 'right'. Omitting...")

        # Double check that all motors are moving in the same direction.
        all_same = self.check_same_direction(motor_directions)

        # Skip the rest of the function if the robot is pivoting.
        if not all_same:
            print("Robot is currently pivoting. Can't do a drive turn right now.")
            return

        # Set appropriate speeds for the motors to allow a turn
        for motor in right_motors:
            trim = motor.trim
            motor.motor.setSpeed(self.fwd_speed + trim)
            motor.motor.run(motor.state)

        for motor in left_motors:
            trim = motor.trim
            motor.motor.setSpeed(self.bwd_speed + trim)
            motor.motor.run(motor.state)

    # END DRIVE MOTOR FUNCTIONS #

    # BEGIN SPOOL MOTOR FUNCTIONS #

    def spool_stop(self):
        """Immediately stops the spool motor. It doesn't move very fast, so immediate stopping isn't a problem.
           Also returns the list of spool motors."""

        spool_motors = []

        for motor in self.spool_motors.values():
            if motor is not None:
                spool_motors.append(motor)

        for motor in spool_motors:
            motor.state = RELEASE
            motor.motor.run(RELEASE)

        return spool_motors

    def spool_clockwise(self):
        """Runs the spool motor clockwise"""

        spool_motors = self.spool_stop()

        for motor in spool_motors:
            motor.state = FORWARD
            motor.motor.setSpeed(self.spool_speed)
            motor.motor.run(FORWARD)

    def spool_counterclockwise(self):
        """Runs the spool motor clockwise"""

        spool_motors = self.spool_stop()

        for motor in spool_motors:
            motor.state = BACKWARD
            motor.motor.setSpeed(self.spool_speed)
            motor.motor.run(BACKWARD)

    # END SPOOL MOTOR FUNCTIONS #
