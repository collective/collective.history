from zope.component.interfaces import IObjectEvent
from zope import component
from zope import interface


class IExtractWhat(interface.Interface):
    """Marker interface for ExtractWhat adapter."""


class ExtractWhat(object):
    interface.implements(IExtractWhat)
    component.adapts(IObjectEvent)

    def __init__(self, event):
        self.event = event

    def __call__(self):
        ifaces = list(interface.implementedBy(self.event.__class__))
        for iface in ifaces:
            if iface.extends(IObjectEvent):
                iface_id = str(iface.__identifier__)
                return iface_id, {}
        return None, {}
