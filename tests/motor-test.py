from motor import MotorPins
from motor import MotorDriver

import time

if __name__ == '__main__':
    # create list with motor driver pins
    motorPinsList = [
        MotorPins(pwm=12, inA=20, inB=21),  # motor 0 pins
        MotorPins(pwm=13, inA=5, inB=6),    # motor 1 pins
        MotorPins(pwm=18, inA=23, inB=24),  # motor 2 pins
        MotorPins(pwm=19, inA=2, inB=3)    # motor 3 pins
    ]

    # intialize motor driver
    driver = MotorDriver(motorPins=motorPinsList)

    # test driving in all four directions
    while True:
        # drive forward
        driver.forward()
        print(driver)
        time.sleep(5)

        # drive backward
        driver.backward()
        print(driver)
        time.sleep(5)

        # drive right
        driver.right()
        print(driver)
        time.sleep(5)

        # drive left
        driver.left()
        print(driver)
        time.sleep(5)
