#!/usr/bin/env python3
""" Kafka-importer for Aminer

This daemon exports data from a kafka topic and sends it via
unix domain sockets to the logdata-anomaly-miner.
"""

import sys

import os
import socket
import configparser
import logging
import logging.config
import argparse
import signal

sys.path = sys.path[1:]+['/usr/lib/akafka']
from metadata import __version_string__, __version__  # skipcq: FLK-E402
from akafka import Akafka # skipcq: FLK-E402
import ast

CONFIGFILE = '/etc/aminer/kafka.conf'
unixpath = "/var/lib/akafka/aminer.sock"
ak = None


def exitgracefully(signum, frame):
    """ Make sure that the akafka-state
        will be saved.
    """
    global ak
    ak.close()
    sys.exit(0)

def read_config():
    global CONFIGFILE
    options = dict()
    kafka_options = dict()
    config = configparser.ConfigParser()
    try:
        config.read(CONFIGFILE)
        options = dict(config.items("DEFAULT"))
        kafka_options = dict(config.items("KAFKA"))
    except:
        options['unixpath'] = unixpath
        options['topics'] = "['aminer']"
        kafka_options['bootstrap_servers'] = "localhost:9092"

    if 'KAFKA_TOPICS' in os.environ:
        options['topics'] = os.environ.get('KAFKA_TOPICS')

    if 'AKAFKA_UNIXPATH' in os.environ:
        options['unixpath'] = os.environ.get('AKAFKA_UNIXPATH')

    if 'KAFKA_BOOTSTRAP_SERVERS' in os.environ:
        kafka_options['bootstrap_servers'] = os.environ.get('KAFKA_BOOTSTRAP_SERVERS')

    if 'AKAFKA_SEARCH' in os.environ:
        options['search'] = os.environ.get('AKAFKA_SEARCH')

    return options,kafka_options


def main():
    global ak
    global unixpath
    global CONFIGFILE
    description="A daemon that polls logs from kafka-topics and writes it to a unix-domain-socket(for logdata-anomaly-miner)"

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-v', '--version', action='version', version=__version_string__)
    args = parser.parse_args()

    options,kafka_options = read_config()
    logger = False

    try:
        logging.config.fileConfig(CONFIGFILE)
    except KeyError:
        logging.basicConfig(level=logging.DEBUG)

    logger = logging.getLogger()

    for key, val in kafka_options.items():
        try:
            kafka_options[key] = int(val)
        except:
            pass

    if options.get('unixpath'):
        unixpath = options.get('unixpath')

    if os.path.exists(unixpath):
        os.remove(unixpath)

    topics = ast.literal_eval(options.get('topics'))

    logger.info("starting akafka daemon...")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(unixpath)
    ak = Akafka(*topics,**kafka_options)

    if options.get('search'):
        ak.filterlist = ast.literal_eval(options.get('search'))

    try:
        while True:
            sock.listen(1)
            logger.debug("Socket: Waiting for connection...")
            conn, addr = sock.accept()
            logger.debug("Socket-connection accepted")
            ak.setsock(conn)
            ak.run()
    except KeyboardInterrupt:
        ak.close()

if __name__=='__main__':
    signal.signal(signal.SIGINT, exitgracefully)
    signal.signal(signal.SIGTERM, exitgracefully)
    signal.signal(signal.SIGUSR1, exitgracefully)
    main()


