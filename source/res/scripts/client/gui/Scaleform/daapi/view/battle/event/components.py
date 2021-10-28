# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/components.py
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import ChatCommunicationComponent, ReplyStateForMarker
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import EventBattleGoal
from messenger.proto.bw_chat2.battle_chat_cmd import AUTOCOMMIT_COMMAND_NAMES
from constants import AOI, EVENT, ECP_HUD_INDEXES, ECP_HUD_TOGGLES
from chat_commands_consts import MarkerType, INVALID_COMMAND_ID, INVALID_MARKER_ID
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from game_event_getter import GameEventGetterMixin
from helpers import isPlayerAvatar
from gui.shared.utils.plugins import IPlugin

class IEventPluginComponent(IPlugin):

    def _onEnvironmentEventIDUpdate(self, eventEnvID):
        pass

    def getMarker(self, markerID, markerType, defaultMarker=None):
        return defaultMarker

    def getMarkerType(self):
        return MarkerType.INVALID_MARKER_TYPE

    def _getMarkerFromTargetID(self, targetID, markerType):
        raise NotImplementedError

    def _invokeMarker(self, markerID, function, *args):
        raise NotImplementedError

    def _setMarkerActive(self, markerID, shouldNotHide):
        raise NotImplementedError

    def _setMarkerSticky(self, markerID, isSticky):
        raise NotImplementedError

    def _setMarkerBoundEnabled(self, markerID, isEnabled):
        raise NotImplementedError


class GameEventComponent(GameEventGetterMixin):
    currentBossFightPhase = property(lambda self: self.__currentBossFightPhase)
    currentEventEnvID = property(lambda self: self.__currentEventEnvID)

    def __init__(self):
        super(GameEventComponent, self).__init__()
        self.__currentEventEnvID = EVENT.INVALID_ENVIRONMENT_ID
        self.__currentBossFightPhase = EVENT.INVALID_BOSSFIGHT_PHASE_ID

    def start(self):
        if self.environmentData is not None:
            self.environmentData.onEnvironmentEventIDUpdate += self.__onEnvironmentEventIDUpdate
            self._onEnvironmentEventIDUpdate(self.environmentData.getCurrentEnvironmentID())
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onTrigger += self._onTrigger
        return

    def stop(self):
        if self.environmentData is not None:
            self.environmentData.onEnvironmentEventIDUpdate -= self.__onEnvironmentEventIDUpdate
            self._onEnvironmentEventIDUpdate(EVENT.INVALID_ENVIRONMENT_ID)
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onTrigger -= self._onTrigger
        return

    def _onEnvironmentEventIDUpdate(self, eventEnvID):
        if self.__currentEventEnvID != eventEnvID:
            self.__currentEventEnvID = eventEnvID
        if self.currentEventEnvID != self.environmentData.getBossFightEnvironmentID():
            self.__currentBossFightPhase = EVENT.INVALID_BOSSFIGHT_PHASE_ID

    def _onTrigger(self, eventId, extra):
        if eventId == EVENT.BOSS_FIGHT_EVENT:
            phaseID = extra['phaseId']
            if self.__currentBossFightPhase != phaseID:
                self.__currentBossFightPhase = phaseID
                self._onEnvironmentEventIDUpdate(self.environmentData.getCurrentEnvironmentID())

    def __onEnvironmentEventIDUpdate(self, eventEnvID):
        if not (self.__currentBossFightPhase == EVENT.INVALID_BOSSFIGHT_PHASE_ID and self.__currentEventEnvID == self.environmentData.getBossFightEnvironmentID()):
            self._onEnvironmentEventIDUpdate(eventEnvID)


class EventChatCommunicationComponent(ChatCommunicationComponent, IEventPluginComponent):

    def start(self):
        super(EventChatCommunicationComponent, self).start()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived += self.__onActionAddedToMarkerReceived
            ctrl.setInFocusForPlayer += self.__setInFocusForPlayer
            ctrl.onAddCommandReceived += self.__onAddCommandReceived
            ctrl.onRemoveCommandReceived += self.__onRemoveCommandReceived
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived -= self.__onActionAddedToMarkerReceived
            ctrl.setInFocusForPlayer -= self.__setInFocusForPlayer
            ctrl.onAddCommandReceived -= self.__onAddCommandReceived
            ctrl.onRemoveCommandReceived -= self.__onRemoveCommandReceived
        super(EventChatCommunicationComponent, self).stop()
        return

    def __onActionAddedToMarkerReceived(self, senderID, commandID, markerType, addID):
        marker = self.getMarker(addID, markerType)
        if marker is not None:
            marker.setState(ReplyStateForMarker.CREATE_STATE)
            marker.setActiveCommandID(commandID)
            if _ACTIONS.battleChatCommandFromActionID(commandID).name in AUTOCOMMIT_COMMAND_NAMES:
                isPlayerSender = senderID == avatar_getter.getPlayerVehicleID()
                marker.setIsSticky(isPlayerSender)
                self._setMarkerRepliesAndCheckState(marker, 1, isPlayerSender)
            else:
                self._setActiveState(marker, ReplyStateForMarker.CREATE_STATE)
            if not avatar_getter.isVehicleAlive() and marker.getBoundCheckEnabled():
                if hasattr(marker, 'setBoundCheckEnabled'):
                    marker.setBoundCheckEnabled(False)
                self._setMarkerBoundEnabled(marker.getMarkerID(), False)
        return

    def __onRemoveCommandReceived(self, removeID, markerType):
        marker = self.getMarker(removeID, markerType)
        if marker is not None:
            marker.setActiveCommandID(INVALID_COMMAND_ID)
            if marker.getReplyCount() != 0:
                marker.setIsRepliedByPlayer(False)
                self._setMarkerReplied(marker, False)
                self._setMarkerReplyCount(marker, 0)
            self._checkNextState(marker)
            if marker.getState() == ReplyStateForMarker.NO_ACTION and not marker.getBoundCheckEnabled():
                if hasattr(marker, 'setBoundCheckEnabled'):
                    marker.setBoundCheckEnabled(True)
                self._setMarkerBoundEnabled(marker.getMarkerID(), True)
        return

    def __setInFocusForPlayer(self, oldTargetID, oldTargetType, newTargetID, newTargetType, oneShot):
        oldTargetMarker = self.getMarker(oldTargetID, oldTargetType)
        newTargetMarker = self.getMarker(newTargetID, newTargetType)
        if oldTargetMarker is not None:
            self.__makeMarkerSticky(oldTargetMarker, False)
        if newTargetMarker is not None:
            self.__makeMarkerSticky(newTargetMarker, True)
        return

    def __makeMarkerSticky(self, marker, setSticky):
        self._setMarkerSticky(marker.getMarkerID(), setSticky)
        marker.setIsSticky(setSticky)
        self._checkNextState(marker)

    def __onAddCommandReceived(self, addedID, markerType):
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        if advChatCmp is not None:
            chatCmdData = advChatCmp.getCommandDataForTargetIDAndMarkerType(addedID, markerType)
            if chatCmdData is not None:
                if chatCmdData.commandCreatorVehID != avatar_getter.getPlayerVehicleID():
                    marker = self.getMarker(addedID, markerType)
                    if marker is not None:
                        marker.setState(ReplyStateForMarker.CREATE_STATE)
                        marker.setActiveCommandID(chatCmdData.command.getID())
                        self._setActiveState(marker, ReplyStateForMarker.CREATE_STATE)
        return


class EventGoalUpdateComponent(IEventPluginComponent, GameEventComponent):

    def __init__(self, parentObj):
        super(EventGoalUpdateComponent, self).__init__(parentObj)
        GameEventComponent.__init__(self)

    def start(self):
        GameEventComponent.start(self)
        battleGoalsCtrl = self.sessionProvider.dynamic.battleGoals
        if battleGoalsCtrl is not None:
            battleGoalsCtrl.events.onGoalChanged += self.__onGoalChanged
        if self.soulCollector is not None:
            self.soulCollector.onSoulsChanged += self.__onCollectorSoulsChanged
        return

    def stop(self):
        battleGoalsCtrl = self.sessionProvider.dynamic.battleGoals
        if battleGoalsCtrl is not None:
            battleGoalsCtrl.events.onGoalChanged -= self.__onGoalChanged
        if self.soulCollector is not None:
            self.soulCollector.onSoulsChanged -= self.__onCollectorSoulsChanged
        GameEventComponent.stop(self)
        return

    def _onEnvironmentEventIDUpdate(self, eventEnvID):
        GameEventComponent._onEnvironmentEventIDUpdate(self, eventEnvID)
        battleGoalsCtrl = self.sessionProvider.dynamic.battleGoals
        if battleGoalsCtrl is not None:
            self.__onGoalChanged(battleGoalsCtrl.currentCollectorID, battleGoalsCtrl.currentGoal)
        return

    def _getCollectorMarker(self, collectorID=None):
        if collectorID is None or collectorID == INVALID_MARKER_ID:
            collectorID = self._getCollectorMarkerID()
        return self._getMarkerFromTargetID(collectorID, MarkerType.BASE_MARKER_TYPE) if collectorID != INVALID_MARKER_ID else None

    def _getCollectorMarkerID(self):
        battleGoalsCtrl = self.sessionProvider.dynamic.battleGoals
        if battleGoalsCtrl is not None:
            collectorID = battleGoalsCtrl.currentCollectorID
            if collectorID is not None:
                return collectorID
        return INVALID_MARKER_ID

    def _getCurrentCollectorSoulsInfo(self):
        battleGoals = self.sessionProvider.dynamic.battleGoals
        return battleGoals.getCurrentCollectorSoulsInfo() if battleGoals else (0, 0)

    def _onCollectorIDChanged(self):
        battleGoalsCtrl = self.sessionProvider.dynamic.battleGoals
        if battleGoalsCtrl is not None:
            self.__onGoalChanged(battleGoalsCtrl.currentCollectorID, battleGoalsCtrl.currentGoal)
        return

    def __onCollectorSoulsChanged(self, _):
        marker = self._getCollectorMarker()
        if marker is not None:
            self.__onProgressChanged(marker)
        return

    def __onGoalChanged(self, collectorID, relevantGoal):
        marker = self._getCollectorMarker(collectorID)
        if marker is not None:
            markerID = marker.getMarkerID()
            if marker.isVolot():
                marker.setRelevantGoal(relevantGoal if relevantGoal is not None else EventBattleGoal.UNKNOWN)
                self.__onProgressChanged(marker)
                if marker.isActive():
                    if relevantGoal == EventBattleGoal.GET_TO_COLLECTOR:
                        self._invokeMarker(markerID, 'setTimer')
                    elif relevantGoal == EventBattleGoal.DELIVER_MATTER:
                        self._invokeMarker(markerID, 'setIconActive', True)
                    elif relevantGoal == EventBattleGoal.COLLECT_MATTER:
                        self._invokeMarker(markerID, 'setIconActive', False)
        return

    def __onProgressChanged(self, marker):
        isActive = marker.getRelevantGoal() != EventBattleGoal.UNKNOWN
        if marker.getRelevantGoal() in (EventBattleGoal.DELIVER_MATTER, EventBattleGoal.COLLECT_MATTER):
            souls, capacity = self._getCurrentCollectorSoulsInfo()
            isActive = isActive and capacity > 0
            marker.setProgress((souls, capacity))
            self._invokeMarker(marker.getMarkerID(), 'setProgress', souls, capacity)
        marker.setActive(isActive)
        self._setMarkerActive(marker.getMarkerID(), isActive)


class EventECPUpdateComponent(IEventPluginComponent):

    def start(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onUpdateScenarioTimer += self.__onMarkerUpdated
        ecpComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'ecp', None)
        if ecpComp is not None:
            ecpComp.ecpHUDEvents[ECP_HUD_INDEXES.marker][ECP_HUD_TOGGLES.on] += self.__onMarkerAdded
            ecpComp.ecpHUDEvents[ECP_HUD_INDEXES.marker][ECP_HUD_TOGGLES.off] += self.__onMarkerRemoved
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onUpdateScenarioTimer -= self.__onMarkerUpdated
        ecpComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'ecp', None)
        if ecpComp is not None:
            ecpComp.ecpHUDEvents[ECP_HUD_INDEXES.marker][ECP_HUD_TOGGLES.on] -= self.__onMarkerAdded
            ecpComp.ecpHUDEvents[ECP_HUD_INDEXES.marker][ECP_HUD_TOGGLES.off] -= self.__onMarkerRemoved
        return

    def _onEnvironmentEventIDUpdate(self, eventEnvID):
        for ecp in self.__iterMarkers():
            self.__onMarkerAdded(ecp)

    def _addMarker(self, symbol, position, ecpID):
        raise NotImplementedError

    def _removeMarker(self, ecpID):
        raise NotImplementedError

    def __onMarkerAdded(self, ecp):
        marker = self.getMarker(ecp.id, MarkerType.BASE_MARKER_TYPE)
        if marker is not None:
            self._removeMarker(ecp.id)
        self._addMarker(ecp.minimapSymbol, ecp.position, ecp.id)
        return

    def __onMarkerRemoved(self, ecp):
        self._removeMarker(ecp.id)

    def __onMarkerUpdated(self, *args):
        for ecp in self.__iterMarkers():
            marker = self.getMarker(ecp.id, MarkerType.BASE_MARKER_TYPE)
            if marker is not None:
                distance = marker.getDistance(avatar_getter.getOwnVehiclePosition())
                if distance is not None:
                    if not marker.isVolot():
                        isInAOI = distance <= AOI.VEHICLE_CIRCULAR_AOI_RADIUS or marker.getReplyCount()
                        if marker.setActive(isInAOI):
                            self._setMarkerActive(marker.getMarkerID(), isInAOI)
                    if marker.isActive():
                        self._invokeMarker(marker.getMarkerID(), 'setDistance', distance)

        return

    def __iterMarkers(self):
        ecpComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'ecp', None)
        if ecpComp is not None:
            ecpCompEntities = ecpComp.getECPEntities()
            for ecp in ecpCompEntities.itervalues():
                yield ecp

        return
