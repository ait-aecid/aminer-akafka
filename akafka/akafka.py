"""A Aminer-Kafka importer

This module reads data from a kafka topic and forwards it 
to a unix-domain socket

"""

import threading
import logging
import json
import copy
import re
import ast
import datetime
from kafka import KafkaConsumer
from dictfilter import query

class Akafka:
    DEFAULT_CONFIG = {
        'bootstrap_servers': 'localhost:9092',
    }

    def __init__(self, *topics, **configs):
        self.config = copy.copy(self.DEFAULT_CONFIG)
        self.timer = None
        self.stopper = False
        self.sort = None
        self.sock = None
        self.use_state = False
        self.topics = topics
        self.searchlist = None
        self.filters = False
        self.filters_delim = '.'

        self.logger = logging.getLogger(__name__)

        for key in self.config:
            if key in configs:
                self.config[key] = configs[key]

        self.consumer = None
        if self.use_state is True:
            self.loadstate()
        self.logger.debug(self.sort)

    def setfilter(self, filters):
        if isinstance(filters, str):
            self.filters = ast.literal_eval(filters)
            if not isinstance(self.filters, list):
                self.logger.info("Warning: conf-parameter filters is not a list!")
                self.filters = None

    def displayfilter(self,hit):
        try:
            json_hit = json.loads(hit)
        except json.decoder.JSONDecodeError:
            self.logger.debug("displayfilter: %s" % hit)
            return hit

        if self.filters is False:
            self.logger.debug("displayfilter with filters is FALSE: %s" % hit)
            return hit
        else:
            ret = {}
            ret = query(json_hit, self.filters, delimiter=self.filters_delim)
            if ret:
                return json.dumps(ret).encode("ascii")
            else:
                return False

    def setlogger(self, logger):
        """Define a logger for this module
        """
        self.logger = logger

    def search(self, value):
        if isinstance(self.searchlist, list):
            for f in self.searchlist:
                if re.findall(f, str(value)):
                    return True
            return False
        else:
            return True

    def handler(self):
        """Scheduler-function that polls kafka

        """
        self.consumer = KafkaConsumer(**self.config)
        self.consumer.subscribe(self.topics)
        try:
            self.sock.send('\n'.encode())
            for msg in self.consumer:
                if self.search(msg.value) is True:
                   self.logger.debug(msg.value)
                   data = self.displayfilter(msg.value)
                   if data:
                       self.logger.debug("Sending data: %s" % data)
                       self.sock.send(data)
                       self.sock.send('\n'.encode())
        except OSError:       
            self.logger.error("Client disconnected", exc_info=False)
            self.stopper = True

            

    def setsock(self, sock):
        """Setter for the unix-socket
        """
        self.sock = sock

    def savestate(self):
        """Save the search-state so that the search
           starts from the last looked up element
        """
        if self.use_state == 'True':
            try:
                filehandle = open(self.config['statefile'], 'w')
                json.dump(self.sort, filehandle)
                filehandle.close()
            except (IOError, json.JSONDecodeError):
                self.logger.error("Could not save state", exc_info=False)

    def loadstate(self):
        """Load the state and start from the last
           looked up element
        """
        try:
            filehandle = open(self.config['statefile'], 'r')
            self.sort = json.load(filehandle)
            if self.sort is not None:
                self.logger.debug("Statefile loaded with timestamp: %s",
                                  datetime.fromtimestamp(self.sort[0] / 1000))
            filehandle.close()
        except (IOError, json.JSONDecodeError):
            self.logger.error("Could not load state", exc_info=False)

    def run(self):
        """Starts the scheduler
        """
        try:
            self.stopper = False
            while self.stopper is False:
                self.logger.debug("Starting another run..")
                self.handler()
        except KeyboardInterrupt:
            self.logger.debug("KeyboardInterrupt detected...")
            self.stopper = True
        finally:
            self.close()

    def close(self):
        """Stops the socket and the scheduler
        """
        self.logger.debug("Cleaning up socket and scheduler")
        self.consumer.unsubscribe()
        self.stopper = True
        if self.sock is not None:
            self.logger.debug("Closing socket...")
            self.sock.close()
        if self.use_state is True:
            self.savestate()
