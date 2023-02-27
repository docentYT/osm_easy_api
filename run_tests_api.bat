@echo off

echo ### test_api ###
python -m unittest tests/api/test_api.py

echo ### test_api_misc ###
python -m unittest tests/api/test_api_misc.py

echo ### test_api_changeset ###
python -m unittest tests/api/test_api_changeset.py

echo ### test_api_changeset_discussion ###
python -m unittest tests/api/test_api_changeset_discussion.py

echo ### test_api_elements ###
python -m unittest tests/api/test_api_elements.py

echo ### test_api_user ###
python -m unittest tests/api/test_api_user.py

echo ### test_api_notes ###
python -m unittest tests/api/test_api_notes.py