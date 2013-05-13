import unittest2 as unittest
from collective.history.tests import base, fake
from collective.history.useraction import BaseUserActionWrapper
import datetime


class IntegrationTestBaseUserAction(base.IntegrationTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """
    def setUp(self):
        base.IntegrationTestCase.setUp(self)
        self.useraction = BaseUserActionWrapper(fake.FakeHandler())

    def test_initialize(self):
        self.assertIsNone(self.useraction.event)
        self.assertIsNone(self.useraction.what)
        self.assertIsNone(self.useraction.when)
        self.assertIsNone(self.useraction.where)
        self.assertIsNone(self.useraction.who)
        self.assertIsNone(self.useraction.target)
        self.useraction.initialize()
        self.assertIsNotNone(self.useraction.event)
#        self.assertIsNotNone(self.useraction.what)
        self.assertIsNotNone(self.useraction.when)
#        self.assertIsNotNone(self.useraction.where)
        self.assertIsNotNone(self.useraction.who)
        self.assertIsNotNone(self.useraction.target)
        self.assertEqual(type(self.useraction.event), fake.FakeEvent)
        self.assertEqual(type(self.useraction.when), datetime.datetime)
        self.assertEqual(self.useraction.who, 'admin')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
