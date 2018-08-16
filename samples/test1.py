#!/usr/bin/python
# -*- coding: utf-8 -*-

# ZipatoPy sample 1:
# 1) identify all devices
# 2) find endpoints for specific device
# 3) get attributes for required endpoint
# 4) request value(s) for specific attribute
# 5) request history log for specific attribute

USERNAME  = 'someuser'
PASSWORD  = 'somepass'
DEVICE    = "Power Plug Server"
ENDPOINT  = "Server Room Plug"
ATTRIBUTE = "CURRENT_CONSUMPTION"
LOCAL     = "http://X.X.X.X:8080/zipato-web/v2/"
LOCAL_ATTR= "c562946b-4759-494c-9234-5b74376fdc9e"

import os, sys
import logging
from logging.handlers import RotatingFileHandler

sys.path.insert(0,'..')
from zipatopy import ZipatoPy

if getattr(sys, 'frozen', False):
    root_folder = os.path.dirname(os.path.abspath(sys.executable))
else:
    root_folder = os.path.dirname(os.path.abspath(__file__))

def my_logger(LOG_FILENAME):
    FORMAT_FILE = '%(asctime)-15s %(levelname)-8s : %(message)s'
    FORMAT_CLI = '%(asctime)-8s %(levelname)-8s %(message)s'
    MAX_BYTES = 3 * 1024 * 1024
    BACKUP_COUNT = 10
    logger = logging.getLogger()
    # logging to file
    fileFormatter = logging.Formatter(FORMAT_FILE)
    fileHandler = logging.handlers.RotatingFileHandler(os.path.abspath(os.path.join(root_folder, LOG_FILENAME)), maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT)
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(fileFormatter)
    logger.addHandler(fileHandler)
    # logging to console
    consoleFormatter = logging.Formatter(FORMAT_CLI, '%H:%M:%S')
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(consoleFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.DEBUG)
    return logger

LOGGER = my_logger("zipato.log")

api = ZipatoPy(USERNAME, PASSWORD, verbose=True)

api.get_devices()
device = api.get_device_by_name(DEVICE)
if device:
    endpoints = api.get_device_endpoints(device)
    if endpoints:
        for endpoint in endpoints:
            if endpoint["name"] == ENDPOINT:
                attributes = api.get_endpoint_attributes(endpoint)
                if attributes:
                    for item in attributes:
                        # NOTE: local API does not return 'name'
                        if not "name" in item:
                            LOGGER.error("Attribute name is not available for local API. Use UUID to get value.")
                            LOGGER.info(api.get_attribute_value(LOCAL_ATTR))
                            sys.exit(1)
                        if item["name"] == ATTRIBUTE:
                            attribute_uuid = item["uuid"]
                            if attribute_uuid:
                                # get last attribure value
                                LOGGER.info(api.get_attribute_value(attribute_uuid))
                                # get history of attribute values
                                LOGGER.info(api.get_attribute_log(attribute_uuid))
