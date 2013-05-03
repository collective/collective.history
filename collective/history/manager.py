from zope import component
from collective.history import backend
from Products.Five.browser import BrowserView
from plone.registry.interfaces import IRegistry


class IUserActionManager(backend.IBackendStorage):
    """The global user action manager provide a complete API to
    manage user actions. It's a wrapper around the backend storage.

    The implementation must be a browser view to know who & where."""

    #context
    #request
    backend = schema.TextLine(title=u"Backend name")


class UserActionManager(BrowserView):
    def __init__(self, context, request):
        self.context = context  # TODO: change this context to become the portal
        self.request = request
        self.backend = None
        self.registry = None

    def update(self):
        if self.registry is None:
            self.registry = component.getUtility(IRegistry)
        if self.backend is None:
            backend = self.registry.get(
                'collective.history.backend',
                'default'
            )
            objects = (self.context, self.request)
            self.backend = component.queryMultiAdapter(
                objects,
                interface=backend.IBackendStorage,
                name=backend
            )
