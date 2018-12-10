#!/usr/env/bin python3

import motorcontrol
import ds4input


class SpoolBot:
    """Manages all of the functionality for setting up and operating the robot."""

    def __init__(self):
        """Sets up the SpoolBot"""

        self._motor_controller = self.init_motor_controller()
        self._remote = self.init_remote_control(self._motor_controller)

        self._remote.scan_events()

    @staticmethod
    def init_motor_controller():
        """Sets up the motor controller, motors, and returns the motor controller object."""

        mc = motorcontrol.MotorController()
        mc.add_drive_motor(name="lefty")
        mc.add_drive_motor(name="righty", side="right", index=4)
        mc.add_spool_motor()

        return mc

    @staticmethod
    def init_remote_control(motor_controller):
        """Sets up the remote control object."""

        return ds4input.DS4Controller(motor_controller)


if __name__ == "__main__":
    print("\n\nSetting up and starting Spool Bot...\n")
    spoolbot = SpoolBot()
