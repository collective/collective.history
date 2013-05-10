import logging
from datetime import datetime
from plone.uuid.interfaces import IUUID, IUUIDAware
from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import newSecurityManager,\
    getSecurityManager, setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser
from collective.history.useraction import ArchetypesUserActionWrapper
from Products.CMFCore.interfaces._events import IActionSucceededEvent


VIEW_NAME = '@@collective.history.manager'
LOG = logging.getLogger("collective.history")


class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id.
    """
    def getId(self):
        """Return the ID of the user.
        """
        return self.getUserName()


class HandleArchetypesAction(object):
    """The handler is in a class to make subtyping easier if needed
    So all the code is in the init because it's called as if it were a method;

    the responsability of the handler:
    * pre filter all non needed events like history / temporary stuff
    * sudo the current user to let anybody has write access during the
    execution of this handler (then close the sudo)
    * call the useraction manager
    * ask the manager to create a new useraction
    * fill the data of the useraction
    * save the useraction using it's manager
    """
    wrapper_class = ArchetypesUserActionWrapper

    def __init__(self, context, event):
        self.context = context
        self.event = event
        self._mtool = None
        self._pstate = None
        if self.mtool is None:
            LOG.info("action not kept: context is not content")
            return
        self._security_manager = getSecurityManager()
        self._sudo("Manager")

        if not self.constraints_validated():
            self._sudo(None)
            return

        manager = self.get_manager()
        if not manager:
            LOG.error('action not kept: no manager')
            self._sudo(None)
            return

        info = self.get_useraction_info()
        if not info:
            LOG.error('action not kept: no info')
            self._sudo(None)
            return

        useraction = manager.create()
        if not useraction:
            LOG.error('action not kept: can t create useraction')
            self._sudo(None)
            return
        #wrapper specialized for Archetypes
        useraction = self.wrapper_class(useraction)

        useraction.what = info["what"]
        useraction.when = info["when"]
        useraction.who = info["who"]
        useraction.where = info["where"]
        useraction.target = info["target"]

        if useraction.is_valid_event():
            manager.add(useraction)
        else:
            LOG.info('action not kept: is not a valid event')
            #del useraction.context
        self._sudo(None)

    def get_useraction_info(self):
        info = {}
        if IUUIDAware.providedBy(self.context):
            info["target"] = "%s" % IUUID(self.context)
        else:
            LOG.error("context is not IUUIDAware: %s" % self.context)
            return
        info["what"] = self.event
        info["when"] = datetime.now()
        info["who"] = self.mtool.getAuthenticatedMember().getId()
        info["where"] = self.context
        return info

    def get_manager(self):
        #now try to save the useraction
        try:
            manager = self.context.restrictedTraverse(VIEW_NAME)
            manager.update()
        except AttributeError:
            LOG.error('action not kept: can t find the manager')
            return
        return manager

    def constraints_validated(self):
        if self._is_temporary():
            LOG.info('action not kept: is temporary')
            return False
        if self._is_history():
            LOG.info('action not kept: is history')
            return False
        if not self._is_installed():
            LOG.info('action not kept: not installed')
            return False
        return True

    @property
    def mtool(self):
        if self._mtool is None:
            mtool = "portal_membership"
            self._mtool = getToolByName(self.context, mtool, None)
        return self._mtool

    @property
    def pstate(self):
        if self._pstate is None:
            pstate = "plone_portal_state"
            self._pstate = self.context.restrictedTraverse(pstate)
        return self._pstate

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
