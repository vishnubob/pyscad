from primitives import *
from core import *
from utils import *
from color import *
from vector import *
from geometry import *
from threads import *

import logging

def configure_logger(name=None, debug=False):
    global logger
    name = name or __name__
    logger = logging.getLogger(name)
    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    datefmt='%c'
    formatter = logging.Formatter("[%(asctime)s %(name)s] %(message)s",  datefmt=datefmt)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

configure_logger(__name__)
