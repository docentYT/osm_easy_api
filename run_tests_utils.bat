@echo off

:: utils
echo ### test_join_url ###
python -m unittest tests/utils/test_join_url.py

echo ### test_write_gzip_to_file ###
python -m unittest tests/utils/test_write_gzip_to_file.py