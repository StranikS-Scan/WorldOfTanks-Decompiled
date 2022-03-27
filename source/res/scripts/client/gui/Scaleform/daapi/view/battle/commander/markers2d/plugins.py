# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/markers2d/plugins.py
import functools
import typing
from collections import namedtuple
import BigWorld
import Math
import BattleReplay
from constants import ATTACK_REASONS
from Event import Event
from RTSShared import RTSOrder, RTSManner
from chat_commands_consts import INVALID_MARKER_ID
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import getHitStateVO, getVehicleDamageType
from gui.battle_control.controllers.commander.rts_commander_ctrl import getPrioritizedCondition
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from items.battle_royale import isSpawnedBot
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import MarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import VehicleMarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.settings import MARKER_SYMBOL_NAME
from gui.Scaleform.daapi.view.battle.commander.markers2d.markers import SupplyMarker, OrderMarker
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID, MARKER_HIT_STATE
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import VehicleConditions
if typing.TYPE_CHECKING:
    from typing import Dict
COMMANDER_ACTION_MARKER_OBSERVED = 'observed'
COMMANDER_ACTION_MARKER_ORDER_CONFIRM = 'orderConfirm'
COMMANDER_ACTION_MARKER_ATTACK_BERSERK = 'attackOrderBerserk'
COMMANDER_ACTION_MARKER_ATTACK = 'attackOrder'
COMMANDER_ACTION_MARKER_HALT = 'negative'
CommanderActionMarker = namedtuple('CommanderActionMarker', ('actionName', 'priority', 'isSticky'))
COMMANDER_ACTION_NAME_TO_DESC = {COMMANDER_ACTION_MARKER_HALT: CommanderActionMarker(actionName=COMMANDER_ACTION_MARKER_HALT, priority=1, isSticky=False),
 COMMANDER_ACTION_MARKER_ORDER_CONFIRM: CommanderActionMarker(actionName=COMMANDER_ACTION_MARKER_ORDER_CONFIRM, priority=1, isSticky=False),
 COMMANDER_ACTION_MARKER_ATTACK: CommanderActionMarker(actionName=COMMANDER_ACTION_MARKER_ATTACK, priority=0, isSticky=False),
 COMMANDER_ACTION_MARKER_ATTACK_BERSERK: CommanderActionMarker(actionName=COMMANDER_ACTION_MARKER_ATTACK_BERSERK, priority=0, isSticky=False)}
ORDER_CONFIRM_TIME = 3.0
SPOTTED_STATE_TIME = 4.0
HALT_STATE_TIME = 3.0
STICKY_MARKER_TIME = 9.0
STICKY_MARKER_MIN_SCALE = 140.0
_SUPPLY_MARKER_CULL_DISTANCE = 1000000
_SUPPLY_MARKER_MIN_SCALE = 0.0
_SUPPLY_MARKER_BOUNDS = Math.Vector4(50, 50, 80, 65)
_INNER_SUPPLY_MARKER_BOUNDS = Math.Vector4(17, 17, 55, 25)
_SUPPLY_MARKER_BOUNDS_MIN_SCALE = Math.Vector2(1.0, 1.0)
_MANNER_TO_ACTION = {RTSManner.DEFENSIVE: 'smart',
 RTSManner.HOLD: 'hold',
 RTSManner.SCOUT: 'scout'}

class _PluginHandler(object):
    __slots__ = ('onSetEvent', 'onResetEvent')

    def __init__(self):
        self.onSetEvent = Event()
        self.onResetEvent = Event()

    def init(self):
        pass

    def fini(self):
        self.onSetEvent.clear()
        self.onResetEvent.clear()


class _OrderConfirmHandler(_PluginHandler):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('__stateCBs',)

    def __init__(self):
        super(_OrderConfirmHandler, self).__init__()
        self.__stateCBs = {}

    def init(self):
        super(_OrderConfirmHandler, self).init()
        self.__sessionProvider.dynamic.rtsCommander.vehicles.onOrderChanged += self.__onOrderChanged

    def fini(self):
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if rtsCommander is not None:
            rtsCommander.vehicles.onOrderChanged -= self.__onOrderChanged
        for cbID in self.__stateCBs.values():
            BigWorld.cancelCallback(cbID)

        self.__stateCBs.clear()
        super(_OrderConfirmHandler, self).fini()
        return

    def __resetCB(self, vehicleID):
        if vehicleID in self.__stateCBs:
            self.__stateCBs.pop(vehicleID)
        self.onResetEvent(vehicleID)

    def __onOrderChanged(self, entityID, order=None, target=None, extra=None, **kwargs):
        if extra and extra.get('halt'):
            return
        if entityID in self.__stateCBs:
            BigWorld.cancelCallback(self.__stateCBs.pop(entityID))
        self.__stateCBs[entityID] = BigWorld.callback(ORDER_CONFIRM_TIME, functools.partial(self.__resetCB, entityID))
        self.onSetEvent(entityID)


class _AttackTargetHandler(_PluginHandler):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('__vehicleTargets',)

    def __init__(self):
        super(_AttackTargetHandler, self).__init__()
        self.__vehicleTargets = {}

    def init(self):
        super(_AttackTargetHandler, self).init()
        vehicles = self.__sessionProvider.dynamic.rtsCommander.vehicles
        vehicles.onVehicleTargeted += self.__onVehicleTargeted

    def fini(self):
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if rtsCommander is not None:
            rtsCommander.vehicles.onVehicleTargeted -= self.__onVehicleTargeted
        super(_AttackTargetHandler, self).fini()
        return

    def __onVehicleTargeted(self, entityID, order):
        prevOrder = self.__vehicleTargets.get(entityID, None)
        if prevOrder != order:
            self.__vehicleTargets[entityID] = order
            if prevOrder == RTSOrder.ATTACK_ENEMY:
                self.onResetEvent(entityID, isAggressive=False)
            elif prevOrder == RTSOrder.FORCE_ATTACK_ENEMY:
                self.onResetEvent(entityID, isAggressive=True)
        if order == RTSOrder.ATTACK_ENEMY:
            self.onSetEvent(entityID, isAggressive=False)
        elif order == RTSOrder.FORCE_ATTACK_ENEMY:
            self.onSetEvent(entityID, isAggressive=True)
        return


class _HaltHandler(_PluginHandler):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('__stateCBs',)

    def __init__(self):
        super(_HaltHandler, self).__init__()
        self.__stateCBs = {}

    def init(self):
        super(_HaltHandler, self).init()
        self.__sessionProvider.dynamic.rtsCommander.vehicles.onOrderChanged += self.__onOrderChanged

    def fini(self):
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if rtsCommander is not None:
            rtsCommander.vehicles.onOrderChanged -= self.__onOrderChanged
        for cbID in self.__stateCBs.values():
            BigWorld.cancelCallback(cbID)

        self.__stateCBs.clear()
        super(_HaltHandler, self).fini()
        return

    def __reset(self, vehicleID):
        if vehicleID in self.__stateCBs:
            self.__stateCBs.pop(vehicleID)
        self.onResetEvent(vehicleID)

    def __set(self, vehicleID):
        if vehicleID in self.__stateCBs:
            BigWorld.cancelCallback(self.__stateCBs.pop(vehicleID))
        self.__stateCBs[vehicleID] = BigWorld.callback(HALT_STATE_TIME, functools.partial(self.__reset, vehicleID))
        self.onSetEvent(vehicleID)

    def __onOrderChanged(self, vehicleID, extra=None, **kwargs):
        if extra and extra.get('halt'):
            self.__set(vehicleID)


class _DeathHandler(_PluginHandler):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('__stateCBs',)

    def __init__(self):
        super(_DeathHandler, self).__init__()
        self.__stateCBs = {}

    def init(self):
        super(_DeathHandler, self).init()
        player = BigWorld.player()
        if player is not None:
            arena = player.arena
            if arena is not None:
                arena.onVehicleKilled += self.__onArenaVehicleKilled
        return

    def fini(self):
        player = BigWorld.player()
        if player is not None:
            arena = player.arena
            if arena is not None:
                arena.onVehicleKilled -= self.__onArenaVehicleKilled
        for cbID in self.__stateCBs.values():
            BigWorld.cancelCallback(cbID)

        self.__stateCBs.clear()
        super(_DeathHandler, self).fini()
        return

    def __resetDeath(self, vehicleID):
        if vehicleID in self.__stateCBs:
            self.__stateCBs.pop(vehicleID)
        self.onResetEvent(vehicleID)

    def __setDeath(self, vehicleID):
        if vehicleID in self.__stateCBs:
            BigWorld.cancelCallback(self.__stateCBs.pop(vehicleID))
        self.__stateCBs[vehicleID] = BigWorld.callback(STICKY_MARKER_TIME, functools.partial(self.__resetDeath, vehicleID))
        self.onSetEvent(vehicleID)

    def __onArenaVehicleKilled(self, vehicleID, *_):
        vehicle = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(vehicleID)
        if vehicle is None or vehicle.isAlive or not vehicle.isAllyBot:
            return
        else:
            self.__setDeath(vehicleID)
            return


class _HelpHandler(_PluginHandler):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('__stateCBs', '__ignoringVehicles')

    def __init__(self):
        super(_HelpHandler, self).__init__()
        self.__stateCBs = {}
        self.__ignoringVehicles = []

    def init(self):
        super(_HelpHandler, self).init()
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        return

    def fini(self):
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        for cbID in self.__stateCBs.values():
            BigWorld.cancelCallback(cbID)

        self.__stateCBs.clear()
        super(_HelpHandler, self).fini()
        return

    def __resetHelp(self, vehicleID):
        if vehicleID in self.__stateCBs:
            self.__stateCBs.pop(vehicleID)
        self.onResetEvent(vehicleID)

    def __setHelp(self, vehicleID):
        if vehicleID in self.__stateCBs:
            BigWorld.cancelCallback(self.__stateCBs.pop(vehicleID))
        self.__stateCBs[vehicleID] = BigWorld.callback(STICKY_MARKER_TIME, functools.partial(self.__resetHelp, vehicleID))
        self.onSetEvent(vehicleID)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if vehicleID in self.__ignoringVehicles:
            return
        else:
            vehicle = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(vehicleID)
            if vehicle is None or not (vehicle.isAlive and vehicle.isAllyBot):
                return
            if eventID == FEEDBACK_EVENT_ID.VEHICLE_HEALTH:
                curHealth = value[0]
                maxHealth = vehicle.maxHealth
                if curHealth < maxHealth / 2:
                    self.__setHelp(vehicleID)
                    self.__ignoringVehicles.append(vehicleID)
            return


class _LinkHandler(_PluginHandler):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def init(self):
        super(_LinkHandler, self).init()
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        rtsCommander.vehicles.onVehicleSpeedLinkChanged += self.__onVehicleSpeedLinkChanged

    def fini(self):
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if rtsCommander:
            rtsCommander.vehicles.onVehicleSpeedLinkChanged -= self.__onVehicleSpeedLinkChanged
        super(_LinkHandler, self).fini()

    def __onVehicleSpeedLinkChanged(self, vID, isSpeedLink):
        if isSpeedLink:
            self.onSetEvent(vID)
        else:
            self.onResetEvent(vID)


class _MannerHandler(_PluginHandler):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(_MannerHandler, self).__init__()
        self.__previousManner = None
        return

    def init(self):
        super(_MannerHandler, self).init()
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        rtsCommander.vehicles.onMannerChanged += self.__onMannerChanged

    def fini(self):
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if rtsCommander:
            rtsCommander.vehicles.onMannerChanged -= self.__onMannerChanged
        super(_MannerHandler, self).fini()

    def __onMannerChanged(self, vID, manner):
        if manner in _MANNER_TO_ACTION:
            self.onSetEvent(vID, _MANNER_TO_ACTION[manner])
            self.__previousManner = manner
        elif self.__previousManner is not None:
            self.onResetEvent(vID, _MANNER_TO_ACTION[self.__previousManner])
        return


class _SpeakingHandler(_PluginHandler):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def init(self):
        super(_SpeakingHandler, self).init()
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        rtsCommander.vehicles.onVehicleSpeaking += self.__onVehicleSpeaking

    def fini(self):
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if rtsCommander:
            rtsCommander.vehicles.onVehicleSpeaking -= self.__onVehicleSpeaking
        super(_SpeakingHandler, self).fini()

    def __onVehicleSpeaking(self, vID, isSpeaking):
        if isSpeaking:
            self.onSetEvent(vID)
        else:
            self.onResetEvent(vID)


class RTSCommanderMarkerPlugin(VehicleMarkerPlugin):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __DEAD_CONDITION_TIMER_DURATION = 10

    def __init__(self, parentObj):
        super(RTSCommanderMarkerPlugin, self).__init__(parentObj)
        self.attackTargetHandler = _AttackTargetHandler()
        self.haltHandler = _HaltHandler()
        self.orderConfirmHandler = _OrderConfirmHandler()
        self.linkHandler = _LinkHandler()
        self.mannerHandler = _MannerHandler()
        self.speakingHandler = _SpeakingHandler()
        self._focusedVehicleID = None
        self._selectedVehicleIDs = set()
        self._actionMarkers = {}
        self.__vehicleStatus = {}
        return

    def start(self):
        super(RTSCommanderMarkerPlugin, self).start()
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        rtsCommander.vehicles.onVehicleUpdated += self.__onVehicleUpdated
        rtsCommander.vehicles.onVehicleGroupChanged += self.__onVehicleGroupChanged
        rtsCommander.vehicles.onFocusVehicleChanged += self._onFocusVehicleChanged
        rtsCommander.vehicles.onVehiclesInDragBoxChanged += self._onVehiclesInDragBoxChanged
        rtsCommander.vehicles.onSelectionChanged += self._onSelectionChanged
        rtsCommander.vehicles.onVehicleReloading += self.__onVehicleReloading
        rtsCommander.vehicles.onVehicleShellsUpdated += self.__onVehicleShellsUpdated
        rtsCommander.vehicles.onVehicleDisabledStateChanged += self.__onVehicleDisabledStateChanged
        rtsCommander.vehicles.onVehicleConditionUpdated += self.onVehicleConditionUpdated
        self.haltHandler.onSetEvent += self.setHalt
        self.haltHandler.onResetEvent += self.resetHalt
        self.haltHandler.init()
        self.orderConfirmHandler.onSetEvent += self._setConfirm
        self.orderConfirmHandler.onResetEvent += self._resetConfirm
        self.orderConfirmHandler.init()
        self.attackTargetHandler.onSetEvent += self._onAttack
        self.attackTargetHandler.onResetEvent += self._onTargetReset
        self.attackTargetHandler.init()
        self.linkHandler.onSetEvent += self._onSetLink
        self.linkHandler.onResetEvent += self._onResetLink
        self.linkHandler.init()
        self.mannerHandler.onSetEvent += self._onSetManner
        self.mannerHandler.onResetEvent += self._onResetManner
        self.mannerHandler.init()
        self.speakingHandler.onSetEvent += self._onSetSpeaking
        self.speakingHandler.onResetEvent += self._onResetSpeaking
        self.speakingHandler.init()
        self._focusedVehicleID = None
        self._selectedVehicleIDs = set()
        vehicles = self.__sessionProvider.dynamic.rtsCommander.vehicles
        self._onFocusVehicleChanged(vehicles.focusedID, True)
        self._onSelectionChanged(set(vehicles.iterkeys(lambda v: v.isSelected)))
        self.__deadConditionTimer = CallbackDelayer()
        return

    def stop(self):
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if rtsCommander is not None:
            rtsCommander.vehicles.onVehicleUpdated -= self.__onVehicleUpdated
            rtsCommander.vehicles.onVehicleGroupChanged -= self.__onVehicleGroupChanged
            rtsCommander.vehicles.onFocusVehicleChanged -= self._onFocusVehicleChanged
            rtsCommander.vehicles.onVehiclesInDragBoxChanged -= self._onVehiclesInDragBoxChanged
            rtsCommander.vehicles.onSelectionChanged -= self._onSelectionChanged
            rtsCommander.vehicles.onVehicleReloading -= self.__onVehicleReloading
            rtsCommander.vehicles.onVehicleShellsUpdated -= self.__onVehicleShellsUpdated
            rtsCommander.vehicles.onVehicleDisabledStateChanged -= self.__onVehicleDisabledStateChanged
            rtsCommander.vehicles.onVehicleConditionUpdated -= self.onVehicleConditionUpdated
        self.haltHandler.onSetEvent -= self.setHalt
        self.haltHandler.onResetEvent -= self.resetHalt
        self.haltHandler.fini()
        self.orderConfirmHandler.onSetEvent -= self._setConfirm
        self.orderConfirmHandler.onResetEvent -= self._resetConfirm
        self.orderConfirmHandler.fini()
        self.attackTargetHandler.onSetEvent -= self._onAttack
        self.attackTargetHandler.onResetEvent -= self._onTargetReset
        self.attackTargetHandler.fini()
        self.linkHandler.onSetEvent -= self._onSetLink
        self.linkHandler.onResetEvent -= self._onResetLink
        self.linkHandler.fini()
        self.mannerHandler.onSetEvent -= self._onSetManner
        self.mannerHandler.onResetEvent -= self._onResetManner
        self.mannerHandler.fini()
        self.speakingHandler.onSetEvent -= self._onSetSpeaking
        self.speakingHandler.onResetEvent -= self._onResetSpeaking
        self.speakingHandler.fini()
        self._focusedVehicleID = None
        self._selectedVehicleIDs = set()
        self.__deadConditionTimer.clearCallbacks()
        super(RTSCommanderMarkerPlugin, self).stop()
        return

    def onVehicleConditionUpdated(self, vehicleID, conditions):
        condition = getPrioritizedCondition(vehicleID, conditions)
        self._showActionMarker(vehicleID, condition)

    def setHalt(self, vehicleID):
        self._showActionMarker(vehicleID, COMMANDER_ACTION_MARKER_HALT)

    def resetHalt(self, vehicleID):
        self._hideActionMarker(vehicleID, COMMANDER_ACTION_MARKER_HALT)

    def updateCommanderDataList(self):
        for vID, _ in BigWorld.player().arena.commanderData.items():
            self._updateRTSInfo(vID)

    def updateCommanderDataVehicle(self, vInfo):
        self._updateRTSInfo(vInfo.vehicleID, isCommander=True)

    def updateVehiclesInfo(self, updated, arenaDP):
        super(RTSCommanderMarkerPlugin, self).updateVehiclesInfo(updated, arenaDP)
        for _, vInfo in updated:
            vehicleID = vInfo.vehicleID
            self._updateRTSInfo(vehicleID)
            self.__onArenaVehicleUpdated(vehicleID)

    def invalidateVehiclesInfo(self, arenaDP):
        super(RTSCommanderMarkerPlugin, self).invalidateVehiclesInfo(arenaDP)
        for vInfo in arenaDP.getVehiclesInfoIterator():
            vehicleID = vInfo.vehicleID
            self._updateRTSInfo(vehicleID)
            self.__onArenaVehicleUpdated(vehicleID)

    def addVehicleInfo(self, vInfo, arenaDP):
        super(RTSCommanderMarkerPlugin, self).addVehicleInfo(vInfo, arenaDP)
        vehicleID = vInfo.vehicleID
        self._updateRTSInfo(vehicleID)
        self.__onArenaVehicleUpdated(vehicleID)

    def _onFocusVehicleChanged(self, focusVehicleID, isInFocus):
        focusVehicleID = focusVehicleID if isInFocus else 0
        self._updateFocusedSelected(self._focusedVehicleID)
        self._focusedVehicleID = focusVehicleID
        self._updateFocusedSelected(self._focusedVehicleID)

    def _onVehiclesInDragBoxChanged(self, vehicleIDs, isInDragBox):
        for vehicleID in vehicleIDs:
            marker = self._markers.get(vehicleID)
            if marker is not None:
                self._invokeMarker(marker.getMarkerID(), 'updateFocusedSelected', isInDragBox, False)

        return

    def _getMarkerSymbol(self, vehicleID):
        vehicle = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(vehicleID)
        return MARKER_SYMBOL_NAME.RTS_CONTROLLABLE_VEHICLE_MARKER if vehicle and vehicle.isAllyBot else MARKER_SYMBOL_NAME.RTS_VEHICLE_MARKER

    def _onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if vehicleID not in self._markers:
            return
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_DEAD:
            marker = self._markers[vehicleID]
            handle = marker.getMarkerID()
            self._hide(handle, vehicleID)
            if not self.__sessionProvider.dynamic.rtsCommander.vehicles[vehicleID].isAlly:
                self._invokeMarker(handle, 'stopActionMarker')
            self._updateMarkerState(handle, 'dead', value)
            self._setMarkerBoundEnabled(handle, False)
            return
        super(RTSCommanderMarkerPlugin, self)._onVehicleFeedbackReceived(eventID, vehicleID, value)

    def _onSelectionChanged(self, selectedVehicleIDs):
        selectedIDs = set(selectedVehicleIDs)
        for vehicleID in selectedIDs ^ self._selectedVehicleIDs:
            self._updateFocusedSelected(vehicleID)

        self._selectedVehicleIDs = selectedIDs

    def _updateFocusedSelected(self, vehicleID):
        marker = self._markers.get(vehicleID)
        if marker is None:
            return
        else:
            vehicles = self.__sessionProvider.dynamic.rtsCommander.vehicles
            vehicle = vehicles.get(vehicleID)
            if vehicle is None or not vehicle.isAlive:
                return
            focused = vehicles.focusedID == vehicleID
            selectedVehicleIDsLength = len(self._selectedVehicleIDs)
            if vehicle.isEnemy and selectedVehicleIDsLength == 0:
                focused = False
            self._invokeMarker(marker.getMarkerID(), 'updateFocusedSelected', focused, vehicle.isSelected)
            return

    def _setConfirm(self, vehicleID):
        self._showActionMarker(vehicleID, COMMANDER_ACTION_MARKER_ORDER_CONFIRM)

    def _resetConfirm(self, vehicleID):
        self._hideActionMarker(vehicleID, COMMANDER_ACTION_MARKER_ORDER_CONFIRM)

    def _onAttack(self, target, isAggressive):
        self._showActionMarker(target, COMMANDER_ACTION_MARKER_ATTACK_BERSERK if isAggressive else COMMANDER_ACTION_MARKER_ATTACK)
        self._triggerClickAnimation(target)

    def _onTargetReset(self, vehicleID, isAggressive):
        self._hideActionMarker(vehicleID, COMMANDER_ACTION_MARKER_ATTACK_BERSERK if isAggressive else COMMANDER_ACTION_MARKER_ATTACK)

    def _showActionMarker(self, vehicleID, actionName):
        marker = self._markers.get(vehicleID)
        if marker is None or actionName == '':
            return
        else:
            markerID = marker.getMarkerID()
            if actionName in VehicleConditions.ALL_CONDITIONS:
                self._invokeMarker(markerID, 'showActionMarker', actionName)
                self._setMarkerSticky(markerID, isSticky=actionName in VehicleConditions.STICKY_CONDITIONS)
                self._actionMarkers[vehicleID] = None
                if actionName == VehicleConditions.DEAD_CONDITION:
                    self.__deadConditionTimer.delayCallback(RTSCommanderMarkerPlugin.__DEAD_CONDITION_TIMER_DURATION, functools.partial(self.__onDeadConditionTimerEnd, vehicleID))
            else:
                newActionMarker = COMMANDER_ACTION_NAME_TO_DESC[actionName]
                oldActionMarker = self._actionMarkers.get(vehicleID)
                if oldActionMarker is not None and newActionMarker.priority < oldActionMarker.priority:
                    return
                self._invokeMarker(markerID, 'showActionMarker', newActionMarker.actionName)
                self._setMarkerSticky(markerID, isSticky=newActionMarker.isSticky)
                self._actionMarkers[vehicleID] = newActionMarker
            return

    def _hideActionMarker(self, vehicleID, actionName=None):
        if actionName is None:
            return
        else:
            marker = self._markers.get(vehicleID)
            if marker is None:
                return
            actionMarker = self._actionMarkers.get(vehicleID)
            if actionMarker is None:
                return
            if actionMarker.actionName != actionName:
                return
            markerID = marker.getMarkerID()
            self._invokeMarker(markerID, 'stopActionMarker')
            self._actionMarkers.pop(vehicleID)
            self._setMarkerSticky(markerID, isSticky=False)
            return

    def _triggerClickAnimation(self, vehicleID):
        marker = self._markers.get(vehicleID)
        if marker is None:
            return
        else:
            self._invokeMarker(marker.getMarkerID(), 'triggerClickAnimation')
            return

    def _showSpecialIcon(self, vehicleID, actionName):
        marker = self._markers.get(vehicleID)
        if marker is None:
            return
        else:
            markerID = marker.getMarkerID()
            self._invokeMarker(markerID, 'showSpecialIcon', actionName)
            return

    def _hideSpecialIcon(self, vehicleID, actionName):
        marker = self._markers.get(vehicleID)
        if marker is None:
            return
        else:
            markerID = marker.getMarkerID()
            self._invokeMarker(markerID, 'stopSpecialIcon', actionName)
            return

    def _updateRTSInfo(self, vehicleID, isCommander=False):
        marker = self._markers.get(vehicleID)
        if marker is None:
            return
        else:
            player = BigWorld.player()
            arenaVehicle = player.arena.vehicles.get(vehicleID)
            self._invokeMarker(marker.getMarkerID(), 'updateRTSInfo', vehicleID, arenaVehicle.get('accountDBID') == 0)
            rtsVehicles = self.__sessionProvider.dynamic.rtsCommander.vehicles
            if vehicleID in rtsVehicles.keys() and not isCommander:
                self.__onVehicleDisabledStateChanged(vehicleID, not rtsVehicles[vehicleID].isEnabled)
                rtsVehicleProxy = rtsVehicles[vehicleID]
                if rtsVehicleProxy.isAllyBot:
                    arena = avatar_getter.getArena()
                    if arena is not None:
                        commanderData = arena.commanderData.get(vehicleID)
                        if not commanderData:
                            return
                        orderData = commanderData.orderData
                        if orderData is None:
                            return
                        manner = _MANNER_TO_ACTION[orderData.manner] if orderData.manner in _MANNER_TO_ACTION else _MANNER_TO_ACTION[RTSManner.DEFAULT]
                        self._onSetManner(vehicleID, manner)
            return

    def _onSetLink(self, vehicleID):
        self._showSpecialIcon(vehicleID, 'link')

    def _onResetLink(self, vehicleID):
        self._hideSpecialIcon(vehicleID, 'link')

    def _onSetManner(self, vehicleID, action):
        self._showSpecialIcon(vehicleID, action)

    def _onResetManner(self, vehicleID, action):
        self._hideSpecialIcon(vehicleID, action)

    def _onSetSpeaking(self, vehicleID):
        marker = self._markers.get(vehicleID)
        if marker is None:
            return
        else:
            markerID = marker.getMarkerID()
            self._invokeMarker(markerID, 'setSpeaking', True)
            return

    def _onResetSpeaking(self, vehicleID):
        marker = self._markers.get(vehicleID)
        if marker is None:
            return
        else:
            markerID = marker.getMarkerID()
            self._invokeMarker(markerID, 'setSpeaking', False)
            return

    def _setMarkerMinScale(self, handle, minscale):
        if self._parentObj is not None:
            self._parentObj.setMarkerMinScale(handle, minscale)
        return

    def _onVehicleMarkerAdded(self, vProxy, vInfo, guiProps):
        super(RTSCommanderMarkerPlugin, self)._onVehicleMarkerAdded(vProxy, vInfo, guiProps)
        self._updateRTSInfo(vInfo.vehicleID)

    def __onVehicleReloading(self, vehicleID, reloadingState):
        marker = self._markers.get(vehicleID)
        if marker is None:
            return
        else:
            updateTime, timeLeft, baseTime = reloadingState
            self._invokeMarker(marker.getMarkerID(), 'setReloading', updateTime, timeLeft, baseTime)
            return

    def __onVehicleShellsUpdated(self, vehicleID, maxCount, currentCount, isAutoload, isDualGun):
        marker = self._markers.get(vehicleID)
        if marker is None:
            return
        else:
            self._invokeMarker(marker.getMarkerID(), 'setClipData', maxCount, currentCount, isAutoload, isDualGun)
            return

    def __onVehicleDisabledStateChanged(self, vehicleID, isDisabled):
        marker = self._markers.get(vehicleID)
        if marker is None:
            return
        else:
            if vehicleID in self._markers:
                marker = self._markers[vehicleID]
                if isDisabled and marker.isActive():
                    marker.setActive(False)
                    markerID = marker.getMarkerID()
                    self._setMarkerActive(markerID, False)
                    self._setMarkerMatrix(markerID, None)
                    marker.detach()
                elif not isDisabled and not marker.isActive():
                    vehicle = BigWorld.entity(vehicleID)
                    if vehicle is None:
                        return
                    vProxy = vehicle.proxy
                    marker.attach(vProxy)
                    marker.setActive(True)
                    self._setMarkerMatrix(marker.getMarkerID(), marker.getMatrixProvider())
                    self._setMarkerActive(marker.getMarkerID(), True)
            return

    def __onArenaVehicleUpdated(self, vehicleID):
        vehicle = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(vehicleID)
        if vehicle is not None:
            self.__onVehicleUpdated(vehicle)
        return

    def __onVehicleUpdated(self, vehicle):
        if vehicle.isControllable:
            self.__onVehicleGroupChanged(vehicle.id, vehicle.groupID)
            self.__onVehicleReloading(vehicle.id, vehicle.reloadingState)

    def __onVehicleGroupChanged(self, vehicleID, commanderGroup):
        marker = self._markers.get(vehicleID)
        if marker is not None:
            self._invokeMarker(marker.getMarkerID(), 'setGroupID', commanderGroup)
        return

    def __onDeadConditionTimerEnd(self, vehicleID):
        marker = self._markers.get(vehicleID)
        if marker:
            markerID = marker.getMarkerID()
            self._invokeMarker(markerID, 'stopActionMarker')
            self._setMarkerSticky(markerID, isSticky=False)


class RTSTankmanMarkerPlugin(VehicleMarkerPlugin):

    def _getMarkerSymbol(self, vehicleID):
        player = BigWorld.player()
        arenaVehicle = player.arena.vehicles.get(vehicleID)
        return MARKER_SYMBOL_NAME.RTS_TANKMAN_VEHICLE_MARKER if arenaVehicle.get('accountDBID') == 0 else super(RTSTankmanMarkerPlugin, self)._getMarkerSymbol(vehicleID)


class _SupplyMarkerPlugin(VehicleMarkerPlugin, IArenaVehiclesController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('_markers', '_clazz', '_playerVehicleID', '_spottedSupplies', '_actionMarkers')

    def __init__(self, parentObj, clazz=SupplyMarker):
        super(_SupplyMarkerPlugin, self).__init__(parentObj)
        self._actionMarkers = {}
        self._markers = {}
        self._playerVehicleID = 0
        self._clazz = clazz
        self._spottedSupplies = []

    def init(self, *args):
        super(_SupplyMarkerPlugin, self).init()
        sessionProvider = self.__sessionProvider
        sessionProvider.addArenaCtrl(self)
        self._playerVehicleID = sessionProvider.getArenaDP().getPlayerVehicleID()
        ctrl = sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded += self.__onVehicleMarkerAdded
            ctrl.onVehicleMarkerRemoved += self.__onVehicleMarkerRemoved
        return

    def fini(self):
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded -= self.__onVehicleMarkerAdded
            ctrl.onVehicleMarkerRemoved -= self.__onVehicleMarkerRemoved
        while self._markers:
            _, marker = self._markers.popitem()
            marker.destroy()

        super(_SupplyMarkerPlugin, self).fini()
        return

    def start(self):
        super(_SupplyMarkerPlugin, self).start()
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if rtsCommander is not None:
            rtsCommander.vehicles.onVehicleReloading += self.__onVehicleReloading
        return

    def stop(self):
        super(_SupplyMarkerPlugin, self).stop()
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if rtsCommander is not None:
            rtsCommander.vehicles.onVehicleReloading -= self.__onVehicleReloading
        return

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(self.__sessionProvider.getArenaDP())

    def invalidateVehiclesInfo(self, arenaDP):
        feedback = self.__sessionProvider.shared.feedback
        for vInfo in arenaDP.getVehiclesInfoIterator():
            vehicleID = vInfo.vehicleID
            vProxy = feedback.getVehicleProxy(vehicleID)
            self.__onVehicleMarkerAdded(vProxy=vProxy, vInfo=vInfo, guiProps=None)

        return

    def isMarkerActive(self, targetID):
        if targetID in self._markers:
            marker = self._markers[targetID]
            return marker.isActive()
        return False

    def updateVehiclesInfo(self, updated, arenaDP):
        for _, vInfo in updated:
            supplyID = vInfo.vehicleID
            if supplyID not in self._markers:
                continue
            marker = self._markers[supplyID]
            self.__setSupplyInfo(marker, vInfo)

    def updateCommanderDataVehicle(self, vInfo):
        if not vInfo.isAlive():
            return
        else:
            supplyID = vInfo.vehicleID
            if supplyID in self._markers:
                commanderData = BigWorld.player().arena.commanderData.get(supplyID)
                if commanderData is not None and commanderData.wasSpotted and supplyID not in self._spottedSupplies:
                    markerID = self._markers[supplyID].getMarkerID()
                    self._setMarkerState(markerID, 'spotted')
                    self._spottedSupplies.append(supplyID)
            return

    def addVehicleInfo(self, vInfo, arenaDP):
        vehicleID = vInfo.vehicleID
        vProxy = self.__sessionProvider.shared.feedback.getVehicleProxy(vehicleID)
        self.__onVehicleMarkerAdded(vProxy=vProxy, vInfo=vInfo, guiProps=None)
        return

    def _onVehicleMarkerAdded(self, vProxy, vInfo, guiProps):
        pass

    def _onVehicleMarkerRemoved(self, vehicleID):
        pass

    def _hideSupplyMarker(self, supplyID):
        if supplyID in self._markers:
            marker = self._markers[supplyID]
            if marker.setActive(False):
                markerID = marker.getMarkerID()
                self._setMarkerActive(markerID, False)
                self._setMarkerMatrix(markerID, None)
            marker.detach()
        return

    def _updateMarkerState(self, handle, newState, isImmediate, text='', iconAnimation=''):
        self._invokeMarker(handle, 'updateState', text, iconAnimation)

    def _showActionMarker(self, vehicleID, actionName):
        marker = self._markers.get(vehicleID)
        if marker is None:
            return
        else:
            newActionMarker = COMMANDER_ACTION_NAME_TO_DESC[actionName]
            oldActionMarker = self._actionMarkers.get(vehicleID)
            if oldActionMarker is not None and newActionMarker.priority < oldActionMarker.priority:
                return
            markerID = marker.getMarkerID()
            self._invokeMarker(markerID, 'showActionMarker', newActionMarker.actionName)
            self._actionMarkers[vehicleID] = newActionMarker
            return

    def _hideActionMarker(self, vehicleID, actionName=None):
        if actionName is None:
            return
        else:
            marker = self._markers.get(vehicleID)
            if marker is None:
                return
            actionMarker = self._actionMarkers.get(vehicleID)
            if actionMarker is None:
                return
            if actionMarker.actionName != actionName:
                return
            markerID = marker.getMarkerID()
            self._invokeMarker(markerID, 'stopActionMarker')
            self._actionMarkers.pop(vehicleID)
            return

    def _triggerClickAnimation(self, vehicleID):
        marker = self._markers.get(vehicleID)
        if marker is None:
            return
        else:
            self._invokeMarker(marker.getMarkerID(), 'triggerClickAnimation')
            return

    def __onVehicleMarkerRemoved(self, supplyID):
        self._hideSupplyMarker(supplyID)

    def __onVehicleMarkerAdded(self, vProxy, vInfo, guiProps):
        if not vProxy:
            return
        else:
            vehicleType = vInfo.vehicleType
            if not vehicleType.isSupply:
                return
            supplyClass = vInfo.vehicleType.classTag
            supplyID = vInfo.vehicleID
            if supplyID in self._markers:
                marker = self._markers[supplyID]
                markerID = marker.getMarkerID()
                if marker.setActive(True):
                    marker.attach(vProxy)
                    self._setMarkerMatrix(markerID, marker.getMatrixProvider())
                    self._setMarkerActive(markerID, True)
            else:
                if vInfo.isObserver():
                    return
                marker = self.__addMarkerToPool(supplyID, supplyClass, vInfo=vInfo, vProxy=vProxy)
            if marker is not None:
                self.__setSupplyInfo(marker, vInfo)
                self.updateCommanderDataVehicle(vInfo)
            return

    def __addMarkerToPool(self, supplyID, supplyClass, vInfo, vProxy=None):
        if not vInfo.isAlive() and isSpawnedBot(vInfo.vehicleType.tags):
            return
        else:
            if vProxy is not None:
                matrixProvider = self._clazz.fetchMatrixProvider(vProxy)
                active = True
            else:
                matrixProvider = None
                active = False
            markerID = self._createMarkerWithMatrix(MARKER_SYMBOL_NAME.COMMANDER_SUPPLY_MARKER, matrixProvider=matrixProvider, active=active)
            self._setMarkerRenderInfo(markerID, _SUPPLY_MARKER_MIN_SCALE, _SUPPLY_MARKER_BOUNDS, _INNER_SUPPLY_MARKER_BOUNDS, _SUPPLY_MARKER_CULL_DISTANCE, _SUPPLY_MARKER_BOUNDS_MIN_SCALE)
            marker = self._clazz(markerID, supplyID, supplyClass, vProxy=vProxy, active=active, isPlayerTeam=vInfo.team == avatar_getter.getPlayerTeam())
            marker.onVehicleModelChanged += self._onVehicleModelChanged
            self._markers[supplyID] = marker
            if marker.isActive():
                if not marker.isAlive():
                    self._setMarkerState(markerID, 'dead')
                    self._onVehicleModelChanged(markerID, marker.getMatrixProvider())
                    self._setMarkerBoundEnabled(markerID, False)
                elif not avatar_getter.isVehicleAlive() and marker.getIsPlayerTeam():
                    self._setMarkerBoundEnabled(markerID, False)
            return marker

    def _onVehicleModelChanged(self, markerID, matrixProvider):
        self._setMarkerMatrix(markerID, matrixProvider)

    def getTargetIDFromMarkerID(self, markerID):
        for vehicleID in self._markers:
            if self._markers[vehicleID].getMarkerID() == markerID:
                return vehicleID

        return INVALID_MARKER_ID

    def _setMarkerState(self, handle, newState):
        supplyID = self.getTargetIDFromMarkerID(handle)
        if supplyID != INVALID_MARKER_ID:
            marker = self._markers[supplyID]
            marker.state = newState
            self._invokeMarker(handle, 'setState', newState)

    def __setSupplyInfo(self, marker, vInfo):
        if marker is not None:
            maxHealth = vInfo.vehicleType.maxHealth
            curHealth = marker.getHealth()
            supplyTag = marker.getSupplyTag()
            supplyName = self.__sessionProvider.getCtx().getPlayerFullNameParts(vInfo.vehicleID).vehicleName
            markerID = marker.getMarkerID()
            self._invokeMarker(markerID, 'setSupplyInfo', supplyTag, supplyName, vInfo.vehicleID, maxHealth, curHealth, 'ally' if marker.getIsPlayerTeam() else 'enemy', 0)
        return

    def __onVehicleReloading(self, vehicleID, reloadingState):
        marker = self._markers.get(vehicleID)
        if marker is None:
            return
        else:
            updateTime, timeLeft, baseTime = reloadingState
            self._invokeMarker(marker.getMarkerID(), 'setReloading', updateTime, timeLeft, baseTime)
            return


class TankmanSupplyMarkerPlugin(_SupplyMarkerPlugin):
    pass


class CommanderSupplyMarkerPlugin(_SupplyMarkerPlugin):
    __slots__ = ('_attackTargetHandler',)

    def __init__(self, parentObj, clazz=SupplyMarker):
        super(CommanderSupplyMarkerPlugin, self).__init__(parentObj, clazz)
        self._attackTargetHandler = _AttackTargetHandler()

    def init(self, *args):
        super(CommanderSupplyMarkerPlugin, self).init(*args)
        self._attackTargetHandler.onSetEvent += self.__onAttack
        self._attackTargetHandler.onResetEvent += self.__onTargetReset
        self._attackTargetHandler.init()

    def fini(self):
        self._attackTargetHandler.onSetEvent -= self.__onAttack
        self._attackTargetHandler.onResetEvent -= self.__onTargetReset
        self._attackTargetHandler.fini()
        super(CommanderSupplyMarkerPlugin, self).fini()

    def _onVehicleFeedbackReceived(self, eventID, supplyID, value):
        if supplyID not in self._markers:
            return
        marker = self._markers[supplyID]
        markerID = marker.getMarkerID()
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_DEAD:
            self._setMarkerState(markerID, 'dead')
            self._onVehicleModelChanged(markerID, marker.getMatrixProvider())
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_HEALTH:
            self.__updateVehicleHealth(supplyID, markerID, *value)
        if eventID in MARKER_HIT_STATE:
            _, stateText, iconAnimation = getHitStateVO(eventID, MARKER_HIT_STATE)
            self._updateMarkerState(markerID, stateText, iconAnimation)

    def __onAttack(self, target, isAggressive):
        self._showActionMarker(target, COMMANDER_ACTION_MARKER_ATTACK_BERSERK if isAggressive else COMMANDER_ACTION_MARKER_ATTACK)
        self._triggerClickAnimation(target)

    def __onTargetReset(self, vehicleID, isAggressive):
        self._hideActionMarker(vehicleID, COMMANDER_ACTION_MARKER_ATTACK_BERSERK if isAggressive else COMMANDER_ACTION_MARKER_ATTACK)

    def __updateVehicleHealth(self, _, handle, newHealth, aInfo, attackReasonID):
        if newHealth < 0:
            newHealth = 0
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
            self._invokeMarker(handle, 'setHealth', newHealth)
        else:
            self._invokeMarker(handle, 'updateHealth', newHealth, getVehicleDamageType(aInfo, self._playerVehicleID, self.sessionProvider), ATTACK_REASONS[attackReasonID])


class RTSOrdersMarkerPlugin(MarkerPlugin):
    _MIN_Y_OFFSET = 1.2
    _MAX_Y_OFFSET = 3.0
    _DISTANCE_FOR_MIN_Y_OFFSET = 400
    _MAX_Y_BOOST = 1.4
    _BOOST_START = 120
    _STATIC_MARKER_BOUNDS = Math.Vector4(30, 30, 90, -15)
    _INNER_STATIC_MARKER_BOUNDS = Math.Vector4(15, 15, 70, -35)
    _STATIC_MARKER_BOUNDS_MIN_SCALE = Math.Vector2(1.0, 0.8)
    _INNER_BASE_MARKER_BOUNDS = Math.Vector4(17, 17, 18, 18)
    _STATIC_MARKER_CULL_DISTANCE = 1800
    _STATIC_MARKER_MIN_SCALE = 60.0
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, parentObj, clazz=OrderMarker):
        super(RTSOrdersMarkerPlugin, self).__init__(parentObj)
        self._markers = {}
        self.__defaultPostfix = 0
        self.__clazz = clazz

    def start(self):
        super(RTSOrdersMarkerPlugin, self).start()
        self.__sessionProvider.dynamic.rtsCommander.onSetMarkerEnabled += self.__setMarkerEnabled
        self.__sessionProvider.dynamic.rtsCommander.onRTSStaticMarkerShow += self.__onRTSStaticMarkerShow
        self.__sessionProvider.dynamic.rtsCommander.onRTSStaticMarkerRemove += self.__onRTSStaticMarkerRemove

    def stop(self):
        rtsCommandsCtrl = self.__sessionProvider.dynamic.rtsCommander
        if rtsCommandsCtrl is not None:
            rtsCommandsCtrl.onRTSStaticMarkerRemove -= self.__onRTSStaticMarkerRemove
            rtsCommandsCtrl.onRTSStaticMarkerShow -= self.__onRTSStaticMarkerShow
            rtsCommandsCtrl.onSetMarkerEnabled -= self.__setMarkerEnabled
        for markerKey in self._markers:
            self._destroyMarker(self._markers[markerKey].getMarkerID())

        self._markers.clear()
        super(RTSOrdersMarkerPlugin, self).stop()
        return

    def __setMarkerEnabled(self, vID, enabled):
        for marker in self._markers.itervalues():
            if marker.getVehicleID() == vID:
                self._invokeMarker(marker.getMarkerID(), 'setEnabled', enabled)
                break

    def __addStaticMarker(self, rtsMarkerID, vID, position, orderType, vehicleName=''):
        markerID = self._createMarkerWithPosition(MARKER_SYMBOL_NAME.RTS_ORDER_MARKER, position)
        marker = self.__clazz(markerID, vID, orderType)
        self._setMarkerRenderInfo(markerID, self._STATIC_MARKER_MIN_SCALE, self._STATIC_MARKER_BOUNDS, self._INNER_STATIC_MARKER_BOUNDS, self._STATIC_MARKER_CULL_DISTANCE, self._STATIC_MARKER_BOUNDS_MIN_SCALE)
        self._setMarkerLocationOffset(markerID, self._MIN_Y_OFFSET, self._MAX_Y_OFFSET, self._DISTANCE_FOR_MIN_Y_OFFSET, self._MAX_Y_BOOST, self._BOOST_START)
        self._markers[rtsMarkerID] = marker
        self._invokeMarker(markerID, 'setOrderIDAndVehicleName', orderType.value, vehicleName)
        if self.sessionProvider.getCtx().isPlayerObserver() or not avatar_getter.isVehicleAlive():
            self._setMarkerBoundEnabled(marker.getMarkerID(), False)

    def __onRTSStaticMarkerShow(self, rtsMarkerID, vID, position, orderType, vehicleName=''):
        marker = self._markers.get(rtsMarkerID, None)
        if marker is None:
            self.__addStaticMarker(rtsMarkerID, vID, position, orderType, vehicleName)
        else:
            markerID = marker.getMarkerID()
            self._setMarkerPosition(markerID, position)
            self._invokeMarker(marker.getMarkerID(), 'setOrderIDAndVehicleName', orderType.value, vehicleName)
        return

    def __onRTSStaticMarkerRemove(self, rtsMarkerID):
        marker = self._markers.get(rtsMarkerID)
        if marker is None:
            return
        else:
            markerID = marker.getMarkerID()
            self._markers.pop(rtsMarkerID, None)
            self._destroyMarker(markerID)
            return


class DisabledMarkerPlugin(MarkerPlugin):
    pass
