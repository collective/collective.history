from zope import interface
from zope.component.interfaces import IObjectEvent


class FakeContext(object):
    def __init__(self):
        self.physical_path = ('Plone', 'foo')

    def getPhysicalPath(self):
        return self.physical_path


class FakeEvent(object):
    interface.implements(IObjectEvent)

    def __init__(self):
        self.object = FakeContext()


class FakeHandler(object):
    def __init__(self):
        self.event = FakeEvent()
        self.mtool = FakeMTool()


class FakeMember(object):
    def __init__(self):
        self.id = 'admin'

    def getId(self):
        return self.id


class FakeMTool(object):
    def __init__(self):
        self.member = FakeMember()

    def getAuthenticatedMember(self):
        return self.member
