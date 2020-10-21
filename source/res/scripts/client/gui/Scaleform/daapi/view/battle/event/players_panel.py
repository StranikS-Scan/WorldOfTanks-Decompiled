# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/players_panel.py
from constants import ARENA_PERIOD
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.Scaleform.daapi.view.meta.EventPlayersPanelMeta import EventPlayersPanelMeta
from PlayerEvents import g_playerEvents
from game_event_getter import GameEventGetterMixin
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.account_helpers.settings_core import ISettingsCore
from gui.Scaleform.genConsts.BATTLE_MINIMAP_CONSTS import BATTLE_MINIMAP_CONSTS
from arena_components.advanced_chat_component import TARGET_CHAT_CMD_FLAG, EMPTY_CHAT_CMD_FLAG, EMPTY_STATE
from account_helpers.settings_core.settings_constants import BattleCommStorageKeys
from gui.Scaleform.daapi.view.battle.event.markers import EventBasePlayerPanelMarker
from gui.Scaleform.daapi.view.battle.event.components import EventChatCommandTargetUpdateComponent

class EventPlayersPanel(EventPlayersPanelMeta, IArenaVehiclesController, GameEventGetterMixin, EventChatCommandTargetUpdateComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(EventPlayersPanel, self).__init__()
        GameEventGetterMixin.__init__(self)
        self._markers = {}
        self._chatCommands = {}
        self.__isEnabled = True
        self.__arenaDP = self.sessionProvider.getArenaDP()

    def getControllerID(self):
        return BATTLE_CTRL_ID.GUI

    def getCtrlScope(self):
        return _SCOPE.VEHICLES

    def invalidateVehiclesInfo(self, _):
        self.__updtateAllTeammates()

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(self.sessionProvider.getArenaDP())

    def addVehicleInfo(self, vInfo, _):
        self.__updateTeammate(vInfo)

    def updateVehiclesInfo(self, updated, arenaDP):
        for _, vInfo in updated:
            self.__updateTeammate(vInfo)

    def _populate(self):
        super(EventPlayersPanel, self)._populate()
        self.__isEnabled = bool(self.settingsCore.getSetting(BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST))
        EventChatCommandTargetUpdateComponent.start(self)
        if self.teammateVehicleHealth is not None:
            self.teammateVehicleHealth.onTeammateVehicleHealthUpdate += self.__onTeammateVehicleHealthUpdate
        if self.souls is not None:
            self.souls.onSoulsChanged += self.__onSoulsChanged
        if self.soulCollector is not None:
            self.soulCollector.onSoulsChanged += self.__onCollectorSoulsChanged
        self.__onCollectorSoulsChanged()
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        battleGoalsCtrl = self.sessionProvider.dynamic.battleGoals
        if battleGoalsCtrl is not None:
            battleGoalsCtrl.events.onGoalChanged += self.__onGoalChanged
            self.as_setCollectorGoalS(int(battleGoalsCtrl.currentGoal))
        self.settingsCore.onSettingsChanged += self.__onSettingsChange
        self.environmentData.onEnvironmentEventIDUpdate += self.__onEnvironmentEventIDUpdate
        self.__updtateAllTeammates()
        return

    def _dispose(self):
        if self.teammateVehicleHealth is not None:
            self.teammateVehicleHealth.onTeammateVehicleHealthUpdate -= self.__onTeammateVehicleHealthUpdate
        if self.souls is not None:
            self.souls.onSoulsChanged -= self.__onSoulsChanged
        if self.soulCollector is not None:
            self.soulCollector.onSoulsChanged -= self.__onCollectorSoulsChanged
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        battleGoalsCtrl = self.sessionProvider.dynamic.battleGoals
        if battleGoalsCtrl is not None:
            battleGoalsCtrl.events.onGoalChanged -= self.__onGoalChanged
        self.settingsCore.onSettingsChanged -= self.__onSettingsChange
        self.environmentData.onEnvironmentEventIDUpdate -= self.__onEnvironmentEventIDUpdate
        EventChatCommandTargetUpdateComponent.stop(self)
        self._markers.clear()
        self._chatCommands.clear()
        super(EventPlayersPanel, self)._dispose()
        return

    def _setChatCommand(self, vehicleID, chatCommandName, chatCommandFlags):
        if not self.__isEnabled:
            return
        self.as_setChatCommandS(vehicleID, chatCommandName, chatCommandFlags)

    def _updateTriggeredChatCommands(self, updateList):
        if not self.__isEnabled:
            return
        self.as_updateTriggeredChatCommandsS(updateList)

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self.__updtateAllTeammates()

    def __updtateAllTeammates(self):
        for vInfo in self.__arenaDP.getVehiclesInfoIterator():
            self.__updateTeammate(vInfo)

    def __updateTeammate(self, vInfo):
        if self.teammateVehicleHealth is None:
            return
        else:
            if vInfo.player.accountDBID > 0 and vInfo.team == self.__arenaDP.getAllyTeams()[0]:
                hpCurrent = self.teammateVehicleHealth.getTeammateHealth(vInfo.vehicleID)
                playerVehicleID = avatar_getter.getPlayerVehicleID()
                isSelf = vInfo.vehicleID == playerVehicleID
                playerSquad = self.__arenaDP.getVehicleInfo(playerVehicleID).squadIndex
                isSquad = playerSquad > 0 and playerSquad == vInfo.squadIndex or isSelf
                badgeId = vInfo.selectedBadge
                suffixBadgeId = vInfo.selectedSuffixBadge
                self.as_setPlayerPanelInfoS({'vehID': vInfo.vehicleID,
                 'name': vInfo.player.name,
                 'typeVehicle': vInfo.vehicleType.classTag,
                 'hpMax': vInfo.vehicleType.maxHealth,
                 'hpCurrent': hpCurrent,
                 'countSouls': self.__getSouls(vInfo.vehicleID),
                 'isSelf': isSelf,
                 'isSquad': isSquad,
                 'badgeIcon': 'badge_{}'.format(badgeId) if badgeId else '',
                 'suffixBadgeIcon': 'badge_{}'.format(suffixBadgeId) if suffixBadgeId else '',
                 'suffixBadgeStripIcon': 'strip_{}'.format(suffixBadgeId) if suffixBadgeId else '',
                 'squadIndex': vInfo.squadIndex})
            return

    def __onTeammateVehicleHealthUpdate(self, diff):
        for vehID, newHealth in diff.iteritems():
            maxHealth = self.__arenaDP.getVehicleInfo(vehID).vehicleType.maxHealth
            self.as_setPlayerPanelHpS(vehID, maxHealth, min(newHealth, maxHealth))
            if newHealth <= 0:
                self.as_setChatCommandS(vehID, EMPTY_STATE, EMPTY_CHAT_CMD_FLAG)
                self.as_setPlayerDeadS(vehID)

    def __onSoulsChanged(self, diff):
        for vehID, (souls, _) in diff.iteritems():
            self.as_setPlayerPanelCountSoulsS(vehID, souls)

    def __getSouls(self, vehID):
        return self.souls.getSouls(vehID) if self.souls is not None else 0

    def __onCollectorSoulsChanged(self, _=None):
        battleGoals = self.sessionProvider.dynamic.battleGoals
        if battleGoals:
            souls, capacity = battleGoals.getCurrentCollectorSoulsInfo()
            self.as_setCollectorNeedValueS(max(0, capacity - souls))

    def __onGoalChanged(self, collectorID, relevantGoal):
        if collectorID is None or relevantGoal is None:
            return
        else:
            self.as_setCollectorGoalS(int(relevantGoal))
            self.__onCollectorSoulsChanged()
            return

    def _getMarkerFromTargetID(self, targetID, markerType):
        return self._markers.get(targetID)

    def _invokeMarker(self, markerID, function, *args):
        if function == BATTLE_MINIMAP_CONSTS.SET_STATE:
            isReply = bool(args[0] == BATTLE_MINIMAP_CONSTS.STATE_REPLY)
            if isReply and not self.__isEnabled:
                return
            self.as_setChatCommandS(args[1], self._markers[markerID].getSymbol() if isReply else EMPTY_STATE, TARGET_CHAT_CMD_FLAG if isReply else EMPTY_CHAT_CMD_FLAG)

    def _addCampOrControlPointMarker(self, symbol, position, ecpID):
        minimapSymbol = EventBasePlayerPanelMarker.MARKER_SYMBOLS[symbol]
        isVolot = minimapSymbol.startswith((EventBasePlayerPanelMarker.VOLOT_SYMBOL,))
        marker = EventBasePlayerPanelMarker(ecpID, True, 'ally' if isVolot else 'enemy')
        marker.setSymbol(minimapSymbol)
        self._markers[ecpID] = marker

    def __onSettingsChange(self, diff):
        if BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST in diff:
            self.__isEnabled = bool(diff.get(BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST, self.__isEnabled))
            if not self.__isEnabled:
                self.__clearChatCommandList()

    def __onEnvironmentEventIDUpdate(self, eventEnvID):
        if eventEnvID and self.__isEnabled:
            self.__clearChatCommandList()
            EventChatCommandTargetUpdateComponent._restart(self)

    def __clearChatCommandList(self):
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        self.as_setChatCommandS(playerVehicleID, EMPTY_STATE, EMPTY_CHAT_CMD_FLAG)
        for vInfo in self.__arenaDP.getVehiclesInfoIterator():
            if vInfo.player.accountDBID > 0 and vInfo.team == self.__arenaDP.getAllyTeams()[0]:
                self.as_setChatCommandS(vInfo.vehicleID, EMPTY_STATE, EMPTY_CHAT_CMD_FLAG)
