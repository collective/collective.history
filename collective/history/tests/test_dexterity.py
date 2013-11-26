import datetime
import unittest2 as unittest
from collective.history.tests import base, fake
from collective.history.dexterity import DxUserActionWrapper
from zope.lifecycleevent import (
    ObjectAddedEvent,
    ObjectModifiedEvent,
)
from Products.DCWorkflow.events import AfterTransitionEvent


class TestDexterityUserAction(base.UnitTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """
    def setUp(self):
        base.UnitTestCase.setUp(self)
        self.handler = fake.FakeHandler()
        self.event = self.handler.event
        self.useraction = DxUserActionWrapper(self.handler)

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

    def test_extract_what(self):
        obj = self.event.object

        #added
        event_added = ObjectAddedEvent(obj)
        self.useraction.event = event_added
        what, info = self.useraction.extract_what()
        self.assertEqual(what, 'created')
        self.assertEqual(type(info), str)
        import json
        info = json.loads(info)
        self.assertIn('newName', info)
        self.assertIn('newParent_url', info)
        self.assertIn('newParent_path', info)
        self.assertEqual(info['newName'], 'name')
        self.assertEqual(info['newParent_url'], "http://nohost/Plone/foo")
        self.assertEqual(info['newParent_path'], "/Plone/foo")

        #modified
        event_modified = ObjectModifiedEvent(obj)
        self.useraction.event = event_modified
        what, info = self.useraction.extract_what()
        self.assertEqual(what, 'modified')
        self.assertIsNone(info)  # must be tested in integration test

        #statechanged
        worklfow = fake.FakeWorkflow("testworkflow")
        old_state = fake.FakeState("private")
        new_state = fake.FakeState("published")
        transition = fake.FakeState("transition")
        status = None
        event = AfterTransitionEvent(
            obj, worklfow, old_state, new_state, transition, status, "kwargs"
        )
        self.useraction.event = event
        what, info = self.useraction.extract_what()
        self.assertEqual('statechanged', what)
        self.assertEqual(type(info), str)
        info = json.loads(info)
        self.assertIn('old_state', info)
        self.assertIn('new_state', info)
        self.assertIn('transition', info)
        self.assertIn('workflow', info)
        self.assertIn('kwargs', info)
        self.assertEqual(info['old_state'], 'private')
        self.assertEqual(info['new_state'], 'published')
        self.assertEqual(info['transition'], 'transition')
        self.assertEqual(info['workflow'], 'testworkflow')
        self.assertEqual(info['kwargs'], 'kwargs')

        #copied, moved, removed must be tested in integration

    def test_is_valid_event(self):
        self.useraction.initialize()
        #blacklisted event
        self.useraction.what = 'OFS.interfaces.IObjectWillBeRemovedEvent'
        self.assertFalse(self.useraction.is_valid_event())

        #wrong moved event
        self.useraction.what = 'moved'
        self.useraction.event.oldName = None
        self.assertFalse(self.useraction.is_valid_event())

        #removed
        self.useraction.event.oldName = "old name"
        self.useraction.event.newName = None
        self.useraction.is_valid_event()
        self.assertEqual(self.useraction.what, "removed")

        #transition
        self.useraction.what = 'statechanged'
        self.useraction.event.oldName = "same name"
        self.useraction.event.newName = "same name"
        self.assertFalse(self.useraction.is_valid_event())


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
