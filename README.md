# osm_easy_api

![Tests](https://github.com/docentYT/automated-python-tests-testing-repo/actions/workflows/tests.yaml/badge.svg)
![coverage](https://raw.githubusercontent.com/docentYT/osm_easy_api/3889ae626be35183253485646b7be9e235a2fc27/coverage-badge.svg)
[![PyPI version](https://badge.fury.io/py/osm_easy_api.svg)](https://badge.fury.io/py/osm_easy_api)

[Me on openstreetmap](https://www.openstreetmap.org/user/kwiatek_123)

Python package for parsing osm diffs and communicating with the osm api. See API.txt for list of supported endpoints.

## What's the point of this package?

This package was created to provide an easy way to create automated scripts and programs that use diff and/or osm api. The main advantage is the classes (data_classes) that provide data of elements (node, way, relation, OsmChange, etc.) in a readable way and the possibility to use them in diff and api without worrying about missing data or dictionaries. You can easily find nodes in diff, add a tag to them and send the corrected version to osm.

## What next?
The plan is to optimise and improve the code, add support for gpx traces, rss support and overpass api.

# Installation

Works on python >= 3.10. (Due to new typehints standard)

Install `osm_easy_api` from [PyPi](https://pypi.org/project/osm-easy-api/):
```
pip install osm_easy_api
``` 

# Documentation

You can view documentation on [github-pages](https://docentyt.github.io/osm_easy_api/osm_easy_api.html).

Documentation is build using [pdoc](https://pdoc.dev).
To run docs on your machine use preferred command: `pdoc --docformat google --no-show-source osm_easy_api !osm_easy_api.utils`.

# Examples

## DIFF

### Print trees

```py
from osm_easy_api import Node, Diff, Frequency

# Download diff from last hour.
d = Diff(Frequency.HOUR)

# Get Meta namedtuple for diff metadata and generator that parse diff file.
meta, gen = d.get(tags="natural")

# Print all created, modified and deleted Nodes with natural=tree tag.
for action, element in gen:
    if type(element) == Node and element.tags.get("natural") == "tree":
        print(action, element.id)
```

### Print incorrectly tagged single tress

```py
from osm_easy_api import Diff, Frequency, Action, Node

d = Diff(Frequency.DAY)

meta, gen = d.get(tags="natural")

for action, element in gen:
    if type(element) == Node:
        if action == Action.CREATE or action == Action.MODIFY:
            if element.tags.get("natural") == "wood":
                print(element)
```
Example output:
```
Node(id = 10208486717, visible = None, version = 1, changeset_id = 129216075, timestamp = 2022-11-22T00:16:44Z, user_id = 17471721, tags = {'leaf_type': 'broadleaved', 'natural': 'wood'}, latitude = 48.6522286, longitude = 12.583809, )
```

## API

### Add missing wikidata tag

```py
from osm_easy_api import Api, Node, Tags

api = Api("https://master.apis.dev.openstreetmap.org", LOGIN, PASSWORD)

node = api.elements.get(Node, 4296460336) # We are getting Node with id 4296460336 where we want to add a new tag to
node.tags.add("wikidata", "Qexample") # Add a new tag to node.

my_changeset = api.changeset.create("Add missing wikidata tag", Tags({"automatic": "yes"})) # Create new changeset with description and tag
api.elements.update(node, my_changeset) # Send new version of a node to osm
api.changeset.close(my_changeset) # Close changeset.
```

# Notes

Note that the following codes do the same thing
```py
from osm_easy_api import Diff, Frequency

d = Diff(Frequency.DAY)

meta, gen = d.get()

for action, element in gen:
    if element.tags.get("shop") == "convenience":
        print(element)
```
```py
from osm_easy_api import Diff, Frequency, Tags

d = Diff(Frequency.DAY)

meta, gen = d.get(tags=Tags({"shop": "convenience"}))

for action, element in gen:
        print(element)
```
but the second seems to be faster.

Also you can use OsmChange object if you don't want to use generator
```py
from osm_easy_api import Diff, Frequency, Action, Node

d = Diff(Frequency.MINUTE)

osmChange = d.get(generator=False)

deleted_nodes = osmChange.get(Node, Action.DELETE)
for node in deleted_nodes:
    print(node.id)
```
but it can consume large amounts of ram and use of this method is not recommended for large diff's.

# Tests

You will need to install `test-requirements.txt`. You can use tox.
To run tests manually use `python -m unittest discover`.