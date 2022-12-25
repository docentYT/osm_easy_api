@echo off

:: data_classes
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