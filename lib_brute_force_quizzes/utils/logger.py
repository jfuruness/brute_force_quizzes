#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module used to contains helpful logging functions"""

__author__ = "Justin Furuness"
__credits__ = ["Justin Furuness"]
__Lisence__ = "BSD"
__maintainer__ = "Justin Furuness"
__email__ = "jfuruness@gmail.com"
__status__ = "Development"

from datetime import datetime
import logging
import os

def config_logging(level=logging.INFO):
    """Configures logging to log to a file"""

    # Makes log path and returns it
    if len(logging.root.handlers) != 1:
        logging.root.handlers = []
        logging.basicConfig(level=level,
                            format='%(asctime)s-%(levelname)s: %(message)s',
                            handlers=[
                                      logging.StreamHandler()])

        logging.captureWarnings(True)
