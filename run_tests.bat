@echo off

:: utils
echo ### test_join_url ###
python -m unittest tests/utils/test_join_url.py

echo ### test_write_gzip_to_file ###
python -m unittest tests/utils/test_write_gzip_to_file.py

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

:: diff
echo ### test_diff_parser ###
python -m unittest tests/diff/test_diff_parser.py

echo ### test_diff ###
python -m unittest tests/diff/test_diff.py