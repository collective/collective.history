from zope import interface
from zope import schema

from plone.directives import form


class IUserAction(form.Schema):
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

