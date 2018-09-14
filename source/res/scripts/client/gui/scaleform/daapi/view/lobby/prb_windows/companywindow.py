# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/CompanyWindow.py
from adisp import process
from messenger.ext import passCensor
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.prb_windows import companies_dps
from gui.Scaleform.daapi.view.meta.CompanyWindowMeta import CompanyWindowMeta
from gui.Scaleform.locale.PREBATTLE import PREBATTLE
from gui.prb_control import formatters, prb_getters
from gui.prb_control.context import prb_ctx
from gui.prb_control.settings import REQUEST_TYPE, PREBATTLE_ROSTER
from gui.prb_control.settings import PREBATTLE_SETTING_NAME
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import i18n
from items.vehicles import VEHICLE_CLASS_TAGS

class CompanyWindow(CompanyWindowMeta):

    def __init__(self, ctx = None):
        super(CompanyWindow, self).__init__(prbName='company')
        self._isInvitesOpen = ctx.get('isInvitesOpen', False)

    def startListening(self):
        super(CompanyWindow, self).startListening()
        self.addListener(events.HideWindowEvent.HIDE_COMPANY_WINDOW, self.__handleCompanyWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)

    def stopListening(self):
        super(CompanyWindow, self).stopListening()
        self.removeListener(events.HideWindowEvent.HIDE_COMPANY_WINDOW, self.__handleCompanyWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)

    @process
    def requestToAssign(self, pID):
        yield self.prbDispatcher.sendPrbRequest(prb_ctx.AssignPrbCtx(pID, PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1, 'prebattle/assign'))

    @process
    def requestToUnassign(self, pID):
        yield self.prbDispatcher.sendPrbRequest(prb_ctx.AssignPrbCtx(pID, PREBATTLE_ROSTER.UNASSIGNED_IN_TEAM1, 'prebattle/assign'))

    @process
    def requestToChangeOpened(self, isOpened):
        result = yield self.prbDispatcher.sendPrbRequest(prb_ctx.ChangeOpenedCtx(isOpened, 'prebattle/change_settings'))
        if not result:
            self.as_setOpenedS(self.prbFunctional.getSettings()[PREBATTLE_SETTING_NAME.IS_OPENED])

    @process
    def requestToChangeComment(self, comment):
        result = yield self.prbDispatcher.sendPrbRequest(prb_ctx.ChangeCommentCtx(comment, 'prebattle/change_settings'))
        if not result:
            self.as_setCommentS(self.prbFunctional.getSettings()[PREBATTLE_SETTING_NAME.COMMENT])

    @process
    def requestToChangeDivision(self, divisionID):
        result = yield self.prbDispatcher.sendPrbRequest(prb_ctx.ChangeDivisionCtx(divisionID, 'prebattle/change_settings'))
        if not result:
            self.as_setDivisionS(self.prbFunctional.getSettings()[PREBATTLE_SETTING_NAME.DIVISION])

    def getCompanyName(self):
        return formatters.getCompanyName()

    def canKickPlayer(self):
        if self.prbFunctional.getTeamState(team=1).isInQueue():
            return False
        return self.prbFunctional.getPermissions().canKick(team=1)

    def canMoveToAssigned(self):
        result = self.prbFunctional.getPermissions().canAssignToTeam(team=1)
        if result:
            result, _ = self.prbFunctional.getLimits().isMaxCountValid(1, True)
        return result

    def canMoveToUnassigned(self):
        result = self.prbFunctional.getPermissions().canAssignToTeam(team=1)
        if result:
            result, _ = self.prbFunctional.getLimits().isMaxCountValid(1, False)
        return result

    def canMakeOpenedClosed(self):
        return self.prbFunctional.getPermissions().canMakeOpenedClosed()

    def canChangeComment(self):
        return self.prbFunctional.getPermissions().canChangeComment()

    def canChangeDivision(self):
        return self.prbFunctional.getPermissions().canChangeDivision()

    def onSettingUpdated(self, functional, settingName, settingValue):
        if settingName == PREBATTLE_SETTING_NAME.DIVISION:
            if not functional.isCreator():
                self.as_setDivisionS(settingValue)
        elif settingName == PREBATTLE_SETTING_NAME.IS_OPENED:
            if not functional.isCreator():
                self.as_setOpenedS(settingValue)
        elif settingName == PREBATTLE_SETTING_NAME.COMMENT:
            if not functional.isCreator():
                self.as_setCommentS(passCensor(settingValue))
        elif settingName == PREBATTLE_SETTING_NAME.LIMITS:
            self.__setLimits(functional.getRosters(), functional.getSettings().getTeamLimits(1))

    def onRostersChanged(self, functional, rosters, full):
        if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1 in rosters:
            self.as_setRosterListS(1, True, self._makeAccountsData(rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1]))
        if PREBATTLE_ROSTER.UNASSIGNED_IN_TEAM1 in rosters:
            self.as_setRosterListS(1, False, self._makeAccountsData(rosters[PREBATTLE_ROSTER.UNASSIGNED_IN_TEAM1]))
        if full:
            self.as_toggleReadyBtnS(not functional.getPlayerInfo().isReady())
        if not self.canSendInvite():
            self._closeSendInvitesWindow()
        self.__setLimits(functional.getRosters(), functional.getSettings().getTeamLimits(1))
        self.as_refreshPermissionsS()

    def onTeamStatesReceived(self, functional, team1State, team2State):
        self.as_enableReadyBtnS(self.isReadyBtnEnabled())
        self.as_enableLeaveBtnS(self.isLeaveBtnEnabled())
        self.as_refreshPermissionsS()
        if team1State.isInQueue():
            self._closeSendInvitesWindow()

    def onPlayerStateChanged(self, functional, roster, playerInfo):
        super(CompanyWindow, self).onPlayerStateChanged(functional, roster, playerInfo)
        self.__setLimits(functional.getRosters(), functional.getSettings().getTeamLimits(1))

    def _populate(self):
        super(CompanyWindow, self)._populate()
        self.__setSettings()
        rosters = self.prbFunctional.getRosters()
        self._setRosterList(rosters)
        self.__setLimits(rosters, self.prbFunctional.getSettings().getTeamLimits(1))
        if self._isInvitesOpen:
            self.showPrebattleSendInvitesWindow()

    def _dispose(self):
        super(CompanyWindow, self)._dispose()

    def _setRosterList(self, rosters):
        accounts = rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1]
        if len(accounts):
            self.as_setRosterListS(1, True, self._makeAccountsData(accounts))
        accounts = rosters[PREBATTLE_ROSTER.UNASSIGNED_IN_TEAM1]
        if len(accounts):
            self.as_setRosterListS(1, False, self._makeAccountsData(accounts))

    def __setSettings(self):
        settings = self.prbFunctional.getSettings()
        self.as_setOpenedS(settings[PREBATTLE_SETTING_NAME.IS_OPENED])
        self.as_setCommentS(passCensor(settings[PREBATTLE_SETTING_NAME.COMMENT]))
        self.as_setDivisionsListS(companies_dps.getDivisionsList(addAll=False), settings[PREBATTLE_SETTING_NAME.DIVISION])

    def __setLimits(self, rosters, teamLimits):
        totalLimit = prb_getters.getTotalLevelLimits(teamLimits)
        totalLevel = 0
        playersCount = 0
        classesLimit = dict(map(lambda vehClass: (vehClass, [0, prb_getters.getClassLevelLimits(teamLimits, vehClass)]), VEHICLE_CLASS_TAGS))
        invalidVehs = []
        if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1 in rosters:
            for playerInfo in rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1]:
                totalLevel += self.__validateVehicle(playerInfo, classesLimit, invalidVehs)
                if playerInfo.isReady():
                    playersCount += 1

        self.as_setClassesLimitsS(map(self.__makeClassLimitItem, classesLimit.iteritems()))
        self.as_setTotalLimitLabelsS(self.__makeTotalLevelString(totalLevel, totalLimit), self.__makeMinMaxString(totalLevel, totalLimit))
        self.as_setMaxCountLimitLabelS(self.__makeMaxCountLimitLabel(playersCount, prb_getters.getMaxSizeLimits(teamLimits)[0]))
        if PREBATTLE_ROSTER.UNASSIGNED_IN_TEAM1 in rosters:
            for playerInfo in rosters[PREBATTLE_ROSTER.UNASSIGNED_IN_TEAM1]:
                self.__validateVehicle(playerInfo, classesLimit, invalidVehs)

        self.as_setInvalidVehiclesS(invalidVehs)

    def __validateVehicle(self, playerInfo, classesLimit, invalidVehs):
        level = 0
        if playerInfo.isVehicleSpecified():
            vehicle = playerInfo.getVehicle()
            vehClass = vehicle.type
            level = vehicle.level
            if vehClass in classesLimit:
                current, (minLimit, maxLimit) = classesLimit[vehClass]
                classesLimit[vehClass][0] = max(current, level)
                if level not in xrange(minLimit, maxLimit + 1):
                    invalidVehs.append(playerInfo.accID)
        return level

    def __makeClassLimitItem(self, data):
        return {'vehClass': data[0],
         'limit': self.__makeMinMaxString(*data[1])}

    def __makeMinMaxString(self, value, limit):
        minValue, maxValue = limit
        if value and value < minValue:
            minString = makeHtmlString('html_templates:lobby/prebattle', 'markInvalidValue', {'value': minValue})
        else:
            minString = str(minValue)
        if value > maxValue:
            maxString = makeHtmlString('html_templates:lobby/prebattle', 'markInvalidValue', {'value': maxValue})
        else:
            maxString = str(maxValue)
        return '{0:>s}-{1:>s}'.format(minString, maxString)

    def __makeTotalLevelString(self, totalLevel, limit):
        minTotalLimit, maxTotalLimit = limit
        if minTotalLimit <= totalLevel <= maxTotalLimit:
            totalString = str(totalLevel)
        else:
            totalString = makeHtmlString('html_templates:lobby/prebattle', 'markInvalidValue', {'value': totalLevel})
        return i18n.makeString(PREBATTLE.LABELS_STATS_TOTALLEVEL, totalLevel=totalString)

    def __makeMaxCountLimitLabel(self, playersCount, maxCount):
        return makeHtmlString('html_templates:lobby/prebattle', 'companyPlayersCount', {'playersCount': playersCount,
         'maxCount': maxCount})

    def __handleCompanyWindowHide(self, _):
        self.destroy()

    def __handleSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.SET_PLAYER_STATE:
            self.as_setCoolDownForReadyButtonS(event.coolDown)
        elif event.requestID is REQUEST_TYPE.CHANGE_SETTINGS:
            self.as_setChangeSettingCoolDownS(event.coolDown)
        elif event.requestID is REQUEST_TYPE.SET_PLAYER_STATE:
            self.as_setCoolDownForReadyButtonS(event.coolDown)
