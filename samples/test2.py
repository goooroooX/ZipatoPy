# ZipatoPy sample 2:
# 1) identify all virtual endpoints
# 2) find virtual endpoint by name
# 3) create new virtual endpoint
# 4) synchronize and save (you may need to wait here)
# 5) set virtual endpoint state
# 6) get virtual endpoint state
# 7) delete virtual endpoint
# 8) synchronize again

# NOTE: deleting virtual endpoint will not delete device.

USERNAME = 'username'
PASSWORD = 'password'

import os, sys
import logging
import time
from logging.handlers import RotatingFileHandler

sys.path.insert(0,'..')
from ZipatoPy import ZipatoPy

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

api.get_virtual_endpoints()
name = "Some Virtual Endpoint"
result = api.get_virt_endpoint_by_name(name)
if not result:
    LOGGER.error("Virtual endpoint not found: '%s'" % name)
else:
    LOGGER.info("%s = %s" % (name, result["uuid"]))

time.sleep(2)

data = {}
data['name']        = "My Test Virtual Sensor - %s" % str(int(time.time()))
data['category']    = "SENSOR"
uuid = api.create_virtual_endpoint(data)
if not uuid:
    LOGGER.error("Failed to create virtual endpoint!")
    sys.exit(1)
LOGGER.info("Created virtual device: %s" % uuid)

time.sleep(2)

LOGGER.info("Sync started...")
result = api.synchronize_and_save(wait="true", timeout=30)
if not result:
    LOGGER.error("Failed to sync-and-save Zipato!")
    sys.exit(1)
LOGGER.info("SYNC-SAVE: %s" % result)

time.sleep(2)

state = True
result = api.set_virtual_endpoint_state(uuid, state)
if not result:
    LOGGER.error("Failed to set endpoint state!")
    sys.exit(1)
LOGGER.info("SET state OK: %s -> transaction %s" % (state, result))

time.sleep(2)

result = api.get_virtual_endpoint_state(uuid)
if not result:
    LOGGER.error("Failed to get endpoint state!")
    sys.exit(1)
LOGGER.info("GET state OK: %s" % result)

time.sleep(2)

# NOTE: you will get empty HTTP response when deleting virtual endpoint.
# NOTE: deleting virtual endpoint will not delete device.
result = api.delete_virtual_endpoint(uuid)
LOGGER.info("Endpoint deleted: %s" % result)

time.sleep(2)

LOGGER.info("Sync started...")
result = api.synchronize_and_save(wait="true", timeout=30)
if not result:
    LOGGER.error("Failed to sync-and-save Zipato!")
    sys.exit(1)
LOGGER.info("SYNC-SAVE: %s" % result)

