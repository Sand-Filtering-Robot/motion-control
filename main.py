# utility imports
import os
import threading
import time
import socket

# environment variables
from env import SERVER_PORT

# motor driver imports
from src.motor import MotorPins
from src.motor import MotorDriver

def handleUserInterface(clientSocket):
    while True:
        # receive a request/message from UI
        recv_msg = clientSocket.recv(64).decode()

        # a message would have the format:
        # CMD PARAMETER_0 PARAMETER_1...
        decoded_msg = recv_msg.strip().split()

        # Not sure if we really need this safety check. But it's here
        # just in case we get some empty data?
        if len(decoded_msg < 1):
            continue
        
        # parse the message and execute corresponding action
        match decoded_msg[0]:   # apparently python has a switch statement now :)
            case 'MODE':
                # do something
                pass

            case 'MOVE':
                match decoded_msg[1]:
                    case 'UP':
                        driver.forward()
                    case 'DOWN':
                        driver.backward()
                    case 'LEFT':
                        driver.left()
                    case 'RIGHT':
                        driver.right()
                    case _:
                        # debug print for invalid state tracking
                        print(f'default move state...? We should not be getting here!')
                        driver.stop()

            case 'SPEED':
                pass

            case _:
                print("default!")
        pass

def main():
    ### MOTOR DRIVER SETUP ###
    # create list with motor driver pins
    motorPinsList = [
        MotorPins(pwm=12, inA=20, inB=21),  # motor 0 pins
        MotorPins(pwm=13, inA=5, inB=6),    # motor 1 pins
        MotorPins(pwm=18, inA=23, inB=24),  # motor 2 pins
        MotorPins(pwm=19, inA=2, inB=3)    # motor 3 pins
    ]

    # intialize motor driver
    global driver
    driver = MotorDriver(motorPins=motorPinsList)

    ### SOCKET SERVER SETUP ###
    # First: instantiate the socket
    try:
        # AF_INET and SOCK_STREAM correspondo to the type of the socket: IPv4 and TCP
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # debug print
        print("Sucesfully created socket")
    except socket.error as err:
        # catch a possible error (typically never happens)
        print(f"Socket creation failed: {err}")

    # Second: bind the socket to a specific address and port
    try:
        # '' is equivalent to 127.0.0.1 (loopback address)
        serverSocket.bind( ('', SERVER_PORT) )
        # debug print
        print(f"Socket was bound to loopback address and PORT: {SERVER_PORT}")
    except socket.error as err:
        print(f"Socket binding failed: {err}")

    # now we will dedicate the remaining of this thread for the server socket to listen
    # and handle any incoming client connections (i.e. user interface client)
    serverSocket.listen(1) # this parameter=1 doesn't matter too much here
    
    # infinite loop to handle client connections
    while True:
        # accept client and extract socket and address
        clientSocket, clientAddress = serverSocket.accept()

        # test client connection
        recv_msg = clientSocket.recv(64).decode()
        print(f'Succesfully connected to IP: {clientAddress}\nGot: {recv_msg}')

        # call user interface handler
        handler = threading.Thread(target=handleUserInterface, args=(clientSocket, ))
        handler.start()
    
if __name__ == '__main__':
    main()