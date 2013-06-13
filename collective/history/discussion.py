from zope.lifecycleevent.interfaces import (
    IObjectAddedEvent,
    IObjectRemovedEvent,
)
from plone.app.discussion.comment import IComment
from plone.uuid.interfaces import IUUID, IUUIDAware

from collective.history.useraction import BaseUserActionWrapper
from collective.history.handler import BaseHandler


class DiscussionUserActionWrapper(BaseUserActionWrapper):
    """Discussion specialized wrapper of useraction"""

    def set_what(self, value):
        if IObjectAddedEvent.providedBy(value):
            self.data["what"] = "added"
            self.event = value
        elif IObjectRemovedEvent.providedBy(value):
            self.data["what"] = "removed"
            self.event = value

    def get_what(self):
        return self.data.get("what", None)

    what = property(get_what, set_what)

    def set_where(self, value):
        if IComment.providedBy(value):
            if hasattr(value, 'REQUEST'):
                self.data["where_uri"] = value.REQUEST.ACTUAL_URL
            if IUUIDAware.providedBy(value):
                self.data["where_uid"] = IUUID(value)
            if hasattr(value, "getPhysicalPath"):
                path = "/".join(value.getPhysicalPath())
                self.data["where_path"] = path

    def get_where(self, value):
        return self.data.get('where', None)

    where = property(get_where, set_where)


class HandleDiscussionUserAction(BaseHandler):
    """This handler is specialized for discussion"""
    wrapper_class = DiscussionUserActionWrapper

    def _is_history(self):
        pass

    def _is_temporary(self):
        pass
