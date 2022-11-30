from src import Node, Action
from src.diff import Diff, Frequency

d = Diff(Frequency.MINUTE)

osmChange = d.get(generator=False)

deleted_nodes = osmChange.get(Node, Action.DELETE)
for node in deleted_nodes:
    print(node.id)