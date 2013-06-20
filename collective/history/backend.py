import logging

from zope import component
from zope import interface

from Products.CMFCore.utils import getToolByName

from plone.dexterity.utils import createContent


LOG = logging.getLogger("collective.history")


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
        self.catalog = None

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
        if self._portal_types is None:
            self._portal_types = getToolByName(self.context, "portal_types")
        self.isReady = True
        if self.catalog is None:
            self.catalog = getToolByName(self.context,
                                         'portal_history_catalog')

    def add(self, useraction_wrapper):
        if not self.isReady:
            return
        useraction = self.create()
        if not useraction:
            return
        self.update_useraction(useraction_wrapper, useraction)
        action_id = useraction.id
        action_ids = self.container.objectIds()

        if action_id in action_ids:
            indice = 1
            while action_id + "-%s" % indice in action_ids:
                indice += 1
            new_id = action_id + "-%s" % indice
            useraction.id = new_id

        self.container[useraction.id] = useraction
        self.catalog.indexObject(self.container[useraction.id])

    def update_useraction(self, original, target):

        target.what = original.what
        target.what_info = original.what_info
        target.on_what = original.on_what
        target.when = original.when
        target.where_uri = original.where_uri
        target.where_uid = original.where_uid
        target.where_path = original.where_path
        target.who = original.who
        target.id = original.id
        target.setTitle(original.title)
        return target

    def rm(self, useraction_id):
        if not self.isReady:
            return
        self.container.manage_delObjects(ids=[useraction_id])

    def search(self, query):
        if not self.isReady:
            return []
        return self.catalog.searchResults(query)

    def get(self, useraction_id):
        if not self.isReady:
            return
        return self.container[useraction_id]

    def create(self):
        if not self.isReady:
            return
        useraction = createContent(TYPE_NAME)
        return useraction
