# utility imports
import os
import threading
import time
import socket

# environment variables
from src.env import SERVER_PORT, STARTING_MODE, DEFAULT_SLEEP_TIME

# motor driver imports
from src.motor import MotorPins
from src.motor import MotorDriver
from src.motor import DEFAULT_SPEED
from src.path_planning_impl import PathPlanner, Direction

# object detection imports
from object_detection.detection import ObjectDetection

# thread for handling user interface commands
def handleUserInterface(clientSocket):
    while True:
        # receive a request/message from UI
        recv_msg = clientSocket.recv(64).decode()

        # a message would have the format:
        # CMD PARAMETER_0 PARAMETER_1...
        decoded_msg = recv_msg.strip().split()

        # safety check for possible empty data :)
        if len(decoded_msg) < 1:
            continue
        
        # parse the message and execute corresponding action
        appState['lock'].acquire()
        match decoded_msg[0]:   # apparently python has a switch statement now :)
            case 'MODE':
                match decoded_msg[1]:
                    case 'MANUAL':
                        if appState['mode'] != 'MANUAL':
                            driver.stop()
                        appState['speed'] = DEFAULT_SPEED
                        appState['mode'] = 'MANUAL'
                    case 'AUTONOMOUS':
                        if appState['mode'] != 'AUTONOMOUS':
                            driver.stop()
                        if appState['path_planner'] != None:
                            appState['mode'] = DEFAULT_SPEED
                            appState['mode'] = 'AUTONOMOUS'
                        else:
                            driver.stop()
                            print('Tried to go autonomous, but path planner has not been initialized!')
                    case _:
                        print(f'default mode state -> error occurred!')
                pass

            case 'MOVE':
                if appState['mode'] == "MANUAL":
                    match decoded_msg[1]:
                        case 'UP':
                            driver.forward(appState['speed'])
                        case 'DOWN':
                            driver.backward(appState['speed'])
                        case 'LEFT':
                            driver.left(appState['speed'])
                        case 'RIGHT':
                            driver.right(appState['speed'])
                        case 'STOP':
                            driver.stop()
                        case _:
                            # debug print for invalid state tracking
                            print(f'default move state...? We should not be getting here!')
                            driver.stop()

            case 'SPEED':
                match decoded_msg[1]:
                    case 'FASTER':
                        if (appState['speed'] < 1):
                            appState['speed'] += 0.1
                        else:
                            appState['speed'] = 1
                    case 'SLOWER':
                        if (appState['speed'] > 0):
                            appState['speed'] -= 0.1
                        else:
                            appState['speed'] = 0
                    case _:
                        print(f'default speed state -> error occurred!')

            case 'COORDS':
                top_lat = decoded_msg[1]
                left_long = decoded_msg[2]
                bottom_lat = decoded_msg[3]
                right_long = decoded_msg[4]
                appState['path_planner'] = PathPlanner(top_lat, left_long, bottom_lat, right_long, True)

            case _:
                print("default!")
        appState['lock'].release()

        time.sleep(0.25)

# path planner auto movement thread
def autoMovement():
    appState['lock'].acquire()
    appState['current_direction'] = None
    appState['lock'].release()
    while True:
        appState['lock'].acquire()
        if appState['mode'] == 'AUTONOMOUS':
            if appState['path_planner'] == None:
                print('ERROR: In autonomous control mode, but PathPlanner has not been initalized!')
            else:
                if appState['current_direction'] == None:
                    appState['current_direction'] = appState['path_planner'].state.direction 
                if appState['path_planner'].move(driver) != -1:
                    move_direction = str(appState['path_planner'].state.direction)
                    if move_direction == appState['current_direction']:
                        driver.forward()
                        appState['sleep_time'] = 1
                    else:
                        match move_direction:
                            case 'LEFT':
                                if appState['current_dircection'] == Direction.UP:
                                    driver.left(appState['speed'])
                                elif appState['current_direction'] == Direction.DOWN:
                                    driver.right(appState['speed'])
                                time.sleep(1)
                                driver.forward(appState['speed'])
                                appState['sleep_time'] = 1
                                appState['current_direction'] = Direction.LEFT
                            case 'RIGHT':
                                if appState['current_dircection'] == Direction.UP:
                                    driver.right(appState['speed'])
                                elif appState['current_direction'] == Direction.DOWN:
                                    driver.left(appState['speed'])
                                time.sleep(1)
                                driver.forward(appState['speed'])
                                appState['sleep_time'] = 1
                                appState['current_direction'] = Direction.RIGHT
                            case 'UP':
                                if appState['current_dircection'] == Direction.LEFT:
                                    driver.right(appState['speed'])
                                elif appState['current_direction'] == Direction.RIGHT:
                                    driver.left(appState['speed'])
                                driver.forward(appState['speed'])
                                appState['sleep_time'] = 0.5
                                appState['current_direction'] = Direction.UP
                            case 'DOWN':
                                if appState['current_dircection'] == Direction.LEFT:
                                    driver.left(appState['speed'])
                                elif appState['current_direction'] == Direction.RIGHT:
                                    driver.right(appState['speed'])
                                driver.forward(appState['speed'])
                                appState['sleep_time'] = 0.5
                                appState['current_direction'] = Direction.DOWN
                            case _:
                                print(f'ERROR: Unexpected direction return ({move_direction}) from PathPlanning')
        appState['lock'].release()
        time.sleep(appState['sleep_time'])

### Detection Thread
def runDetection():
    while True:
        detection.run_detection(detectedState, debug=False) # debug=True prints model outputs to terminal
        time.sleep(1)

### Path planner helper method that checks whether a person has been detected
def checkDetection() -> bool:
    detectedState['lock'].acquire()
    is_detected = detectedState['state']
    detectedState['lock'].release()

    return is_detected

### Main function definition
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

    ### OBJECT DETECTION SETUP ###
    # initialize global detection variable accessed by path planner
    global detectedState
    detectedState = {'lock': threading.Lock(),
                     'state': False}

    # initializes the camera and ssdlite model
    global detection
    detection = ObjectDetection()

    # configure the camera settings
    detection.configure_camera(debug=True) # debug=True enables the preview window
    
    # initialize detection
    detectionThread = threading.Thread(target=runDetection)
    detectionThread.start()

    ### PATH PLANNER SETUP ###
    # initialize global appState
    global appState
    appState = {'lock': threading.Lock(),
                 'speed': DEFAULT_SPEED, 
                 'mode': STARTING_MODE, 
                 'path_planner': PathPlanner(0, 0, 0, 0, True), 
                 'sleep_time': DEFAULT_SLEEP_TIME}

    # intialize path planning auto movement thread
    motionHandler = threading.Thread(target=autoMovement)
    motionHandler.start()

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
        handler = threading.Thread(target=handleUserInterface, args=(clientSocket))
        handler.start()
    
# program entry point
if __name__ == '__main__':
    main() # call defined main()