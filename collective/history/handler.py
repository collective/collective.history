from datetime import datetime
from plone.uuid.interfaces import IUUID, IUUIDAware
from Products.Archetypes.interfaces.event import IObjectEditedEvent,\
    IObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from zope.lifecycleevent.interfaces import IObjectCopiedEvent, IObjectMovedEvent,\
    IObjectAddedEvent, IObjectRemovedEvent, IObjectModifiedEvent
from plone.app.controlpanel.interfaces import IConfigurationChangedEvent
from plone.app.form.interfaces import IEditSavedEvent
from plone.app.iterate.interfaces import IWorkingCopyDeletedEvent, ICheckinEvent,\
    ICheckoutEvent
from plone.registry.interfaces import IRecordModifiedEvent
from plone.schemaeditor.interfaces import ISchemaModifiedEvent


VIEW_NAME = '@@collective.history.manager'


class HandleAction(object):
    def __init__(self, context, event):
        self.context = context
        self.event = event
        #check if the context is temporary object
        if self._is_temporary():
            return
        if self._is_history():
            return

        try:
            manager = self.context.restrictedTraverse(VIEW_NAME)
            manager.update()
        except AttributeError:
            return
        useraction = manager.create()
        if not useraction:
            return
        useraction.what = self.get_what()
        useraction.when = datetime.now()
        mtool = getToolByName(self.context, "portal_membership")
        useraction.who = mtool.getAuthenticatedMember().getId()
        useraction.where = context.getPhysicalPath()
        if IUUIDAware.providedBy(context):
            useraction.target = IUUID(context)
        else:
            import pdb;pdb.set_trace()
#        useraction.transactionid = ???
        manager.add(useraction)

    def get_what(self):
        #Archetypes
        if IObjectEditedEvent.providedBy(self.event):
            return 'edited'
        elif IObjectInitializedEvent.providedBy(self.event):
            return 'added'
        #plone
        elif IConfigurationChangedEvent.providedBy(self.event):
            return 'configurationchanged'
        #plone.app.form (formlib)
        elif IEditSavedEvent.providedBy(self.event):
            return 'editsaved'
        #plone.app.iterate
        elif ICheckinEvent.providedBy(self.event):
            return 'checkedin'
        elif ICheckoutEvent.providedBy(self.event):
            return 'checkedout'
        elif IWorkingCopyDeletedEvent.providedBy(self.event):
            return 'workingcopydeleted'
        #plone.app.registry
        elif IRecordModifiedEvent.providedBy(self.event):
            return 'recordmodified'
        #plone.schemaeditor
        elif ISchemaModifiedEvent.providedBy(self.event):
            return 'schemamodified'
        #zope
        elif IObjectCopiedEvent.providedBy(self.event):
            return 'copied'
        elif IObjectMovedEvent.providedBy(self.event):
            return 'moved'
        elif IObjectAddedEvent.providedBy(self.event):
            return 'added'
        elif IObjectRemovedEvent.providedBy(self.event):
            return 'removed'
        elif IObjectModifiedEvent.providedBy(self.event):
            return 'modified'
        import pdb;pdb.set_trace()
        return 'unknown'

    def _is_temporary(self):
        portal_factory = getToolByName(self.context, 'portal_factory')
        return portal_factory.isTemporary(self.context)

    def _is_history(self):
        ptype = False
        phistory = False
        if self.context.portal_type == "collective.history.useraction":
            ptype = True
        if self.context.getId() == "portal_history":
            phistory = True
        return ptype or phistory
