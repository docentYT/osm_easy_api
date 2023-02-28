import unittest
import responses
import os

import osm_easy_api.diff as diff


class TestDiff(unittest.TestCase):
    @responses.activate
    def test_diff__get_state(self):
        body = "#Sat Nov 12 14:22:10 UTC 2022\nsequenceNumber=5315422\ntimestamp=2022-11-12T14\\:22\\:07Z"
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/minute/state.txt",
            "body": body,
            "status": 200
        })

        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/hour/state.txt",
            "body": body,
            "status": 404
        })

        d = diff.Diff(diff.Frequency.MINUTE, "https://test.pl")
        self.assertEqual(d._get_state(), body)
        
        d = diff.Diff(diff.Frequency.HOUR, "https://test.pl")
        self.assertRaises(ValueError, d._get_state)

    def test_diff__get_sequence_number_from_state(self):
        # With new line
        sequence_number = "5315422\n"
        sequence_number_expected = "5315422"
        body = f"#Sat Nov 12 14:22:10 UTC 2022\nsequenceNumber={sequence_number}timestamp=2022-11-12T14\\:22\\:07Z"
        d = diff.Diff(diff.Frequency.MINUTE, "https://test.pl")
        self.assertEqual(d._get_sequence_number_from_state(body), sequence_number_expected)

        # Without new line
        sequence_number = "5315422"
        sequence_number_expected = "5315422"
        body = f"#Sat Nov 12 14:22:10 UTC 2022\nsequenceNumber={sequence_number}timestamp=2022-11-12T14\\:22\\:07Z"
        d = diff.Diff(diff.Frequency.MINUTE, "https://test.pl")
        self.assertEqual(d._get_sequence_number_from_state(body), sequence_number_expected)

    @responses.activate
    def test_diff_get_sequence_number(self):
        sequence_number = "5315422\n"
        sequence_number_expected = "5315422"
        body = f"#Sat Nov 12 14:22:10 UTC 2022\nsequenceNumber={sequence_number}timestamp=2022-11-12T14\\:22\\:07Z"
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/minute/state.txt",
            "body": body,
            "status": 200
        })

        d = diff.Diff(diff.Frequency.MINUTE, "https://test.pl")
        self.assertEqual(d.get_sequence_number(), sequence_number_expected)

    def test_diff__build_url(self):
        d = diff.Diff(diff.Frequency.MINUTE, "https://test.pl")
        self.assertEqual(d._build_url(d.url, d.frequency, "5"), "https://test.pl/minute/000/000/005.osc.gz")
        self.assertEqual(d._build_url(d.url, d.frequency, "53"), "https://test.pl/minute/000/000/053.osc.gz")
        self.assertEqual(d._build_url(d.url, d.frequency, "531"), "https://test.pl/minute/000/000/531.osc.gz")
        self.assertEqual(d._build_url(d.url, d.frequency, "5315"), "https://test.pl/minute/000/005/315.osc.gz")
        self.assertEqual(d._build_url(d.url, d.frequency, "53154"), "https://test.pl/minute/000/053/154.osc.gz")
        self.assertEqual(d._build_url(d.url, d.frequency, "531542"), "https://test.pl/minute/000/531/542.osc.gz")
        self.assertEqual(d._build_url(d.url, d.frequency, "5315422"), "https://test.pl/minute/005/315/422.osc.gz")
        self.assertEqual(d._build_url(d.url, d.frequency, "53154221"), "https://test.pl/minute/053/154/221.osc.gz")
        self.assertEqual(d._build_url(d.url, d.frequency, "531542219"), "https://test.pl/minute/531/542/219.osc.gz")

    @responses.activate
    def test_diff_get_generator(self):
        sequence_number = "5315422"
        body = open(os.path.join("tests", "fixtures", "hour.xml.gz"), "rb")
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/minute/state.txt",
            "body": sequence_number,
            "status": 200
        })
        
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/minute/005/315/422.osc.gz",
            "body": body,
            "status": 200
        })

        d = diff.Diff(diff.Frequency.MINUTE, "https://test.pl")
        meta, gen = d.get(sequence_number=sequence_number)
        act, element = next(gen)
        self.assertEqual(meta.sequence_number, sequence_number)
        self.assertEqual(element.id, 4222078)

    @responses.activate
    def test_diff_get(self):
        sequence_number = "5315422"
        body = open(os.path.join("tests", "fixtures", "hour.xml.gz"), "rb")
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/minute/state.txt",
            "body": sequence_number,
            "status": 200
        })
        
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/minute/005/315/422.osc.gz",
            "body": body,
            "status": 200
        })

        d = diff.Diff(diff.Frequency.MINUTE, "https://test.pl")
        osmChange = d.get(sequence_number=sequence_number, generator=False)

        should_print = f"OsmChange(version=0.6, generator=Osmosis 0.47.4, sequence_number={sequence_number}. Node: Create(2), Modify(14), Delete(1), None(0). Way: Create(0), Modify(1), Delete(0), None(0). Relation: Create(1), Modify(0), Delete(0), None(0)."
        self.assertEqual(str(osmChange), should_print)