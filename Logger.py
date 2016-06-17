import logging
import Utilities

def init_logger():
    logfileName = Utilities.LOG_FILE_NAME + Utilities.getTimeStamp() + Utilities.TXT_FILE 
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s => %(module)s:  %(levelname)s: %(message)s',
                        filename=logfileName,
                        filemode='w')
    logger = logging.getLogger(Utilities.LOGGER_NAME)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    return logger
def get_logger():
    logger = logging.getLogger(Utilities.LOGGER_NAME)
    return logger
