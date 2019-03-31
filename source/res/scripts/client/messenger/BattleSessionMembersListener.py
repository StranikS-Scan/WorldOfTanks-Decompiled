# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/BattleSessionMembersListener.py
# Compiled at: 2011-05-10 17:24:02
from account_helpers.AccountPrebattle import AccountPrebattle
import BigWorld
import constants
from debug_utils import LOG_ERROR
from helpers import time_utils
from datetime import datetime, timedelta
from helpers import i18n
from messenger.UsersManager import UsersManager
from messenger.wrappers import TeamPlayerWrapper
import weakref

class BattleSessionMembersListener(object):
    _TEAM_ROSTERS = {1: (1, 17),
     2: (2, 18)}
    _ROSTERS = (1, 17)
    _MAX_SIZE = 20
    __playerState = constants.PREBATTLE_ACCOUNT_STATE.UNKNOWN
    __playerRoles = 0
    __isFull = False
    __teamState = constants.PREBATTLE_TEAM_STATE.NOT_READY
    __players = {}
    __playerStatesMessageKeys = {constants.PREBATTLE_ACCOUNT_STATE.READY: '#system_messages:bs/memberReady',
     constants.PREBATTLE_ACCOUNT_STATE.NOT_READY: '#system_messages:bs/memberNotReady',
     constants.PREBATTLE_ACCOUNT_STATE.OFFLINE: '#system_messages:bs/memberOffline'}

    def __init__(self, page):
        self.__pageProxy = weakref.proxy(page)

    def start(self):
        self.__subscribeToPrebattleEvents()

    def destroy(self):
        self.__unsubscribeFromPrebattleEvents()
        self.__pageProxy = None
        self.__playerState = constants.PREBATTLE_ACCOUNT_STATE.UNKNOWN
        self.__isFull = False
        self.__teamState = constants.PREBATTLE_TEAM_STATE.NOT_READY
        self.__players.clear()
        return

    def isCanSendInvite(self):
        return self.__playerRoles & constants.PREBATTLE_ROLE.INVITE != 0 and not self.__isFull and self.__teamState == constants.PREBATTLE_TEAM_STATE.NOT_READY

    def isCanKick(self):
        if AccountPrebattle.getMemberTeam() == 1:
            return self.__playerRoles & constants.PREBATTLE_ROLE.KICK_1 != 0
        return self.__playerRoles & constants.PREBATTLE_ROLE.KICK_2 != 0

    def isCanAssign(self):
        if self.__teamState != constants.PREBATTLE_TEAM_STATE.NOT_READY:
            return False
        if AccountPrebattle.getMemberTeam() == 1:
            return self.__playerRoles & constants.PREBATTLE_ROLE.ASSIGNMENT_1 != 0
        return self.__playerRoles & constants.PREBATTLE_ROLE.ASSIGNMENT_2 != 0

    def isCanChangeComment(self):
        return self.__playerRoles & constants.PREBATTLE_ROLE.CHANGE_COMMENT != 0

    def isCreator(self):
        return self.__playerRoles & constants.PREBATTLE_ROLE.COMPANY_CREATOR != 0

    def isCanChangeOpenState(self):
        return self.__playerRoles & constants.PREBATTLE_ROLE.OPEN_CLOSE != 0

    def isPlayerReady(self):
        return self.getPlayerState() == constants.PREBATTLE_ACCOUNT_STATE.READY

    def isTeamReady(self):
        return self.getTeamState() != constants.PREBATTLE_TEAM_STATE.NOT_READY

    @property
    def params(self):
        params = []
        if not self.__getClientPrebattle().settings:
            settings = {}
            properties = self.__getClientPrebattle().properties or {}
            extraData = settings.get('extraData', {})
            session = AccountPrebattle.getPrebattleLocalizedData(extraData).get('session_name', '')
            description = AccountPrebattle.getPrebattleLocalizedData(extraData).get('desc', '')
            description = session and session + '\n' + description
        params.append(description)
        battlesLimit = settings.get('battlesLimit', 0)
        winsLimit = settings.get('winsLimit', '-')
        params.append('%d/%s' % (battlesLimit, str(winsLimit)))
        arenaTypeID = settings.get('arenaTypeID', False)
        if arenaTypeID:
            from ArenaType import g_cache
            params.append(g_cache.get(arenaTypeID).name)
        else:
            params.append('')
        firstTeam = extraData.get('opponents', {}).get('1', {}).get('name', '')
        secondTeam = extraData.get('opponents', {}).get('2', {}).get('name', '')
        params.append(firstTeam)
        params.append(secondTeam)
        wins = properties.get('wins', [0, 0, 0])
        params.append('%d:%d' % (wins[1], wins[2]))
        params.append(AccountPrebattle.getPrebattleLocalizedData(extraData).get('event_name', ''))
        return params

    @property
    def startTime(self):
        if not self.__getClientPrebattle().settings:
            settings = {}
            startTime = settings.get('startTime', 0)
            if startTime:
                localUTC = datetime.utcfromtimestamp(time_utils.makeLocalServerTime(startTime))
                delta = localUTC > datetime.utcnow() and datetime.utcfromtimestamp(time_utils.makeLocalServerTime(startTime)) - datetime.utcnow()
                return delta.seconds

    @property
    def totalLevelLimit(self):
        return self.__getClientPrebattle().settings.get('limit_total_level', (0, 65535))

    @property
    def maxPlayersLimit(self):
        return self.__getClientPrebattle().settings.get('limit_max_count', {}).get(AccountPrebattle.getMemberTeam(), '-')

    @property
    def isOpened(self):
        return bool(self.__getClientPrebattle().settings.get('isOpened', False))

    @property
    def creator(self):
        creator = self.__getClientPrebattle().settings.get('creator', '')
        clan = self.__getClientPrebattle().settings.get('creatorClanAbbrev', '')
        if clan != '':
            creator += '[%s]' % clan
        return creator

    def getPlayerState(self):
        return self.__playerState

    def getTeamState(self):
        return self.__teamState

    def getPlayersList(self, roster):
        return self.__players.get(roster, {}).values()

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
            if AccountPrebattle.getMemberTeam():
                self._ROSTERS = self._TEAM_ROSTERS[AccountPrebattle.getMemberTeam()]
            self._MAX_SIZE = sum([ settings.get('limit_max_count', {}).get(roster, 4) for roster in self._ROSTERS ])
            if type not in (constants.PREBATTLE_TYPE.TOURNAMENT, constants.PREBATTLE_TYPE.CLAN):
                return False
        for roster in self._ROSTERS:
            players = prebattle.rosters.get(roster, {})
            for accID, accInfo in players.iteritems():
                player = TeamPlayerWrapper(id=accID, **accInfo)
                player.roles = settings.get('roles', {}).get(player.dbID, 0)
                if not player.roles:
                    player.roles = settings.get('clanRoles', {}).get(player.clanDBID, 0)
                if not player.roles:
                    player.roles = settings.get('teamRoles', {}).get(AccountPrebattle.getMemberTeam(), 0)
                if UsersManager.isCurrentPlayer(player.dbID):
                    self.__playerState = player.state
                    self.__playerRoles = player.roles
                if not self.__players.get(roster, {}):
                    self.__players[roster] = {}
                self.__players[roster][accID] = player

        self.__isFull = sum([ len(players) for players in self.__players.values() ]) == self._MAX_SIZE
        self.__teamState = prebattle.teamStates[self._ROSTERS[0]]
        return True

    def __subscribeToPrebattleEvents(self):
        prebattle = self.__getClientPrebattle()
        if prebattle is not None:
            if not self.__getRequiredInfo(prebattle):
                LOG_ERROR('settings not set or it is not team')
                return
            prebattle.onRosterReceived += self.__onRosterReceived
            prebattle.onPlayerAdded += self.__onPlayerAdded
            prebattle.onPlayerRemoved += self.__onPlayerRemoved
            prebattle.onPlayerStateChanged += self.__onPlayerStateChanged
            prebattle.onSettingUpdated += self.__onSettingUpdated
            prebattle.onTeamStatesReceived += self.__onTeamStatesReceived
            prebattle.onPlayerRosterChanged += self.__onPlayerRosterChanged
            prebattle.onPropertiesReceived += self.__onPropertiesChange
            prebattle.onPropertyUpdated += self.__onPropertiesChange
        elif constants.IS_DEVELOPMENT:
            LOG_ERROR("Can't subscribe to ClientPrebattle events. ClientPrebattle is None")
        return

    def __unsubscribeFromPrebattleEvents(self):
        prebattle = self.__getClientPrebattle()
        if prebattle is not None:
            prebattle.onRosterReceived -= self.__onRosterReceived
            prebattle.onPlayerAdded -= self.__onPlayerAdded
            prebattle.onPlayerRemoved -= self.__onPlayerRemoved
            prebattle.onPlayerStateChanged -= self.__onPlayerStateChanged
            prebattle.onSettingUpdated -= self.__onSettingUpdated
            prebattle.onTeamStatesReceived -= self.__onTeamStatesReceived
            prebattle.onPlayerRosterChanged -= self.__onPlayerRosterChanged
            prebattle.onPropertiesReceived += self.__onPropertiesChange
            prebattle.onPropertyUpdated += self.__onPropertiesChange
        return

    def __onRosterReceived(self):
        prebattle = self.__getClientPrebattle()
        if prebattle is not None and self.__getRequiredInfo(prebattle):
            self.__pageProxy.refreshMemberList()
        return

    def __onPlayerStateChanged(self, id, roster, *args):
        if roster in self._ROSTERS:
            player = self.__players.get(roster, {}).get(id)
            if player is not None:
                accInfo = self.__getClientPrebattle().rosters.get(roster).get(id)
                player.state = accInfo['state']
                player.vehCompDescr = accInfo['vehCompDescr']
                self.__pageProxy.refreshMemberList()
                if UsersManager.isCurrentPlayer(player.dbID):
                    self.__playerState = player.state
                    self.__pageProxy.refreshSettings()
                else:
                    messageKey = self.__playerStatesMessageKeys.get(player.state)
                    if messageKey is not None:
                        message = i18n.makeString(messageKey, player.name)
                        self.__pageProxy.addSystemMessage(message)
        return

    def __onPlayerAdded(self, id, roster, *args):
        if roster in self._ROSTERS:
            accInfo = self.__getClientPrebattle().rosters.get(roster).get(id)
            player = TeamPlayerWrapper(id=id, **accInfo)
            if not self.__players.get(roster, {}):
                self.__players[roster] = {}
            self.__players[roster][id] = player
            self.__isFull = sum([ len(players) for players in self.__players.values() ]) == self._MAX_SIZE
            self.__pageProxy.refreshMemberList()
            if BigWorld.player().id != id:
                message = i18n.makeString('#system_messages:bs/memberJoined', player.name)
                self.__pageProxy.addSystemMessage(message)

    def __onPlayerRemoved(self, id, roster, *args):
        if roster in self._ROSTERS:
            player = self.__players.get(roster, {}).pop(id)
            self.__isFull = sum([ len(players) for players in self.__players.values() ]) == self._MAX_SIZE
            self.__pageProxy.refreshMemberList()
            if BigWorld.player().id != id:
                message = i18n.makeString('#system_messages:bs/memberLeave', player.name)
                self.__pageProxy.addSystemMessage(message)

    def __onSettingUpdated(self, name):
        if name == 'roles':
            settings = self.__getClientPrebattle().settings
            if settings is not None:
                rolesMap = settings.get('roles', {})
                for roster in self._ROSTERS:
                    for player in self.__players.get(roster, {}).values():
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
                self._MAX_SIZE = sum([ settings.get('limit_max_count', {}).get(roster, 4) for roster in self._ROSTERS ])
        self.__pageProxy.refreshSettings()
        return

    def __onTeamStatesReceived(self):
        self.__teamState = self.__getClientPrebattle().teamStates[self._ROSTERS[0]]
        self.__pageProxy.refreshSettings()

    def __onPlayerRosterChanged(self, accId, oldRoster, roster, actorID):
        if not self.__players.get(roster, {}):
            self.__players[roster] = {}
        player = self.__players[oldRoster][accId]
        if not self.__players[self._ROSTERS[0]].get(actorID):
            actor = self.__players[self._ROSTERS[1]].get(actorID)
            self.__players[roster][accId] = self.__players[oldRoster].pop(accId)
            self.__pageProxy.refreshMemberList()
            if actor:
                message = roster == self._ROSTERS[0] and i18n.makeString('#system_messages:memberRosterChangedMain', actor.name, player.name)
            else:
                message = i18n.makeString('#system_messages:memberRosterChangedSecond', actor.name, player.name)
            self.__pageProxy.addSystemMessage(message)

    def __onPropertiesChange(self, name=None):
        self.__pageProxy.refreshSettings()
