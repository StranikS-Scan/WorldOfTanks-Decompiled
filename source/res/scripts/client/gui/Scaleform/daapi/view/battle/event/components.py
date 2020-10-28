# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/components.py
import BigWorld
from arena_components.advanced_chat_component import EMPTY_STATE, EMPTY_CHAT_CMD_FLAG
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import EventBattleGoal
from messenger.proto.bw_chat2.battle_chat_cmd import BATTLE_CHAT_COMMAND_NAMES
from gui.Scaleform.genConsts.BATTLE_MINIMAP_CONSTS import BATTLE_MINIMAP_CONSTS
from gui.Scaleform.daapi.view.battle.event.markers import EventBaseMarker, EventBaseMinimapMarker
from constants import AOI
from chat_commands_consts import MarkerType
from messenger_common_chat2 import BATTLE_CHAT_COMMANDS, MESSENGER_ACTION_IDS as _ACTIONS

class EventComponent(object):

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def _restart(self):
        raise NotImplementedError

    def getMarkerType(self):
        return MarkerType.BASE_MARKER_TYPE

    def _getMarkerFromTargetID(self, targetID, markerType):
        raise NotImplementedError

    def _invokeMarker(self, markerID, function, *args):
        raise NotImplementedError


class EventTargetMarkerUpdateComponent(EventComponent):
    SUPPORTED_COMMAND_NAMES = (BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE, BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE)
    __SUPPORTED_COMMAND_IDS = []
    for cmd in BATTLE_CHAT_COMMANDS:
        cmdID = cmd.id
        cmdName = cmd.name
        if cmdName in SUPPORTED_COMMAND_NAMES:
            __SUPPORTED_COMMAND_IDS.append(cmdID)

    def start(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived += self.__onActionAddedToMarkerReceived
            ctrl.onReplyFeedbackReceived += self.__onReplyFeedbackReceived
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived -= self.__onActionAddedToMarkerReceived
            ctrl.onReplyFeedbackReceived -= self.__onReplyFeedbackReceived
        return

    def _restart(self):
        pass

    def __onActionAddedToMarkerReceived(self, senderID, commandID, markerType, targetID):
        if commandID in self.__SUPPORTED_COMMAND_IDS:
            self.__onReplyFeedbackReceived(targetID, senderID, markerType, 0, 1)

    def __onReplyFeedbackReceived(self, targetID, replierID, markerType, oldReplyCount, newReplyCount):
        if markerType != MarkerType.BASE_MARKER_TYPE:
            return
        else:
            marker = self._getMarkerFromTargetID(targetID, markerType)
            if marker is None:
                return
            isReply = newReplyCount > oldReplyCount
            marker.setIsReplied(isReply or newReplyCount > 0)
            self._invokeMarker(marker.getMarkerID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_REPLY if isReply else BATTLE_MINIMAP_CONSTS.STATE_DEFAULT, replierID)
            return


class EventGoalUpdateComponent(EventComponent):

    def start(self):
        battleGoalsCtrl = self.sessionProvider.dynamic.battleGoals
        if battleGoalsCtrl is not None:
            battleGoalsCtrl.events.onGoalChanged += self.__onGoalChanged
        return

    def stop(self):
        battleGoalsCtrl = self.sessionProvider.dynamic.battleGoals
        if battleGoalsCtrl is not None:
            battleGoalsCtrl.events.onGoalChanged -= self.__onGoalChanged
        return

    def _restart(self):
        battleGoalsCtrl = self.sessionProvider.dynamic.battleGoals
        if battleGoalsCtrl is not None:
            self.__onGoalChanged(battleGoalsCtrl.currentCollectorID, battleGoalsCtrl.currentGoal)
        return

    def _getCollectorMarkerID(self):
        battleGoalsCtrl = self.sessionProvider.dynamic.battleGoals
        if battleGoalsCtrl is not None:
            marker = self._getMarkerFromTargetID(battleGoalsCtrl.currentCollectorID, MarkerType.BASE_MARKER_TYPE)
            if marker is not None:
                return marker.getMarkerID()
        return

    def _setMarkerActive(self, markerID, shouldNotHide):
        raise NotImplementedError

    def __onGoalChanged(self, collectorID, relevantGoal):
        if collectorID is None:
            return
        else:
            marker = self._getMarkerFromTargetID(collectorID, self.getMarkerType())
            if marker is not None:
                symbol = marker.getSymbol()
                isVolot = symbol is not None and symbol.startswith((EventBaseMinimapMarker.VOLOT_SYMBOL,))
                if not isVolot:
                    return
                markerID = marker.getMarkerID()
                self._setMarkerActive(markerID, relevantGoal == EventBattleGoal.UNKNOWN)
                if relevantGoal == EventBattleGoal.GET_TO_COLLECTOR:
                    self._invokeMarker(markerID, 'setTimer')
                elif relevantGoal == EventBattleGoal.DELIVER_MATTER:
                    self._invokeMarker(markerID, 'setIconActive', True)
                elif relevantGoal == EventBattleGoal.COLLECT_MATTER:
                    self._invokeMarker(markerID, 'setIconActive', False)
                marker.setIsInProgress(relevantGoal in (EventBattleGoal.DELIVER_MATTER, EventBattleGoal.COLLECT_MATTER))
                if marker.getIsInProgress():
                    battleGoals = self.sessionProvider.dynamic.battleGoals
                    if battleGoals:
                        souls, capacity = battleGoals.getCurrentCollectorSoulsInfo()
                        marker.setProgress((souls, capacity))
                        self._invokeMarker(markerID, 'setProgress', souls, capacity)
            return


class EventECPUpdateComponent(EventComponent):

    def start(self):
        battleMarkersCtrl = self.sessionProvider.dynamic.battleMarkers
        if battleMarkersCtrl is not None:
            battleMarkersCtrl.events.onECPAdded += self.__onECPAdded
            battleMarkersCtrl.events.onECPRemoved += self.__onECPRemoved
            battleMarkersCtrl.events.onECPUpdated += self.__onECPUpdated
        return

    def stop(self):
        battleMarkersCtrl = self.sessionProvider.dynamic.battleMarkers
        if battleMarkersCtrl is not None:
            battleMarkersCtrl.events.onECPAdded -= self.__onECPAdded
            battleMarkersCtrl.events.onECPRemoved -= self.__onECPRemoved
            battleMarkersCtrl.events.onECPUpdated -= self.__onECPUpdated
        return

    def _restart(self):
        for markerKey in self._markers.iterkeys():
            self._destroyMarker(self._markers[markerKey].getMarkerID())

        self._markers.clear()
        ecpComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'ecp', None)
        if ecpComp is not None:
            ecpCompEntities = ecpComp.getECPEntities()
            for ecp in ecpCompEntities.values():
                self.__onECPAdded(ecp)

        return

    def _setProgressToMarker(self, marker, progress):
        if marker.getSymbol().startswith((marker.VOLOT_SYMBOL,)):
            self._setMarkerActive(marker.getMarkerID(), bool(progress[1]))
            if marker.getProgress() != progress:
                marker.setProgress(progress)
                self._invokeMarker(marker.getMarkerID(), 'setProgress', progress[0], progress[1])

    def _setDistanceToObject(self, marker):
        player = BigWorld.player()
        distance = marker.getDistance(player.position)
        if distance is None:
            return
        else:
            if not marker.getSymbol().startswith((marker.VOLOT_SYMBOL,)):
                shouldNotHide = distance <= AOI.VEHICLE_CIRCULAR_AOI_RADIUS or marker.getReplyCount()
                self._setMarkerActive(marker.getMarkerID(), shouldNotHide)
                marker.setActive(shouldNotHide)
            self._invokeMarker(marker.getMarkerID(), 'setDistance', distance)
            return

    def _setMarkerActive(self, markerID, shouldNotHide):
        raise NotImplementedError

    def _destroyMarker(self, markerID):
        raise NotImplementedError

    def _addCampOrControlPointMarker(self, symbol, position, ecpID):
        raise NotImplementedError

    def __onECPAdded(self, ecp):
        if ecp.minimapSymbol and ecp.minimapSymbol is not None:
            minimapSymbol = EventBaseMarker.MARKER_SYMBOLS.get(ecp.minimapSymbol, None)
            if minimapSymbol is None:
                return
            self._addCampOrControlPointMarker(ecp.minimapSymbol, ecp.position, ecp.id)
        return

    def __onECPRemoved(self, ecp):
        if ecp.id in self._markers:
            marker = self._markers[ecp.id]
            self._destroyMarker(marker.getMarkerID())
            del self._markers[ecp.id]

    def __onECPUpdated(self, progress):
        for marker in self._markers.itervalues():
            self._setProgressToMarker(marker, progress)
            self._setDistanceToObject(marker)


class EventChatCommandTargetUpdateComponent(EventTargetMarkerUpdateComponent, EventECPUpdateComponent):
    UNSUPPORTED_COMMAND_NAMES = (BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE,
     BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE,
     BATTLE_CHAT_COMMAND_NAMES.DEFEND_BASE,
     BATTLE_CHAT_COMMAND_NAMES.ATTACK_BASE,
     BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION,
     BATTLE_CHAT_COMMAND_NAMES.SOS)
    __UNSUPPORTED_COMMAND_VEH_MARKERS = []
    for cmd in BATTLE_CHAT_COMMANDS:
        vehMarker = cmd.vehMarker
        cmdName = cmd.name
        if cmdName in UNSUPPORTED_COMMAND_NAMES:
            __UNSUPPORTED_COMMAND_VEH_MARKERS.append(vehMarker)

    def start(self):
        EventTargetMarkerUpdateComponent.start(self)
        EventECPUpdateComponent.start(self)
        arena = avatar_getter.getArena()
        if arena is not None:
            arena.onChatCommandTriggered += self.__onChatCommandTriggered
            arena.onChatCommandTargetUpdate += self.__onChatCommandTargetUpdate
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onAddCommandReceived += self.__onAddCommandReceived
            ctrl.onRemoveCommandReceived += self.__onRemoveCommandReceived
        return

    def stop(self):
        EventTargetMarkerUpdateComponent.stop(self)
        EventECPUpdateComponent.stop(self)
        arena = avatar_getter.getArena()
        if arena is not None:
            arena.onChatCommandTriggered -= self.__onChatCommandTriggered
            arena.onChatCommandTargetUpdate -= self.__onChatCommandTargetUpdate
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onAddCommandReceived -= self.__onAddCommandReceived
            ctrl.onRemoveCommandReceived -= self.__onRemoveCommandReceived
        return

    def _restart(self):
        EventECPUpdateComponent._restart(self)
        EventTargetMarkerUpdateComponent._restart(self)

    def _setDistanceToObject(self, marker):
        pass

    def _setProgressToMarker(self, marker, progress):
        pass

    def _setMarkerActive(self, markerID, shouldNotHide):
        pass

    def _destroyMarker(self, markerID):
        pass

    def _setChatCommand(self, vehicleID, chatCommandName, chatCommandFlags):
        raise NotImplementedError

    def _updateTriggeredChatCommands(self, updateList):
        raise NotImplementedError

    def __onChatCommandTargetUpdate(self, _, chatCommands):
        self.__onChatCommandTriggered(chatCommands)

    def __onChatCommandTriggered(self, chatCommands):
        data = list()
        for vehicleID, state in chatCommands.iteritems():
            chatCommandName, chatCommandFlags = state
            if chatCommandName in self.__UNSUPPORTED_COMMAND_VEH_MARKERS:
                continue
            self._setChatCommand(vehicleID, chatCommandName, chatCommandFlags)
            entry = {'chatCommandName': str(chatCommandName),
             'vehicleID': int(vehicleID)}
            data.append(entry)

        updateList = {'chatCommands': data}
        self._updateTriggeredChatCommands(updateList)

    def __onRemoveCommandReceived(self, removeID, _):
        chatCommand = self._chatCommands.get(removeID)
        if chatCommand is None:
            return
        else:
            chatCmd = {chatCommand.commandCreatorVehID: (EMPTY_STATE, EMPTY_CHAT_CMD_FLAG)}
            del self._chatCommands[removeID]
            self.__onChatCommandTriggered(chatCmd)
            return

    def __onAddCommandReceived(self, addedID, markerType):
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        if advChatCmp is None:
            return
        else:
            chatCmdData = advChatCmp.getCommandDataForTargetIDAndMarkerType(addedID, markerType)
            if chatCmdData is None:
                return
            if chatCmdData.commandCreatorVehID == avatar_getter.getPlayerVehicleID():
                return
            cmdVehMarker = _ACTIONS.battleChatCommandFromActionID(chatCmdData.command.getID()).vehMarker
            if cmdVehMarker in self.__UNSUPPORTED_COMMAND_VEH_MARKERS:
                return
            self._chatCommands[addedID] = chatCmdData
            return
