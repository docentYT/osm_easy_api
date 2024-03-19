"""Endpoints used to communicate with the API.

The module structure is based on the [official API specification](https://wiki.openstreetmap.org/wiki/API_v0.6).

All endpoints may throw one of the exception from `osm_easy_api.api.exceptions.STATUS_CODE_EXCEPTIONS` (unless the endpoint documentation states otherwise).
"""
from .misc import Misc_Container
from .changeset import Changeset_Container
from .elements import Elements_Container
from .gpx import Gpx_Container
from .user import User_Container
from .notes import Notes_Container