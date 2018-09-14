# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/SendInvitesWindow.py
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.meta.SendInvitesWindowMeta import SendInvitesWindowMeta
from gui.Scaleform.genConsts.CONTACTS_ALIASES import CONTACTS_ALIASES
from gui import SystemMessages
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.prb_control.context import SendInvitesCtx
from gui.prb_control.prb_helpers import prbDispatcherProperty
from gui.prb_control.settings import REQUEST_TYPE, CTRL_ENTITY_TYPE
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import i18n
from messenger.gui.Scaleform.data.contacts_vo_converter import ContactConverter
from messenger.gui.Scaleform.view.ContactsTreeComponent import ContactsTreeComponent
from messenger.proto.interfaces import ISearchHandler
from messenger.proto.events import g_messengerEvents

class SendInvitesWindow(SendInvitesWindowMeta, ISearchHandler):

    def __init__(self, ctx = None):
        super(SendInvitesWindow, self).__init__()
        self._onlineMode = True
        self._ctx = ctx
        self._converter = ContactConverter()
        if 'ctrlType' in ctx:
            self._ctrlType = ctx['ctrlType']
        else:
            self._ctrlType = CTRL_ENTITY_TYPE.UNKNOWN
            LOG_ERROR('Control type is not defined', ctx)
        if 'prbName' in ctx:
            self._prbName = ctx['prbName']
        else:
            self._prbName = 'prebattle'
        if 'showClanOnly' in ctx:
            self._showClanOnly = ctx['showClanOnly']
        else:
            self._showClanOnly = False
        if 'invites' in ctx:
            self._invites = ctx['invites']
        else:
            self._invites = ()

    def getAllAvailableContacts(self):
        return self.pyTree.getMainDP().getContactsList()

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    @property
    def pyTree(self):
        tree = None
        if CONTACTS_ALIASES.CONTACTS_TREE in self.components:
            tree = self.components[CONTACTS_ALIASES.CONTACTS_TREE]
        return tree

    def showError(self, value):
        SystemMessages.pushI18nMessage(value, type=SystemMessages.SM_TYPE.Error)

    def setOnlineFlag(self, value):
        if value is False:
            self._onlineMode = None
        else:
            self._onlineMode = True
        tree = self.pyTree
        if tree:
            tree.showContacts(onlineMode=self._onlineMode, showEmptyGroups=False, showFriends=not self._showClanOnly, showGroupMenu=False)
        return

    def _getTitle(self):
        return i18n.makeString(DIALOGS.SENDINVITES_COMMON_TITLE)

    def sendInvites(self, accountsToInvite, comment):
        functional = self.prbDispatcher.getFunctional(self._ctrlType)
        if functional:
            functional.request(SendInvitesCtx(accountsToInvite, comment))
        else:
            LOG_ERROR('Functional is not found', self._ctrlType)

    def onWindowClose(self):
        self.destroy()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(SendInvitesWindow, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == CONTACTS_ALIASES.CONTACTS_TREE:
            tree = viewPy
            tree.onListStateChanged += self.__onTreeListStateChanged
            tree.showContacts(onlineMode=self._onlineMode, showEmptyGroups=False, showFriends=not self._showClanOnly, showGroupMenu=False)

    def _populate(self):
        super(SendInvitesWindow, self)._populate()
        usersEvents = g_messengerEvents.users
        usersEvents.onUserActionReceived += self.__onUserDataChanged
        usersEvents.onUserStatusUpdated += self.__onUserStatusUpdated
        self._initCooldown()
        self.as_setWindowTitleS(self._getTitle())
        self.as_setDefaultOnlineFlagS(self._onlineMode)

    def _dispose(self):
        self.pyTree.onListStateChanged -= self.__onTreeListStateChanged
        usersEvents = g_messengerEvents.users
        usersEvents.onUserActionReceived -= self.__onUserDataChanged
        usersEvents.onUserStatusUpdated -= self.__onUserStatusUpdated
        self._finiCooldown()
        super(SendInvitesWindow, self)._dispose()

    def _initCooldown(self):
        self.addListener(events.CoolDownEvent.PREBATTLE, self._handleSetCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)

    def _finiCooldown(self):
        self.removeListener(events.CoolDownEvent.PREBATTLE, self._handleSetCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)

    def _handleSetCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.SEND_INVITE:
            self.as_onReceiveSendInvitesCooldownS(event.coolDown)

    def __onUserDataChanged(self, _, user):
        self.as_onContactUpdatedS(self._converter.makeVO(user))

    def __onUserStatusUpdated(self, user):
        self.as_onContactUpdatedS(self._converter.makeVO(user))

    def __onTreeListStateChanged(self, state, isEmpty):
        if state == ContactsTreeComponent.LIST_EMPTY_STATE:
            self.as_onListStateChangedS(isEmpty)
