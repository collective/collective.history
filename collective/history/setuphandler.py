## setuphandlers.py
import logging

from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation
from plone.dexterity.interfaces import IDexterityContainer


LOG = logging.getLogger("collective.history")


def setupVarious(context):
    """Create the history container"""

    if context.readDataFile('collective_history.txt') is None:
        return

    portal = context.getSite()
    if "portal_history" not in portal.objectIds():
        createHistory(portal)
    updateHistoryContainer(portal.portal_history)


def updateHistoryContainer(obj):
    obj.unindexObject()
    obj.setLayout("collective_history_view")
    if IExcludeFromNavigation.providedBy(obj):
        obj.exclude_from_nav = True
    else:
        obj.setExcludeFromNav(True)

    aspect = ISelectableConstrainTypes(obj)
    addable = aspect.getImmediatelyAddableTypes()
    if "collective.history.useraction" not in addable:
        aspect.setConstrainTypesMode(1)  # select manually
        types = ["collective.history.useraction"]
        if IDexterityContainer.providedBy(obj):
            #bypass check for available types
            obj.immediately_addable_types = types
        else:
            aspect.setImmediatelyAddableTypes(types)


def createHistory(parent):
    existing = parent.objectIds()
    if "portal_history" not in existing:
        _createObjectByType(
            "Folder",
            parent,
            id="portal_history",
            title="History of the site"
        )
