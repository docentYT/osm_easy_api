import unittest
import responses
from copy import copy

import os
from dotenv import load_dotenv
load_dotenv()
LOGIN, PASSWORD = os.getenv("login"), os.getenv("password")

from src import Api
from src.api import exceptions as ApiExceptions

class TestApiChangeset(unittest.TestCase):

    @responses.activate
    def test_subscribe_unsubscribe(self):
        responses.add(**{
            "method": responses.POST,
            "url": "https://test.pl/api/0.6/changeset/111/subscribe",
            "status": 200
        })
        responses.add(**{
            "method": responses.POST,
            "url": "https://test.pl/api/0.6/changeset/111/unsubscribe",
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        def subscribe(): return api.changeset.discussion.subscribe("111")
        def unsubscribe(): return api.changeset.discussion.unsubscribe("111")
        subscribe()
        responses.add(**{
            "method": responses.POST,
            "url": "https://test.pl/api/0.6/changeset/111/subscribe",
            "status": 409
        })
        self.assertRaises(ApiExceptions.AlreadySubscribed, subscribe)
        unsubscribe()
        responses.add(**{
            "method": responses.POST,
            "url": "https://test.pl/api/0.6/changeset/111/unsubscribe",
            "status": 404
        })
        self.assertRaises(ApiExceptions.NotSubscribed, unsubscribe)

    @responses.activate
    def test_hide(self):
        responses.add(**{
            "method": responses.POST,
            "url": "https://test.pl/api/0.6/changeset/comment/111/hide",
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        def hide(): return api.changeset.discussion.hide("111")
        hide()
        responses.add(**{
            "method": responses.POST,
            "url": "https://test.pl/api/0.6/changeset/comment/111/hide",
            "status": 403
        })
        self.assertRaises(ApiExceptions.NotAModerator, hide)
        responses.add(**{
            "method": responses.POST,
            "url": "https://test.pl/api/0.6/changeset/comment/111/hide",
            "status": 404
        })
        self.assertRaises(ApiExceptions.IdNotFoundError, hide)

    @responses.activate
    def test_hide(self):
        responses.add(**{
            "method": responses.POST,
            "url": "https://test.pl/api/0.6/changeset/comment/111/unhide",
            "status": 200
        })

        api = Api("https://test.pl", LOGIN, PASSWORD)
        def unhide(): return api.changeset.discussion.unhide("111")
        unhide()
        responses.add(**{
            "method": responses.POST,
            "url": "https://test.pl/api/0.6/changeset/comment/111/unhide",
            "status": 403
        })
        self.assertRaises(ApiExceptions.NotAModerator, unhide)
        responses.add(**{
            "method": responses.POST,
            "url": "https://test.pl/api/0.6/changeset/comment/111/unhide",
            "status": 404
        })
        self.assertRaises(ApiExceptions.IdNotFoundError, unhide)
