import unittest2 as unittest
from collective.history.tests import base
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes


class TestSetup(base.IntegrationTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def test_browserlayer(self):
        from plone.browserlayer import utils
        from collective.history import layer
        self.assertIn(layer.Layer, utils.registered_layers())

    def test_types(self):
        types = self.layer['portal'].portal_types
        _type = 'collective.history.useraction'
        actions = types.listActions(object=_type)
        self.assertIsNotNone(actions)

    def test_upgrades(self):
        profile = 'collective.history:default'
        setup = self.layer['portal'].portal_setup
        upgrades = setup.listUpgrades(profile, show_old=True)
        self.assertTrue(len(upgrades) > 0)
        for upgrade in upgrades:
            upgrade['step'].doStep(setup)

    def test_setuphandler(self):
        self.assertIn('portal_history', self.layer['portal'].objectIds())
        history = self.layer['portal'].portal_history
        self.assertEqual(history.getLayout(), 'collective_history_view')
        aspect = ISelectableConstrainTypes(history)
        addable = aspect.getImmediatelyAddableTypes()
        type_name = "collective.history.useraction"
        self.assertIn(type_name, addable)

    def test_type_not_searched(self):
        type_name = "collective.history.useraction"
        properties = self.layer['portal'].portal_properties.site_properties
        tns = properties.getProperty('types_not_searched')
        self.assertIn(type_name, tns)
        self.assertNotEqual(len(tns), 1)

    def test_i18n(self):
        from collective.history import i18n
        self.assertTrue(hasattr(i18n, '_'))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
