import logging
from Logger import init_logger
from Logger import get_logger
from Utilities import getDateTime
import socket
import sys
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import XMLParser
import Queue
import threading
import re

class prioRegExPair:
    def __init__(self,regEx,prio):
        self.regEx = regEx
        self.prio = prio

class targetFile:
    def __init__(self,_path):
        self.filePath = _path
    def addKeyWord(self, _keyword):
        self.keywordCollection.append(_keyword)

class WorkerThread(threading.Thread):
    def __init__(self, logfilePath, keyWords, messageQueue, is_running, closeEvent):
        threading.Thread.__init__(self)
        self.logfilePath = logfilePath
        self.keyWords = keyWords
        self.is_running = is_running
        self.closeThreadsEvent = closeEvent
        self.logger = Utilities.get_logger()
    def run(self):
        file = open(self.logfile,'r')
        st_results = os.stat(self.logfile)
        st_size = st_results[6]
        file.seek(st_size)
        self.logger(Utilities.getDateTime() + 'Started to monitorize file ' + self.logfile)

        while(self.closeThreadsEvent.is_set is not True):
            where = file.tell()
            line = file.readline()
            if not line:
                file.seek(where)
            else:
                for regEx in self.keyWords:
                    pattern = re.compile(regEx.regEx)
                    if pattern.match(line):
                        messageQueue.put(Utilities.getDateTime() + "{}" + regEx.prio  + "{}" + line )
                
    

class Worker:
    threadCount = 0
    
    def __init__(self, _UDPip, _configXml):
        self.ip = _UDPip
        newConfigFileName = "ConfigForThread_" + str(threadCount) + ".xml"
        newConfigFile = open(newConfigFileName, "w")
        newConfigFile.write(_configXml)
        newConfigFile.close()
        self.Run_Bool = True
        self.Q = Queue()
        self.reconnectCounter = 0
        self.closeThreadsEvent = threading.Event()
        self.closeThreadsEvent.clear()
        self.logger = Utilities.get_logger()
        
        self.tree = ET.parse(newConfigFileName)
        root = self.tree.getroot()
        for filePath in root.findall('FILE'):
            self.logger.info(Utilities.getDateTime() + 'Added a new file for monitoring into Worker thread: ' + filePath)
            self.newTargetFile = targetFile(filePath)
            for keyWord in filePath.findall('KEY'):
                regEx = keyWord.text
                priority = keyWord.get('priority')
                newPair = prioRegExPair(regEx, priority)
                newTargetFile.addKeyWord(newPair)
                self.logger.info(Utilities.getDateTime() + 'Added keyword ' + regEx + ' with priority ' + priority +'.')
            newWorker = WorkerThread(filePath, newTargetFile, Q, Run_Bool ,closeThreadsEvent)
            self.ThreadList.append(newWorker)
            
    def start_monitoring(self):
        for thread in self.ThreadList:
            thread.start()
        self.closeThreadsEvent.wait()
        for thread in self.ThreadList:
            thread.join()
            
    def init_connection(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip_and_port = self.ip.split(":")
            port = ip[1]
            ip = ip[0]
            self.logger.info(Utilities.getDateTime() + 'Worker connecting to ' + self.ip)
            self.sock.connect((ip,port))
        except:
            self.logger.error('Could not connect to server ip ( ' + self.ip + ' )')
            # naspa

        self.logger.info(Utilities.getDateTime() + 'Connection was succesfull ( ' + self.ip + ' )')
        while(self.Run_Bool == True):
            while(self.Q.qsize() > 0):
                try:
                    self.sock.send(messageQueue.get())
                    messageQueue.task_done()
                except:
                    self.logger.warning('WorkerThread : init_connection(): Reconnect attempt: ' + self.reconnectCounter)
                    self.reconnectCounter = self.reconnectCounter + 1
                    time.sleep(1)
                    if(self.reconnectCounter == 5):
                        self.error('WorkerThread: Aborted connection to socket due to multiple attempts')
                        self.RunBool = False
                        self.sock.close()
            time.sleep(1)
                
            
            
                
                

        
