import DateTime
import unittest2 as unittest
from Products.CMFCore.utils import getToolByName

from collective.history.tests import base
from plone.app import testing


class TestCatalog(base.IntegrationTestCase):
    """We tests the catalog of the addons. You should check all
    useractions are properly indexed.
    """

    def setUp(self):
        base.IntegrationTestCase.setUp(self)
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        testing.login(self.portal, testing.TEST_USER_NAME)
        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Document',
                                  'test-document',
                                  title="D1")
        d1 = self.portal["test-document"]
        d1.setCreationDate(DateTime.DateTime('12.25.2012'))
        d1.processForm()
        testing.logout()

        acl_users = getToolByName(self.portal, 'acl_users')
        acl_users.userFolderAddUser('toto', 'password',
                                    ['Member', 'Contributor'], [])
        testing.login(self.portal, 'toto')
        self.portal.invokeFactory('Document',
                                  'test-document-2',
                                  title="D2")
        d2 = self.portal["test-document-2"]
        d2.setCreationDate(DateTime.DateTime('1.25.2013'))
        d2.processForm()

        self.catalog = self.layer['portal'].portal_history_catalog

    def test_what_index(self):
        result = self.catalog.searchResults({'what': 'created'})
        self.assertEqual(len(result), 2)
        brain = result[0]
        try:
            brain.getObject()
        except:
            self.assertTrue(False, "getObject should work")

    def test_who_index(self):
        result = self.catalog.searchResults({'who': 'toto'})

        self.assertEqual(len(result), 1)
        try:
            useraction = result[0].getObject()
        except:
            self.assertTrue(False, "getObject should work")
        self.assertEqual(useraction.who, 'toto')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
