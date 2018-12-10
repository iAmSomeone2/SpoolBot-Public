#!/usr/bin/env python3

# Written by Brenden Davidson on Dec 5 2018.
# Version info found in constants file.

# This module manages the user input for the robot. 6 Buttons will be utilized. 2 buttons control spool rotation.
# 4 buttons control robot movement. Input from these 4 buttons can be combined to control more advanced movement such as
# turning left or right while also moving forward or backward.

import constants
import RPi.GPIO as GPIO
from time import sleep


class Button:
    """Base class for a tactile switch button."""

    def __init__(self, pin_num, name="button"):
        """Sets up a basic button."""

        self._pin_num = pin_num
        self._name = name
        self._pressed = False

        # Set up button in GPIO
        GPIO.setup(pin_num, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def get_name(self):
        """Returns the button's name."""

        return self._name

    def toggle_press(self):
        """Toggles pressed state of the button."""

        if self._pressed:
            self._pressed = False
        else:
            self._pressed = True

    def get_pin(self):
        """Returns value of the button's pin number."""

        return self._pin_num

    def set_pressed(self, is_pressed):
        """Sets the specific value of whether the button is pressed or not."""

        self._pressed = is_pressed

    def get_pressed(self):
        """Returns the value of _pressed"""

        return self._pressed


class SpoolButton(Button):
    """Class for buttons that control spool rotation."""

    def __init__(self, pin_num, name="spool button", direction="cw"):
        """Sets up a spool rotation control button."""

        super().__init__(pin_num, name=name)
        self._direction = direction

    def get_direction(self):
        """Retrieves assigned direction"""

        return self._direction


class MoveButton(Button):
    """Class for buttons that control directional movement of the robot."""

    # Move buttons are special and are only to be considered active when they are depressed.
    # I can't decide whether the MoveButton class should be able to manipulate the motor controller or not. If it can,
    # then I have consistency with the SpoolButton class. If it can't, then motor control must be manipulated in the
    # RemoteControl class, a new class, or helper functions.

    def __init__(self, pin_num, direction, name="move button"):
        """Sets up robot movement control button."""

        super().__init__(pin_num, name=name)
        self._direction = direction

    def get_direction(self):
        """Returns the direction assigned to the button."""
        return self._direction


class RemoteControl:
    """A class for managing the 6-button controller for the robot."""

    def __init__(self, motor_control):
        """Creates the remote control object, sets up the GPIO interface, and maps pin numbers to button names."""

        self.spool_is_active = False
        self._active_buttons = []
        self._motor_controller = motor_control
        self._move_buttons = []
        self._spool_buttons = []
        self._spool_spin = "stop" # Options: stop, cw, ccw
        self._direction = "stop"  # Options: stop, fwd, bwd, fwd_left, fwd_right, bwd_left, bwd_right, left, right

        GPIO.setmode(GPIO.BCM)  # Set pin numbering scheme

        # Create the button objects and add them to the active buttons list.
        for pin in constants.BTN_PINS:

            # Determine attributes of the button to add.
            style = "button"
            direction = "none"
            name = constants.BTN_PINS[pin]

            if name == "btn_cw":
                # A clockwise spool button should be made
                style = "spool"
                direction = "cw"
            elif name == "btn_ccw":
                # A counter-clockwise spool button should be made
                style = "spool"
                direction = "ccw"
            elif name == "btn_fwd":
                # Set up movement button
                style = "move"
                direction = "fwd"
            elif name == "btn_bwd":
                # Set up movement button
                style = "move"
                direction = "bwd"
            elif name == "btn_left":
                # Set up movement button
                style = "move"
                direction = "left"
            elif name == "btn_right":
                # Set up movement button
                style = "move"
                direction = "right"

            # Add new button to list of active buttons based on the button's style.
            if style == "spool":
                self._active_buttons.append(SpoolButton(pin, name=name, direction=direction))
            elif style == "move":
                self._active_buttons.append(MoveButton(pin, name=name, direction=direction))

        # Copy the move buttons and spool buttons to their own lists
        for button in self._active_buttons:
            if "cw" not in button.get_name():
                self._move_buttons.append(button)
                print("Move Buttons: " + str(self._move_buttons))
            else:
                self._spool_buttons.append(button)
                print("Spool Buttons: " + str(self._spool_buttons))

    def scan_buttons(self):
        """Updates the states of all of the buttons in the remote."""

        for button in self._active_buttons:
            pin = button.get_pin()
            is_pressed = GPIO.input(pin)  # this should return 'True' if the button is being pressed.

            button.set_pressed(is_pressed)

    # SPOOL MOVEMENT SECTION BEGIN

    def determine_spin(self):
        """Determines the direction the spool should be moving based on button presses."""

        pressed_btns = []
        for button in self._spool_buttons:
            if button.get_pressed():
                pressed_btns.append(button)

        if len(pressed_btns) == 1:
            # One button is being pressed.

            button = pressed_btns[0]
            if self._spool_spin is "stop":
                # Spool can be spun in either direction.
                self._spool_spin = button.get_direction()
            else:
                # Spool needs to be stopped first.
                self._spool_spin = "stop"

        elif len(pressed_btns) == 2:
            # Two buttons are being pressed.
            # Stop the spool
            self._spool_spin = "stop"

    def move_spool(self):
        """Rotates the spool based on the direction determined by which button was activated."""

        self.determine_spin()

        spool_dir = self._spool_spin

        if spool_dir is "stop":
            # Stop movement
            self._motor_controller.spool_stop()
        elif spool_dir is "cw":
            # Move spool clockwise.
            self._motor_controller.spool_clockwise()
        elif spool_dir is "ccw":
            # Move spool counter-clockwise
            self._motor_controller.spool_counterclockwise()

    # SPOOL MOVEMENT SECTION END

    # GROUND MOVEMENT SECTION BEGIN

    def determine_direction(self):
        """Sets the direction based on which buttons are being held."""
        # Valid Inputs:
        # forward = fwd
        # backward = bwd
        # left = left
        # right = right
        # forward + left = fwd_left
        # forward + right = fwd_right
        # backward + left = bwd_left
        # backward + right = bwd_right

        # Make a list of which buttons are being pressed.
        pressed_btns = []
        for button in self._move_buttons:
            if button.get_pressed():
                pressed_btns.append(button)

        # If a valid input combo is pressed, set the appropriate direction.
        if len(pressed_btns) == 1:
            # The button directions and the move directions are the same, so they can be used.
            self._direction = pressed_btns[0].get_direction()
        elif len(pressed_btns) == 2:
            # The button values must be combined to get the correct direction.
            self._direction = "stop"
            direction_0 = pressed_btns[0].get_direction()
            direction_1 = pressed_btns[1].get_direction()

            if direction_0 == "fwd" or direction_0 == "bwd":
                # Apply fwd or bwd to the direction, first.
                self._direction = direction_0

            # Append direction_1 to the direction, second.
            self._direction += "_" + direction_1

        else:
            # No buttons are pressed, or an incorrect number are pressed, so the robot stops.
            self._direction = "stop"

        print("Current direction: " + self._direction)

    def run_movement(self):
        """Uses determine_direction to begin with and applies the correct settings to the motor controller."""

        self.determine_direction()

        # Use current direction info to determine movement.
        # This is going to be a long-ass if statement, and I can't do much about that. :(

        if self._direction is "fwd":
            # Move forward
            self._motor_controller.drive_forward()
        elif self._direction is "bwd":
            # Move backward
            self._motor_controller.drive_backward()
        elif self._direction is "left":
            # Pivot left
            self._motor_controller.drive_pivot_left()
        elif self._direction is "right":
            # Pivot right
            self._motor_controller.drive_pivot_right()
        elif self._direction is "fwd_left" or self._direction is "bwd_left":
            # Do a moving left turn.
            self._motor_controller.drive_turn_left()
        elif self._direction is "fwd_right" or self._direction is "fwd_right":
            # Do a moving right turn
            self._motor_controller.drive_turn_right()
        else:
            # Stop movement
            self._motor_controller.drive_stop()

    # GROUND MOVEMENT SECTION END

    def main_control_loop(self):
        """Loops through all control functions needed for operation."""

        while True:
            # First, check to see which buttons have been pressed.
            self.scan_buttons()

            # Second, handle the spool buttons

            self.move_spool()

            # Last, deal with ground movement
            self.run_movement()

            # Wait a bit for the next loop. This doesn't need to run more than 120 times per second, and the delay will
            # assist with debouncing the input.
            sleep(constants.CYCLE_WAIT)
