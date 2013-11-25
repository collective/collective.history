import datetime
import unittest2 as unittest
from collective.history.tests import base, fake
from collective.history.dexterity import DxUserActionWrapper


class TestDexterityUserAction(base.UnitTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """
    def setUp(self):
        base.UnitTestCase.setUp(self)
        self.useraction = DxUserActionWrapper(fake.FakeHandler())

    def test_initialize(self):
        self.assertIsNone(self.useraction.event)
        self.assertIsNone(self.useraction.what)
        self.assertIsNone(self.useraction.when)
        self.assertIsNone(self.useraction.where)
        self.assertIsNone(self.useraction.who)
        self.useraction.initialize()
        self.assertIsNotNone(self.useraction.event)
#        self.assertIsNotNone(self.useraction.what)
        self.assertIsNotNone(self.useraction.when)
        self.assertIsNotNone(self.useraction.where)
        self.assertIsNotNone(self.useraction.who)
        self.assertEqual(type(self.useraction.event), fake.FakeEvent)
        self.assertEqual(type(self.useraction.when), datetime.datetime)
        self.assertEqual(self.useraction.who, 'admin')

    def test_what(self):
        self.useraction.what = "test"
        self.assertEqual(self.useraction.what, "test")
        self.useraction.what = fake.FakeEvent()
        iface = "collective.history.tests.fake.IFakeEvent"
        self.assertEqual(self.useraction.what, iface)

    def test_what_info(self):
        self.useraction.what_info = {"test": "info"}
        self.assertEqual(self.useraction.what_info, '{"test": "info"}')
        self.useraction.data["what_info"] = None

        self.useraction.what_info = '{"test": "info"}'
        self.assertEqual(self.useraction.what_info, '{"test": "info"}')
        self.useraction.data["what_info"] = None

        self.useraction.what_info = "notvalid"
        self.assertIsNone(self.useraction.what_info)

    def test_when(self):
        now = datetime.datetime.now()
        self.useraction.when = now
        self.assertEqual(self.useraction.when, now)
        self.useraction.data["when"] = None

        self.useraction.when = "notvalid"
        self.assertIsNone(self.useraction.when)

    def test_where(self):
        phy = fake.FakeContext()
        self.useraction.where = phy
        self.assertEqual(self.useraction.where_path, '/Plone/foo')
        uri = 'http://nohost/Plone/foo/edit'
        self.assertEqual(self.useraction.where_uri, uri)

    def test_who(self):
        self.useraction.who = 'admin'
        self.assertEqual(self.useraction.who, 'admin')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
