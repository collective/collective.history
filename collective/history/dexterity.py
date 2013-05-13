import json
import logging

#events
from zope.lifecycleevent.interfaces import (
    IObjectCopiedEvent,
    IObjectMovedEvent,
    IObjectRemovedEvent,
    IObjectModifiedEvent,
    IObjectAddedEvent
)
from Products.DCWorkflow.interfaces import (
    IAfterTransitionEvent,
)

from collective.history.useraction import BaseUserActionWrapper
from collective.history.handler import BaseHandler

LOG = logging.getLogger("collective.history")


class DxUserActionWrapper(BaseUserActionWrapper):
    def extract_what(self):
        #dx ?
        if IObjectAddedEvent.providedBy(self.event):
            return 'created', self.get_object_added_info()
        if IObjectModifiedEvent.providedBy(self.event):
            return 'modified', self.get_object_modified_info()
        # DCWorkflow
        elif IAfterTransitionEvent.providedBy(self.event):
            return 'statechanged', self.get_transition_info()
        # zope
#        elif IObjectAddedEvent.providedBy(self.event):
#            return 'added', self.get_object_moved_info()
        elif IObjectCopiedEvent.providedBy(self.event):
            return 'copied', self.get_object_copied_info()
        elif IObjectMovedEvent.providedBy(self.event):
            return 'moved', self.get_object_moved_info()
        elif IObjectRemovedEvent.providedBy(self.event):
            return 'deleted', self.get_object_moved_info()
        else:
            #TODO: provide a query component to let addon register things
            pass
        return None, {}

    def is_valid_event(self):
        blacklist = (
            'OFS.interfaces.IObjectWillBeRemovedEvent',
            'OFS.interfaces.IObjectWillBeMovedEvent',
            'Products.CMFCore.interfaces._events.IActionSucceededEvent',
            'Products.CMFCore.interfaces._events.IActionWillBeInvokedEvent',
            'Products.DCWorkflow.interfaces.IBeforeTransitionEvent',
            'plone.dexterity.interfaces.IEditBegunEvent',
            'plone.dexterity.interfaces.IEditFinishedEvent',
        )
        for iface in blacklist:
            if self.what == iface:
                return False
        # do not keep moved event from the add process
        if self.what == 'moved':
            newName = self.event.newName
            oldName = self.event.oldName
            if not oldName:
                return False
            if not newName:
                self.data["what"] = "deleted"
        if self.what == "statechanged":
            if self.event.old_state == self.event.new_state:
                return False
        validated = super(DxUserActionWrapper, self).is_valid_event()
        return validated

    def get_object_modified_info(self):
        """
        (Pdb) self.event.descriptions
        (<zope.lifecycleevent.Attributes object at 0x109907410>,
         <zope.lifecycleevent.Attributes object at 0x10992c550>)
        (Pdb) self.event.descriptions[0].attributes
        ('IDublinCore.title',)
        (Pdb) self.event.descriptions[0].interface
        <SchemaClass plone.app.dexterity.behaviors.metadata.IBasic>
        (Pdb) self.event.descriptions[1].interface
        <InterfaceClass plone.dexterity.schema.generated.Plone_0_Document>
        (Pdb) self.event.descriptions[1].attributes
        ('text',)
        """
        if not self.event.descriptions:
            return
        info = []
        for description in self.event.descriptions:
            info.append({"attributes": description.attributes,
                         "interface": description.interface.__identifier__})
        return json.dumps(info)

    def get_object_added_info(self):
        """
        (Pdb) self.event.newName
        'capture-d2019ecran-2013-04-30-a-16-30-26.png'
        (Pdb) self.event.newParent
        <PloneSite at /Plone>
        (Pdb) self.event.object
        <File at /Plone/capture-d2019ecran-2013-04-30-a-16-30-26.png>
        (Pdb) self.event.oldName
        (Pdb) self.event.oldParent
        (Pdb) self.event
        <zope.lifecycleevent.ObjectAddedEvent object at 0x10b9a3ed0>
        """
        info = {}
        newName = self.event.newName
        if newName:
            info["newName"] = newName
        newParent = self.event.newParent
        if newParent:
            info["newParent_path"] = '/'.join(newParent.getPhysicalPath())
            info["newParent_url"] = newParent.absolute_url()
        return json.dumps(info)


class HandleDxUserAction(BaseHandler):
    """This handler is specialized for archetypes"""

    wrapper_class = DxUserActionWrapper

    def _is_temporary(self):
        return False
