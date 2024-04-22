# utility imports
import os
import threading
import time
import socket

# environment variables
from env import SERVER_PORT, STARTING_MODE, DEFAULT_SLEEP_TIME

# motor driver imports
from src.motor import MotorPins
from src.motor import MotorDriver
from src.motor import DEFAULT_SPEED
from path_planning_prototype.path_planning_impl import PathPlanner, Direction

# object detection imports
from object_detection.detection import ObjectDetection

def handleUserInterface(clientSocket):
    while True:
        # receive a request/message from UI
        recv_msg = clientSocket.recv(64).decode()

        # a message would have the format:
        # CMD PARAMETER_0 PARAMETER_1...
        decoded_msg = recv_msg.strip().split()

        # Not sure if we really need this safety check. But it's here
        # just in case we get some empty data?
        if len(decoded_msg) < 1:
            continue
        
        # parse the message and execute corresponding action
        app_state['lock'].acquire()
        match decoded_msg[0]:   # apparently python has a switch statement now :)
            case 'MODE':
                match decoded_msg[1]:
                    case 'MANUAL':
                        if app_state['mode'] != 'MANUAL':
                            driver.stop()
                        app_state['speed'] = DEFAULT_SPEED
                        app_state['mode'] = 'MANUAL'
                    case 'AUTONOMOUS':
                        if app_state['mode'] != 'AUTONOMOUS':
                            driver.stop()
                        if app_state['path_planner'] != None:
                            app_state['mode'] = DEFAULT_SPEED
                            app_state['mode'] = 'AUTONOMOUS'
                        else:
                            driver.stop()
                            print('Tried to go autonomous, but path planner has not been initialized!')
                    case _:
                        print(f'default mode state -> error occurred!')
                pass

            case 'MOVE':
                if app_state['mode'] == "MANUAL":
                    match decoded_msg[1]:
                        case 'UP':
                            driver.forward(app_state['speed'])
                        case 'DOWN':
                            driver.backward(app_state['speed'])
                        case 'LEFT':
                            driver.left(app_state['speed'])
                        case 'RIGHT':
                            driver.right(app_state['speed'])
                        case 'STOP':
                            driver.stop()
                        case _:
                            # debug print for invalid state tracking
                            print(f'default move state...? We should not be getting here!')
                            driver.stop()

            case 'SPEED':
                match decoded_msg[1]:
                    case 'FASTER':
                        if (app_state['speed'] < 1):
                            app_state['speed'] += 0.1
                        else:
                            app_state['speed'] = 1
                    case 'SLOWER':
                        if (app_state['speed'] > 0):
                            app_state['speed'] -= 0.1
                        else:
                            app_state['speed'] = 0
                    case _:
                        print(f'default speed state -> error occurred!')

            case 'COORDS':
                top_lat = decoded_msg[1]
                left_long = decoded_msg[2]
                bottom_lat = decoded_msg[3]
                right_long = decoded_msg[4]
                app_state['path_planner'] = PathPlanner(top_lat, left_long, bottom_lat, right_long, True)

            case _:
                print("default!")
        app_state['lock'].release()

        time.sleep(0.25)


def auto_movement():
    app_state['lock'].acquire()
    app_state['current_direction'] = None
    app_state['lock'].release()
    while True:
        app_state['lock'].acquire()
        if app_state['mode'] == 'AUTONOMOUS':
            if app_state['path_planner'] == None:
                print('ERROR: In autonomous control mode, but PathPlanner has not been initalized!')
            else:
                if app_state['current_direction'] == None:
                    app_state['current_direction'] = app_state['path_planner'].state.direction 
                if app_state['path_planner'].move(driver) != -1:
                    move_direction = str(app_state['path_planner'].state.direction)
                    if move_direction == app_state['current_direction']:
                        driver.forward()
                        app_state['sleep_time'] = 1
                    else:
                        match move_direction:
                            case 'LEFT':
                                if app_state['current_dircection'] == Direction.UP:
                                    driver.left(app_state['speed'])
                                elif app_state['current_direction'] == Direction.DOWN:
                                    driver.right(app_state['speed'])
                                time.sleep(1)
                                driver.forward(app_state['speed'])
                                app_state['sleep_time'] = 1
                                app_state['current_direction'] = Direction.LEFT
                            case 'RIGHT':
                                if app_state['current_dircection'] == Direction.UP:
                                    driver.right(app_state['speed'])
                                elif app_state['current_direction'] == Direction.DOWN:
                                    driver.left(app_state['speed'])
                                time.sleep(1)
                                driver.forward(app_state['speed'])
                                app_state['sleep_time'] = 1
                                app_state['current_direction'] = Direction.RIGHT
                            case 'UP':
                                if app_state['current_dircection'] == Direction.LEFT:
                                    driver.right(app_state['speed'])
                                elif app_state['current_direction'] == Direction.RIGHT:
                                    driver.left(app_state['speed'])
                                driver.forward(app_state['speed'])
                                app_state['sleep_time'] = 0.5
                                app_state['current_direction'] = Direction.UP
                            case 'DOWN':
                                if app_state['current_dircection'] == Direction.LEFT:
                                    driver.left(app_state['speed'])
                                elif app_state['current_direction'] == Direction.RIGHT:
                                    driver.right(app_state['speed'])
                                driver.forward(app_state['speed'])
                                app_state['sleep_time'] = 0.5
                                app_state['current_direction'] = Direction.DOWN
                            case _:
                                print(f'ERROR: Unexpected direction return ({move_direction}) from PathPlanning')
        app_state['lock'].release()
        time.sleep(app_state['sleep_time'])

### Detection Thread
def run_detection():
    while True:
        detection.run_detection(detected, detectedLock, debug=True)
        time.sleep(1)

### Helper method that checks whether a person has been detected
# Used by path planner
def check_detection() -> bool:
    detectedLock.acquire()
    is_detected = detected[0]
    detectedLock.release()

    return is_detected

### Fake path planner (just for checking detection status)
def fake_path_planner_thread():
    while True:
        print(f'Detection Status: {check_detection()}')
        time.sleep(1)

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
    global detected
    global detectedLock
    detected = [False]
    detectedLock = threading.Lock()

    # initializes the camera and ssdlite model
    global detection
    detection = ObjectDetection()

    # configure the camera settings
    detection.configure_camera(debug=True)
    
    # initialize detection
    detectionThread = threading.Thread(target=run_detection)
    detectionThread.start()

    ### Fake path planner initialization
    fake_planner = threading.Thread(target=fake_path_planner_thread)
    fake_planner.start()

    # Update path planner to a real path planner after testing
    global app_state
    app_state = {'lock': threading.Lock(),'speed': DEFAULT_SPEED, 'mode': STARTING_MODE, 'path_planner': PathPlanner(0, 0, 0, 0, True), 'sleep_time': DEFAULT_SLEEP_TIME}

    motion_handler = threading.Thread(target=auto_movement)
    motion_handler.start()

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
    
if __name__ == '__main__':
    main()