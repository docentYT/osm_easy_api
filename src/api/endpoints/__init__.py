"""Endpoints used to communicate with API. Use as follow: methods from changeset submodule -> `api.changeset`. (NOTE: changeset_discussion -> `api.changeset.discussion`. Not `api.changeset_discussion`) . Structure base on official API specification https://wiki.openstreetmap.org/wiki/API_v0.6 ."""
from .misc import Misc_Container
from .changeset import Changeset_Container
from .elements import Elements_Container
from .gpx import Gpx_Container