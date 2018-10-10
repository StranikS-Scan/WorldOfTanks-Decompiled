# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattleTraining/epic_battle_training_room.py
from adisp import process
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.trainings import formatters
from gui.prb_control.items.prb_items import getPlayersComparator
from gui.prb_control.settings import PREBATTLE_ROSTER
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.Scaleform.daapi.view.meta.EpicBattleTrainingRoomMeta import EpicBattleTrainingRoomMeta
from gui.prb_control.entities.base.legacy.ctx import GroupAssignLegacyCtx, GroupSwapInTeamLegacyCtx, GroupSwapBetweenTeamLegacyCtx
from helpers import int2roman, i18n
from debug_utils import LOG_DEBUG
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES

class EpicBattleTrainingRoom(EpicBattleTrainingRoomMeta):

    def __init__(self, _=None):
        super(EpicBattleTrainingRoom, self).__init__()
        self._firstTime = True

    def canChangeSetting(self):
        return False

    def _addListeners(self):
        self.addListener(events.CoolDownEvent.PREBATTLE, self._handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.TrainingSettingsEvent.UPDATE_EPIC_TRAINING_SETTINGS, self._updateTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        self.removeListener(events.CoolDownEvent.PREBATTLE, self._handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.TrainingSettingsEvent.UPDATE_EPIC_TRAINING_SETTINGS, self._updateTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)

    @process
    def py_swapTeamLane(self, fromTeam, fromLane, toTeam, toLane):
        if fromTeam == toTeam:
            result = yield self.prbDispatcher.sendPrbRequest(GroupSwapInTeamLegacyCtx(fromTeam, fromLane, toLane, waitingID='prebattle/swap'))
        else:
            result = yield self.prbDispatcher.sendPrbRequest(GroupSwapBetweenTeamLegacyCtx(fromLane, waitingID='prebattle/swap'))
        if not result:
            SystemMessages.pushMessage(i18n.makeString(SYSTEM_MESSAGES.TRAINING_ERROR_SWAPTEAMS), type=SystemMessages.SM_TYPE.Error)

    @process
    def py_changeTeamLane(self, accID, team, lane):
        selectedLane = int(lane)
        roster = int(team)
        if not roster:
            roster = self.prbEntity.getRosterKey(accID)
            if not roster & PREBATTLE_ROSTER.UNASSIGNED:
                roster |= PREBATTLE_ROSTER.UNASSIGNED
        LOG_DEBUG('accID ' + str(accID) + ' lane selected ' + str(selectedLane) + ' team selected ' + str(team))
        result = yield self.prbDispatcher.sendPrbRequest(GroupAssignLegacyCtx(accID, roster, selectedLane, waitingID='prebattle/assign'))
        if not result:
            self._showActionErrorMessage()

    def onRostersChanged(self, functional, rosters, full):
        parent = super(EpicBattleTrainingRoom, self)
        parent.onRostersChanged(functional, rosters, full)
        if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1 in rosters:
            self.as_setTeam1S(self.__makeAccountsDataForLane(rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1], 1, EPIC_BATTLE.EPICTRAINING_INFO_TEAM1LANELABEL))
        if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1 in rosters:
            self.as_setTeam1S(self.__makeAccountsDataForLane(rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1], 2, EPIC_BATTLE.EPICTRAINING_INFO_TEAM1LANELABEL))
        if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1 in rosters:
            self.as_setTeam1S(self.__makeAccountsDataForLane(rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1], 3, EPIC_BATTLE.EPICTRAINING_INFO_TEAM1LANELABEL))
        if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2 in rosters:
            self.as_setTeam2S(self.__makeAccountsDataForLane(rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2], 1, EPIC_BATTLE.EPICTRAINING_INFO_TEAM2LANELABEL))
        if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2 in rosters:
            self.as_setTeam2S(self.__makeAccountsDataForLane(rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2], 2, EPIC_BATTLE.EPICTRAINING_INFO_TEAM2LANELABEL))
        if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2 in rosters:
            self.as_setTeam2S(self.__makeAccountsDataForLane(rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2], 3, EPIC_BATTLE.EPICTRAINING_INFO_TEAM2LANELABEL))
        if PREBATTLE_ROSTER.UNASSIGNED in rosters:
            self.as_setOtherS(self._makeAccountsData(rosters[PREBATTLE_ROSTER.UNASSIGNED], EPIC_BATTLE.EPICTRAINING_INFO_OTHERLABEL))
        self._updateStartButton(functional)

    def _showRosters(self, functional, rosters):
        parent = super(EpicBattleTrainingRoom, self)
        parent._showRosters(functional, rosters)
        if self._firstTime:
            self.as_setTeam1S(self.__makeAccountsDataForLane([], 1, EPIC_BATTLE.EPICTRAINING_INFO_TEAM1LANELABEL))
            self.as_setTeam2S(self.__makeAccountsDataForLane([], 1, EPIC_BATTLE.EPICTRAINING_INFO_TEAM2LANELABEL))
            self.as_setOtherS(self._makeAccountsData([], EPIC_BATTLE.EPICTRAINING_INFO_OTHERLABEL))
            self._firstTime = False
        accounts = rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1]
        if accounts:
            if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1 in rosters:
                self.as_setTeam1S(self.__makeAccountsDataForLane(accounts, 1, EPIC_BATTLE.EPICTRAINING_INFO_TEAM1LANELABEL))
            if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1 in rosters:
                self.as_setTeam1S(self.__makeAccountsDataForLane(accounts, 2, EPIC_BATTLE.EPICTRAINING_INFO_TEAM1LANELABEL))
            if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1 in rosters:
                self.as_setTeam1S(self.__makeAccountsDataForLane(accounts, 3, EPIC_BATTLE.EPICTRAINING_INFO_TEAM1LANELABEL))
        accounts = rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2]
        if accounts:
            if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2 in rosters:
                self.as_setTeam2S(self.__makeAccountsDataForLane(accounts, 1, EPIC_BATTLE.EPICTRAINING_INFO_TEAM2LANELABEL))
            if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2 in rosters:
                self.as_setTeam2S(self.__makeAccountsDataForLane(accounts, 2, EPIC_BATTLE.EPICTRAINING_INFO_TEAM2LANELABEL))
            if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2 in rosters:
                self.as_setTeam2S(self.__makeAccountsDataForLane(accounts, 3, EPIC_BATTLE.EPICTRAINING_INFO_TEAM2LANELABEL))
        accounts = rosters[PREBATTLE_ROSTER.UNASSIGNED]
        if accounts:
            self.as_setOtherS(self._makeAccountsData(accounts))
        self._updateStartButton(functional)

    def __makeAccountsDataForLane(self, accounts, lane, label=None):
        listData = []
        isPlayerSpeaking = self.app.voiceChatManager.isPlayerSpeaking
        accounts = sorted(accounts, cmp=getPlayersComparator())
        getUser = self.usersStorage.getUser
        lanecounter = [0, 0, 0]
        for account in accounts:
            lanecounter[account.group - 1] += 1
            if lane >= 0 and lane == account.group:
                vContourIcon = ''
                vShortName = ''
                vLevel = ''
                dbID = account.dbID
                user = getUser(dbID)
                if account.isVehicleSpecified():
                    vehicle = account.getVehicle()
                    vContourIcon = vehicle.iconContour
                    vShortName = vehicle.shortUserName
                    vLevel = int2roman(vehicle.level)
                listData.append({'accID': account.accID,
                 'dbID': account.dbID,
                 'userName': account.name,
                 'fullName': account.getFullName(),
                 'stateString': formatters.getPlayerStateString(account.state),
                 'icon': vContourIcon,
                 'vShortName': vShortName,
                 'vLevel': vLevel,
                 'tags': list(user.getTags()) if user else [],
                 'isPlayerSpeaking': bool(isPlayerSpeaking(account.dbID)),
                 'clanAbbrev': account.clanAbbrev,
                 'region': self.lobbyContext.getRegionCode(account.dbID),
                 'igrType': account.igrType})

        if label is not None:
            label = text_styles.main(i18n.makeString(label, lane1=str(lanecounter[0]), lane2=str(lanecounter[1]), lane3=str(lanecounter[2])))
        result = {'listData': listData,
         'teamLabel': label,
         'lane': lane}
        return result
