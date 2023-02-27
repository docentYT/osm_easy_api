# osm-python-api
Python package for parsing osm diffs and communicating with the osm api. See API.txt for list of supported endpoints.

## What's the point of this package?
This package was created to provide an easy way to create automated scripts and programs that use diff and/or osm api. The main advantage is the classes (data_classes) that provide data of elements (node, way, relation, OsmChange, etc.) in a readable way and the possibility to use them in diff and api without worrying about missing data or dictionaries. You can easily find nodes in diff, add a tag to them and send the corrected version to osm.

# Installation
//TODO

# Documentation
You can view documentation on github-pages [URL HERE]

Documentation is build using [pdoc](https://pdoc.dev).
To run docs on your machine use preffered command: `pdoc --docformat google --no-show-source src !src.utils`.

# Examples
## DIFF
### Print trees
```py
from src import Node
from src.diff import Diff, Frequency

# Download diff from last hour.
d = Diff(Frequency.HOUR)

# Get Meta namedtuple for diff metadata and generator that parse diff file.
meta, gen = d.get(tags="natural")

# Print all created, modyfied and deleted Nodes with natural=tree tag.
for action, element in gen:
    if type(element) == Node and element.tags.get("natural") == "tree":
        print(action, element.id)
```

### Print incorrectly tagged single tress
```py
from src import Node, Action
from src.diff import Diff, Frequency

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
from src import Api, Node, Tags

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
from src.diff import Diff, Frequency

d = Diff(Frequency.DAY)

meta, gen = d.get()

for action, element in gen:
    if element.tags.get("shop") == "convenience":
        print(element)
```
```py
from src import Tags
from src.diff import Diff, Frequency

d = Diff(Frequency.DAY)

meta, gen = d.get(tags=Tags({"shop": "convenience"}))

for action, element in gen:
        print(element)
```
but the second seems to be faster.

Also you can use OsmChange object if you don't want to use generator
```py
from src import Node, Action
from src.diff import Diff, Frequency

d = Diff(Frequency.MINUTE)

osmChange = d.get(generator=False)

deleted_nodes = osmChange.get(Node, Action.DELETE)
for node in deleted_nodes:
    print(node.id)
```
but it can consume large amounts of ram and use of this method is not recommended for large diff's.

# Tests
You will need to install requirements: `install_test_depediences.bat`. To test API module you will need `.env` file with `LOGIN` and `PASSWORD` field.
To run tests use `run_tests_<module>.bat`.