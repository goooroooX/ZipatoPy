#!/usr/bin/python
# -*- coding: utf-8 -*-
#################################################
#                Zipato Python API              #
#            author: Dmitry Nikolaenya          #
#            https://github.com/goooroooX       #
#               https://gooorooo.com            #
#################################################

__version__ = "0.1"

# "No handler found" warnings suppress, Python 2.7+
import logging

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())

from ZipatoPy import ZipatoPy
