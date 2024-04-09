from typing import List
from gpiozero import PWMOutputDevice
from gpiozero import DigitalOutputDevice

# constants
DEFAULT_SPEED = 0.2

class MotorPins:
    def __init__(self, pwm, inA, inB) -> None:
        self.pwmPin = pwm
        self.inA = inA
        self.inB = inB
        
class MotorDriver:
    motorPWM = []
    motorControlA = []
    motorControlB = []

    def __init__(self, motorPins: List) -> None:
        # initialize a motor instance that creates all necessary GPIO and PWM to drive
        # SandE in all directions at variable speed
        for i in range(len(motorPins)):
            self.motorPWM.append(PWMOutputDevice(motorPins[i].pwmPin))
            self.motorControlA.append(DigitalOutputDevice(motorPins[i].inA))
            self.motorControlB.append(DigitalOutputDevice(motorPins[i].inB))
            print(f'[INFO]: Motor {i} on PWM {motorPins[i].pwmPin} has been succesfully initialized')
        
        self.numMotors = len(motorPins)
        self.maxSpeed = 0.5

    # forward motion is defined as in_a = 1, in_b = 0, pwm = speed
    def forward(self, speed=DEFAULT_SPEED) -> None:
        print(f'[INFO]: Moving forward at {speed * 100}% speed!')
        for i in range(self.numMotors):
            if (speed > self.maxSpeed):
                print('[WARNING]: MAX SPEED THRESHOLD WAS EXCEEDED')
                self.motorPWM[i].value = self.maxSpeed
            else:
                self.motorPWM[i].value = speed
            self.motorControlA[i].value = 1
            self.motorControlB[i].value = 0

    # backward motion is defined as in_a = 0, in_b = 1, pwm = speed
    def backward(self, speed=DEFAULT_SPEED) -> None:
        print(f'[INFO]: Moving backward at {speed * 100}% speed!')
        for i in range(self.numMotors):
            if (speed > self.maxSpeed):
                print('[WARNING]: MAX SPEED THRESHOLD WAS EXCEEDED')
                self.motorPWM[i].value = self.maxSpeed
            else:
                self.motorPWM[i].value = speed
            self.motorControlA[i].value = 0
            self.motorControlB[i].value = 1

    # right motion is defined as a mix of forward and backward
    def right(self, speed=DEFAULT_SPEED) -> None:
        # left wheels go forward (wheels 0 and 2)
        # right wheels go backward (wheels 1 and 3)
        print(f'[INFO]: Moving right at {speed * 100}% speed!')
        for i in range(self.numMotors):
            if (speed > self.maxSpeed):
                print('[WARNING]: MAX SPEED THRESHOLD WAS EXCEEDED')
                self.motorPWM[i].value = self.maxSpeed
            else:
                self.motorPWM[i].value = speed
            self.motorControlA[i].value = 1 - (i % 2)
            self.motorControlB[i].value = i % 2

    def left(self, speed=DEFAULT_SPEED) -> None:
        # left wheels go backward (wheels 0 and 2)
        # right wheels go forward (wheels 1 and 3)
        print(f'[INFO]: Moving left at {speed * 100}% speed!')
        for i in range(self.numMotors):
            if (speed > self.maxSpeed):
                print('[WARNING]: MAX SPEED THRESHOLD WAS EXCEEDED')
                self.motorPWM[i].value = self.maxSpeed
            else:
                self.motorPWM[i].value = speed
            self.motorControlA[i].value = i % 2
            self.motorControlB[i].value = 1 - (i % 2)
    
    def __str__(self) -> str:
        driverString = f'MOTOR DRIVER INSTANCE'
        for i in range(self.numMotors):
            driverString += f'\nMOTOR {i} PWM: {self.motorPWM[i].value}'
            driverString += f'\nMOTOR {i} inA: {self.motorControlA[i].value}'
            driverString += f'\nMOTOR {i} inB: {self.motorControlB[i].value}'

        return driverString
