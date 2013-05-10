import logging
import json
from datetime import datetime

from zope import component
from zope import interface
from zope import schema
from zope.component.interfaces import IObjectEvent

from plone.directives import form
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.Archetypes.interfaces.event import IObjectEditedEvent,\
    IObjectInitializedEvent
from plone.uuid.interfaces import IUUID, IUUIDAware
from plone.app.controlpanel.interfaces import IConfigurationChangedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent, IObjectAddedEvent,\
    IObjectMovedEvent, IObjectRemovedEvent
from Products.CMFCore.interfaces._events import IActionSucceededEvent
from Products.DCWorkflow.interfaces import ITransitionEvent,\
    IAfterTransitionEvent
from plone.registry.interfaces import IRecordModifiedEvent
from Products.CMFCore.utils import getToolByName


LOG = logging.getLogger("collective.history")


class IUserAction(form.Schema):
    """The schema of a user action"""
    id = schema.ASCIILine(title=u"ID")
    what = schema.ASCIILine(title=u"What")
    when = schema.Datetime(title=u"When")
    where = schema.ASCIILine(title=u"Where")
    where_uid = schema.ASCIILine(title=u"Where UID")
    who = schema.ASCIILine(title=u"Who")
    what_info = schema.TextLine(title=u"What more info")
    transactionid = schema.ASCIILine(title=u"Transaction ID")


class BaseUserActionWrapper(object):
    """User action wrapper of the dexterity object"""

    def __init__(self, context):
        self.context = context
        self.event = None

    def set_what(self, value):
        if IObjectEvent.providedBy(value):
            self.event = value
            what, what_info = self.get_what_info(value)
            self.context.what_info = what_info
            if what is not None:
                self.context.what = what
            else:
                ifaces = list(interface.implementedBy(value.__class__))
                for iface in ifaces:
                    if iface.extends(IObjectEvent):
                        iface_id = str(iface.__identifier__)
                        self.context.what = iface_id
                        break

    def get_what(self):
        return self.context.what

    what = property(get_what, set_what)

    def set_when(self, value):
        if type(value) == datetime:
            self.context.when = value

    def get_when(self):
        return self.context.when

    when = property(get_when, set_when)

    def set_where(self, value):
        if hasattr(value, 'getPhysicalPath'):
            self.context.where = '/'.join(value.getPhysicalPath())
        if IUUIDAware.providedBy(value):
            self.context.where_uid = IUUID(value)
        if type(value) == str:
            self.context.where = value

    def get_where(self, value):
        return self.context.where

    where = property(get_where, set_where)

    def set_who(self, value):
        self.context.who = value

    def get_who(self):
        return self.context.who

    who = property(get_who, set_who)

    def set_target(self, value):
        self.context.target = value

    def get_target(self):
        return self.context.target

    def update_before_add(self):
        normalizer = component.getUtility(IIDNormalizer)

        title = "%s" % self.when.strftime("%Y-%m-%d")
        title += "-%s" % normalizer.normalize(self.who)
        title += "-%s" % self.what.lower()
        title += "-%s" % self.target

        self.context.setTitle(title)
        self.context.id = title

    def is_valid_event(self):
        what = self.context.what is not None
        when = self.context.when is not None
        where = self.context.where is not None
        who = self.context.who
#        info = (what, when, where, who)
#        LOG.info("what: %s; when: %s; where: %s; who: %s" % info)
        return bool(what and when and where and who)

    def get_what_info(self, event):
        raise NotImplementedError

    def get_object_modified_info(self, event):
        if event.descriptions:
            info = {"descriptions": event.descriptions}
            return json.dumps(info)

    def get_object_moved_info(self, event):
        oldParent = event.oldParent
        newParent = event.newParent
        if oldParent:
            try:
                old_uid = IUUID(oldParent)
            except:
                old_uid = '/'.join(oldParent.getPhysicalPath())
        else:
            old_uid = None
        if newParent:
            try:
                new_uid = IUUID(newParent)
            except:
                new_uid = '/'.join(newParent.getPhysicalPath())
        else:
            new_uid = None
        info = {}
        if old_uid:
            info["oldParent"] = old_uid
        if event.oldName:
            info["oldName"] = event.oldName
        if new_uid:
            info["newParent"] = new_uid
        if event.newName:
            info["newName"] = event.newName
        if info:
            return json.dumps(info)

    def get_configuration_changed_info(self, event):
        if event.data:
            info = {"data": event.data}
            return json.dumps(info)

    def get_object_copied_info(self, event):
        if event.original:
            info = {"original": IUUID(event.original)}
            return json.dumps(info)

    def get_action_succeed_info(self, event):
        info = {}
        if event.workflow:
            info["workflow"] = event.workflow.id
        if event.action:
            info["action"] = event.action
        if event.result:
            info["result"] = event.result
        if info:
            return json.dumps(info)

    def get_transition_info(self, event):
        info = {}
        if event.workflow:
            info["workflow"] = event.workflow.id
        if event.old_state:
            info["old_state"] = event.old_state.id
        if event.new_state:
            info["new_state"] = event.new_state.id
        if event.transition:
            info["transition"] = event.transition.id
        if event.kwargs:
            info["kwargs"] = event.kwargs
        if info:
            return json.dumps(info)

    def get_record_modified_info(self, event):
        info = {}
        if event.oldValue:
            info["oldValue"] = event.oldValue
        if event.newValue:
            info["newValue"] = event.newValue
        if info:
            return json.dumps(info)

    def get_what_from_event(self, str_event_iface):
        raise NotImplementedError


class PloneSiteUserActionWrapper(BaseUserActionWrapper):
    def get_what_info(self, event):
        #plone
        if IConfigurationChangedEvent.providedBy(event):
            return 'configuration', self.get_configuration_changed_info(event)
#        #plone.app.form (formlib)
#        elif IEditSavedEvent.providedBy(event):
#            return 'editsaved'
#        #plone.app.registry
        elif IRecordModifiedEvent.providedBy(event):
            return 'registry', self.get_record_modified_info(event)


class ArchetypesUserActionWrapper(BaseUserActionWrapper):
    """This is an archetypes specialized wrapper of useraction"""
    def get_what_info(self, event):
        #Archetypes
        if IObjectInitializedEvent.providedBy(event):
            return 'created', self.get_object_modified_info(event)
        elif IObjectEditedEvent.providedBy(event):
            return 'edited', self.get_object_modified_info(event)
#        #TODO: plone.app.iterate
#        elif ICheckinEvent.providedBy(event):
#            return 'checkedin'
#        elif ICheckoutEvent.providedBy(event):
#            return 'checkedout'
#        elif IWorkingCopyDeletedEvent.providedBy(event):
#            return 'workingcopydeleted'
        # DCWorkflow
        elif IAfterTransitionEvent.providedBy(event):
            return 'statechanged', self.get_transition_info(event)
        # CMFCore (useless)
#        elif IActionSucceededEvent.providedBy(event):
#            return None
#            return 'statechanged', self.get_action_succeed_info(event)
        # zope
#        elif IObjectAddedEvent.providedBy(event):
#            return 'added', self.get_object_moved_info(event)
        elif IObjectCopiedEvent.providedBy(event):
            return 'copied', self.get_object_copied_info(event)
        elif IObjectMovedEvent.providedBy(event):
            return 'moved', self.get_object_moved_info(event)
        elif IObjectRemovedEvent.providedBy(event):
            return 'deleted', self.get_object_moved_info(event)
#        elif IObjectModifiedEvent.providedBy(event):
#            return 'modified'
        else:
            #TODO: provide a query component to let addon register things
            pass
        return None, {}

    def is_valid_event(self):
        blacklist = (
            'Products.Archetypes.interfaces.event.IEditBegunEvent',
            'Products.CMFCore.interfaces._events.IActionSucceededEvent',
            'zope.lifecycleevent.interfaces.IObjectCreatedEvent',
            'zope.lifecycleevent.interfaces.IObjectAddedEvent',
            'zope.lifecycleevent.interfaces.IObjectModifiedEvent',
        )
        for iface in blacklist:
            if self.what == iface:
                return False
        # do not keep moved event from the add process
        if self.what == 'moved':
            plone_tool = getToolByName(self.event.object, 'plone_utils')
            newName = self.event.newName
            oldName = self.event.oldName
            if newName and plone_tool.isIDAutoGenerated(self.event.newName):
                return False
            if oldName and plone_tool.isIDAutoGenerated(self.event.oldName):
                return False
            #remove is moved ... kinda weird, let's fix it:
            if not newName:
                self.context.what = 'deleted'
        # do not keep dcworkflow initialization
        if self.what == 'statechanged':
            if self.event.old_state == self.event.new_state:
                return False
        validated = super(ArchetypesUserActionWrapper, self).is_valid_event()
        return validated
