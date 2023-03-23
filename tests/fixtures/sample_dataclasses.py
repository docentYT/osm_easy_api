from copy import deepcopy

from osm_easy_api import Node, Way, Relation, Member, Tags, User

def node(key: str) -> Node:
    return deepcopy(_nodes[key])

def way(key: str) -> Way:
    return deepcopy(_ways[key])

def relation(key: str) -> Relation:
    return deepcopy(_relations[key])

def tags(key: str) -> Tags:
    return deepcopy(_tags[key])

def user(key: str) -> User:
    return deepcopy(_users[key])

_nodes: dict[str, Node] = {
    "simple_1": Node(123),
    "simple_2": Node(321),
    "full_1": Node(
            id=123,
            visible=True, 
            version=1, 
            changeset_id=321,
            timestamp="2022-11-11T21:15:26Z", 
            user_id=111,
            latitude="50.54321",
            longitude="20.12345",
            tags=Tags({"natural": "tree"})
        ),
    "full_2": Node(
            id=12345,
            visible=True, 
            version=2, 
            changeset_id=32109,
            timestamp="2022-11-11T21:15:26Z", 
            user_id=111222,
            latitude="50.12345",
            longitude="20.54321",
            tags=Tags({"building": "yes", "levels": "3"})
        )
}

_ways: dict[str, Way] = {
    "simple_1": Way(123),
    "simple_2": Way(321),
    "full_without_nodes": Way(
            id=123,
            version=1, 
            changeset_id=321,
            timestamp="2022-11-11T21:15:26Z", 
            user_id=111,
            tags=Tags({"ABC": "CBA"})
        ),
    "full_with_nodes": Way(
            id=123,
            version=1, 
            changeset_id=321,
            timestamp="2022-11-11T21:15:26Z", 
            user_id=111,
            tags=Tags({"ABC": "CBA"}),
            nodes=[_nodes["full_1"], _nodes["full_2"]]
        )
}

_relations: dict[str, Relation] = {
    "simple_1": Relation(123),
    "simple_2": Relation(321),
    "full_without_members": Relation(
            id=123,
            version=1, 
            changeset_id=321,
            timestamp="2022-11-11T21:15:26Z", 
            user_id=111,
            tags=Tags({"type": "multipolygon"})
        ),
    "full_with_members": Relation(
            id=123,
            version=1, 
            changeset_id=321,
            timestamp="2022-11-11T21:15:26Z", 
            user_id=111,
            tags=Tags({"type": "multipolygon"}),
            members=[Member(_nodes["full_1"], "role_1"), Member(_nodes["full_2"], "role_2"), Member(_ways["full_with_nodes"], "role_3")]
        )
}

_tags: dict[str, Tags] = {
    "one": Tags({"building": "yes"}),
    "two": Tags({"building": "yes", "building:levels": "3",}),
    "three": Tags({"building": "yes", "building:levels": "3", "roof:levels": "1"})
}

_users: dict[str, User] = {
    "simple_1": User(123),
    "full_1": User(
            id=123,
            display_name="abc",
            account_created_at="11:22",
            description="desc",
            contributor_terms_agreed=True,
            img_url= "test.pl",
            roles=["moderator"],
            changesets_count=4,
            traces_count=1,
            blocks={
            "received": {
            "count": 3,
            "active": 0
            },
            "issued": {
            "count": 2,
            "active": 1
            }
            }
    ),
    "full_1_without_blocks": User(
            id=123,
            display_name="abc",
            account_created_at="11:22",
            description="desc",
            contributor_terms_agreed=True,
            img_url= "test.pl",
            roles=["moderator"],
            changesets_count=4,
            traces_count=1,
            blocks=None
        )
}