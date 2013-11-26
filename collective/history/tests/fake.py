from datetime import datetime
from zope import interface
from zope.component.interfaces import IObjectEvent


class IFakeEvent(IObjectEvent):
    """fake event"""


class FakeContext(object):
    def __init__(self):
        self.physical_path = ('', 'Plone', 'foo')
        self.REQUEST = FakeRequest()
        self.REQUEST.ACTUAL_URL += '/Plone/foo/edit'
        self.__parent__ = self
        self.__name__ = "name"

    def getPhysicalPath(self):
        return self.physical_path

    def absolute_url(self):
        return 'http://nohost' + '/'.join(self.physical_path)


class FakeRequest(object):
    def __init__(self):
        self.ACTUAL_URL = 'http://nohost'


class FakeEvent(object):
    interface.implements(IFakeEvent)

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


class FakeCursor(object):
    def __init__(self):
        self.description = (("id",), ("what",))


class FakeUserAction(object):
    def __init__(self):
        self.id = "foo-bar"
        self.what = "edit"
        self.on_what = "Document"
        self.what_info = {"foo": "bar"}
        self.when = datetime.now()
        self.where_uri = "http://example.com/foo/bar/@@view"
        self.where_uid = "UID1234"
        self.where_path = "/foo/bar"
        self.who = "me"
        self.transactionid = None


class FakeWorkflow():
    def __init__(self, id):
        self.id = id


class FakeState():
    def __init__(self, id):
        self.id = id
