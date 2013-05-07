import logging
from datetime import datetime
from plone.uuid.interfaces import IUUID, IUUIDAware
from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import newSecurityManager,\
    getSecurityManager, setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser


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
        self.mtool = getToolByName(self.context, "portal_membership", None)
        if self.mtool is None:
            LOG.info("action not kept: context is not content")
            return
        self.pstate = self.context.restrictedTraverse("plone_portal_state")
        self._security_manager = getSecurityManager()
        self._sudo("Manager")

        #check if we can use history
        if self._is_temporary():
            LOG.info('action not kept: is temporary')
            self._sudo(None)
            return
        if self._is_history():
            LOG.info('action not kept: is history')
            self._sudo(None)
            return
        if not self._is_installed():
            LOG.info('action not kept: not installed')
            self._sudo(None)
            return

        #retrieve info on the event
        what = event
        when = datetime.now()
        who = self.mtool.getAuthenticatedMember().getId()
        where = '/'.join(context.getPhysicalPath())
        if IUUIDAware.providedBy(context):
            target = "%s" % IUUID(context)
        else:
            LOG.error("context is not IUUIDAware: %s" % context)
            self._sudo(None)
            return

        #now try to save the useraction
        try:
            manager = self.context.restrictedTraverse(VIEW_NAME)
            manager.update()
        except AttributeError:
            LOG.error('action not kept: can t find the manager')
            self._sudo(None)
            return

        useraction = manager.create()
        if not useraction:
            LOG.error('action not kept: can t create useraction')
            self._sudo(None)
            return
        useraction.what = what
        useraction.when = when
        useraction.who = who
        useraction.where = where
        useraction.target = target
        if useraction.is_valid_event():
            manager.add(useraction)
        else:
            LOG.info('action not kept: is not a valid event')
        self._sudo(None)

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

    def _sudo(self, role):
        """Give admin power to the current call"""
        #TODO: verify the call is emited from the bank server
        if role is not None:
            if self.mtool.getAuthenticatedMember().has_role(role):
                return
            # http://developer.plone.org/security/permissions.html#bypassing-permission-checks
            sm = getSecurityManager()
            acl_users = getToolByName(self.context, 'acl_users')
            tmp_user = UnrestrictedUser(
                sm.getUser().getId(), '', [role], ''
            )
            tmp_user = tmp_user.__of__(acl_users)
            newSecurityManager(None, tmp_user)
        else:
            #back to the security manager in the init
            setSecurityManager(self._security_manager)
