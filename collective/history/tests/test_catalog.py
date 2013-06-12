import datetime
import DateTime
import unittest2 as unittest
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from Products.CMFCore.utils import getToolByName

from collective.history.tests import base
from collective.history.tests import fake
from collective.history.manager import UserActionManager
from collective.history.backend import DexterityBackend
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
        self.catalog = self.layer['portal'].portal_history_catalog

    def test_what_index(self):
        result = self.catalog.searchResults({'what': 'created'})
        import pdb; pdb.set_trace()


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
