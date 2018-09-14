# Embedded file name: scripts/client/gui/battle_control/battle_feedback.py
from collections import defaultdict
import weakref
import BigWorld
import Event
from constants import VEHICLE_HIT_FLAGS as _VHF, BATTLE_EVENT_TYPE as _SET, ATTACK_REASONS as _AR, IS_DEVELOPMENT
from debug_utils import LOG_CODEPOINT_WARNING, LOG_DEBUG
from shared_utils import findFirst
from gui import GUI_SETTINGS
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID
_VHF_NAMES = dict([ (k, v) for k, v in _VHF.__dict__.iteritems() if not k.startswith('_') ])
_VHF_NAMES.pop('IS_ANY_DAMAGE_MASK', None)
_VHF_NAMES.pop('IS_ANY_PIERCING_MASK', None)
_CELL_BLINKING_DURATION = 3.0
_RAMMING_COOLDOWN = 1.0

class BattleFeedbackAdaptor(object):
    __slots__ = ('onPlayerFeedbackReceived', 'onAimPositionUpdated', 'onVehicleMarkerAdded', 'onVehicleMarkerRemoved', 'onVehicleFeedbackReceived', 'onMinimapVehicleAdded', 'onMinimapVehicleRemoved', 'onMinimapFeedbackReceived', '__isPEEnabled', '__arenaDP', '__series', '__rammingCallbackID', '__queue', '__callbackID', '__aimProps', '__visible', '__pending', '__weakref__')

    def __init__(self):
        super(BattleFeedbackAdaptor, self).__init__()
        self.__isPEEnabled = False
        self.__arenaDP = None
        self.__queue = []
        self.__series = defaultdict(lambda : 0)
        self.__visible = set()
        self.__pending = {}
        self.__callbackID = None
        self.__rammingCallbackID = None
        self.__aimProps = None
        self.onPlayerFeedbackReceived = Event.Event()
        self.onVehicleMarkerAdded = Event.Event()
        self.onVehicleMarkerRemoved = Event.Event()
        self.onVehicleFeedbackReceived = Event.Event()
        self.onMinimapVehicleAdded = Event.Event()
        self.onMinimapVehicleRemoved = Event.Event()
        self.onMinimapFeedbackReceived = Event.Event()
        self.onAimPositionUpdated = Event.Event()
        return

    def start(self, arenaDP):
        self.__arenaDP = weakref.proxy(arenaDP)

    def stop(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        if self.__rammingCallbackID is not None:
            BigWorld.cancelCallback(self.__rammingCallbackID)
            self.__rammingCallbackID = None
        self.__visible.clear()
        while self.__pending:
            _, callbackID = self.__pending.popitem()
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        self.__isPEEnabled = False
        self.__arenaDP = None
        self.__aimProps = None
        return

    def setPlayerVehicle(self, vID):
        if vID:
            self.__isPEEnabled = not self.__arenaDP.isObserver(vID)
        else:
            self.__isPEEnabled = False

    def setAimPositionUpdated(self, mode, x, y):
        self.__aimProps = (mode, x, y)
        self.onAimPositionUpdated(mode, x, y)

    def getAimProps(self):
        return self.__aimProps

    def setPlayerShotResults(self, vehHitFlags, _):
        if not self.__isPEEnabled:
            return
        if IS_DEVELOPMENT:
            result = []
            for name, bit in _VHF_NAMES.iteritems():
                if vehHitFlags & bit > 0:
                    result.append(name)

            LOG_DEBUG('Player is received shot result', ','.join(result))
        if _VHF.MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_PROJECTILE & vehHitFlags > 0 or _VHF.MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_EXPLOSION & vehHitFlags > 0:
            self.__pushPlayerEvent(_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY)
        if _VHF.DEVICE_DAMAGED_BY_PROJECTILE & vehHitFlags > 0 or _VHF.DEVICE_DAMAGED_BY_EXPLOSION & vehHitFlags > 0:
            self.__pushPlayerEvent(_EVENT_ID.PLAYER_DAMAGED_DEVICE_ENEMY)

    def setPlayerAssistResult(self, assistType, details):
        if not self.__isPEEnabled:
            return
        else:
            eventID = None
            series = 1
            if assistType == _SET.SPOTTED:
                eventID = _EVENT_ID.PLAYER_SPOTTED_ENEMY
                series = self.__getSeries(details)
            elif assistType in (_SET.RADIO_HIT_ASSIST, _SET.RADIO_KILL_ASSIST, _SET.TRACK_ASSIST):
                if assistType == _SET.TRACK_ASSIST:
                    series = self.__getSeries(details)
                eventID = _EVENT_ID.PLAYER_ASSIST_TO_KILL_ENEMY
            elif assistType == _SET.BASE_CAPTURE_POINTS:
                eventID = _EVENT_ID.PLAYER_CAPTURED_BASE
            elif assistType == _SET.BASE_CAPTURE_DROPPED:
                eventID = _EVENT_ID.PLAYER_DROPPED_CAPTURE
            elif assistType == _SET.TANKING:
                eventID = _EVENT_ID.PLAYER_USED_ARMOR
                series = findFirst(None, details, default=1)
            else:
                LOG_CODEPOINT_WARNING(assistType)
            if eventID:
                self.__pushPlayerEvent(eventID, series)
            return

    def setPlayerKillResult(self, targetID):
        if not self.__isPEEnabled:
            return
        vo = self.__arenaDP.getVehicleInfo(targetID)
        if self.__arenaDP.isEnemyTeam(vo.team):
            self.__pushPlayerEvent(_EVENT_ID.PLAYER_KILLED_ENEMY)

    def startVehicleVisual(self, vProxy, isImmediate = False):
        vehicleID = vProxy.id
        vInfo = self.__arenaDP.getVehicleInfo(vehicleID)
        if vInfo.isObserver():
            return
        guiProps = self.__arenaDP.getPlayerGuiProps(vehicleID, vInfo.team)
        self.__visible.add(vehicleID)
        if not vProxy.isPlayer:

            def __addVehicleToUI():
                self.__pending[vehicleID] = None
                self.onVehicleMarkerAdded(vProxy, vInfo, guiProps)
                self.onMinimapVehicleAdded(vProxy, vInfo, guiProps)
                if not isImmediate and not vProxy.isAlive():
                    self.setVehicleState(vProxy.id, _EVENT_ID.VEHICLE_DEAD, True)
                return

            if isImmediate:
                __addVehicleToUI()
            else:
                self.__pending[vehicleID] = BigWorld.callback(0.0, __addVehicleToUI)

    def stopVehicleVisual(self, vehicleID, isPlayer):
        callbackID = self.__pending.pop(vehicleID, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        self.__visible.discard(vehicleID)
        if not isPlayer:
            self.onVehicleMarkerRemoved(vehicleID)
        self.onMinimapVehicleRemoved(vehicleID)
        return

    def setVehicleState(self, vehicleID, eventID, isImmediate = False):
        if vehicleID != avatar_getter.getPlayerVehicleID():
            self.onVehicleFeedbackReceived(eventID, vehicleID, isImmediate)

    def showActionMarker(self, vehicleID, vMarker = '', mMarker = ''):
        if vMarker and vehicleID != avatar_getter.getPlayerVehicleID():
            self.onVehicleFeedbackReceived(_EVENT_ID.VEHICLE_SHOW_MARKER, vehicleID, vMarker)
        if mMarker:
            self.onMinimapFeedbackReceived(_EVENT_ID.MINIMAP_SHOW_MARKER, vehicleID, mMarker)

    def setVehicleNewHealth(self, vehicleID, newHealth, attackerID = 0, attackReasonID = 0):
        self._setVehicleHealthChanged(vehicleID, newHealth, attackerID, attackReasonID)
        self._findPlayerFeedbackByAttack(vehicleID, newHealth, attackerID, attackReasonID)

    def markCellOnMinimap(self, cell):
        self.onMinimapFeedbackReceived(_EVENT_ID.MINIMAP_MARK_CELL, 0, (cell, _CELL_BLINKING_DURATION))

    def _setVehicleHealthChanged(self, vehicleID, newHealth, attackerID, attackReasonID):
        if attackerID:
            aInfo = self.__arenaDP.getVehicleInfo(attackerID)
        else:
            aInfo = None
        self.onVehicleFeedbackReceived(_EVENT_ID.VEHICLE_HEALTH, vehicleID, (newHealth, aInfo, attackReasonID))
        return

    def _findPlayerFeedbackByAttack(self, vehicleID, newHealth, attackerID, attackReasonID):
        if not self.__isPEEnabled or not newHealth or not attackerID or attackerID != avatar_getter.getPlayerVehicleID():
            return
        else:
            vo = self.__arenaDP.getVehicleInfo(vehicleID)
            if self.__arenaDP.isAllyTeam(vo.team):
                return
            if attackReasonID >= len(_AR):
                return
            LOG_DEBUG("Enemy's vehicle health has been changed by player action", newHealth, _AR[attackReasonID])
            if _AR[attackReasonID] == 'ramming':
                if self.__rammingCallbackID is None:
                    self.__setRammingCooldown()
                    self.__pushPlayerEvent(_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY)
                else:
                    BigWorld.cancelCallback(self.__rammingCallbackID)
                    self.__setRammingCooldown()
            return

    def __setRammingCooldown(self):
        self.__rammingCallbackID = BigWorld.callback(_RAMMING_COOLDOWN, self.__clearRammingCooldown)

    def __clearRammingCooldown(self):
        self.__rammingCallbackID = None
        return

    def __pushPlayerEvent(self, eventID, series = 1):
        if eventID not in self.__queue:
            self.__queue.append(eventID)
        self.__series[eventID] += series
        if self.__callbackID is None:
            self.__callbackID = BigWorld.callback(GUI_SETTINGS.playerFeedbackDelay, self.__delayPlayerEvents)
        return

    def __delayPlayerEvents(self):
        self.__callbackID = None
        self.__firePlayerEvents()
        return

    def __getSeries(self, vehiclesIDs):
        if hasattr(vehiclesIDs, '__len__'):
            return len(vehiclesIDs)
        return 1

    def __firePlayerEvents(self):
        LOG_DEBUG('Fires events to show ribbons', self.__queue, self.__series)
        for eventID in self.__queue:
            self.onPlayerFeedbackReceived(eventID, self.__series[eventID])

        self.__queue = []
        self.__series.clear()


class BattleFeedbackPlayer(BattleFeedbackAdaptor):

    def setAimPositionUpdated(self, mode, x, y):
        pass

    def setPlayerShotResults(self, vehHitFlags, enemyID):
        pass

    def setPlayerAssistResult(self, assistType, vehicleID):
        pass

    def setPlayerKillResult(self, targetID):
        pass

    def setVehicleNewHealth(self, vehicleID, newHealth, attackerID = 0, attackReasonID = 0):
        self._setVehicleHealthChanged(vehicleID, newHealth, attackerID=attackerID, attackReasonID=attackReasonID)


def createFeedbackAdaptor(isReplayPlaying):
    if isReplayPlaying:
        adaptor = BattleFeedbackPlayer()
    else:
        adaptor = BattleFeedbackAdaptor()
    return adaptor
