import logging
from Logger import init_logger
from Logger import get_logger
from Utilities import getDateTime
import Utilities
import getpass
import socket
import sys
from xml.etree import ElementTree as ET
import Worker

def client_handle(_socket):
    returnResult = False
    
    handle = _socket.recv(4096)
    print(handle)
    request = int(handle)
    numberOfBytes = sys.getsizeof(request)
    print str(numberOfBytes)
    if numberOfBytes == 24:
        if request == 0x10:
            print 'OK'
            returnResult = True
    return returnResult

def sendOkResponse(_socket):
    try:
        _socket.send(str(1))
    except:
        logger.error('Could not send OK connection back to the server')
        return False
    return True

def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:
        return False

    return True


def getIpAddress(_socket):
    fullIp = _socket.recv(4096)
    isOk = False
    isOk = is_valid_ipv4_address(fullIp)
    if not isOk:
        return fullIp
    else:
        return str(-1)

def getXml(_socket):
    EntireXML = _socket.recv(9182)
    try:
        x = ET.fromstring(EntireXML)
    except:
        EntireXML = str(-1)
    return EntireXML
    
def StartLoggingThread(_ip, _xml):
    Worker = Worker(_ip, _xml)
    Worker.init_connection()
    Worker.start_monitoring()
    
if __name__ == '__main__':

    failed = False
    logger = init_logger()

    try:
        station_id = getpass.getuser()
    except:
        logger.error(Utilities.getDateTime() + 'Could not get station ID')
        exception = sys.exc_info()[0]
        logger.error(Utilities.getDateTime() + 'Ex: ' + exception)
        station_id = 'Unknown'
    
    logger.info(Utilities.getDateTime() + 'Started Client for station ' + station_id)

    logger.info(Utilities.getDateTime() + 'Attempting to open listener socket on localhost:13456')
    try:
        
        listenerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        listenerSocket.bind(('localhost', Utilities.CLIENT_PORT))
        listenerSocket.listen(5)
    except:
        logger.error(Utilities.getDateTime() + 'Could not bind socket for client to localhost')
        exception = sys.exc_info()[0]
        logger.error(Utilities.getDateTime() + 'Ex: ' + str(exception))
        logger.error(sys.exc_info()[0])
        failed = True

    if not failed:
        logger.info(Utilities.getDateTime() + 'Socket is listening to 127.0.0.1:13456')
        
        while True:
            (clientsocket, address) = listenerSocket.accept()
            validRequest = client_handle(clientsocket)
            if validRequest:
                getInfo = sendOkResponse(clientsocket)
                if getInfo is not False:
                    logger.info(Utilities.getDateTime() + 'Received new connection request . Starting negociating')
                try :
                    if getInfo is not False:
                        received_ip = getIpAddress(clientsocket)
                    else:
                        received_ip = str(-1)
                        
                    if received_ip != str(-1):
                        received_xml = getXml(clientsocket)
                        if received_xml != str(-1):
                            getInfo = True
                        else:
                            getInfo = False
                    else:
                        getInfo = False
                except :
                    getInfo = False
                    logger.error(Utilities.getDateTime() + 'Error at negociating')
                    pass

                if getInfo:
                    logger.info(Utilities.getDateTime() + 'Received valid xml from ' + received_ip)
                    StartLoggingThread(received_ip, received_xml)
                    
            else:
                logger.info(Utilities.getDateTime() + 'Unknown request received')

        logger.error('Exited while loop by force')
        
    else:
        logger.info(Utilities.getDateTime() + 'Closing application due to failure')

    
        

    
