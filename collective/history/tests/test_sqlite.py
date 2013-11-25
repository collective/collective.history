from datetime import datetime, timedelta
import unittest2 as unittest
from Products.CMFCore.utils import getToolByName
from collective.history.manager import UserActionManager

from collective.history.tests import base, fake
from collective.history import backend_sqlite
from plone.app import testing


class TestSQLiteBackend(base.UnitTestCase):

    def test_dict_factory(self):
        dict_factory = backend_sqlite.dict_factory
        cursor = fake.FakeCursor()
        row = ("myid", "mywhat")
        info = dict_factory(cursor, row)
        self.assertEqual(type(info), dict)
        self.assertEqual(info["id"], row[0])
        self.assertEqual(info["what"], row[1])

    def test_date_to_int(self):
        date = datetime.strptime('2013-11-22 19:42:00', '%Y-%m-%d %H:%M:%S')
        dateint = backend_sqlite.date_to_int(date)
        self.assertEqual(dateint, 20131122194200)

    def test_int_to_date(self):
        date = backend_sqlite.int_to_date(20131122194200)
        self.assertEqual(date.year, 2013)
        self.assertEqual(date.month, 11)
        self.assertEqual(date.day, 22)
        self.assertEqual(date.hour, 19)
        self.assertEqual(date.minute, 42)
        self.assertEqual(date.second, 0)

    def test_useraction(self):
        date = datetime.strptime('2013-11-22 19:42:00', '%Y-%m-%d %H:%M:%S')
        original = {}
        original['what'] = 'what_value'
        original['what_info'] = '{"key":"value"}'
        original['on_what'] = 'on_what_value'
        original['when'] = 20131122194200
        original['where_uri'] = 'uri_value'
        original['where_uid'] = 'uid_value'
        original['where_path'] = '/foo/bar'
        original['who'] = "me"
        original['id'] = "id_value"
        useraction = backend_sqlite.UserAction(original)
        self.assertEqual(useraction.what, "what_value")
        self.assertEqual(useraction.what_info['key'], "value")
        self.assertEqual(useraction.on_what, "on_what_value")
        self.assertEqual(useraction.when, date)
        self.assertEqual(useraction.where_uri, 'uri_value')
        self.assertEqual(useraction.where_uid, 'uid_value')
        self.assertEqual(useraction.where_path, '/foo/bar')
        self.assertEqual(useraction.who, "me")
        self.assertEqual(useraction.id, "id_value")

    def test_backend_add(self):
        now = datetime.now() - timedelta(seconds=1)  #delay to let sql
        yesterday = datetime.now() - timedelta(days=1)
        tomorrow = datetime.now() + timedelta(days=1)

        backend = backend_sqlite.SQLiteBackend(None, None)
        backend.db_path = ":memory:"
        backend.update()
        self.assertTrue(backend.isReady)
        self.assertIsNone(backend.db)
        backend._initdb()
        self.assertIsNotNone(backend.db)
        backend._closedb()
        self.assertIsNone(backend.db)

        backend._should_closedb = False
        useraction = fake.FakeUserAction()
        useraction.id = 'foo-bar-1'
        backend.add(useraction)

        history = backend.search()
        self.assertEqual(len(history), 1)

        useraction2 = fake.FakeUserAction()
        useraction2.id = 'foo-bar-2'
        useraction2.when = yesterday
        backend.add(useraction2)
        useraction3 = fake.FakeUserAction()
        useraction3.when = tomorrow
        useraction3.id = 'foo-bar-3'
        backend.add(useraction3)

        history = backend.search()
        self.assertEqual(len(history), 3)

        when = {"query": now, "range": "min"}
        history = backend.search(when=when)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].id, 'foo-bar-3')
        self.assertEqual(history[1].id, 'foo-bar-1')

        when = {"query": now, "range": "max"}
        history = backend.search(when=when)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].id, 'foo-bar-2')

        backend.rm("foo-bar-1")
        history = backend.search()
        self.assertEqual(len(history), 2)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
