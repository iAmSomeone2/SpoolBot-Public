#!/usr/bin/env python3

# Written by Brenden Davidson on Dec 8 2018.
# Version info found in constants file.

# This module manages the user input for the robot. 6 Buttons will be utilized. 2 buttons control spool rotation.
# 4 buttons control robot movement. Input from these 4 buttons can be combined to control more advanced movement such as
# turning left or right while also moving forward or backward.

import constants
import pygame
import os
from time import sleep
from pprint import pprint

# set SDL to use the dummy NULL video driver,
#   so it doesn't need a windowing system.
os.environ["SDL_VIDEODRIVER"] = "dummy"


# class Button:
#     """Base class for a DS4 button."""
#
#     def __init__(self, num, name="button"):
#         """Sets up a basic button."""
#
#         self._num = num
#         self._name = name
#         self._pressed = False
#
#     def get_name(self):
#         """Returns the button's name."""
#
#         return self._name
#
#     def toggle_press(self):
#         """Toggles pressed state of the button."""
#
#         if self._pressed:
#             self._pressed = False
#         else:
#             self._pressed = True
#
#     def get_num(self):
#         """Returns value of the button's pin number."""
#
#         return self._num
#
#     def set_pressed(self, is_pressed):
#         """Sets the specific value of whether the button is pressed or not."""
#
#         self._pressed = is_pressed
#
#     def get_pressed(self):
#         """Returns the value of _pressed"""
#
#         return self._pressed
#
#
# class SpoolButton(Button):
#     """Class for buttons that control spool rotation."""
#
#     def __init__(self, num, name="spool button", direction="cw"):
#         """Sets up a spool rotation control button."""
#
#         super().__init__(num, name=name)
#         self._direction = direction
#
#     def get_direction(self):
#         """Retrieves assigned direction"""
#
#         return self._direction
#
#
# class MoveButton(Button):
#     """Class for buttons that control directional movement of the robot."""
#
#     # Move buttons are special and are only to be considered active when they are depressed.
#     # I can't decide whether the MoveButton class should be able to manipulate the motor controller or not. If it can,
#     # then I have consistency with the SpoolButton class. If it can't, then motor control must be manipulated in the
#     # RemoteControl class, a new class, or helper functions.
#
#     def __init__(self, num, direction, name="move button"):
#         """Sets up robot movement control button."""
#
#         super().__init__(num, name=name)
#         self._direction = direction
#
#     def get_direction(self):
#         """Returns the direction assigned to the button."""
#         return self._direction


class DS4Controller:
    """Class representing the DualShock 4 controller."""

    def __init__(self, motor_controller):
        """Initialize the controller."""

        self._motor_controller = motor_controller
        self._spool_spin = "stop"
        self._spool_buttons = []
        self._move_buttons = []
        self._direction = "stop"
        self._active_buttons = []
        self._stop_lockout = False
        self._controller_present = True

        pygame.init()
        self._display_surf = pygame.display.set_mode(constants.PYGAME_SCREEN, pygame.HWSURFACE | pygame.DOUBLEBUF)
        try:
            pygame.joystick.init()
            self._controller = pygame.joystick.Joystick(0)
            self._controller.init()
        except:
            self._controller_present = False

        self._keys = None

        self._axis_data = None
        self._button_data = None
        self._hat_data = None

        # Create the button objects and add them to the active buttons list.
        # for btn in constants.BTN_NUMS:
        #
        #     # Determine attributes of the button to add.
        #     style = "button"
        #     direction = "none"
        #     name = constants.BTN_NUMS[btn]
        #
        #     if name == "btn_cw":
        #         # A clockwise spool button should be made
        #         style = "spool"
        #         direction = "cw"
        #     elif name == "btn_ccw":
        #         # A counter-clockwise spool button should be made
        #         style = "spool"
        #         direction = "ccw"
        #     elif name == "btn_fwd":
        #         # Set up movement button
        #         style = "move"
        #         direction = "fwd"
        #     elif name == "btn_bwd":
        #         # Set up movement button
        #         style = "move"
        #         direction = "bwd"
        #     elif name == "btn_left":
        #         # Set up movement button
        #         style = "move"
        #         direction = "left"
        #     elif name == "btn_right":
        #         # Set up movement button
        #         style = "move"
        #         direction = "right"
        #
        #     # Add new button to list of active buttons based on the button's style.
        #     if style == "spool":
        #         self._active_buttons.append(SpoolButton(btn, name=name, direction=direction))
        #     elif style == "move":
        #         self._active_buttons.append(MoveButton(btn, name=name, direction=direction))
        #
        # # Copy the move buttons and spool buttons to their own lists
        # for button in self._active_buttons:
        #     if "cw" not in button.get_name():
        #         self._move_buttons.append(button)
        #         print("Move Buttons: " + str(self._move_buttons))
        #     else:
        #         self._spool_buttons.append(button)
        #         print("Spool Buttons: " + str(self._spool_buttons))

    # SPOOL MOVEMENT SECTION BEGIN

    def determine_spin(self):
        """Determines the direction the spool should be moving based on button presses."""

        pressed_btns = []
        if self._controller_present:
            for button, pressed in self._button_data.items():
                if pressed:
                    pressed_btns.append(button)
        elif len(self._keys) < 2:
            return
        else:
            if self._keys[pygame.K_q] and self._keys[pygame.K_e]:
                pressed_btns = [1, 2]
            elif self._keys[pygame.K_q] or self._keys[pygame.K_e]:
                pressed_btns = [1]

        if len(pressed_btns) == 1:
            # One button is being pressed.

            button = pressed_btns[0]
            if self._spool_spin is "stop":
                # Spool can be spun in either direction.
                if button == constants.BTN_CW or self._keys[pygame.K_q]:
                    self._spool_spin = "cw"
                elif button == constants.BTN_CCW or self._keys[pygame.K_e]:
                    self._spool_spin = "ccw"
            else:
                # Spool needs to be stopped first.
                self._spool_spin = "stop"

        elif len(pressed_btns) == 2:
            # Two buttons are being pressed
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

        # Utilize self._hat_data[0]

        if self._controller_present:
            hat_value = self._hat_data[0]
        elif len(self._keys) < 1:
            returnre
        else:
            hat_value = (0, 0)

        # If a valid input combo is pressed, set the appropriate direction.
        if hat_value == (0, 1) or self._keys[pygame.K_UP]:
            # Up is pressed. Go forward.
            self._direction = "fwd"
        elif hat_value == (0, -1) or self._keys[pygame.K_DOWN]:
            # Down is pressed. Go backward.
            self._direction = "bwd"
        elif hat_value == (1, 0) or self._keys[pygame.K_RIGHT]:
            # Right is pressed. Do the thing.
            self._direction = "right"
        elif hat_value == (-1, 0) or self._keys[pygame.K_LEFT]:
            # GO LEFT, DAMN IT!
            self._direction = "left"
        elif hat_value == (1, 1) or (self._keys[pygame.K_UP] and self._keys[pygame.K_RIGHT]):
            # Go forward-right
            self._direction = "fwd_right"
        elif hat_value == (-1, 1) or (self._keys[pygame.K_UP] and self._keys[pygame.K_LEFT]):
            self._direction = "fwd_left"
        elif hat_value == (1, -1) or (self._keys[pygame.K_DOWN] and self._keys[pygame.K_RIGHT]):
            self._direction = "bwd_right"
        elif hat_value == (-1, -1) or (self._keys[pygame.K_DOWN] and self._keys[pygame.K_LEFT]):
            self._direction = "bwd_left"
        else:
            # No buttons are pressed, or an incorrect number are pressed, so the robot stops.
            if self._direction is not "stop":
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

    def scan_events(self):
        """Listen for controller events."""

        if self._controller_present:
            if not self._axis_data:
                self._axis_data = {}

            if not self._button_data:
                self._button_data = {}
                for i in range(self._controller.get_numbuttons()):
                    self._button_data[i] = False

            if not self._hat_data:
                self._hat_data = {}
                for i in range(self._controller.get_numhats()):
                    self._hat_data[i] = (0, 0)

        if not self._keys:
            self._keys = []

        while True:
            for event in pygame.event.get():
                if self._controller_present:
                    if event.type == pygame.JOYAXISMOTION:
                        # An axis has been moved
                        self._axis_data[event.axis] = round(event.value, 2)
                    elif event.type == pygame.JOYBUTTONDOWN:
                        # A button has been pressed
                        self._button_data[event.button] = True
                    elif event.type == pygame.JOYBUTTONUP:
                        # A button has been released
                        self._button_data[event.button] = False
                    elif event.type == pygame.JOYHATMOTION:
                        # The D-pad was used
                        self._hat_data[event.hat] = event.value
                if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    # A Keyboard button has been pressed
                    self._keys = pygame.key.get_pressed()

            os.system('clear')
            print("Input values:")
            pprint(self._button_data)
            pprint(self._axis_data)
            pprint(self._hat_data)
            pprint(self._keys)

            print("\n\t\tCONTROLS:\nLeft = left arrow\nRight = right arrow\nForward = up arrow\nBackward = down arrow"
                  "\nSpool clockwise = q\nSpool counter-clockwise = e")

            # Second, handle the spool buttons

            self.move_spool()

            # Last, deal with ground movement
            self.run_movement()

            # Wait a bit for the next loop. This doesn't need to run more than 120 times per second, and the delay will
            # assist with debouncing the input.
            #sleep(constants.CYCLE_WAIT)
