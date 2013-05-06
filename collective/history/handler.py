import logging
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
from AccessControl.SecurityManagement import newSecurityManager,\
    getSecurityManager, setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser
from Products.DCWorkflow.interfaces import ITransitionEvent


VIEW_NAME = '@@collective.history.manager'
LOG = logging.getLogger("collective.history")


class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id.
    """
    def getId(self):
        """Return the ID of the user.
        """
        return self.getUserName()


class HandleAction(object):
    def __init__(self, context, event):
        self.context = context
        self.event = event
        self._security_manager = getSecurityManager()
        self._sudo()

        #check if we can use history
        if self._is_temporary():
            LOG.info('action not kept: is temporary')
            self._sudo(exit=1)
            return
        if self._is_history():
            LOG.info('action not kept: is history')
            self._sudo(exit=1)
            return
        if not self._is_installed():
            LOG.info('action not kept: not installed')
            self._sudo(exit=1)
            return

        #retrieve info on the event
        what = self.get_what()
        if what is None:
            LOG.info('action not kept: can t find the what')
            self._sudo(exit=1)
            return
        when = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        mtool = getToolByName(self.context, "portal_membership")
        who = mtool.getAuthenticatedMember().getId()
        where = '/'.join(context.getPhysicalPath())
        if IUUIDAware.providedBy(context):
            target = "%s" % IUUID(context)
        else:
            LOG.error("context is not IUUIDAware: %s" % context)
            self._sudo(exit=1)
            return

        #now try to save the useraction
        try:
            manager = self.context.restrictedTraverse(VIEW_NAME)
            manager.update()
        except AttributeError:
            LOG.error('action not kept: can t find the manager')
            self._sudo(exit=1)
            return

        useraction = manager.create()
        if not useraction:
            LOG.error('action not kept: can t create useraction')
            self._sudo(exit=1)
            return
        useraction.what = what
        useraction.when = when
        useraction.who = who
        useraction.where = where
        useraction.target = target
#        useraction.transactionid = ???
        manager.add(useraction)
        self._sudo(exit=1)

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
        #DCWorkflow
        elif ITransitionEvent.providedBy(self.event):
            return 'workflowstatechanged'
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

    def _is_installed(self):
        qi = getToolByName(self.context, 'portal_quickinstaller')
        addon = 'collective.history'
        return qi.isProductInstalled(addon)

    def _sudo(self, exit=0):
        """Give admin power to the current call"""
        #TODO: verify the call is emited from the bank server
        if exit == 0:
            # http://developer.plone.org/security/permissions.html#bypassing-permission-checks
            sm = getSecurityManager()
            acl_users = getToolByName(self.context, 'acl_users')
            tmp_user = UnrestrictedUser(
                sm.getUser().getId(), '', ['admin'], ''
            )
            tmp_user = tmp_user.__of__(acl_users)
            newSecurityManager(None, tmp_user)
        else:
            #back to the security manager in the init
            setSecurityManager(self._security_manager)
