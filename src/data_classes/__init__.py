"""Module containing classes for osm data."""
from .node import Node
from .way import Way
from .relation import Relation
from .OsmChange import OsmChange, Action
from .tags import Tags

from .changeset import Changeset
from .user import User