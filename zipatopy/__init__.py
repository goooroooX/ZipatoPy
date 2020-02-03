#################################################
#                Zipato Python API              #
#            author: Dmitry Nikolaenya          #
#            https://github.com/goooroooX       #
#               https://gooorooo.com            #
#################################################

# Copyright 2019 Dmitry Nikolaenya
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__version__ = "0.4"

# "No handler found" warnings suppress, Python 2.7+
import logging

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())

import sys
import traceback
import json
import ssl
import hashlib
import re

try:
    from urllib2 import Request, HTTPError, urlopen
except ImportError:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError

try:
    from urllib import quote, quote_plus
except ImportError:
    from urllib.parse import quote, quote_plus

try:
    from urlparse import urlsplit, urlunsplit
except ImportError:
    from urllib.parse import urlsplit, urlunsplit

LOGGER = logging.getLogger(__name__)

class BaseAPIClient(object):

    def __init__(self, username, password, url = None, verbose = False):
        self.local_mode = False
        if not url:
            self.url = "https://my.zipato.com:443/zipato-web/v2/"
        else:
            self.url = url
            self.local_mode = True
        self.verbose = verbose
        self.username = username
        self.password = password
        LOGGER.info("ZipatoPy initialization for %s @ %s" % (self.username, self.url))
        self.headers    = None
        init_data       = self.user_init()
        self.nonce      = init_data['nonce']
        self.jsessionid = init_data['jsessionid']
        self.token      = self.get_token()

        self.headers = {'Accept'        : 'application/json',
                        'Content-Type'  : 'application/json; charset=UTF-8',
                        'Cookie'        : 'JSESSIONID=%s' % self.jsessionid
                        }
        self.login      = self.user_login()
        if self.login:
            LOGGER.info("ZipatoPy initialization success.")
        else:
            LOGGER.error("Initialization failed!")
            sys.exit(1)

        # initialize internal data structures
        self.devices            = None
        self.virtual_endpoints  = None

    def get_token(self):
        hash_password   = hashlib.sha1(self.password.encode('utf-8'))
        hex_password    = hash_password.hexdigest()
        combined        = self.nonce + hex_password
        hash_token      = hashlib.sha1(combined.encode('utf-8'))
        return hash_token.hexdigest()

    def user_init(self):
        endpoint = "user/init"
        return self.call_api(endpoint, "GET")

    def user_login(self):
        if not self.token:
            LOGGER.error("No hex token, unable to login.")
            return None
        endpoint = "user/login?username=" + self.username + "&token=" + self.token + "&method=SHA1"
        return self.call_api(endpoint, "GET")

    def call_api(self, endpoint, method, headers=None, params=None, data=None):
        path = self.parse_path(endpoint, params)
        if data:
            data = json.dumps(data).encode('utf8')
            if self.verbose:
                LOGGER.debug("   >> URL data: %s" % data)
        if self.headers:
            actual_headers = self.headers.copy()
        else:
            actual_headers = None
        if headers is not None:
            for header_key in headers:
                actual_headers[header_key] = headers[header_key]

        # handle direct links
        if path.startswith("http"):
            request_string = path
        else:
            request_string = self.url + path

        if self.verbose:
            LOGGER.debug("   >> URL request: %s" % request_string)
            LOGGER.debug("   >> URL headers: %s" % actual_headers)

        if " " in request_string:
            request_string = self.url_fix(request_string)
            LOGGER.debug("   >> Fixed URL: %s" % request_string)
        if actual_headers:
            request = Request(request_string, headers=actual_headers)
        else:
            request = Request(request_string)
        request.get_method = lambda: method

        if sys.version_info >= (2, 7, 5):
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        else:
            ctx = None
        try:
            if ctx:
                result_raw = urlopen(request, data=data, context=ctx)
            else:
                result_raw = urlopen(request, data=data)

            output = result_raw.read()
            if not output:
                LOGGER.warning("Empty HTTP response!")
                return None
            try:
                result = json.loads(output)
            except:
                LOGGER.error("Failed to interpret JSON data: %s" % traceback.format_exc())
                LOGGER.error("Raw result: %s" % output)
                return None
            else:
                if "success" in result:
                    if result["success"] == False:
                        LOGGER.error("API call failed: %s" % result["error"])
                        return None
                if self.verbose:
                    LOGGER.debug("   >> API call result: %s" % result)
                return result

        except HTTPError as e:
            LOGGER.error(e)
            if self.verbose:
                LOGGER.debug("HTTP Error details: %s" % e.info())
            return None

    @staticmethod
    def url_fix(s, charset='utf-8'):
        if isinstance(s, unicode):
            s = s.encode(charset, 'ignore')
        scheme, netloc, path, qs, anchor = urlsplit(s)
        path = quote(path, '/%')
        qs = quote_plus(qs, ':&=')
        return urlunsplit((scheme, netloc, path, qs, anchor))

    @staticmethod
    def parse_path(endpoint, params):
        if not params:
            params = {}
        path = endpoint + '?'
        if isinstance(params, list):
            for kv in params:
                if kv[1]:
                    path += kv[0] + '=' + quote(kv[1]) + '&'
        else:
            for k, v in params.items():
                if params[k]:
                    path += k + '=' + quote(v) + '&'
        # removes last '&' or hanging '?' if no params.
        return path[:len(path) - 1]

    @staticmethod
    def debug_json(json_data):
        formatted = json.dumps(json_data, indent=2, separators=(',', ':'))
        LOGGER.info("   >> JSON output: %s" % formatted)

class ZipatoPy(BaseAPIClient):

    def check_local(self):
        return self.local_mode

    def get_devices(self):
        # endpoint returns a list of dictionaries
        endpoint = "devices"
        self.devices = self.call_api(endpoint, "GET")
        return self.devices

    def get_device_status(self, uuid):
        endpoint = "devices/" + uuid + "/status"
        return self.call_api(endpoint, "GET")

    def get_device_config(self, uuid):
        endpoint = "devices/" + uuid + "/config"
        return self.call_api(endpoint, "GET")

    def get_device_by_name(self, device_name):
        # return first device found with specific name
        # there can be several devices with the same name
        if not self.devices:
            LOGGER.error("Device list not initialized. Please use get_devices() first.")
            return None
        else:
            for device in self.devices:
                if device_name == device["name"]:
                    return device
        return None

    def get_device_endpoints(self, device):
        if not "uuid" in device:
            LOGGER.error("UUID is missed in device data structure: '%s'." % device)
            return None
        else:
            uuid = device["uuid"]
            endpoint = "devices/" + uuid + "/endpoints"
            return self.call_api(endpoint, "GET")

    def get_endpoint_content(self, endpoint):
        if not "uuid" in endpoint:
            LOGGER.error("UUID is missed in endpoint data structure: '%s'." % endpoint)
            return None
        else:
            uuid = endpoint["uuid"]
            endpoint = "endpoints/" + uuid
            return self.call_api(endpoint, "GET")

    def get_endpoint_attributes(self, endpoint):
        if not "uuid" in endpoint:
            LOGGER.error("UUID is missed in endpoint data structure: '%s'." % endpoint)
            return None
        else:
            uuid = endpoint["uuid"]
            endpoint = "endpoints/" + uuid + "?attributes=true"
            result = self.call_api(endpoint, "GET")
            if not "attributes" in result:
                LOGGER.error("Failed to get attributes for endpoint '%s'." % uuid)
                return None
            else:
                return result["attributes"]

    def get_attribute_value(self, uuid):
        endpoint = "attributes/" + uuid + "/value"
        return self.call_api(endpoint, "GET")

    def get_attribute_log(self, uuid, count=100, order="desc"):
        endpoint = "log/attribute/" + uuid + "?count=%s&order=%s" % (count, order)
        result = self.call_api(endpoint, "GET")
        if not "values" in result:
            LOGGER.error(("Failed to get values log for endpoint '%s'." % uuid))
            return None
        else:
            return result["values"]

    def get_virtual_endpoints(self):
        endpoint = "virtualEndpoints"
        self.virtual_endpoints = self.call_api(endpoint, "GET")
        return self.virtual_endpoints

    def get_virt_endpoint_by_name(self, endpoint_name):
        # return first endpoint found with specific name
        if not self.virtual_endpoints:
            LOGGER.error("Virtual endpoints list not initialized. Please use get_virtual_endpoints() first.")
            return None
        else:
            for endpoint in self.virtual_endpoints:
                if endpoint_name == endpoint["name"]:
                    return endpoint
        return None

    def create_virtual_endpoint(self, data):
        supported_categories = \
             ["SENSOR",
              "METER",
              "GAUGE",
              "ONOFF",
              "LEVEL_CONTROL"]
        if not "category" in data:
            LOGGER.error("Failed to create virtual endpoint: no category provided in data: %s" % data)
            return None
        category = data["category"]
        if not category in supported_categories:
            LOGGER.error("Failed to create virtual endpoint: unsupported category '%s'." % category)
            return None

        endpoint = "virtualEndpoints/?category=" + category
        result = self.call_api(endpoint, "POST", data=data)
        if not result:
            LOGGER.error("Failed to get virtualEndpoints!")
            return None
        if not "uuid" in result:
            LOGGER.error("Failed to create virtual endpoint: no UUID defined in POST results: %s" % result)
            return None
        return result["uuid"]

    def get_virtual_endpoint_config(self, uuid):
        endpoint = "virtualEndpoints/" + uuid + "/config"
        return self.call_api(endpoint, "GET")

    def get_virtual_endpoint_value(self, uuid):
        endpoint = "virtualEndpoints/" + uuid
        return self.call_api(endpoint, "GET")

    def get_virtual_endpoint_state(self, uuid):
        ve = self.get_virtual_endpoint_value(uuid)
        try:
            state_attribute_uuid = ve["attributeUrls"][0]["uuid"]
        except:
            LOGGER.error("Failed to get virtual endpoint state UUID.")
            self.debug_json(ve)
            return None
        result = self.get_attribute_value(state_attribute_uuid)
        if not result:
            LOGGER.error("Failed to get responce from attribute!")
            return None
        if not "value" in result:
            LOGGER.error("Failed to get virtual endpoint state.")
            return None
        return result["value"]

    def set_virtual_endpoint_state(self, uuid, state):
        if not isinstance(state, bool):
            LOGGER.error("Invalid state for virtual endpoint (should be boolean): '%s'" % state)
            return None

        if state == True:
            state_str = "1"
        else:
            state_str = "0"
        ve = self.get_virtual_endpoint_value(uuid)
        try:
            endpoint = ve["attributeUrls"][0]["url"]
        except:
            LOGGER.error("Failed to get virtual endpoint URL.")
            self.debug_json(ve)
            return None
        endpoint = endpoint + state_str
        return self.call_api(endpoint, "GET")

    def delete_virtual_endpoint(self, uuid):
        # NOTE: deleting virtual endpoint will not delete device.
        endpoint = "virtualEndpoints/" + uuid
        return self.call_api(endpoint, "DELETE")

    def set_attributes_config(self, uuid, data):
        endpoint = "attributes/" + uuid + "/config"
        return self.call_api(endpoint, "PUT", data=data)

    def set_attributes_value(self, uuid, data):
        endpoint = "attributes/" + uuid + "/value"
        return self.call_api(endpoint, "PUT", data=data)

    def synchronize_and_save(self, wait="false", timeout=30):
        endpoint = "box/saveAndSynchronize?wait=" + wait + "&timeout=" + str(timeout)
        result = self.call_api(endpoint, "GET")
        if not result:
            LOGGER.error("Failed to save and synchronize.")
            return None
        if not "transactionId" in result:
            LOGGER.warning("'transactionId' not defined when performing 'sync-and-save'.")
            return None
        return result["transactionId"]

    def synchronize_only(self, ifneeded="false", wait="false", timeout=30):
        endpoint = "box/synchronize?ifNeeded=" + ifneeded + "&wait=" + wait + "&timeout=" + str(timeout)
        result = self.call_api(endpoint, "GET")
        if not result:
            LOGGER.error("Failed to synchronize.")
            return None
        if not "transactionId" in result:
            LOGGER.warning("'transactionId' not defined when performing 'sync-only'.")
            return None
        return result["transactionId"]

