## setuphandlers.py
import logging

from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes


LOG = logging.getLogger("collective.history")


def setupVarious(context):
    """Create the history container"""

    if context.readDataFile('collective_history.txt') is None:
        return

    portal = context.getSite()
    if "portal_history" not in portal.objectIds():
        info = {
            'id': 'portal_history',
            'title': 'History of the site',
            'type': 'Folder',
            'exclude_from_nav': True,
            'layout': 'collective_history_view'
        }
        _createObjects(portal, info)


def _createObjects(parent, new_object):

    LOG.info("Creating %s in %s" % (new_object, parent))

    existing = parent.objectIds()
    if new_object['id'] in existing:
        LOG.info("%s exists, skipping" % new_object['id'])
    else:
        _createObjectByType(
            new_object['type'],
            parent,
            id=new_object['id'],
            title=new_object['title']
        )
    LOG.info("Now to modify the new_object...")

    obj = parent.get(new_object['id'], None)
    if obj is None:
        msg = "can't get new_object %s to modify it!" % new_object['id']
        LOG.info(msg)
    else:
        if obj.Type() != new_object['type']:
            LOG.info("types don't match!")
        else:
            if 'layout' in new_object:
                obj.setLayout(new_object['layout'])
            if 'exclude_from_nav' in new_object:
                obj.setExcludeFromNav(new_object['exclude_from_nav'])
            obj.reindexObject()

    aspect = ISelectableConstrainTypes(obj)
    addable = aspect.getImmediatelyAddableTypes()
    if "collective.history.useraction" not in addable:
        aspect.setConstrainTypesMode(1)  # select manually
        aspect.setImmediatelyAddableTypes(["collective.history.useraction"])
