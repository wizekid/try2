import logging
from Logger import init_logger
from Logger import get_logger
from Utilities import getDateTime
import Utilities
import getpass
import socket
import sys
from xml.etree import ElementTree as ET
from S_Worker import Receiver

def client_handle(_socket):
    returnResult = False
    
    handle = _socket.recv(4096)
    print(handle)
    request = int(handle)
    numberOfBytes = sys.getsizeof(request)
    print str(numberOfBytes)
    if numberOfBytes == 24:
        if request == 0x11:
            print 'OK'
            returnResult = True
    return returnResult

def sendOkResponse(_socket):
    try:
        print Utilities.RequestType.RESP_SUCCESS
        _socket.send(str(Utilities.RequestType.RESP_SUCCESS))
    except:
        logger.error('Could not send OK connection back to the client')
        return False
    return True

def is_valid_ipv4_address(address):
    try:
        print 'incerc'
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:
        return False
    print 'returnez'
    return True


def getIpAddress(_socket):
    fullIp = _socket.recv(4096)
    isOk = False
    print 'PRIMIT IP ' + fullIp
    isOk = is_valid_ipv4_address(fullIp)
    print 'S-a verificat'
    if not isOk:
        return fullIp
    else:
        return str(-1)

def getXml(_socket):
    print 'astept reguli'
    EntireXML = _socket.recv(9182)
    print 'am primit' + EntireXML
    try:
        x = ET.fromstring(EntireXML)
    except:
        EntireXML = str(-1)
    return EntireXML
  
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
    logger.info(Utilities.getDateTime() + 'Started Server for station ' + station_id)

    try:
        
        listenerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        listenerSocket.bind(('localhost', Utilities.CLIENT_PORT))
        listenerSocket.listen(5)
    except:
        logger.error(Utilities.getDateTime() + 'Could not bind socket for server to localhost')
        exception = sys.exc_info()[0]
        logger.error(Utilities.getDateTime() + 'Ex: ' + str(exception))
        logger.error(sys.exc_info()[0])
        failed = True

    try:
        file = open('configuration.xml,'r')
        tasks = ParseXMLFileForTasks(file)
    except:
        logger.error(Utilities.getDateTime() + 'Error at parsing xml file')             
    try:
                
        for task in tasks:
                newReceiver = Receiver(task.file, task.rules)
                newReceiver.createSocket()
                newReceiver.createStorageFile()
                try:
                    newReceiver.start(listenerSocket)
                except:
                    logger.error(Utilities.getDateTime() + 'Error at binding sockets')
        while True:
            (clientsocket, address) = listenerSocket.accept()
            validRequest = server_handle(clientsocket)
            if validRequest:
                sendOkResponse(clientsocket)
                fileName = os.getfiles(os.cwd)
                try:
                    for file in fileName:
                        if "SerialLogg" in file:
                            with open(fileName) as f:
                            content = f.readline()
                            clientsocket.send(content)
                except:
                    logger.error(Utilities.getDateTime() + 'Exception thrown at sending logs') 
    except:
           logger.error(Utilities.getDateTime() + 'Exception thrown at breaking of tasks and sending')     
     
    
