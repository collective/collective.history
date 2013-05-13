#zope
from zope import component
from zope import interface
from zope import schema

#Zope2
from Products.Five.browser import BrowserView

#Plone
from plone.registry.interfaces import IRegistry

#internal
from collective.history import backend


class IUserActionManager(backend.IBackendStorage):
    """The global user action manager provide a complete API to
    manage user actions. It's a wrapper around the backend storage
    responsible to choose the backend to use.

    This design make it simple to code an other backend without changing
    anything more than just a record in portal_registry.

    Notice: The implementation must be a browser view to know who & where.
    """

    backend = schema.TextLine(title=u"Backend name")


class UserActionManager(BrowserView):
    interface.implements(IUserActionManager)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.backend = None
        self.registry = None

    def update(self):
        if self.registry is None:
            self.registry = component.queryUtility(IRegistry)
            if self.registry is None:
                return
        if self.backend is None:
            backend = self.registry.get(
                'collective.history.backend',
                'collective.history.backend.dexterity'
            )
            self.backend = self.context.restrictedTraverse(backend)
            try:
                self.backend.update()
            except AttributeError:
                self.backend = False

    def create(self):
        if not self.backend:
            return
        return self.backend.create()

    def add(self, useraction):
        if not self.backend:
            return
        return self.backend.add(useraction)
