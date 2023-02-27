@echo off

:: data_classes
echo ### test_osm_object_primitive ###
python -m unittest tests/data_classes/test_osmObjectPrimitive.py

echo ### test_node ###
python -m unittest tests/data_classes/test_node.py

echo ### test_way ###
python -m unittest tests/data_classes/test_way.py

echo ### test_relation ###
python -m unittest tests/data_classes/test_relation.py

echo ### test_tags ###
python -m unittest tests/data_classes/test_tags.py

echo ### test_osmChange ###
python -m unittest tests/data_classes/test_osmChange.py

echo ### test_user ###
python -m unittest tests/data_classes/test_user.py

echo ### test_note ###
python -m unittest tests/data_classes/test_note.py