import unittest
import gzip
import os
from ..fixtures.compare_files import _compare_files

from osm_easy_api.utils import write_gzip_to_file

class TestMiscWriteGzipToFile(unittest.TestCase):
    def test_write(self):
        f_from_path = os.path.join("tests", "fixtures", "hour.xml.gz")
        f_to_path = os.path.join("tests", "fixtures", "write_gzip_to_file_to.xml.gz")
        f_from = gzip.GzipFile(f_from_path)
        
        write_gzip_to_file(f_from, f_to_path)

        self.assertTrue(_compare_files(f_from_path, f_to_path))
        os.remove(f_to_path)