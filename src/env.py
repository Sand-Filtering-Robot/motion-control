'''
Environment variables for motion control, motor driving, and server socket implementation.
'''
SERVER_PORT = 8080
STARTING_MODE = 'MANUAL'
DEFAULT_SLEEP_TIME = 0.25

'''
Environment variables relevant for path planning and GPS implementation.
'''

# Serial port name, will be updated when installed on Pt
GPS_SERIAL_PORT_NAME = "COM9"

# Fake GPS coords for testing
TESTING_CURRENT_GPS_POSITION_X = 34.4382967
TESTING_CURRENT_GPS_POSITION_Y = 84.7193700