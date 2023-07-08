# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/stats_exchange/stats_ctrl.py
import BigWorld
from account_helpers.settings_core.settings_constants import GAME
from account_helpers.settings_core.settings_constants import GRAPHICS
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import broker
from gui.Scaleform.daapi.view.meta.BattleStatisticDataControllerMeta import BattleStatisticDataControllerMeta
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.battle_control.arena_info import team_overrides
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.arena_info.interfaces import IVehiclesAndPersonalInvitationsController
from gui.battle_control.arena_info.settings import INVALIDATE_OP
from gui.battle_control.arena_info.settings import PERSONAL_STATUS
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, BATTLE_CTRL_ID
from gui.server_events.events_helpers import MISSIONS_STATES
from gui.shared.formatters import text_styles, icons
from helpers import dependency
from messenger.proto.events import g_messengerEvents
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
_BOOL_SETTING_TO_BIT = ((GAME.PLAYERS_PANELS_SHOW_LEVELS, PERSONAL_STATUS.IS_VEHICLE_LEVEL_SHOWN), (GAME.SHOW_VEHICLES_COUNTER, PERSONAL_STATUS.IS_VEHICLE_COUNTER_SHOWN), (GRAPHICS.COLOR_BLIND, PERSONAL_STATUS.IS_COLOR_BLIND))

def _makePersonalStatusFromSettingsStorage(settingsCore):
    getter = settingsCore.getSetting
    status = PERSONAL_STATUS.DEFAULT
    for key, bit in _BOOL_SETTING_TO_BIT:
        if getter(key):
            status |= bit

    return status


def _makePersonalStatusFromSettingsDiff(diff):
    added, removed = (0, 0)
    for key, bit in _BOOL_SETTING_TO_BIT:
        if key in diff:
            value = diff[key]
            if value:
                added |= bit
            else:
                removed |= bit

    return (added, removed)


def _createExchangeCtx(battleCtx):
    return broker.ExchangeCtx(battleCtx.createPlayerFullNameFormatter(showVehShortName=False))


class BattleStatisticsDataController(BattleStatisticDataControllerMeta, IVehiclesAndPersonalInvitationsController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(BattleStatisticsDataController, self).__init__()
        self._battleCtx = None
        self._arenaVisitor = None
        self._personalInfo = None
        self._exchangeBroker = None
        self._statsCollector = None
        self.__personalStatus = PERSONAL_STATUS.DEFAULT
        self.__reusable = {}
        self.__avatarTeam = None
        self.__isPMBattleProgressEnabled = False
        self.__isDogTagInBattleEnabled = False
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.GUI

    def getStatsCollector(self):
        return self._statsCollector

    def startControl(self, battleCtx, arenaVisitor):
        self._personalInfo = team_overrides.PersonalInfo()
        self._battleCtx = battleCtx
        self._arenaVisitor = arenaVisitor
        exchangeCtx = _createExchangeCtx(self._battleCtx)
        self._exchangeBroker = self._createExchangeBroker(exchangeCtx)
        self._statsCollector = self._createExchangeCollector()
        if BigWorld.player().isObserver():
            self.__avatarTeam = BigWorld.player().team

    def stopControl(self):
        if self._exchangeBroker is not None:
            self._exchangeBroker.destroy()
            self._exchangeBroker = None
        self._statsCollector = None
        self._battleCtx = None
        self._arenaVisitor = None
        return

    def __isEnemyTeam(self, arenaDP, team):
        return team != self.__avatarTeam if self.__avatarTeam is not None else arenaDP.isEnemyTeam(team)

    def invalidateArenaInfo(self):
        self.__setArenaDescription()
        arenaDP = self._battleCtx.getArenaDP()
        self.invalidateVehiclesInfo(arenaDP)
        self.invalidateVehiclesStats(arenaDP)

    def invalidateVehiclesInfo(self, arenaDP):
        self.__updatePersonalPrebattleID(arenaDP)
        self.__updateSquadRestrictions()
        exchange = self._exchangeBroker.getVehiclesInfoExchange()
        collection = vos_collections.VehiclesInfoCollection()
        for vInfoVO in collection.iterator(arenaDP):
            if vInfoVO.isObserver():
                continue
            isEnemy, overrides = self.__getTeamOverrides(vInfoVO, arenaDP)
            with exchange.getCollectedComponent(isEnemy) as item:
                item.addVehicleInfo(vInfoVO, overrides)

        exchange.addSortIDs(arenaDP, False, True)
        data = exchange.get()
        if data:
            self.as_setVehiclesDataS(data)

    def invalidateVehiclesStats(self, arenaDP):
        exchange = self._exchangeBroker.getVehiclesStatsExchange()
        collection = vos_collections.VehiclesItemsCollection()
        for vos in collection.iterator(arenaDP):
            vInfoVO, vStatsVO = vos
            if vInfoVO.isObserver():
                continue
            self._statsCollector.addVehicleStatsUpdate(vInfoVO, vStatsVO)
            isEnemy = self.__isEnemyTeam(arenaDP, vInfoVO.team)
            with exchange.getCollectedComponent(isEnemy) as item:
                item.addStats(vStatsVO)

        exchange.addTotalStats(self._statsCollector.getTotalStats(self._arenaVisitor, self.sessionProvider))
        exchange.addSortIDs(arenaDP, False, True)
        data = exchange.get(forced=True)
        if self.sessionProvider.isReplayPlaying and not data:
            self.as_resetFragsS()
        elif data:
            self.as_setFragsS(data)

    def addVehicleInfo(self, vo, arenaDP):
        isEnemy, overrides = self.__getTeamOverrides(vo, arenaDP)
        exchange = self._exchangeBroker.getVehiclesInfoExchange()
        with exchange.getCollectedComponent(isEnemy) as item:
            item.addVehicleInfo(vo, overrides)
        exchange.addSortIDs(arenaDP, isEnemy)
        data = exchange.get()
        if data:
            self.as_addVehiclesInfoS(data)

    def updateVehiclesInfo(self, updated, arenaDP):
        shared = INVALIDATE_OP.NONE
        for f, _ in updated:
            shared |= f

        if shared & INVALIDATE_OP.PREBATTLE_CHANGED > 0:
            self.__updatePersonalPrebattleID(arenaDP)
            self.__updateSquadRestrictions()
        exchange = self._exchangeBroker.getVehiclesInfoExchange()
        reusable = set()
        for flags, vInfoVO in updated:
            if vInfoVO.isObserver():
                continue
            isEnemy, overrides = self.__getTeamOverrides(vInfoVO, arenaDP)
            if flags & INVALIDATE_OP.SORTING > 0:
                reusable.add(isEnemy)
            with exchange.getCollectedComponent(isEnemy) as item:
                item.addVehicleInfo(vInfoVO, overrides)

        if reusable:
            exchange.addSortIDs(arenaDP, *reusable)
        data = exchange.get()
        if data:
            self.as_updateVehiclesInfoS(data)

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        if vo is None:
            return
        else:
            arenaTeamSwitched = False
            if self._battleCtx.isPlayerObserver():
                currentArenaTeam = arenaDP.getNumberOfTeam()
                if currentArenaTeam != self.__avatarTeam:
                    if self.__avatarTeam is not None:
                        arenaDP.switchCurrentTeam(self.__avatarTeam)
                    arenaTeamSwitched = True
            isEnemy = self.__isEnemyTeam(arenaDP, vo.team)
            exchange = self._exchangeBroker.getVehicleStatusExchange(isEnemy)
            exchange.addVehicleInfo(vo)
            if flags & INVALIDATE_OP.SORTING > 0:
                exchange.addSortIDs(arenaDP)
            if not vo.isObserver():
                self._statsCollector.addVehicleStatusUpdate(vo)
            exchange.addTotalStats(self._statsCollector.getTotalStats(self._arenaVisitor, self.sessionProvider))
            data = exchange.get()
            if data:
                self.as_updateVehicleStatusS(data)
            if arenaTeamSwitched:
                arenaDP.switchCurrentTeam(currentArenaTeam)
            return

    def updateVehiclesStats(self, updated, arenaDP):
        exchange = self._exchangeBroker.getVehiclesStatsExchange()
        reusable = set()
        getVehicleInfo = arenaDP.getVehicleInfo
        for flags, vStatsVO in updated:
            vInfoVO = getVehicleInfo(vStatsVO.vehicleID)
            if vInfoVO.isObserver():
                continue
            self._statsCollector.addVehicleStatsUpdate(vInfoVO, vStatsVO)
            isEnemy = self.__isEnemyTeam(arenaDP, vInfoVO.team)
            if flags & INVALIDATE_OP.SORTING > 0:
                reusable.add(isEnemy)
            with exchange.getCollectedComponent(isEnemy, forced=True) as item:
                item.addStats(vStatsVO)

        if reusable:
            exchange.addSortIDs(arenaDP, *reusable)
        exchange.addTotalStats(self._statsCollector.getTotalStats(self._arenaVisitor, self.sessionProvider))
        data = exchange.get()
        if data:
            self.as_updateVehiclesStatsS(data)

    def updateTriggeredChatCommands(self, chatCommands, arenaDP):
        data = list()
        for vehicleID, state in chatCommands.iteritems():
            chatCommandName, _ = state
            entry = {'chatCommandName': str(chatCommandName),
             'vehicleID': int(vehicleID)}
            data.append(entry)

        updateList = {'chatCommands': data}
        self.as_updateTriggeredChatCommandsS(updateList)

    def invalidatePlayerStatus(self, flags, vo, arenaDP):
        isEnemy, overrides = self.__getTeamOverrides(vo, arenaDP)
        exchange = self._exchangeBroker.getPlayerStatusExchange(isEnemy)
        exchange.setVehicleID(vo.vehicleID)
        exchange.setStatus(overrides.getPlayerStatus(vo))
        data = exchange.get()
        if data:
            self.as_updatePlayerStatusS(data)

    def invalidateUsersTags(self):
        arenaDP = self._battleCtx.getArenaDP()
        exchange = self._exchangeBroker.getUsersTagsExchange()
        collection = vos_collections.VehiclesInfoCollection()
        for vInfoVO in collection.iterator(arenaDP):
            with exchange.getCollectedComponent(self.__isEnemyTeam(arenaDP, vInfoVO.team)) as item:
                item.addVehicleInfo(vInfoVO)

        data = exchange.get()
        if data:
            self.as_setUserTagsS(data)

    def invalidateUserTags(self, user):
        avatarSessionID = user.getID()
        arenaDP = self._battleCtx.getArenaDP()
        vehicleID = arenaDP.getVehIDBySessionID(avatarSessionID)
        if vehicleID:
            vo = arenaDP.getVehicleInfo(vehicleID)
            isEnemy = self.__isEnemyTeam(arenaDP, vo.team)
            exchange = self._exchangeBroker.getUserTagsItemExchange(isEnemy)
            exchange.addVehicleInfo(vo)
            exchange.addUserTags(user.getTags())
            data = exchange.get(forced=True)
            if data:
                self.as_updateUserTagsS(data)

    def invalidateInvitationsStatuses(self, vos, arenaDP):
        exchange = self._exchangeBroker.getInvitationsExchange()
        for vo in vos:
            isEnemy, overrides = self.__getTeamOverrides(vo, arenaDP)
            with exchange.getCollectedComponent(isEnemy) as item:
                item.setVehicleID(vo.vehicleID)
                item.setStatus(overrides.getInvitationDeliveryStatus(vo))

        data = exchange.get()
        if data:
            self.as_updateInvitationsStatusesS(data)

    def _populate(self):
        super(BattleStatisticsDataController, self)._populate()
        g_messengerEvents.voip.onChannelEntered += self.__onVOIPChannelStateToggled
        g_messengerEvents.voip.onChannelLeft += self.__onVOIPChannelStateToggled
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.sessionProvider.addArenaCtrl(self)
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        self.__isPMBattleProgressEnabled = self.lobbyContext.getServerSettings().isPMBattleProgressEnabled()
        qProgressCtrl = self.sessionProvider.shared.questProgress
        if qProgressCtrl is not None and self.__isPMBattleProgressEnabled:
            qProgressCtrl.onConditionProgressUpdate += self.__onQuestProgressUpdate
            qProgressCtrl.onFullConditionsUpdate += self.__onFullConditionsUpdate
            qProgressCtrl.onQuestProgressInited += self.__onFullConditionsUpdate
            qProgressCtrl.onHeaderProgressesUpdate += self.__onHeaderProgressesUpdate
            if qProgressCtrl.isInited():
                self.__onFullConditionsUpdate()
        self.__isDogTagInBattleEnabled = self.lobbyContext.getServerSettings().isDogTagInBattleEnabled()
        dogTagsCtrl = self.sessionProvider.dynamic.dogTags
        if dogTagsCtrl is not None and self.__isDogTagInBattleEnabled:
            dogTagsCtrl.onArenaVehicleVictimDogTagUpdated += self.invalidateVehicleStatus
        battleFieldCtrl = self.sessionProvider.dynamic.battleField
        if battleFieldCtrl is not None:
            battleFieldCtrl.onSpottedStatusChanged += self.updateVehiclesStats
        if self._battleCtx is not None:
            self.__setPersonalStatus()
        return

    def _dispose(self):
        g_messengerEvents.voip.onChannelEntered -= self.__onVOIPChannelStateToggled
        g_messengerEvents.voip.onChannelLeft -= self.__onVOIPChannelStateToggled
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        qProgressCtrl = self.sessionProvider.shared.questProgress
        if qProgressCtrl is not None and self.__isPMBattleProgressEnabled:
            qProgressCtrl.onConditionProgressUpdate -= self.__onQuestProgressUpdate
            qProgressCtrl.onFullConditionsUpdate -= self.__onFullConditionsUpdate
            qProgressCtrl.onQuestProgressInited -= self.__onFullConditionsUpdate
            qProgressCtrl.onHeaderProgressesUpdate -= self.__onHeaderProgressesUpdate
        dogTagsCtrl = self.sessionProvider.dynamic.dogTags
        if dogTagsCtrl is not None and self.__isDogTagInBattleEnabled:
            dogTagsCtrl.onArenaVehicleVictimDogTagUpdated -= self.invalidateVehicleStatus
        battleFieldCtrl = self.sessionProvider.dynamic.battleField
        if battleFieldCtrl is not None:
            battleFieldCtrl.onSpottedStatusChanged -= self.updateVehiclesStats
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.sessionProvider.removeArenaCtrl(self)
        self.__clearTeamOverrides()
        super(BattleStatisticsDataController, self)._dispose()
        return

    def _createExchangeBroker(self, exchangeCtx):
        raise NotImplementedError

    def _createExchangeCollector(self):
        raise NotImplementedError

    def _getArenaWinTextShort(self):
        return self._battleCtx.getArenaWinString()

    def __setPersonalStatus(self):
        self.__personalStatus = _makePersonalStatusFromSettingsStorage(self.settingsCore)
        self.__personalStatus |= PERSONAL_STATUS.SHOW_ALLY_INVITES
        if self._battleCtx.isInvitationEnabled():
            self.__personalStatus |= PERSONAL_STATUS.CAN_SEND_INVITE_TO_ALLY
            if self._battleCtx.hasSquadRestrictions():
                self.__personalStatus |= PERSONAL_STATUS.SQUAD_RESTRICTIONS
        if self.__personalStatus != PERSONAL_STATUS.DEFAULT:
            self.as_setPersonalStatusS(self.__personalStatus)

    def __updatePersonalPrebattleID(self, arenaDP):
        self._personalInfo.prebattleID = arenaDP.getVehicleInfo().prebattleID

    def __updateSquadRestrictions(self):
        noRestrictions = self.__personalStatus & PERSONAL_STATUS.SQUAD_RESTRICTIONS == 0
        if noRestrictions and self._battleCtx.hasSquadRestrictions():
            self.__personalStatus |= PERSONAL_STATUS.SQUAD_RESTRICTIONS
            self.as_updatePersonalStatusS(PERSONAL_STATUS.SQUAD_RESTRICTIONS, PERSONAL_STATUS.DEFAULT)

    def __setArenaDescription(self):
        battleCtx = self._battleCtx
        questProgress = self.sessionProvider.shared.questProgress
        arenaInfoData = {'mapName': battleCtx.getArenaTypeName(),
         'winText': battleCtx.getArenaWinString(),
         'winTextShort': self._getArenaWinTextShort(),
         'battleTypeLocaleStr': battleCtx.getArenaDescriptionString(isInBattle=False),
         'battleTypeIconPathBig': battleCtx.getBattleTypeIconPathBig(),
         'battleTypeIconPathSmall': battleCtx.getBattleTypeIconPathSmall(),
         'allyTeamName': battleCtx.getTeamName(enemy=False),
         'enemyTeamName': battleCtx.getTeamName(enemy=True)}
        self.as_setArenaInfoS(arenaInfoData)
        selectedQuest = questProgress.getSelectedQuest()
        if selectedQuest:
            self.as_setQuestStatusS(self.__getStatusData(selectedQuest))

    def __getStatusData(self, selectedQuest):
        if selectedQuest.isOnPause:
            status = MISSIONS_STATES.IS_ON_PAUSE
            icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ONPAUSE, 16, 16, -3, 8)
            text = text_styles.playerOnline(INGAME_GUI.STATISTICS_TAB_QUESTS_STATUS_ONPAUSE)
        else:
            status = MISSIONS_STATES.IN_PROGRESS
            icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_INPROGRESSICON, 16, 16, -2, 8)
            if selectedQuest.isMainCompleted():
                text = text_styles.neutral(INGAME_GUI.STATISTICS_TAB_QUESTS_STATUS_INCREASERESULT)
            else:
                text = text_styles.neutral(INGAME_GUI.STATISTICS_TAB_QUESTS_STATUS_INPROGRESS)
        statusLabel = text_styles.concatStylesToSingleLine(icon, text)
        return {'statusLabel': statusLabel,
         'status': status}

    def __getTeamOverrides(self, vo, arenaDP):
        team = vo.team
        if team in self.__reusable:
            isEnemy, overrides = self.__reusable[team]
        else:
            isEnemy = self.__isEnemyTeam(arenaDP, team)
            overrides = team_overrides.makeOverrides(isEnemy, team, self._personalInfo, self._arenaVisitor, isReplayPlaying=self.sessionProvider.isReplayPlaying)
            self.__reusable[team] = (isEnemy, overrides)
        return (isEnemy, overrides)

    def __clearTeamOverrides(self):
        while self.__reusable:
            _, (_, overrides) = self.__reusable.popitem()
            overrides.clear()

    def __onSettingsChanged(self, diff):
        added, removed = _makePersonalStatusFromSettingsDiff(diff)
        if (added, removed) != (PERSONAL_STATUS.DEFAULT,) * 2:
            self.__personalStatus |= added
            self.__personalStatus ^= removed
            self.as_updatePersonalStatusS(added, removed)

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.PLAYER_INFO:
            arenaDP = self._battleCtx.getArenaDP()
            previousID = self._personalInfo.changeSelected(value)
            self.invalidatePlayerStatus(0, arenaDP.getVehicleInfo(previousID), arenaDP)
            if value != previousID:
                self.invalidatePlayerStatus(0, arenaDP.getVehicleInfo(value), arenaDP)

    def __onVOIPChannelStateToggled(self, *args):
        if self._battleCtx is None:
            return
        else:
            arenaDP = self._battleCtx.getArenaDP()
            self.invalidatePlayerStatus(INVALIDATE_OP.PLAYER_STATUS, arenaDP.getVehicleInfo(), arenaDP)
            return

    def __onQuestProgressUpdate(self, progressID, conditionVO):
        self.as_updateQuestProgressS(progressID, conditionVO)

    def __onFullConditionsUpdate(self, *args):
        questProgress = self.sessionProvider.shared.questProgress
        selectedQuest = questProgress.getSelectedQuest()
        if selectedQuest:
            self.as_setQuestStatusS(self.__getStatusData(selectedQuest))
        self.as_setQuestsInfoS(questProgress.getQuestFullData(), self.sessionProvider.isReplayPlaying)

    def __onHeaderProgressesUpdate(self, *args):
        self.as_updateQuestHeaderProgressS(self.sessionProvider.shared.questProgress.getQuestHeaderProgresses())
