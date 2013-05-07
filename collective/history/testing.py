from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE

from plone.testing import z2


class Layer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.history
        self.loadZCML(package=collective.history)

#        z2.installProduct(app, 'collective.history')

    def setUpPloneSite(self, portal):
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')
        self.applyProfile(portal, 'collective.history:default')

#    def tearDownZope(self, app):
#        z2.uninstallProduct(app, 'collective.history')


FIXTURE = Layer()
INTEGRATION = IntegrationTesting(bases=(FIXTURE,),
                                 name="collective.history:Integration")
FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,),
                               name="collective.history:Functional")

ROBOT = FunctionalTesting(
    bases=(AUTOLOGIN_LIBRARY_FIXTURE, FIXTURE, z2.ZSERVER),
    name="collective.history:Robot")
