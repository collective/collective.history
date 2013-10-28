import logging
import json
from datetime import datetime

from zope import component
from zope import schema
from zope.component.interfaces import IObjectEvent

from plone.directives import form
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.uuid.interfaces import IUUID, IUUIDAware
from plone.app.controlpanel.interfaces import IConfigurationChangedEvent,\
    IPloneControlPanelForm
from plone.registry.interfaces import IRecordModifiedEvent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

from collective.history.adapter import IExtractWhat

LOG = logging.getLogger("collective.history")


class IUserAction(form.Schema):
    """The schema of a user action"""
    id = schema.ASCIILine(title=u"ID")
    what = schema.ASCIILine(title=u"What")
    on_what = schema.ASCIILine(title=u"On what")
    what_info = schema.TextLine(title=u"What more info")
    when = schema.Datetime(title=u"When")
    where_uri = schema.URI(title=u"Where URI")
    where_uid = schema.ASCIILine(title=u"Where UID")
    where_path = schema.ASCIILine(title=u"Where path")
    who = schema.ASCIILine(title=u"Who")
    transactionid = schema.ASCIILine(title=u"Transaction ID")


class BaseUserActionWrapper(object):
    """User action wrapper of the dexterity object"""

    def __init__(self, handler):
        self.event = None
        self.handler = handler
        self.useraction = None
        self.data = {}

    def initialize(self):
        """two step init. you create the wrapper and then intialize it"""
        self.event = self.handler.event
        self.what = self.event
        self.on_what = self.event.object
        self.when = datetime.now()
        self.who = self.handler.mtool.getAuthenticatedMember().getId()
        self.where = self.event.object

    def set_what(self, value):
        if IObjectEvent.providedBy(value):
            self.event = value
            what, what_info = self.extract_what()
            if what_info is not None:
                self.data["what_info"] = what_info
            if what is not None:
                self.data["what"] = what
            else:
                extracts = component.getAdapter(self.event, IExtractWhat)
                what, what_info = extracts()
                self.data["what"] = what
                self.data["what_info"] = what_info
        elif type(value) == str:
            self.data["what"] = value

    def get_what(self):
        return self.data.get("what", None)

    what = property(get_what, set_what)

    def set_what_info(self, value):
        if type(value) == dict:
            self.data["what_info"] = json.dumps(value)
        else:
            try:
                json.loads(value)
                self.data["what_info"] = value
            except ValueError:
                LOG.error("what_info is not valide json")

    def get_what_info(self):
        return self.data.get("what_info", {})

    what_info = property(get_what_info, set_what_info)

    def set_on_what(self, value):
        if hasattr(value, 'portal_type'):
            self.data["on_what"] = value.portal_type

    def get_on_what(self):
        return self.data.get("on_what", None)

    on_what = property(get_on_what, set_on_what)

    def set_when(self, value):
        if type(value) == datetime:
            self.data["when"] = value

    def get_when(self):
        return self.data.get("when", None)

    when = property(get_when, set_when)

    def set_where(self, value):
        if hasattr(value, 'REQUEST'):
            self.data["where_uri"] = value.REQUEST.ACTUAL_URL
        if IUUIDAware.providedBy(value):
            self.data["where_uid"] = IUUID(value)
        if hasattr(value, 'getPhysicalPath'):
            self.data["where_path"] = '/'.join(value.getPhysicalPath())

    def get_where(self):
        where = {}
        uri = self.data.get("where_uri", None)
        if uri:
            where["uri"] = uri
        uid = self.data.get("where_uid", None)
        if uid:
            where["uid"] = uid
        path = self.data.get("where_path", None)
        if path:
            where["path"] = path
        if where:
            return where

    where = property(get_where, set_where)

    @property
    def where_uri(self):
        return self.data.get("where_uri", None)

    @property
    def where_uid(self):
        return self.data.get("where_uid", None)

    @property
    def where_path(self):
        return self.data.get("where_path", None)

    def set_who(self, value):
        if type(value) == str:
            self.data["who"] = value

    def get_who(self):
        return self.data.get("who", None)

    who = property(get_who, set_who)

    def is_valid_event(self):
        what = self.data.get("what", None) is not None
        when = self.data.get("when", None) is not None
        where_uri = self.data.get("where_uri", None) is not None
        where_uid = self.data.get("where_uid", None) is not None
        where_path = self.data.get("where_path", None) is not None
        where = where_uri or where_uid or where_path
        who = self.data.get("who", None)
#        info = (what, when, where, who)
#        LOG.info("what: %s; when: %s; where: %s; who: %s" % info)
        return bool(what and when and where and who)

    def extract_what(self):
        """Return (what, what_info) from self.event
        what is supposed to be a string
        what_info is either a dict or a json string
        """
        return None, {}

    def get_object_modified_info(self):
        if self.event.descriptions:
            info = {"descriptions": self.event.descriptions}
            return json.dumps(info)

    def get_object_moved_info(self):
        oldParent = self.event.oldParent
        newParent = self.event.newParent
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
        if self.event.oldName:
            info["oldName"] = self.event.oldName
        if new_uid:
            info["newParent"] = new_uid
        if self.event.newName:
            info["newName"] = self.event.newName
        if info:
            return json.dumps(info)

    def get_configuration_changed_info(self):
        if self.event.data:
            info = {"data": self.event.data}
            try:
                return json.dumps(info)
            except TypeError:
                data = {}
                for key in self.event.data:
                    value = self.event.data[key]
                    try:
                        json.dumps({"test": value})
                        data[key] = value
                    except TypeError:
                        pass
                return json.dumps({"data": data})

    def get_object_copied_info(self):
        if self.event.original:
            info = {"original": IUUID(self.event.original)}
            return json.dumps(info)

    def get_action_succeed_info(self):
        info = {}
        if self.event.workflow:
            info["workflow"] = self.event.workflow.id
        if self.event.action:
            info["action"] = self.event.action
        if self.event.result:
            info["result"] = self.event.result
        if info:
            return json.dumps(info)

    def get_transition_info(self):
        info = {}
        if self.event.workflow:
            info["workflow"] = self.event.workflow.id
        if self.event.old_state:
            info["old_state"] = self.event.old_state.id
        if self.event.new_state:
            info["new_state"] = self.event.new_state.id
        if self.event.transition:
            info["transition"] = self.event.transition.id
        if self.event.kwargs:
            info["kwargs"] = self.event.kwargs
        if info:
            return json.dumps(info)

    def get_record_modified_info(self):
        info = {}
        if self.event.oldValue:
            info["oldValue"] = self.event.oldValue
        if self.event.newValue:
            info["newValue"] = self.event.newValue
        if info:
            return json.dumps(info)

    @property
    def title(self):
        normalizer = component.getUtility(IIDNormalizer)

        title = "%s" % self.when.strftime("%Y-%m-%d-%H-%M-%S")
        title += "-%s" % normalizer.normalize(self.who)
        title += "-%s" % normalizer.normalize(self.what.lower())
        title += "-%s" % normalizer.normalize(self.where_uid)

        if type(title) == unicode:
            return title.encode("utf-8")
        return title

    id = title


class ConfigurationUserActionWrapper(BaseUserActionWrapper):
    """This version is specialized to IPloneSiteRoot"""

    def initialize(self):
        self.event = self.handler.event
        self.what = self.event
        self.when = datetime.now()
        self.who = self.handler.mtool.getAuthenticatedMember().getId()
        self.where = self.event.context

    def set_what(self, value):
        if IConfigurationChangedEvent.providedBy(value):
            self.data["what"] = "configuration"
            self.what_info = self.get_configuration_changed_info()
            self.event = value
        elif IRecordModifiedEvent.providedBy(value):
            self.data["what"] = "registry"
            self.what_info = self.get_record_modified_info()
            self.event = value
#        elif IEditSavedEvent.providedBy(value):
#            self.data["what"] = "editsaved"
#            what_info = self.get_edit_saved()
#            self.event = value

    def get_what(self):
        return self.data.get("what", None)

    what = property(get_what, set_what)

#    def is_valid_event(self):
#        if self.what and self.what.startswith('zope.traversing.interfaces.'):
#            return False
#        return super(ConfigurationUserActionWrapper, self).is_valid_event()

    def set_where(self, value):
        if IPloneControlPanelForm.providedBy(value):
            context = value.context
            request = value.request
            self.data["where_uri"] = request.ACTUAL_URL
            if IUUIDAware.providedBy(context):
                self.data["where_uid"] = IUUID(context)
            elif hasattr(context, 'UID'):
                self.data["where_uid"] = context.UID()
            elif IPloneSiteRoot.providedBy(context):
                self.data["where_uid"] = "Plone"
            if hasattr(context, "getPhysicalPath"):
                path = "/".join(value.context.getPhysicalPath())
                self.data["where_path"] = path
        else:
            LOG.error("target is not a controlpanel form")

    def get_where(self):
        return self.data.get("where", None)

    where = property(get_where, set_where)
