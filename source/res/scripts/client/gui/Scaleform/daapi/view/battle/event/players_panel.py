# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/players_panel.py
import BigWorld
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.Scaleform.daapi.view.meta.EventPlayersPanelMeta import EventPlayersPanelMeta
from gui.Scaleform.daapi.view.battle.event.markers import EventPlayerPanelMarker
from gui.Scaleform.daapi.view.battle.event.components import GameEventComponent, EventChatCommunicationComponent
from gui.Scaleform.settings import ICONS_SIZES
from gui.shared.badges import buildBadge
from helpers import dependency, isPlayerAvatar
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.settings_constants import BattleCommStorageKeys
from chat_commands_consts import MarkerType
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from arena_components.advanced_chat_component import EMPTY_CHAT_CMD_FLAG, EMPTY_STATE
from gui.battle_control.battle_constants import EventBattleGoal

class EventPlayersPanel(EventPlayersPanelMeta, IBattleFieldListener, IAbstractPeriodView, GameEventComponent, EventChatCommunicationComponent):
    __slots__ = ('_markers', '__vehCmds', '__isChatCommandVisible')
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(EventPlayersPanel, self).__init__()
        GameEventComponent.__init__(self)
        self._markers = dict()
        self.__vehCmds = dict()
        self.__isChatCommandVisible = True

    def updateVehicleHealth(self, vehicleID, newHealth, maxHealth):
        self.__setVehicleHealth(vehicleID, newHealth)

    def updateDeadVehicles(self, aliveAllies, deadAllies, aliveEnemies, deadEnemies):
        for vehicleID in deadAllies:
            self.__setVehicleHealth(vehicleID, 0)

    def getMarker(self, markerID, markerType, defaultMarker=None):
        marker = defaultMarker
        if markerType in EventPlayerPanelMarker.ALLOWED_MARKER_TYPES:
            if markerType not in self._markers:
                self._markers[markerType] = dict()
            markersByType = self._markers[markerType]
            marker = markersByType.get(markerID, defaultMarker)
            if marker is defaultMarker:
                marker = self._setupMarker(markerID, markerType, defaultMarker)
                if marker is not None:
                    markersByType[markerID] = marker
        return marker

    def _getMarkerFromTargetID(self, targetID, markerType):
        return self.getMarker(targetID, markerType)

    def _setupMarker(self, markerID, markerType, defaultMarker):
        markerSymbolName = None
        if markerType == MarkerType.BASE_MARKER_TYPE:
            ecpComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'ecp', None)
            if ecpComp is not None:
                for ecp in ecpComp.getECPEntities().values():
                    if ecp.id == markerID:
                        markerSymbolName = ecp.minimapSymbol
                        break

        else:
            advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
            if advChatCmp is not None:
                chatCmdData = advChatCmp.getCommandDataForTargetIDAndMarkerType(markerID, markerType)
                if chatCmdData is not None:
                    cmdVehMarker = _ACTIONS.battleChatCommandFromActionID(chatCmdData.command.getID()).vehMarker
                    if cmdVehMarker in EventPlayerPanelMarker.ALLOWED_MARKER_TYPES[markerType]:
                        markerSymbolName = cmdVehMarker
        return defaultMarker if markerSymbolName is None else EventPlayerPanelMarker(markerID=markerID, markerType=markerType, markerSymbolName=markerSymbolName)

    def _populate(self):
        super(EventPlayersPanel, self)._populate()
        self.__isChatCommandVisible = bool(self.settingsCore.getSetting(BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST))
        if self.souls is not None:
            self.souls.onSoulsChanged += self.__onSoulsChanged
        if self.soulCollector is not None:
            self.soulCollector.onSoulsChanged += self.__onCollectorSoulsChanged
        self.__onCollectorSoulsChanged()
        battleGoalsCtrl = self.sessionProvider.dynamic.battleGoals
        if battleGoalsCtrl is not None:
            battleGoalsCtrl.events.onGoalChanged += self.__onGoalChanged
            self.__onGoalChanged(battleGoalsCtrl.currentCollectorID, battleGoalsCtrl.currentGoal)
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl:
            feedbackCtrl.onVehicleMarkerRemoved += self.__onVehicleMarkerRemoved
        self.settingsCore.onSettingsChanged += self.__onSettingsChange
        GameEventComponent.start(self)
        EventChatCommunicationComponent.start(self)
        if isPlayerAvatar():
            arena = BigWorld.player().arena
            if arena is not None:
                arena.onVehicleKilled += self.__onArenaVehicleKilled
        return

    def _dispose(self):
        if self.souls is not None:
            self.souls.onSoulsChanged -= self.__onSoulsChanged
        if self.soulCollector is not None:
            self.soulCollector.onSoulsChanged -= self.__onCollectorSoulsChanged
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl:
            feedbackCtrl.onVehicleMarkerRemoved -= self.__onVehicleMarkerRemoved
        battleGoalsCtrl = self.sessionProvider.dynamic.battleGoals
        if battleGoalsCtrl is not None:
            battleGoalsCtrl.events.onGoalChanged -= self.__onGoalChanged
        self.settingsCore.onSettingsChanged -= self.__onSettingsChange
        EventChatCommunicationComponent.stop(self)
        GameEventComponent.stop(self)
        if isPlayerAvatar():
            arena = BigWorld.player().arena
            if arena is not None:
                arena.onVehicleKilled -= self.__onArenaVehicleKilled
        self._markers.clear()
        self.__vehCmds.clear()
        super(EventPlayersPanel, self)._dispose()
        return

    def _setActiveState(self, marker, state):
        EventChatCommunicationComponent._setActiveState(self, marker, state)
        self.__updateMarkerOwners(marker)

    def _setMarkerReplyCount(self, marker, replyCount):
        EventChatCommunicationComponent._setMarkerReplyCount(self, marker, replyCount)
        self.__updateMarkerOwners(marker)

    def _invokeMarker(self, markerID, function, *args):
        pass

    def _setMarkerActive(self, markerID, shouldNotHide):
        pass

    def _setMarkerSticky(self, markerID, isSticky):
        pass

    def _setMarkerBoundEnabled(self, markerID, isEnabled):
        pass

    def __getChatCmdData(self, marker):
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        return advChatCmp.getCommandDataForTargetIDAndMarkerType(marker.getMarkerID(), marker.getMarkerType()) if advChatCmp is not None else None

    def __updateMarkerOwners(self, marker):
        chatCmdData = self.__getChatCmdData(marker)
        if chatCmdData is not None:
            chatCommandName = marker.getMarkerSubtype()
            isOwners = set(chatCmdData.owners)
            wasOwners = marker.getMarkerOwners()
            for vehicleID in wasOwners - isOwners:
                self.__onChatCommandUpdated(vehicleID)

            for vehicleID in isOwners - wasOwners:
                self.__onChatCommandUpdated(vehicleID, chatCommandName, EMPTY_CHAT_CMD_FLAG)

            marker.setMarkerOwners(isOwners)
        return

    def __onVehicleMarkerRemoved(self, vehicleID):
        marker = self.getMarker(vehicleID, MarkerType.VEHICLE_MARKER_TYPE)
        if marker is not None:
            playerVehicleID = avatar_getter.getPlayerVehicleID()
            if playerVehicleID in marker.getMarkerOwners():
                self.__onChatCommandUpdated(playerVehicleID, forceUpdate=True)
            chatCmdData = self.__getChatCmdData(marker)
            if chatCmdData is not None and playerVehicleID in chatCmdData.owners:
                commands = self.sessionProvider.shared.chatCommands
                if commands is not None:
                    commands.sendCancelReplyChatCommand(vehicleID, _ACTIONS.battleChatCommandFromActionID(chatCmdData.command.getID()).name)
        return

    def __onArenaVehicleKilled(self, targetID, *args):
        if not self.sessionProvider.getArenaDP().isAlly(targetID):
            marker = self.getMarker(targetID, MarkerType.VEHICLE_MARKER_TYPE)
            if marker is not None:
                for ownerID in marker.getMarkerOwners():
                    self.__onChatCommandUpdated(ownerID, forceUpdate=True)

                chatCmdData = self.__getChatCmdData(marker)
                if chatCmdData is not None:
                    for ownerID in chatCmdData.owners:
                        self.__onChatCommandUpdated(ownerID, forceUpdate=True)

        return

    def __setVehicleHealth(self, vehID, health):
        arenaDP = self.sessionProvider.getArenaDP()
        vInfo = arenaDP.getVehicleInfo(vehID)
        if not vInfo.isObserver():
            self.__updateTeammate(vInfo, health)

    def __updateTeammate(self, vInfo, hpCurrent):
        arenaDP = self.sessionProvider.getArenaDP()
        isPlayerObserver = arenaDP.isPlayerObserver()
        playerTeam = avatar_getter.getPlayerTeam()
        isAlly = vInfo.team == playerTeam if isPlayerObserver else arenaDP.isAllyTeam(vInfo.team)
        if not isAlly:
            marker = self.getMarker(vInfo.vehicleID, MarkerType.VEHICLE_MARKER_TYPE)
            if marker is not None:
                for ownerID in marker.getMarkerOwners():
                    self.__onChatCommandUpdated(ownerID, forceUpdate=True)

                del self._markers[MarkerType.VEHICLE_MARKER_TYPE][vInfo.vehicleID]
            return
        else:
            playerVehicleID = avatar_getter.getPlayerVehicleID()
            isSelf = vInfo.vehicleID == playerVehicleID
            playerSquad = arenaDP.getVehicleInfo(playerVehicleID).squadIndex
            isSquad = False
            if playerSquad > 0 and playerSquad == vInfo.squadIndex or playerSquad == 0 and vInfo.vehicleID == playerVehicleID:
                isSquad = True
            badgeID = vInfo.selectedBadge
            badge = buildBadge(badgeID, vInfo.getBadgeExtraInfo())
            badgeVO = badge.getBadgeVO(ICONS_SIZES.X24, {'isAtlasSource': True}, shortIconName=True) if badge else None
            suffixBadgeId = vInfo.selectedSuffixBadge
            self.as_setPlayerPanelInfoS({'vehID': vInfo.vehicleID,
             'name': vInfo.player.name,
             'badgeVO': badgeVO,
             'suffixBadgeIcon': 'badge_{}'.format(suffixBadgeId) if suffixBadgeId else '',
             'suffixBadgeStripIcon': 'strip_{}'.format(suffixBadgeId) if suffixBadgeId else '',
             'nameVehicle': vInfo.vehicleType.shortName,
             'typeVehicle': vInfo.vehicleType.classTag,
             'hpMax': vInfo.vehicleType.maxHealth,
             'hpCurrent': hpCurrent,
             'isSelf': isSelf,
             'isSquad': isSquad,
             'squadIndex': vInfo.squadIndex,
             'countSouls': self.__getSouls(vInfo.vehicleID)})
            if hpCurrent <= 0:
                chatCommandName, _ = self.__vehCmds.pop(vInfo.vehicleID, (EMPTY_STATE, EMPTY_CHAT_CMD_FLAG))
                if chatCommandName != EMPTY_STATE:
                    self.__onChatCommandUpdated(vInfo.vehicleID, forceUpdate=True)
            elif vInfo.vehicleID not in self.__vehCmds:
                self.__onChatCommandUpdated(vInfo.vehicleID, forceUpdate=True)
            return

    def __onSoulsChanged(self, diff):
        for vehID, (souls, _) in diff.iteritems():
            self.as_setPlayerPanelCountSoulsS(vehID, souls)

    def __getSouls(self, vehID):
        return self.souls.getSouls(vehID) if self.souls is not None else 0

    def __onCollectorSoulsChanged(self, _=None):
        battleGoals = self.sessionProvider.dynamic.battleGoals
        if battleGoals:
            souls, capacity = battleGoals.getCurrentCollectorSoulsInfo()
            needValue = max(0, capacity - souls)
            if not needValue:
                self.as_setCollectorGoalS(int(EventBattleGoal.GET_TO_COLLECTOR))
            self.as_setCollectorNeedValueS(needValue)

    def __onGoalChanged(self, collectorID, relevantGoal):
        if collectorID is None and relevantGoal in (None, EventBattleGoal.UNKNOWN):
            self.as_setCollectorGoalS(int(EventBattleGoal.GET_TO_COLLECTOR))
            return
        else:
            self.as_setCollectorGoalS(int(relevantGoal))
            self.__onCollectorSoulsChanged()
            return

    def __onSettingsChange(self, diff):
        if BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST in diff:
            self.__isChatCommandVisible = bool(diff.get(BattleCommStorageKeys.SHOW_COM_IN_PLAYER_LIST, self.__isChatCommandVisible))
            self.__clearChatCommandList()

    def _onEnvironmentEventIDUpdate(self, eventEnvID):
        self.__clearMarkers()
        self.__clearChatCommandList()
        GameEventComponent._onEnvironmentEventIDUpdate(self, eventEnvID)
        EventChatCommunicationComponent._onEnvironmentEventIDUpdate(self, eventEnvID)

    def __clearMarkers(self):
        for markersByType in self._markers.itervalues():
            for marker in markersByType.itervalues():
                if marker is not None:
                    chatCmdData = self.__getChatCmdData(marker)
                    if chatCmdData is not None and avatar_getter.getPlayerVehicleID() in chatCmdData.owners:
                        commands = self.sessionProvider.shared.chatCommands
                        if commands is not None:
                            commands.sendCancelReplyChatCommand(marker.getMarkerID(), _ACTIONS.battleChatCommandFromActionID(chatCmdData.command.getID()).name)

        self._markers.clear()
        return

    def __clearChatCommandList(self):
        for vehicleID in self.__vehCmds:
            self.__onChatCommandUpdated(vehicleID, forceUpdate=True)

    def __onChatCommandUpdated(self, vehicleID, chatCommandName=EMPTY_STATE, chatCommandFlags=EMPTY_CHAT_CMD_FLAG, forceUpdate=False):
        self.__vehCmds[vehicleID] = (chatCommandName, chatCommandFlags)
        if self.__isChatCommandVisible or forceUpdate:
            self.as_setChatCommandS(vehicleID, str(chatCommandName), chatCommandFlags)
            self.as_updateTriggeredChatCommandsS({'chatCommands': [{'chatCommandName': str(chatCommandName),
                               'vehicleID': int(vehicleID)}]})
