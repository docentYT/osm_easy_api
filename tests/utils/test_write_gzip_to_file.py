import unittest
import gzip
import os
from xml.etree import ElementTree

from src.utils import write_gzip_to_file

class TestMiscWriteGzipToFile(unittest.TestCase):
    def _parse_file(self, file):
        for e, i in ElementTree.iterparse(file):
            yield i

    def _compare_files(self, first_path, second_path):
        """Compare two files and returns False if files don't have similar content. Otherwise returns True."""
        first = gzip.GzipFile(first_path)
        second = gzip.GzipFile(second_path)

        one = self._parse_file(first)
        two = self._parse_file(second)
        for i in one:
            n = next(two)
            if i.tag != n.tag or i.attrib != n.attrib: 
                first.close()
                second.close()
                return False
        first.close()
        second.close()
        return True

    def test_write(self):
        f_from_path = os.path.join("tests", "fixtures", "hour.xml.gz")
        f_to_path = os.path.join("tests", "fixtures", "write_gzip_to_file_to.xml.gz")
        f_from = gzip.GzipFile(f_from_path)
        
        write_gzip_to_file(f_from, f_to_path)

        self.assertTrue(self._compare_files(f_from_path, f_to_path))
        os.remove(f_to_path)