import time
import datetime
import logging

# Constants
LOG_FILE_NAME = "ClientLogger"
TXT_FILE = ".txt"
LOGGER_NAME = "ClientLogger"
CLIENT_PORT = 13456

class RequestType(): #request types for listener
    RESP_SUCCESS = 0x01
    RESP_FAILURE = 0x02
    REQT_SERVER_CONNECT_CLIENT = 0x10
    REQT_SERVER_SENT_XML = 0x11
    REQT_SERVER_KILL_CLIENT = 0x12

def getTimeStamp():  # timestamp file format
    time = datetime.datetime.now()
    timestamp = time.strftime('%d_%m_%y_%H_%M_%S')
    return timestamp

def getDateTime():    # timestamp log format
    time = datetime.datetime.now()
    timestamp = time.strftime('%y/%m/%d %H/%M/%S: ')
    logger = logging.getLogger(LOGGER_NAME)
    logger.info('module mesage')
    return timestamp
