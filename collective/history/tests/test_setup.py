import unittest2 as unittest
from collective.history.tests import base


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


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
