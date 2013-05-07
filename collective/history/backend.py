import logging
from datetime import datetime

from zope import component
from zope import interface

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes

from plone.dexterity.utils import createContent

from collective.history.useraction import UserActionWrapper


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

    def add(self, useraction_wrapper):
        if not self.isReady:
            return
        useraction_wrapper.update_before_add()
        useraction = useraction_wrapper.context
        useraction = self._filter(useraction)
        if not useraction:
            return
        action_id = useraction.id
        action_ids = self.container.objectIds()

        if action_id in action_ids:
            action_id += "-1"
            indice = 1
            while action_id + "-%s" % indice in action_ids:
                indice += 1
            new_id = action_id + "-%s" % indice
            useraction.id = new_id

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
        return UserActionWrapper(useraction, self)

    def _filter(self, useraction):
        """delete the user action and return None
        if this one should not be kept"""
        delete = False
        if "Before" in useraction.what:
            delete = True
        if "WillBe" in useraction.what:
            delete = True
        if useraction.what == "EditBegun":
            delete = True
        if delete:
            del useraction
            return
        return useraction
