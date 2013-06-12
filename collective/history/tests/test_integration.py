import datetime
import unittest2 as unittest
from collective.history.tests import base
from plone.app import testing
from plone.uuid.interfaces import IUUID


class TestIntegration(base.IntegrationTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """
    def setUp(self):
        base.IntegrationTestCase.setUp(self)
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        testing.login(self.portal, testing.TEST_USER_NAME)
        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Manager'])

    def test_addcontent(self):
        self.portal.invokeFactory('Document', 'test-document', title="D1")
        d1 = self.portal["test-document"]
        d1.processForm()
        history = self.portal.portal_history.objectValues()
        self.assertEqual(len(history), 1)
        h1, = history
        self.assertEqual(h1.what, "created")
        self.assertEqual(type(h1.when), datetime.datetime)
        self.assertEqual(h1.who, testing.TEST_USER_ID)
        self.assertEqual(h1.where_path, '/plone/test-document')
        self.assertEqual(h1.where_uid, IUUID(d1))
        self.assertEqual(h1.where_uri, 'http://nohost')

    def test_rename(self):
        self.portal.invokeFactory('Document', 'test-document', title="D1")
        d1 = self.portal["test-document"]
        d1.processForm()
        d1.manage_renameObject("test-document", "new-test-doc")
        history = self.portal.portal_history.objectValues()
        self.assertEqual(len(history), 2)
        h2 = history[1]
        self.assertEqual(h2.what, "moved")
        self.assertEqual(type(h2.when), datetime.datetime)
        self.assertEqual(h2.who, testing.TEST_USER_ID)
        self.assertEqual(h2.where_path, '/plone/new-test-doc')
        self.assertEqual(h2.where_uid, IUUID(d1))
        self.assertEqual(h2.where_uri, 'http://nohost')

    def test_delete(self):
        self.portal.invokeFactory('Document', 'test-document', title="D1")
        d1 = self.portal["test-document"]
        d1.processForm()
        self.portal.manage_delObjects(["test-document"])
        history = self.portal.portal_history.objectValues()
        self.assertEqual(len(history), 2)
        h2 = history[1]
        self.assertEqual(h2.what, "removed")
        self.assertEqual(type(h2.when), datetime.datetime)
        self.assertEqual(h2.who, testing.TEST_USER_ID)
        self.assertEqual(h2.where_path, '/plone/test-document')
        self.assertEqual(h2.where_uid, IUUID(d1))
        self.assertEqual(h2.where_uri, 'http://nohost')

    def test_edit(self):
        self.portal.invokeFactory('Document', 'test-document', title="D1")
        d1 = self.portal["test-document"]
        d1.processForm()
        d1.setTitle('New title')
        d1.processForm()
        history = self.portal.portal_history.objectValues()
        self.assertEqual(len(history), 2)
        h2 = history[1]
        self.assertEqual(h2.what, "modified")
        self.assertEqual(type(h2.when), datetime.datetime)
        self.assertEqual(h2.who, testing.TEST_USER_ID)
        self.assertEqual(h2.where_path, '/plone/test-document')
        self.assertEqual(h2.where_uid, IUUID(d1))
        self.assertEqual(h2.where_uri, 'http://nohost')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
