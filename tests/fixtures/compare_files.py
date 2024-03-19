import gzip
from xml.etree import ElementTree   

def _compare_files(first_path, second_path):
        """Compare two files and returns False if files don't have similar content. Otherwise returns True."""
        def _parse_file(file):
            for e, i in ElementTree.iterparse(file):
                yield i

        first = gzip.GzipFile(first_path)
        second = gzip.GzipFile(second_path)

        one = _parse_file(first)
        two = _parse_file(second)
        for i in one:
            n = next(two)
            if i.tag != n.tag or i.attrib != n.attrib: 
                first.close()
                second.close()
                return False
        first.close()
        second.close()
        return True