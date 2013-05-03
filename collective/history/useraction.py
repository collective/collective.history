from zope import interface
from zope import schema


class IUserAction(interface.Interface):
    """The schema of a user action"""
    id = schema.ASCIILine(title=u"ID")
    trigger = schema.Choice(
        title=u"Trigger",
        vocabulary="collective.history.vocabulary.trigger"
    )
    what = schema.ASCIILine(title=u"What")
    when = schema.Datetime(title=u"When")
    where = schema.ASCIILine(title=u"Where")
    who = schema.ASCIILine(title=u"Who")

    transactionid = schema.ASCIILine(title=u"Transaction ID")


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


class IUserActionManager(IBackendStorage):
    """The global user action manager provide a complete API to
    manage user actions. It's a wrapper around the backend storage.

    The implementation must be a browser view to know who & where."""

    #context
    #request
    backend = schema.TextLine(title=u"Backend name")

