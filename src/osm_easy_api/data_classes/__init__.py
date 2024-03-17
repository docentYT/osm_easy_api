"""Module containing classes for osm data.
If `user_id` is `-1`, it means that the user who created/edited/deleted the element no longer exists or that it was a historical anonymous edit."""
from .node import Node
from .way import Way
from .relation import Relation, Member
from .OsmChange import OsmChange, Action
from .tags import Tags

from .changeset import Changeset
from .user import User
from .note import Note, Comment

from .GpxFile import GpxFile, Visibility