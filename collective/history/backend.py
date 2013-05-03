from zope import interface


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


class DexterityBackend(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def add(self, useraction):
        self.context['id'] = useraction

    def rm(self, useraction_id):
        self.context.manage_delObjects(ids=[useraction_id])

    def search(self, query):
        return []

    def get(self, useraction_id):
        return self.context[useraction_id]
