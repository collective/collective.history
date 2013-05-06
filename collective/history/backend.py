from datetime import datetime
from random import random

from zope import component
from zope import interface

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes

from plone.dexterity.utils import createContent
from plone.i18n.normalizer.interfaces import IIDNormalizer

from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation
from plone.app.dexterity.behaviors.metadata import IBasic


class IBackendStorage(interface.Interface):
    """A backend storage is a named utility able to store user action"""

    def add(useraction):
        """add the user IUserAction the database"""

    def rm(useraction_id):
        """delete the IUserAction with id"""

    def search(query):
        """get all IUserAction which respect the criteria in the query"""

    def get(useraction_id):
        """return the IUserAction object with id"""


TYPE_NAME = "collective.history.useraction"


class DexterityBackend(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.portal_state = None
        self.container = None
        self.isReady = False
        self._portal_types = None

    def update(self):
        context = (self.context, self.request)
        if self.portal_state is None:
            self.portal_state = component.getMultiAdapter(
                context,
                name="plone_portal_state"
            )
        if self.container is None:
            portal = self.portal_state.portal()
            self.container = portal.portal_history
            self._check_container()
        if self._portal_types is None:
            self._portal_types = getToolByName(self.context, "portal_types")

    def add(self, useraction):
        if not self.isReady:
            return
        self._update_action(useraction)
        self.container[useraction.id] = useraction

    def rm(self, useraction_id):
        if not self.isReady:
            return
        self.container.manage_delObjects(ids=[useraction_id])

    def search(self, query):
        if not self.isReady:
            return []
        return []

    def get(self, useraction_id):
        if not self.isReady:
            return
        return self.container[useraction_id]

    def create(self):
        if not self.isReady:
            return
#        suffix = "%s" % int(random()*10000)
#        dt = datetime.now().strftime('%Y%m%d%H%M%f')
#        newid = dt + suffix
#        type_info = self._portal_types.getTypeInfo(TYPE_NAME)
#        useraction = type_info._constructInstance(self.container, newid)
        useraction = createContent(TYPE_NAME)
        return useraction

    def _check_container(self):
        aspect = ISelectableConstrainTypes(self.container)
        if TYPE_NAME not in aspect.getImmediatelyAddableTypes():
            aspect.setConstrainTypesMode(1)  #select manually
            aspect.setImmediatelyAddableTypes([TYPE_NAME])
        self.isReady = True

    def _update_action(self, useraction):
        """set title and id to be as friendly as possible
        when-who-what-where
        """
        normalizer = component.getUtility(IIDNormalizer)

        title = "%s" % useraction.when.strftime("%Y-%m-%d-%H-%M-%S-%f")
        title += "-%s" % normalizer.normalize(useraction.who)
        title += "-%s" % useraction.what
        title += "-%s" % useraction.target

        useraction.setTitle(title)
        useraction.id = title
