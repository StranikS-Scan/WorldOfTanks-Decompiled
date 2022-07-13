# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/hangar/battle_result/context_menu.py
from stats_params import BATTLE_ROYALE_STATS_ENABLED
from helpers import dependency
from gui.shared import utils, events, g_eventBus
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.shared import event_dispatcher as shared_events
from skeletons.gui.lobby_context import ILobbyContext
from gui.prb_control.entities.base.ctx import PrbAction
from messenger.storage import storage_getter
from messenger.proto import proto_getter
from messenger import g_settings
from messenger.m_constants import PROTO_TYPE
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS

class VEHICLE(object):
    USER_INFO = 'userInfo'
    ADD_TO_FRIEND = 'addToFriends'
    CREATE_PRIVATE_CHANNEL = 'createPrivateChannel'
    COPY_TO_CLIP_BOARD = 'copyToClipBoard'
    CREATE_BR_SQUAD = 'createBattleRoyaleSquad'
    ADD_TO_IGNORED = 'addToIgnored'
    REMOVE_FROM_FRIENDS = 'removeFromFriends'
    REMOVE_FROM_IGNORED = 'removeFromIgnored'


class BRBattleResultContextMenu(AbstractContextMenuHandler):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, cmProxy, ctx=None):
        handlers = {VEHICLE.USER_INFO: 'showUserInfo',
         VEHICLE.ADD_TO_FRIEND: 'addToFriend',
         VEHICLE.CREATE_PRIVATE_CHANNEL: 'createPrivetChannel',
         VEHICLE.COPY_TO_CLIP_BOARD: 'copyToClipBoard',
         VEHICLE.CREATE_BR_SQUAD: 'createBRSquad',
         VEHICLE.ADD_TO_IGNORED: 'addToIgnored',
         VEHICLE.REMOVE_FROM_FRIENDS: 'removeFromFriends',
         VEHICLE.REMOVE_FROM_IGNORED: 'removeFromIgnored'}
        super(BRBattleResultContextMenu, self).__init__(cmProxy, ctx, handlers)
        self.__playerName = ctx.userName
        self.__playerDBId = ctx.databaseID

    def _generateOptions(self, ctx=None):
        options = []
        options.append(self._makeItem(VEHICLE.USER_INFO, MENU.contextmenu(VEHICLE.USER_INFO)))
        user = self.usersStorage.getUser(self.__playerDBId)
        enabledInroaming = self.__isEnabledInRoaming(self.__playerDBId)
        isFriend = user is not None and user.isFriend()
        if enabledInroaming and not isFriend:
            options.append(self._makeItem(VEHICLE.ADD_TO_FRIEND, MENU.contextmenu(VEHICLE.ADD_TO_FRIEND)))
        options.append(self._makeItem(VEHICLE.CREATE_PRIVATE_CHANNEL, MENU.contextmenu(VEHICLE.CREATE_PRIVATE_CHANNEL)))
        options.append(self._makeItem(VEHICLE.COPY_TO_CLIP_BOARD, MENU.contextmenu(VEHICLE.COPY_TO_CLIP_BOARD)))
        options.append(self._makeItem(VEHICLE.CREATE_BR_SQUAD, MENU.contextmenu(VEHICLE.CREATE_BR_SQUAD)))
        if enabledInroaming and user is not None and user.isIgnored():
            options.append(self._makeItem(VEHICLE.REMOVE_FROM_IGNORED, MENU.contextmenu(VEHICLE.REMOVE_FROM_IGNORED)))
        if enabledInroaming and isFriend:
            options.append(self._makeItem(VEHICLE.ADD_TO_IGNORED, MENU.contextmenu(VEHICLE.ADD_TO_IGNORED)))
            options.append(self._makeItem(VEHICLE.REMOVE_FROM_FRIENDS, MENU.contextmenu(VEHICLE.REMOVE_FROM_FRIENDS)))
        return options

    def showUserInfo(self):

        def onDossierReceived(databaseID, userName):
            eventOwner = 'battleRoyale' if BATTLE_ROYALE_STATS_ENABLED else None
            shared_events.showProfileWindow(databaseID, userName, selectedAlias=VIEW_ALIAS.PROFILE_STATISTICS, eventOwner=eventOwner)
            return

        shared_events.requestProfile(self.__playerDBId, self.__playerName, successCallback=onDossierReceived)

    def addToFriend(self):
        self.proto.contacts.addFriend(self.__playerDBId, self.__playerName)

    def createPrivetChannel(self):
        self.proto.contacts.createPrivateChannel(self.__playerDBId, self.__playerName)

    def copyToClipBoard(self):
        utils.copyToClipboard(self.__playerName)

    def createBRSquad(self):
        action = PrbAction(PREBATTLE_ACTION_NAME.BATTLE_ROYALE_SQUAD, accountsToInvite=(self.__playerDBId,))
        event = events.PrbActionEvent(action, events.PrbActionEvent.SELECT)
        g_eventBus.handleEvent(event, EVENT_BUS_SCOPE.LOBBY)

    def addToIgnored(self):
        self.proto.contacts.addIgnored(self.__playerDBId, self.__playerName)

    def removeFromFriends(self):
        self.proto.contacts.removeFriend(self.__playerDBId)

    def removeFromIgnored(self):
        self.proto.contacts.removeIgnored(self.__playerDBId)

    @storage_getter('users')
    def usersStorage(self):
        return None

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    def __isEnabledInRoaming(self, dbID):
        roaming = self.__lobbyContext.getServerSettings().roaming
        if g_settings.server.XMPP.isEnabled():
            isEnabled = roaming.isSameRealm(dbID)
        else:
            isEnabled = not roaming.isInRoaming() and not roaming.isPlayerInRoaming(dbID)
        return isEnabled
