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
from plone.uuid.interfaces import IUUID
from plone.app.controlpanel.interfaces import IConfigurationChangedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent, IObjectAddedEvent,\
    IObjectMovedEvent, IObjectRemovedEvent
from Products.CMFCore.interfaces._events import IActionSucceededEvent
from Products.DCWorkflow.interfaces import ITransitionEvent
from plone.schemaeditor.utils import SchemaModifiedEvent
from plone.registry.interfaces import IRecordModifiedEvent


LOG = logging.getLogger("collective.history")


class IUserAction(form.Schema):
    """The schema of a user action"""
    id = schema.ASCIILine(title=u"ID")
    what = schema.ASCIILine(title=u"What")
    when = schema.Datetime(title=u"When")
    where = schema.ASCIILine(title=u"Where")
    who = schema.ASCIILine(title=u"Who")
    what_info = schema.TextLine(title=u"What more info")
    transactionid = schema.ASCIILine(title=u"Transaction ID")


class UserActionWrapper(object):
    """User action wrapper of the dexterity object"""

    def __init__(self, context, manager):
        self.context = context
        self.manager = manager

    def set_what(self, value):
        if self.what is not None:
            LOG.error("try to set multiple time the what ?")
            return
        if IObjectEvent.providedBy(value):
            self.context.what_info = self.get_what_info(value)
            ifaces = list(interface.implementedBy(value.__class__))
            for iface in ifaces:
                if iface.extends(IObjectEvent):
                    self.what = str(iface.__identifier__)
                    break

        elif type(value) == str:
            new_value = value.split('.')[-1]
            if new_value.startswith('I'):
                new_value = new_value[1:]
            if new_value.startswith('Object'):
                new_value = new_value[6:]
            if new_value.endswith('Event'):
                new_value = new_value[:-5]
            self.context.what = new_value

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
        return what and when and where and who

    def get_what_info(self, event):
        #Archetypes
        if IObjectEditedEvent.providedBy(event):
            return self.get_object_modified_info(event)
        elif IObjectInitializedEvent.providedBy(event):
            return self.get_object_modified_info(event)
        #plone
        elif IConfigurationChangedEvent.providedBy(event):
            return self.get_configuration_changed_info(event)
#        #plone.app.form (formlib)
#        elif IEditSavedEvent.providedBy(event):
#            return 'editsaved'
#        #plone.app.iterate
#        elif ICheckinEvent.providedBy(event):
#            return 'checkedin'
#        elif ICheckoutEvent.providedBy(event):
#            return 'checkedout'
#        elif IWorkingCopyDeletedEvent.providedBy(event):
#            return 'workingcopydeleted'
#        #plone.app.registry
        elif IRecordModifiedEvent.providedBy(event):
            return self.get_record_modified_info(event)
        # DCWorkflow
        elif ITransitionEvent.providedBy(event):
            return self.get_transition_info(event)
        # CMFCore
        elif IActionSucceededEvent.providedBy(event):
            return self.get_action_succeed_info(event)
        # zope
        elif IObjectCopiedEvent.providedBy(event):
            return self.get_object_copied_info(event)
        elif IObjectMovedEvent.providedBy(event):
            return self.get_object_moved_info(event)
        elif IObjectAddedEvent.providedBy(event):
            return self.get_object_moved_info(event)
        elif IObjectRemovedEvent.providedBy(event):
            return self.get_object_moved_info(event)
#        elif IObjectModifiedEvent.providedBy(event):
#            return 'modified'

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
