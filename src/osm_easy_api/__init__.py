"""Python package for parsing osm diffs and communicating with the OpenStreetMap api."""
VERSION = "2.2.0"

from .data_classes import *
from .diff import Diff, Frequency

from .api import Api