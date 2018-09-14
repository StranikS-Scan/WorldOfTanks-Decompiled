# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/BattleSessionWindow.py
import BigWorld
import constants
import nations
from adisp import process
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.utils import functions
from gui.prb_control import formatters, prb_getters
from gui.prb_control.context import prb_ctx
from gui.prb_control.settings import PREBATTLE_ROSTER, REQUEST_TYPE, PREBATTLE_SETTING_NAME
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.daapi.view.meta.BattleSessionWindowMeta import BattleSessionWindowMeta
from gui import makeHtmlString

class BattleSessionWindow(BattleSessionWindowMeta):
    START_TIME_SYNC_PERIOD = 10
    NATION_ICON_PATH = '../maps/icons/filters/nations/%(nation)s.png'

    def __init__(self, ctx = None):
        super(BattleSessionWindow, self).__init__(prbName='battleSession')
        self.__setStaticData()
        self.__startTimeSyncCallbackID = None
        self.__team = None
        return

    def startListening(self):
        super(BattleSessionWindow, self).startListening()
        self.addListener(events.HideWindowEvent.HIDE_BATTLE_SESSION_WINDOW, self.__handleBSWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)

    def stopListening(self):
        super(BattleSessionWindow, self).stopListening()
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HideWindowEvent.HIDE_BATTLE_SESSION_WINDOW, self.__handleBSWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)

    def onTeamStatesReceived(self, functional, team1State, team2State):
        self.as_enableReadyBtnS(self.isReadyBtnEnabled())
        self.as_enableLeaveBtnS(self.isLeaveBtnEnabled())
        if team1State.isInQueue():
            self._closeSendInvitesWindow()

    def onRostersChanged(self, functional, rosters, full):
        self._setRosterList(rosters)
        self.__updateCommonRequirements(functional.getTeamLimits(), rosters)

    def onPlayerStateChanged(self, functional, roster, playerInfo):
        super(BattleSessionWindow, self).onPlayerStateChanged(functional, roster, playerInfo)
        self.as_setInfoS(self.__battlesWinsString, self.__arenaName, self.__firstTeam, self.__secondTeam, self.prbFunctional.getProps().getBattlesScore(), self.__eventName, self.__sessionName)
        self.__updateCommonRequirements(functional.getTeamLimits(), functional.getRosters())

    def onSettingUpdated(self, functional, settingName, settingValue):
        pass

    def canMoveToAssigned(self):
        result = self.prbFunctional.getPermissions().canAssignToTeam(self._getPlayerTeam())
        if result:
            result, _ = self.prbFunctional.getLimits().isMaxCountValid(self._getPlayerTeam(), True)
        return result

    def canMoveToUnassigned(self):
        result = self.prbFunctional.getPermissions().canAssignToTeam(self._getPlayerTeam())
        if result:
            result, _ = self.prbFunctional.getLimits().isMaxCountValid(self._getPlayerTeam(), False)
        return result

    def canKickPlayer(self):
        return self.prbFunctional.getPermissions().canKick(self._getPlayerTeam())

    def canSendInvite(self):
        return self.prbFunctional.getPermissions().canSendInvite()

    @process
    def requestToAssignMember(self, pID):
        yield self.prbDispatcher.sendPrbRequest(prb_ctx.AssignPrbCtx(pID, self._getPlayerTeam() | PREBATTLE_ROSTER.ASSIGNED, 'prebattle/assign'))

    @process
    def requestToUnassignMember(self, pID):
        yield self.prbDispatcher.sendPrbRequest(prb_ctx.AssignPrbCtx(pID, self._getPlayerTeam() | PREBATTLE_ROSTER.UNASSIGNED, 'prebattle/assign'))

    @process
    def requestToKickPlayer(self, pID):
        yield self.prbDispatcher.sendPrbRequest(prb_ctx.KickPlayerCtx(pID, 'prebattle/kick'))

    def _populate(self):
        super(BattleSessionWindow, self)._populate()
        rosters = self.prbFunctional.getRosters()
        teamLimits = self.prbFunctional.getTeamLimits()
        self.__syncStartTime()
        self._setRosterList(rosters)
        self.__updateCommonRequirements(teamLimits, rosters)
        self.as_setInfoS(self.__battlesWinsString, self.__arenaName, self.__firstTeam, self.__secondTeam, self.prbFunctional.getProps().getBattlesScore(), self.__eventName, self.__sessionName)
        self.__updateLimits(teamLimits, rosters)

    def _dispose(self):
        self.__team = None
        self.__clearSyncStartTimeCallback()
        super(BattleSessionWindow, self)._dispose()
        return

    def _getPlayerTeam(self):
        if self.__team is None:
            self.__team = self.prbFunctional.getPlayerTeam()
        return self.__team

    def _setRosterList(self, rosters):
        self.as_setRosterListS(self._getPlayerTeam(), True, self._makeAccountsData(rosters[self._getPlayerTeam() | PREBATTLE_ROSTER.ASSIGNED]))
        self.as_setRosterListS(self._getPlayerTeam(), False, self._makeAccountsData(rosters[self._getPlayerTeam() | PREBATTLE_ROSTER.UNASSIGNED]))

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
        startTime = self.prbFunctional.getSettings()[PREBATTLE_SETTING_NAME.START_TIME]
        startTime = formatters.getStartTimeLeft(startTime)
        self.as_setStartTimeS(startTime)
        if startTime > 0:
            self.__startTimeSyncCallbackID = BigWorld.callback(self.START_TIME_SYNC_PERIOD, self.__syncStartTime)

    def __setStaticData(self):
        settings = self.prbFunctional.getSettings()
        extraData = settings[PREBATTLE_SETTING_NAME.EXTRA_DATA]
        self.__arenaName = functions.getArenaShortName(settings[PREBATTLE_SETTING_NAME.ARENA_TYPE_ID])
        self.__firstTeam, self.__secondTeam = formatters.getPrebattleOpponents(extraData)
        battlesLimit = settings[PREBATTLE_SETTING_NAME.BATTLES_LIMIT]
        winsLimit = settings[PREBATTLE_SETTING_NAME.WINS_LIMIT]
        self.__battlesWinsString = '%d/%s' % (battlesLimit, str(winsLimit or '-'))
        self.__eventName = formatters.getPrebattleEventName(extraData)
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

        self.as_setCommonLimitsS(totalLvl, minTotalLvl, maxTotalLvl, playersMaxCount)
        self.as_setPlayersCountTextS(makeHtmlString('html_templates:lobby/prebattle', 'specBattlePlayersCount', {'membersCount': playersCount,
         'maxMembersCount': playersMaxCount}))

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
        levelsInfo = map(lambda v: (v['minLevel'], v['maxLevel']), levelLimits.values())
        maxCurrentLevel = max(map(lambda v: v['maxCurLevel'], levelLimits.values()))
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
        if minValue == 0 and maxValue == 0:
            return '-'
        else:
            return '{0:>s}-{1:>s}'.format(minString, maxString)
