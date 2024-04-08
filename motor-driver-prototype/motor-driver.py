import gpiozero
from gpiozero import PWMOutputDevice
from gpiozero import DigitalOutputDevice

from time import sleep

# main
if __name__ == '__main__':
    # define pwm for motor
    motor_0 = PWMOutputDevice(12)
    motor_1 = PWMOutputDevice(13)
    motor_2 = PWMOutputDevice(18)
    motor_3 = PWMOutputDevice(19)
    # control signals for direction
    in_a = DigitalOutputDevice(20)
    in_b = DigitalOutputDevice(21)

    while True:
        print('moving motors...')
        
        # now let's drive forward :)
        in_a.on()
        in_b.off()
        motor_0.value = 0.1
        motor_1.value = 0.1
        motor_2.value = 0.1
        motor_3.value = 0.1
        sleep(1)
        

