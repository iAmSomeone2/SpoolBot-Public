from Adafruit_MotorHAT import Adafruit_MotorHAT
import constants
import atexit

_MOTOR_HAT = Adafruit_MotorHAT(constants.HAT_ADDRESS)


# Set up a function to auto-disable the motors when the script stops
def turn_off_motors():
    try:
        _MOTOR_HAT.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        _MOTOR_HAT.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        _MOTOR_HAT.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        _MOTOR_HAT.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
    except TypeError:
        print("Motor controller not initialized.")
    finally:
        print("Have a great day! :)")


atexit.register(turn_off_motors)
