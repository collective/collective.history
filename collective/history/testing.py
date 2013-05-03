from plone.app.testing import *
import collective.history


FIXTURE = PloneWithPackageLayer(
    zcml_filename="configure.zcml",
    zcml_package=collective.history,
    additional_z2_products=[],
    gs_profile_id='collective.history:default',
    name="collective.history:FIXTURE"
)

INTEGRATION = IntegrationTesting(
    bases=(FIXTURE,), name="collective.history:Integration"
)

FUNCTIONAL = FunctionalTesting(
    bases=(FIXTURE,), name="collective.history:Functional"
)
