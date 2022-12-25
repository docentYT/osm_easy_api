@echo off

:: diff
echo ### test_diff_parser ###
python -m unittest tests/diff/test_diff_parser.py

echo ### test_diff ###
python -m unittest tests/diff/test_diff.py