# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/BattleSessionWindow.py
import functools
import BigWorld
from shared_utils import safeCancelCallback
import constants
import nations
from account_helpers import getAccountDatabaseID
from adisp import process
from constants import PREBATTLE_MAX_OBSERVERS_IN_TEAM, OBSERVERS_BONUS_TYPES, PREBATTLE_ERRORS
from gui import SystemMessages
from gui import makeHtmlString
from gui.Scaleform.daapi.view.meta.BattleSessionWindowMeta import BattleSessionWindowMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.prb_control import formatters, prb_getters
from gui.prb_control.entities.base.legacy.ctx import AssignLegacyCtx, KickPlayerCtx, SetPlayerStateCtx
from gui.prb_control.settings import PREBATTLE_ROSTER, REQUEST_TYPE, PREBATTLE_SETTING_NAME, PREBATTLE_PROPERTY_NAME, PREBATTLE_PLAYERS_COMPARATORS
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.utils import functions
from helpers import time_utils, i18n

class BattleSessionWindow(BattleSessionWindowMeta):
    START_TIME_SYNC_PERIOD = 10
    NATION_ICON_PATH = '../maps/icons/filters/nations/%(nation)s.png'

    def __init__(self, ctx=None):
        super(BattleSessionWindow, self).__init__(prbName='battleSession')
        self.__setStaticData()
        self.__startTimeSyncCallbackID = None
        self.__team = None
        self.__timerCallbackID = None
        return

    def requestToLeave(self):
        self._doLeave(True)

    def startListening(self):
        super(BattleSessionWindow, self).startListening()
        self.addListener(events.HideWindowEvent.HIDE_BATTLE_SESSION_WINDOW, self.__handleBSWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)

    def stopListening(self):
        super(BattleSessionWindow, self).stopListening()
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HideWindowEvent.HIDE_BATTLE_SESSION_WINDOW, self.__handleBSWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)

    def onTeamStatesReceived(self, entity, team1State, team2State):
        self.as_enableReadyBtnS(self.isReadyBtnEnabled())
        self.as_enableLeaveBtnS(self.isLeaveBtnEnabled())
        if team1State.isInQueue():
            self._closeSendInvitesWindow()

    def isReadyBtnEnabled(self):
        result = super(BattleSessionWindow, self).isReadyBtnEnabled()
        if self.__isTurnamentBattle:
            result = result and self.__isCurrentPlayerInAssigned()
        return result

    def onRostersChanged(self, entity, rosters, full):
        if self.__isTurnamentBattle:
            self.requestToReady(self.isPlayerReady() and self.__isCurrentPlayerInAssigned())
        self._setRosterList(rosters)
        self.__updateCommonRequirements(entity.getTeamLimits(), rosters)

    def onPlayerStateChanged(self, entity, roster, playerInfo):
        super(BattleSessionWindow, self).onPlayerStateChanged(entity, roster, playerInfo)
        rosters = entity.getRosters()
        self._setRosterList(rosters)
        self.as_setInfoS(self.__isTurnamentBattle, self.__battlesWinsString, self.__arenaName, self.__firstTeam, self.__secondTeam, self.prbEntity.getProps().getBattlesScore(), self.__eventName, self.__sessionName)
        self.__updateCommonRequirements(entity.getTeamLimits(), rosters)

    def onSettingUpdated(self, entity, settingName, settingValue):
        if settingName == PREBATTLE_SETTING_NAME.ARENA_TYPE_ID:
            self.__arenaName = functions.getArenaShortName(settingValue)
            self.as_setInfoS(self.__isTurnamentBattle, self.__battlesWinsString, self.__arenaName, self.__firstTeam, self.__secondTeam, self.prbEntity.getProps().getBattlesScore(), self.__eventName, self.__sessionName)

    def onPropertyUpdated(self, entity, propertyName, propertyValue):
        if propertyName == PREBATTLE_PROPERTY_NAME.TEAMS_POSITIONS:
            self.__showAttackDirection()

    def canMoveToAssigned(self):
        return self.prbEntity.getPermissions().canAssignToTeam(self._getPlayerTeam())

    def canMoveToUnassigned(self):
        return self.prbEntity.getPermissions().canAssignToTeam(self._getPlayerTeam())

    def canKickPlayer(self):
        return self.prbEntity.getPermissions().canKick(self._getPlayerTeam())

    def canSendInvite(self):
        return self.prbEntity.getPermissions().canSendInvite()

    def __getWinnerIfDraw(self):
        s = self.prbEntity.getSettings()
        if s[PREBATTLE_SETTING_NAME.SWITCH_TEAMS]:
            teamsPositions = self.prbEntity.getProps().teamsPositions
            winnerIfDraw = teamsPositions[0]
            if winnerIfDraw:
                return teamsPositions[winnerIfDraw]

    def __showAttackDirection(self):
        self.as_setWinnerIfDrawS(self.__getWinnerIfDraw())

    def __checkObserversCondition(self):
        observerCount = 0
        accounts = self.prbEntity.getRosters()[self._getPlayerTeam() | PREBATTLE_ROSTER.ASSIGNED]
        for account in accounts:
            if account.isVehicleSpecified():
                vehicle = account.getVehicle()
                if vehicle.isObserver:
                    observerCount += 1

        return observerCount >= PREBATTLE_MAX_OBSERVERS_IN_TEAM

    def __getPlayersMaxCount(self):
        playersMaxCount = self.prbEntity.getTeamLimits()['maxCount'][0]
        if self.prbEntity.getSettings()['bonusType'] in OBSERVERS_BONUS_TYPES:
            playersMaxCount -= PREBATTLE_MAX_OBSERVERS_IN_TEAM
        return playersMaxCount

    def __checkPlayersCondition(self):
        playerCount = 0
        accounts = self.prbEntity.getRosters()[self._getPlayerTeam() | PREBATTLE_ROSTER.ASSIGNED]
        for account in accounts:
            if account.isVehicleSpecified():
                vehicle = account.getVehicle()
                if not vehicle.isObserver:
                    playerCount += 1

        return playerCount >= self.__getPlayersMaxCount()

    def __getUnassignedPlayerByAccID(self, accID):
        accounts = self.prbEntity.getRosters()[self._getPlayerTeam() | PREBATTLE_ROSTER.UNASSIGNED]
        for account in accounts:
            if account.accID == accID:
                return account

        return None

    def __isCurrentPlayerInAssigned(self):
        dbIDs = [ playerInfo.dbID for playerInfo in self.prbEntity.getRosters()[self._getPlayerTeam() | PREBATTLE_ROSTER.ASSIGNED] ]
        return getAccountDatabaseID() in dbIDs

    def requestToAssignMember(self, pID):
        playerInfo = self.__getUnassignedPlayerByAccID(pID)
        if playerInfo is not None and playerInfo.isReady():
            observersCondition = self.__checkObserversCondition()
            playersCondition = self.__checkPlayersCondition()
            if observersCondition and playersCondition:
                self._showActionErrorMessage(PREBATTLE_ERRORS.ROSTER_LIMIT)
                return
            if playerInfo.isVehicleSpecified() and playerInfo.getVehicle().isObserver:
                if observersCondition:
                    self._showActionErrorMessage(PREBATTLE_ERRORS.OBSERVERS_LIMIT)
                    return
            elif playersCondition:
                self._showActionErrorMessage(PREBATTLE_ERRORS.PLAYERS_LIMIT)
                return
        self.__doRequestToAssignMember(pID)
        return

    @process
    def requestToReady(self, value):
        if value:
            waitingID = 'prebattle/player_ready'
        else:
            waitingID = 'prebattle/player_not_ready'
        ctx = SetPlayerStateCtx(value, waitingID=waitingID)
        result = yield self.prbDispatcher.sendPrbRequest(ctx)
        if result:
            self.as_toggleReadyBtnS(not value)
        else:
            self._showActionErrorMessage(ctx.getLastErrorString())

    @process
    def __doRequestToAssignMember(self, pID):
        ctx = AssignLegacyCtx(pID, self._getPlayerTeam() | PREBATTLE_ROSTER.ASSIGNED, 'prebattle/assign')
        result = yield self.prbDispatcher.sendPrbRequest(ctx)
        if not result:
            self._showActionErrorMessage(ctx.getLastErrorString())

    @process
    def requestToUnassignMember(self, pID):
        yield self.prbDispatcher.sendPrbRequest(AssignLegacyCtx(pID, self._getPlayerTeam() | PREBATTLE_ROSTER.UNASSIGNED, 'prebattle/assign'))

    @process
    def requestToKickPlayer(self, pID):
        yield self.prbDispatcher.sendPrbRequest(KickPlayerCtx(pID, 'prebattle/kick'))

    def _populate(self):
        super(BattleSessionWindow, self)._populate()
        rosters = self.prbEntity.getRosters()
        teamLimits = self.prbEntity.getTeamLimits()
        self.__syncStartTime()
        self._setRosterList(rosters)
        self.__updateCommonRequirements(teamLimits, rosters)
        self.as_setInfoS(self.__isTurnamentBattle, self.__battlesWinsString, self.__arenaName, self.__firstTeam, self.__secondTeam, self.prbEntity.getProps().getBattlesScore(), self.__eventName, self.__sessionName)
        self.__updateLimits(teamLimits, rosters)
        self.__showAttackDirection()

    def _dispose(self):
        self.__team = None
        self.__clearSyncStartTimeCallback()
        self.__cancelTimerCallback()
        super(BattleSessionWindow, self)._dispose()
        return

    def _getPlayerTeam(self):
        if self.__team is None:
            self.__team = self.prbEntity.getPlayerTeam()
        return self.__team

    def _setRosterList(self, rosters):
        playerTeam = self._getPlayerTeam()
        self.as_setRosterListS(playerTeam, True, self._makeAccountsData(rosters[playerTeam | PREBATTLE_ROSTER.ASSIGNED], PREBATTLE_PLAYERS_COMPARATORS.OBSERVERS_TO_BOTTOM))
        self.as_setRosterListS(playerTeam, False, self._makeAccountsData(rosters[playerTeam | PREBATTLE_ROSTER.UNASSIGNED]))

    def __handleBSWindowHide(self, _):
        self.destroy()

    def __handleSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.SET_PLAYER_STATE:
            self.as_setCoolDownForReadyButtonS(event.coolDown)

    def __clearSyncStartTimeCallback(self):
        if self.__startTimeSyncCallbackID is not None:
            BigWorld.cancelCallback(self.__startTimeSyncCallbackID)
            self.__startTimeSyncCallbackID = None
        return

    def __syncStartTime(self):
        self.__clearSyncStartTimeCallback()
        if self.prbEntity is None:
            return
        else:
            startTime = self.prbEntity.getSettings()[PREBATTLE_SETTING_NAME.START_TIME]
            startTime = formatters.getStartTimeLeft(startTime)
            self.__cancelTimerCallback()
            self.__showTimer(startTime)
            if startTime > 0:
                self.__startTimeSyncCallbackID = BigWorld.callback(self.START_TIME_SYNC_PERIOD, self.__syncStartTime)
            return

    def __showTimer(self, timeLeft):
        self.__timerCallbackID = None
        self.as_setStartTimeS(time_utils.getTimeLeftFormat(timeLeft))
        if timeLeft > 0:
            self.__timerCallbackID = BigWorld.callback(1, functools.partial(self.__showTimer, timeLeft - 1))
        return

    def __cancelTimerCallback(self):
        if self.__timerCallbackID is not None:
            safeCancelCallback(self.__timerCallbackID)
            self.__timerCallbackID = None
        return

    def __setStaticData(self):
        settings = self.prbEntity.getSettings()
        extraData = settings[PREBATTLE_SETTING_NAME.EXTRA_DATA]
        self.__arenaName = functions.getArenaShortName(settings[PREBATTLE_SETTING_NAME.ARENA_TYPE_ID])
        self.__firstTeam, self.__secondTeam = formatters.getPrebattleOpponents(extraData)
        battlesLimit = settings[PREBATTLE_SETTING_NAME.BATTLES_LIMIT]
        winsLimit = settings[PREBATTLE_SETTING_NAME.WINS_LIMIT]
        self.__battlesWinsString = '%d/%s' % (battlesLimit, str(winsLimit or '-'))
        self.__eventName = formatters.getPrebattleEventName(extraData)
        clansToInvite = settings['clansToInvite']
        self.__isTurnamentBattle = not clansToInvite
        self.__sessionName = formatters.getPrebattleSessionName(extraData)
        description = formatters.getPrebattleDescription(extraData)
        if description:
            self.__sessionName = '%s\n%s' % (self.__sessionName, description)

    def __updateCommonRequirements(self, teamLimits, rosters):
        minTotalLvl, maxTotalLvl = prb_getters.getTotalLevelLimits(teamLimits)
        playersMaxCount = prb_getters.getMaxSizeLimits(teamLimits)[0]
        totalLvl = 0
        playersCount = 0
        for roster, players in rosters.iteritems():
            if roster ^ self.__team == PREBATTLE_ROSTER.ASSIGNED:
                for player in players:
                    if player.isReady():
                        playersCount += 1
                    if player.isVehicleSpecified():
                        totalLvl += player.getVehicle().level

        if minTotalLvl <= totalLvl and totalLvl <= maxTotalLvl:
            teamLevelStr = text_styles.main(str(totalLvl))
        else:
            teamLevelStr = text_styles.error(str(totalLvl))
        self.as_setCommonLimitsS(teamLevelStr, playersMaxCount)
        self.as_setPlayersCountTextS(makeHtmlString('html_templates:lobby/prebattle', 'specBattlePlayersCount', {'membersCount': playersCount,
         'maxMembersCount': playersMaxCount}))
        playerTeam = len(self._makeAccountsData(rosters[self._getPlayerTeam() | PREBATTLE_ROSTER.ASSIGNED]))
        playersStyleFunc = text_styles.main if playerTeam < playersMaxCount else text_styles.error
        playersCountStr = playersStyleFunc('%d/%d' % (playerTeam, playersMaxCount))
        self.as_setTotalPlayersCountS(playersCountStr)

    def __updateLimits(self, teamLimits, rosters):
        levelLimits = {}
        for className in constants.VEHICLE_CLASSES:
            classLvlLimits = prb_getters.getClassLevelLimits(teamLimits, className)
            levelLimits[className] = {'minLevel': classLvlLimits[0],
             'maxLevel': classLvlLimits[1],
             'maxCurLevel': 0}

        for roster, players in rosters.iteritems():
            if roster & PREBATTLE_ROSTER.ASSIGNED:
                for player in players:
                    vehicle = player.getVehicle()
                    levelLimits[vehicle.type]['maxCurLevel'] = max(levelLimits[vehicle.type]['maxCurLevel'], vehicle.level)

        strlevelLimits = dict(((t, '') for t in constants.VEHICLE_CLASSES))
        classesLimitsAreIdentical, commonInfo = self.__compareVehicleLimits(levelLimits)
        if classesLimitsAreIdentical:
            strlevelLimits['lightTank'] = self.__makeMinMaxString(commonInfo)
        else:
            for className in constants.VEHICLE_CLASSES:
                strlevelLimits[className] = self.__makeMinMaxString(levelLimits[className])

        self.as_setClassesLimitsS(strlevelLimits, classesLimitsAreIdentical)
        nationsLimits = prb_getters.getNationsLimits(teamLimits)
        nationsLimitsResult = None
        if nationsLimits is not None and len(nationsLimits) != len(nations.AVAILABLE_NAMES):
            nationsLimitsResult = []
            for nation in nationsLimits:
                nationsLimitsResult.append({'icon': self.NATION_ICON_PATH % {'nation': nation},
                 'tooltip': MENU.nations(nation)})

        self.as_setNationsLimitsS(nationsLimitsResult)
        return

    def __compareVehicleLimits(self, levelLimits):
        levelsInfo = [ (v['minLevel'], v['maxLevel']) for v in levelLimits.values() ]
        maxCurrentLevel = max((v['maxCurLevel'] for v in levelLimits.values()))
        for lvlInfo in levelsInfo[1:]:
            if lvlInfo != levelsInfo[0]:
                return (False, None)

        return (True, {'minLevel': levelsInfo[0][0],
          'maxLevel': levelsInfo[0][1],
          'maxCurLevel': maxCurrentLevel})

    def __makeMinMaxString(self, classLimits):
        minValue = classLimits['minLevel']
        maxValue = classLimits['maxLevel']
        value = classLimits['maxCurLevel']
        if value and value < minValue:
            minString = makeHtmlString('html_templates:lobby/prebattle', 'markInvalidValue', {'value': minValue})
        else:
            minString = str(minValue)
        if value > maxValue:
            maxString = makeHtmlString('html_templates:lobby/prebattle', 'markInvalidValue', {'value': maxValue})
        else:
            maxString = str(maxValue)
        return '-' if minValue == 0 and maxValue == 0 else '{0:>s}-{1:>s}'.format(minString, maxString)

    def _showActionErrorMessage(self, errType):
        errors = {PREBATTLE_ERRORS.ROSTER_LIMIT: (SYSTEM_MESSAGES.BATTLESESSION_ERROR_LIMITS, {}),
         PREBATTLE_ERRORS.PLAYERS_LIMIT: (SYSTEM_MESSAGES.BATTLESESSION_ERROR_ADDPLAYER, {'numPlayers': self.__getPlayersMaxCount()}),
         PREBATTLE_ERRORS.OBSERVERS_LIMIT: (SYSTEM_MESSAGES.BATTLESESSION_ERROR_ADDOBSERVER, {'numPlayers': PREBATTLE_MAX_OBSERVERS_IN_TEAM})}
        errMsg = errors.get(errType)
        if errMsg:
            SystemMessages.pushMessage(i18n.makeString(errMsg[0], **errMsg[1]), type=SystemMessages.SM_TYPE.Error)
