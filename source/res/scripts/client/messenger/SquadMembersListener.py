# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/SquadMembersListener.py
# Compiled at: 2011-07-07 18:22:19
import BigWorld
import constants
from debug_utils import LOG_ERROR
from helpers import i18n
from messenger.UsersManager import UsersManager
from messenger.wrappers import SquadPlayerWrapper
import weakref

class SquadMembersListener(object):
    _SQUAD_ROSTER = 1
    _SQUAD_MAX_SIZE = 4
    __playerState = constants.PREBATTLE_ACCOUNT_STATE.UNKNOWN
    __playerRoles = 0
    __teamState = constants.PREBATTLE_TEAM_STATE.NOT_READY
    __players = {}
    __playerStatesMessageKeys = {constants.PREBATTLE_ACCOUNT_STATE.READY: '#system_messages:squad/memberReady',
     constants.PREBATTLE_ACCOUNT_STATE.NOT_READY: '#system_messages:squad/memberNotReady',
     constants.PREBATTLE_ACCOUNT_STATE.OFFLINE: '#system_messages:squad/memberOffline'}

    def __init__(self, page):
        self.__pageProxy = weakref.proxy(page)

    def start(self):
        self.__subscribeToPrebattleEvents()

    def destroy(self):
        self.__unsubscribeFromPrebattleEvents()
        self.__pageProxy = None
        self.__playerState = constants.PREBATTLE_ACCOUNT_STATE.UNKNOWN
        self.__teamState = constants.PREBATTLE_TEAM_STATE.NOT_READY
        self.__players.clear()
        return

    def isCanSendInvite(self):
        return self.__playerRoles & constants.PREBATTLE_ROLE.INVITE != 0 and not len(self.__players) >= self._SQUAD_MAX_SIZE and self.__teamState == constants.PREBATTLE_TEAM_STATE.NOT_READY

    def isCanKick(self):
        return self.__playerRoles & constants.PREBATTLE_ROLE.KICK_1 != 0

    def isCreator(self):
        return self.__playerRoles & constants.PREBATTLE_ROLE.COMPANY_CREATOR != 0

    def isPlayerReady(self):
        return self.getPlayerState() == constants.PREBATTLE_ACCOUNT_STATE.READY

    def isTeamReady(self):
        return self.getTeamState() != constants.PREBATTLE_TEAM_STATE.NOT_READY

    def getPlayerState(self):
        return self.__playerState

    def getTeamState(self):
        return self.__teamState

    def getPlayersList(self):
        return self.__players.values()

    def kickPlayer(self, accId):
        player = BigWorld.player()
        kickFunc = getattr(player, 'prb_kick', None) if player else None
        if kickFunc is not None:
            kickFunc(accId, lambda resultID: None)
        elif constants.IS_DEVELOPMENT:
            LOG_ERROR('Method BigWorld.player().prb_kick not found')
        return

    def __getClientPrebattle(self):
        player = BigWorld.player()
        if player:
            return getattr(player, 'prebattle', None)
        else:
            return None

    def __setPlayerNotReadyState(self, state):
        if state == self.__playerState:
            return
        else:
            player = BigWorld.player()
            setStateFunc = getattr(player, 'prb_notReady', None) if player else None
            if setStateFunc is not None:
                setStateFunc(state, lambda resultID: None)
            elif constants.IS_DEVELOPMENT:
                LOG_ERROR('Method BigWorld.player().prb_notReady not found')
            return

    def __getRequiredInfo(self, prebattle):
        self.__players.clear()
        settings = prebattle.settings
        if settings is not None:
            type = settings.get('type')
            self._SQUAD_MAX_SIZE = settings.get('limit_max_count', {}).get(self._SQUAD_ROSTER, 4)
            if type != constants.PREBATTLE_TYPE.SQUAD:
                return False
        players = prebattle.rosters.get(self._SQUAD_ROSTER, {})
        for accID, accInfo in players.iteritems():
            player = SquadPlayerWrapper(id=accID, **accInfo)
            player.roles = settings.get('roles', {}).get(player.dbID, 0)
            if UsersManager.isCurrentPlayer(player.dbID):
                self.__playerState = player.state
                self.__playerRoles = player.roles
            self.__players[accID] = player

        self.__teamState = prebattle.teamStates[self._SQUAD_ROSTER]
        return True

    def __subscribeToPrebattleEvents(self):
        prebattle = self.__getClientPrebattle()
        if prebattle is not None:
            if not self.__getRequiredInfo(prebattle):
                LOG_ERROR('settings not set or it is not squad')
                return
            prebattle.onRosterReceived += self.__onRosterReceived
            prebattle.onPlayerAdded += self.__onPlayerAdded
            prebattle.onPlayerRemoved += self.__onPlayerRemoved
            prebattle.onPlayerStateChanged += self.__onPlayerStateChanged
            prebattle.onSettingUpdated += self.__onSettingUpdated
            prebattle.onTeamStatesReceived += self.__onTeamStatesReceived
        elif constants.IS_DEVELOPMENT:
            LOG_ERROR("Can't subscribe to ClientPrebattle events. ClientPrebattle is None")
        return

    def __unsubscribeFromPrebattleEvents(self):
        prebattle = self.__getClientPrebattle()
        if prebattle is not None:
            prebattle.onRosterReceived += self.__onRosterReceived
            prebattle.onPlayerAdded -= self.__onPlayerAdded
            prebattle.onPlayerRemoved -= self.__onPlayerRemoved
            prebattle.onPlayerStateChanged -= self.__onPlayerStateChanged
            prebattle.onSettingUpdated -= self.__onSettingUpdated
            prebattle.onTeamStatesReceived -= self.__onTeamStatesReceived
        return

    def __onRosterReceived(self):
        prebattle = self.__getClientPrebattle()
        if prebattle is not None and self.__getRequiredInfo(prebattle):
            self.__pageProxy.refreshMemberList()
        return

    def __onPlayerStateChanged(self, id, roster, *args):
        if roster == self._SQUAD_ROSTER:
            player = self.__players.get(id)
            if player is not None:
                accInfo = self.__getClientPrebattle().rosters.get(roster).get(id)
                player.state = accInfo['state']
                player.vehCompDescr = accInfo['vehCompDescr']
                if UsersManager.isCurrentPlayer(player.dbID):
                    self.__playerState = player.state
                else:
                    messageKey = self.__playerStatesMessageKeys.get(player.state)
                    if messageKey is not None:
                        message = i18n.makeString(messageKey, player.name)
                        self.__pageProxy.addSystemMessage(message)
                self.__pageProxy.refreshMemberList()
        return

    def __onPlayerAdded(self, id, roster, *args):
        if roster == self._SQUAD_ROSTER:
            accInfo = self.__getClientPrebattle().rosters.get(roster).get(id)
            player = SquadPlayerWrapper(id=id, **accInfo)
            self.__players[id] = player
            self.__pageProxy.refreshMemberList()
            if BigWorld.player().id != id:
                message = i18n.makeString('#system_messages:squad/memberJoined', player.name)
                self.__pageProxy.addSystemMessage(message)

    def __onPlayerRemoved(self, id, roster, *args):
        if roster == self._SQUAD_ROSTER:
            player = self.__players.pop(id)
            self.__pageProxy.refreshMemberList()
            if BigWorld.player().id != id:
                message = i18n.makeString('#system_messages:squad/memberLeave', player.name)
                self.__pageProxy.addSystemMessage(message)

    def __onSettingUpdated(self, name):
        if name == 'roles':
            settings = self.__getClientPrebattle().settings
            if settings is not None:
                rolesMap = settings.get('roles', {})
                for player in self.__players.values():
                    roles = rolesMap.get(player.dbID, 0)
                    if player:
                        player.roles = roles
                        if UsersManager.isCurrentPlayer(player.dbID):
                            self.__playerState = player.state
                            self.__playerRoles = player.roles

                self.__pageProxy.refreshMemberList()
        if name == 'limit_max_count':
            settings = self.__getClientPrebattle().settings
            if settings is not None:
                self._SQUAD_MAX_SIZE = settings.get('limit_max_count', {}).get(self._SQUAD_ROSTER, 4)
                self.__pageProxy.refreshMemberList()
        return

    def __onTeamStatesReceived(self):
        self.__teamState = self.__getClientPrebattle().teamStates[self._SQUAD_ROSTER]
        self.__pageProxy.refreshMemberList()
