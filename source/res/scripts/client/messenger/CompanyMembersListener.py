# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/CompanyMembersListener.py
# Compiled at: 2011-11-29 14:05:19
import BigWorld
import constants
from debug_utils import LOG_ERROR
from helpers import i18n
from messenger import passCensor
from messenger.UsersManager import UsersManager
from messenger.wrappers import TeamPlayerWrapper
import weakref

class CompanyMembersListener(object):
    _ROSTERS = (1, 17)
    _MAX_SIZE = 20
    __playerState = constants.PREBATTLE_ACCOUNT_STATE.UNKNOWN
    __playerRoles = 0
    __playerRoster = None
    __isFull = False
    __teamState = constants.PREBATTLE_TEAM_STATE.NOT_READY
    __players = {}
    __playerStatesMessageKeys = {constants.PREBATTLE_ACCOUNT_STATE.READY: '#system_messages:team/memberReady',
     constants.PREBATTLE_ACCOUNT_STATE.NOT_READY: '#system_messages:team/memberNotReady',
     constants.PREBATTLE_ACCOUNT_STATE.OFFLINE: '#system_messages:team/memberOffline'}
    division = constants.PREBATTLE_COMPANY_DIVISION.ABSOLUTE

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
        return self.__playerRoles & constants.PREBATTLE_ROLE.KICK_1 != 0

    def isCanAssign(self):
        return self.__teamState == constants.PREBATTLE_TEAM_STATE.NOT_READY and self.__playerRoles & constants.PREBATTLE_ROLE.ASSIGNMENT_1 != 0

    def isCanChangeComment(self):
        return self.__playerRoles & constants.PREBATTLE_ROLE.CHANGE_COMMENT != 0

    def isCanChangeDivision(self):
        return self.__playerRoles & constants.PREBATTLE_ROLE.CHANGE_DIVISION != 0 and not self.isTeamReady()

    def isCreator(self):
        return self.__playerRoles & constants.PREBATTLE_ROLE.COMPANY_CREATOR != 0

    def isCanChangeOpenState(self):
        return self.__playerRoles & constants.PREBATTLE_ROLE.OPEN_CLOSE != 0

    def isPlayerReady(self):
        return self.getPlayerState() == constants.PREBATTLE_ACCOUNT_STATE.READY

    def isTeamReady(self):
        return self.getTeamState() != constants.PREBATTLE_TEAM_STATE.NOT_READY

    def isInMainRoster(self):
        return self.__playerRoster == self._ROSTERS[0]

    @property
    def comment(self):
        prebattle = self.__getClientPrebattle()
        comment = prebattle.settings.get('comment', '') if prebattle is not None else ''
        if self.isCreator():
            return comment
        else:
            return passCensor(comment)

    @property
    def isOpened(self):
        prebattle = self.__getClientPrebattle()
        if prebattle is not None:
            return bool(prebattle.settings.get('isOpened', False))
        else:
            return False

    @property
    def creator(self):
        prebattle = self.__getClientPrebattle()
        creator = ''
        if prebattle is not None:
            creator = prebattle.settings.get('creator', '')
            clan = prebattle.settings.get('creatorClanAbbrev', '')
            if clan != '':
                creator += '[%s]' % clan
        return creator

    @property
    def creatorName(self):
        prebattle = self.__getClientPrebattle()
        if prebattle is not None:
            return prebattle.settings.get('creator', '')
        else:
            return ''

    def getLevelsLimits(self):
        prebattle = self.__getClientPrebattle()
        if prebattle is not None:
            return prebattle.settings.get('limit_level', (1, 10))
        else:
            return (1, 10)

    def getLightTanksLevelsLimits(self):
        prebattle = self.__getClientPrebattle()
        if prebattle is not None:
            mn, mx = self.getLevelsLimits()
            return prebattle.settings.get('limit_class_level', {}).get('lightTank', (mn, mx))
        else:
            return (1, 10)

    def getMediumTanksLevelsLimits(self):
        prebattle = self.__getClientPrebattle()
        if prebattle is not None:
            mn, mx = self.getLevelsLimits()
            return prebattle.settings.get('limit_class_level', {}).get('mediumTank', (mn, mx))
        else:
            return (1, 10)

    def getHeavyTanksLevelsLimits(self):
        prebattle = self.__getClientPrebattle()
        if prebattle is not None:
            mn, mx = self.getLevelsLimits()
            return prebattle.settings.get('limit_class_level', {}).get('heavyTank', (mn, mx))
        else:
            return (1, 10)

    def getSPGLevelsLimits(self):
        prebattle = self.__getClientPrebattle()
        if prebattle is not None:
            mn, mx = self.getLevelsLimits()
            return prebattle.settings.get('limit_class_level', {}).get('SPG', (mn, mx))
        else:
            return (1, 10)

    def getATSPGLevelsLimits(self):
        prebattle = self.__getClientPrebattle()
        if prebattle is not None:
            mn, mx = self.getLevelsLimits()
            return prebattle.settings.get('limit_class_level', {}).get('AT-SPG', (mn, mx))
        else:
            return (1, 10)

    def getTotalLevelsLimits(self):
        prebattle = self.__getClientPrebattle()
        if prebattle is not None:
            return prebattle.settings.get('limit_total_level', (1, 150))
        else:
            return (1, 150)

    @property
    def maxCountLimit(self):
        prebattle = self.__getClientPrebattle()
        if prebattle is not None:
            return prebattle.settings.get('limit_max_Count', {}).get(self._ROSTERS[0], 15)
        else:
            return 15

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
            self._MAX_SIZE = sum([ settings.get('limit_max_count', {}).get(roster, 4) for roster in self._ROSTERS ])
            if type != constants.PREBATTLE_TYPE.COMPANY:
                return False
            self.division = settings.get('division', constants.PREBATTLE_COMPANY_DIVISION.ABSOLUTE)
        for roster in self._ROSTERS:
            players = prebattle.rosters.get(roster, {})
            for accID, accInfo in players.iteritems():
                player = TeamPlayerWrapper(id=accID, **accInfo)
                player.roles = settings.get('roles', {}).get(player.dbID, 0)
                if UsersManager.isCurrentPlayer(player.dbID):
                    self.__playerState = player.state
                    self.__playerRoles = player.roles
                    self.__playerRoster = roster
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
                message = i18n.makeString('#system_messages:team/memberJoined', player.name)
                self.__pageProxy.addSystemMessage(message)

    def __onPlayerRemoved(self, id, roster, *args):
        if roster in self._ROSTERS:
            player = self.__players.get(roster, {}).pop(id)
            self.__isFull = sum([ len(players) for players in self.__players.values() ]) == self._MAX_SIZE
            self.__pageProxy.refreshMemberList()
            if BigWorld.player().id != id:
                message = i18n.makeString('#system_messages:team/memberLeave', player.name)
                self.__pageProxy.addSystemMessage(message)

    def __onSettingUpdated(self, name):
        settings = self.__getClientPrebattle().settings
        if name in ('roles', 'limit_level', 'limit_total_level'):
            if settings is not None:
                rolesMap = settings.get('roles', {})
                if name == 'roles':
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
            if settings is not None:
                self._MAX_SIZE = sum([ settings.get('limit_max_count', {}).get(roster, 4) for roster in self._ROSTERS ])
        if name == 'division':
            if settings is not None:
                self.division = settings.get('division', constants.PREBATTLE_COMPANY_DIVISION.ABSOLUTE)
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
            if UsersManager.isCurrentPlayer(player.dbID):
                self.__playerRoster = roster
                self.__pageProxy.refreshSettings()
            self.__players[roster][accId] = self.__players[oldRoster].pop(accId)
            self.__pageProxy.refreshMemberList()
            if actor:
                message = roster == self._ROSTERS[0] and i18n.makeString('#system_messages:memberRosterChangedMain', actor.name, player.name)
            else:
                message = i18n.makeString('#system_messages:memberRosterChangedSecond', actor.name, player.name)
            self.__pageProxy.addSystemMessage(message)
