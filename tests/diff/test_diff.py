import unittest
import responses
import os

from osm_easy_api.diff import Diff, Frequency
from osm_easy_api.data_classes import OsmChange, Node, Way, Relation, Action


class TestDiff(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.SEQUENCE_NUMBER = "5315422"
        cls.SEQUENCE_NUMBER_NEW_LINE = "5315422\n"

    @responses.activate
    def test_diff__get_state(self):
        URL_MINUTE = "https://test.pl/minute/state.txt"
        URL_HOUR = "https://test.pl/hour/state.txt"
        URL_DAY = "https://test.pl/day/state.txt"
        BODY = "#Sat Nov 12 14:22:10 UTC 2022\nsequenceNumber=5315422\ntimestamp=2022-11-12T14\\:22\\:07Z"
        DIFF = Diff(Frequency.MINUTE, "https://test.pl")

        def addResponse(url: str, body: str, status_code: int):
            responses.add(**{
                "method": responses.GET,
                "url": url,
                "body": body,
                "status": status_code
            })

        # 200
        addResponse(URL_MINUTE, BODY, 200)
        DIFF.frequency = Frequency.MINUTE
        self.assertEqual(DIFF._get_state(), BODY)
        self.assertTrue(responses.assert_call_count(URL_MINUTE, 1))

        addResponse(URL_HOUR, BODY, 200)
        DIFF.frequency = Frequency.HOUR
        self.assertEqual(DIFF._get_state(), BODY)
        self.assertTrue(responses.assert_call_count(URL_HOUR, 1))

        addResponse(URL_DAY, BODY, 200)
        DIFF.frequency = Frequency.DAY
        self.assertEqual(DIFF._get_state(), BODY)
        self.assertTrue(responses.assert_call_count(URL_DAY, 1))

        # 404 ValueError
        addResponse(URL_MINUTE, BODY, 404)
        DIFF.frequency = Frequency.MINUTE
        self.assertRaises(ValueError, DIFF._get_state)
        self.assertTrue(responses.assert_call_count(URL_MINUTE, 2))

        addResponse(URL_HOUR, BODY, 404)
        DIFF.frequency = Frequency.HOUR
        self.assertRaises(ValueError, DIFF._get_state)
        self.assertTrue(responses.assert_call_count(URL_HOUR, 2))

        addResponse(URL_DAY, BODY, 404)
        DIFF.frequency = Frequency.DAY
        self.assertRaises(ValueError, DIFF._get_state)
        self.assertTrue(responses.assert_call_count(URL_DAY, 2))

    def test_diff__get_sequence_number_from_state(self):
        BODY = "#Sat Nov 12 14:22:10 UTC 2022\nsequenceNumber={sequence_number}timestamp=2022-11-12T14\\:22\\:07Z"
        DIFF = Diff(Frequency.MINUTE, "https://test.pl")

        self.assertEqual(DIFF._get_sequence_number_from_state(BODY.format(sequence_number=self.SEQUENCE_NUMBER)), self.SEQUENCE_NUMBER)
        self.assertEqual(DIFF._get_sequence_number_from_state(BODY.format(sequence_number=self.SEQUENCE_NUMBER_NEW_LINE)), self.SEQUENCE_NUMBER)

    @responses.activate
    def test_diff_get_sequence_number(self):
        BODY = f"#Sat Nov 12 14:22:10 UTC 2022\nsequenceNumber={self.SEQUENCE_NUMBER_NEW_LINE}timestamp=2022-11-12T14\\:22\\:07Z"
        DIFF = Diff(Frequency.MINUTE, "https://test.pl")
        
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/minute/state.txt",
            "body": BODY,
            "status": 200
        })

        self.assertEqual(DIFF.get_sequence_number(), self.SEQUENCE_NUMBER)

    def test_diff__build_url(self):
        DIFF = Diff(Frequency.MINUTE, "https://test.pl")
        self.assertEqual(DIFF._build_url(DIFF.url, DIFF.frequency, "5"), "https://test.pl/minute/000/000/005.osc.gz")
        self.assertEqual(DIFF._build_url(DIFF.url, DIFF.frequency, "53"), "https://test.pl/minute/000/000/053.osc.gz")
        self.assertEqual(DIFF._build_url(DIFF.url, DIFF.frequency, "531"), "https://test.pl/minute/000/000/531.osc.gz")
        self.assertEqual(DIFF._build_url(DIFF.url, DIFF.frequency, "5315"), "https://test.pl/minute/000/005/315.osc.gz")
        self.assertEqual(DIFF._build_url(DIFF.url, DIFF.frequency, "53154"), "https://test.pl/minute/000/053/154.osc.gz")
        self.assertEqual(DIFF._build_url(DIFF.url, DIFF.frequency, "531542"), "https://test.pl/minute/000/531/542.osc.gz")
        self.assertEqual(DIFF._build_url(DIFF.url, DIFF.frequency, "5315422"), "https://test.pl/minute/005/315/422.osc.gz")
        self.assertEqual(DIFF._build_url(DIFF.url, DIFF.frequency, "53154221"), "https://test.pl/minute/053/154/221.osc.gz")
        self.assertEqual(DIFF._build_url(DIFF.url, DIFF.frequency, "531542219"), "https://test.pl/minute/531/542/219.osc.gz")

    @responses.activate
    def test_diff_get_generator(self):
        body = open(os.path.join("tests", "fixtures", "hour.xml.gz"), "rb")
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/minute/state.txt",
            "body": self.SEQUENCE_NUMBER,
            "status": 200
        })
        
        responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/minute/005/315/422.osc.gz",
            "body": body,
            "status": 200
        })

        d = Diff(Frequency.MINUTE, "https://test.pl")
        meta, gen = d.get(sequence_number=self.SEQUENCE_NUMBER)
        act, element = next(gen)
        self.assertEqual(meta.sequence_number, self.SEQUENCE_NUMBER)
        self.assertEqual(element.id, 4222078)

    @responses.activate
    def test_diff_get(self):
        def check_osm_change(osm_change: OsmChange):
            self.assertEqual(osm_change.get(Node, Action.CREATE).__len__(),  2)
            self.assertEqual(osm_change.get(Node, Action.MODIFY).__len__(),  14)
            self.assertEqual(osm_change.get(Node, Action.DELETE).__len__(),  1)
            self.assertEqual(osm_change.get(Node, Action.NONE).__len__(),    0)

            self.assertEqual(osm_change.get(Way, Action.CREATE).__len__(),   0)
            self.assertEqual(osm_change.get(Way, Action.MODIFY).__len__(),   1)
            self.assertEqual(osm_change.get(Way, Action.DELETE).__len__(),   0)
            self.assertEqual(osm_change.get(Way, Action.NONE).__len__(),     0)

            self.assertEqual(osm_change.get(Relation, Action.CREATE).__len__(),   1)
            self.assertEqual(osm_change.get(Relation, Action.MODIFY).__len__(),   0)
            self.assertEqual(osm_change.get(Relation, Action.DELETE).__len__(),   0)
            self.assertEqual(osm_change.get(Relation, Action.NONE).__len__(),     0)

        with open(os.path.join("tests", "fixtures", "hour.xml.gz"), "rb") as f:
            responses.add(**{
                "method": responses.GET,
                "url": "https://test.pl/minute/005/315/422.osc.gz",
                "body": f,
                "status": 200
            })

            DIFF = Diff(Frequency.MINUTE, "https://test.pl")
            osm_change = DIFF.get(sequence_number=self.SEQUENCE_NUMBER, generator=False)
            assert isinstance(osm_change, OsmChange)
            check_osm_change(osm_change)

            self.assertTrue(responses.assert_call_count("https://test.pl/minute/state.txt", 0))
            self.assertTrue(responses.assert_call_count("https://test.pl/minute/005/315/422.osc.gz", 1))

        with open(os.path.join("tests", "fixtures", "hour.xml.gz"), "rb") as f:
            responses.add(**{
                "method": responses.GET,
                "url": "https://test.pl/minute/005/315/422.osc.gz",
                "body": f,
                "status": 200
            })

            responses.add(**{
            "method": responses.GET,
            "url": "https://test.pl/minute/state.txt",
            "body": f"""#Mon Mar 18 19:34:09 UTC 2024
sequenceNumber={self.SEQUENCE_NUMBER}
timestamp=2024-03-18T19\:33\:45Z""",
            "status": 200
        })

            osm_change = DIFF.get(generator=False)
            assert isinstance(osm_change, OsmChange)
            check_osm_change(osm_change)
            self.assertTrue(responses.assert_call_count("https://test.pl/minute/state.txt", 1))
            self.assertTrue(responses.assert_call_count("https://test.pl/minute/005/315/422.osc.gz", 2))
