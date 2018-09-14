# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/feedback_adaptor.py
import weakref
from collections import defaultdict
import BigWorld
import Event
from constants import VEHICLE_HIT_FLAGS as _VHF, BATTLE_EVENT_TYPE as _SET, ATTACK_REASONS as _AR, IS_DEVELOPMENT
from debug_utils import LOG_CODEPOINT_WARNING, LOG_DEBUG, LOG_CURRENT_EXCEPTION
from gui import GUI_SETTINGS
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID, BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from shared_utils import findFirst
_VHF_NAMES = dict([ (k, v) for k, v in _VHF.__dict__.iteritems() if not k.startswith('_') ])
_VHF_NAMES.pop('IS_ANY_DAMAGE_MASK', None)
_VHF_NAMES.pop('IS_ANY_PIERCING_MASK', None)
_CELL_BLINKING_DURATION = 3.0
_RAMMING_COOLDOWN = 1.0

class _DamagedDevicesExtraFetcher(object):
    __slots__ = ('__total', '__critical', '__destroyed', '__isInFire')

    def __init__(self, total, critical, destroyed):
        super(_DamagedDevicesExtraFetcher, self).__init__()
        self.__total = map(self.__convertExtra, total)
        self.__critical = critical
        self.__destroyed = destroyed
        self.__isInFire = False

    def getDamagedDevices(self):
        for idx in self.__critical:
            name = self.__total[idx]
            if name == 'fire':
                self.__isInFire = True
                continue
            yield (name, 'damaged')

        for idx in self.__destroyed:
            yield (self.__total[idx], 'destroyed')

    def isInFire(self):
        return self.__isInFire

    @staticmethod
    def __convertExtra(extra):
        return extra.name


class BattleFeedbackAdaptor(IBattleController):
    __slots__ = ('onPlayerFeedbackReceived', 'onVehicleMarkerAdded', 'onVehicleMarkerRemoved', 'onVehicleFeedbackReceived', 'onMinimapVehicleAdded', 'onMinimapVehicleRemoved', 'onMinimapFeedbackReceived', '__isPEEnabled', '__arenaDP', '__series', '__rammingCallbackID', '__queue', '__callbackID', '__visible', '__pending', '__attrs', '__weakref__', '__arenaVisitor')

    def __init__(self, setup):
        super(BattleFeedbackAdaptor, self).__init__()
        self.__isPEEnabled = False
        self.__arenaDP = weakref.proxy(setup.arenaDP)
        self.__arenaVisitor = weakref.proxy(setup.arenaVisitor)
        self.__queue = []
        self.__series = defaultdict(lambda : 0)
        self.__visible = set()
        self.__pending = {}
        self.__callbackID = None
        self.__rammingCallbackID = None
        self.__attrs = {}
        self.onPlayerFeedbackReceived = Event.Event()
        self.onVehicleMarkerAdded = Event.Event()
        self.onVehicleMarkerRemoved = Event.Event()
        self.onVehicleFeedbackReceived = Event.Event()
        self.onMinimapVehicleAdded = Event.Event()
        self.onMinimapVehicleRemoved = Event.Event()
        self.onMinimapFeedbackReceived = Event.Event()
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.FEEDBACK

    def startControl(self):
        pass

    def stopControl(self):
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
        self.__arenaVisitor = None
        self.__attrs = {}
        return

    def setPlayerVehicle(self, vID):
        if vID:
            self.__isPEEnabled = not self.__arenaDP.isObserver(vID)
        else:
            self.__isPEEnabled = False

    def getVisibleVehicles(self):
        getInfo = self.__arenaDP.getVehicleInfo
        getProps = self.__arenaDP.getPlayerGuiProps
        for vehicleID in self.__visible:
            vehicle = BigWorld.entity(vehicleID)
            if vehicle is None:
                continue
            info = getInfo(vehicleID)
            props = getProps(vehicleID, info.team)
            try:
                if not vehicle.isPlayerVehicle:
                    yield (vehicle.proxy, info, props)
            except AttributeError:
                LOG_CURRENT_EXCEPTION()

        return

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

    def startVehicleVisual(self, vProxy, isImmediate=False):
        vehicleID = vProxy.id
        vInfo = self.__arenaDP.getVehicleInfo(vehicleID)
        if vInfo.isObserver():
            return
        guiProps = self.__arenaDP.getPlayerGuiProps(vehicleID, vInfo.team)
        self.__visible.add(vehicleID)
        if not vProxy.isPlayerVehicle:

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

    def stopVehicleVisual(self, vehicleID, isPlayerVehicle):
        callbackID = self.__pending.pop(vehicleID, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        self.__visible.discard(vehicleID)
        if not isPlayerVehicle:
            self.onVehicleMarkerRemoved(vehicleID)
        self.onMinimapVehicleRemoved(vehicleID)
        return

    def setVehicleState(self, vehicleID, eventID, isImmediate=False):
        if vehicleID != avatar_getter.getPlayerVehicleID():
            self.onVehicleFeedbackReceived(eventID, vehicleID, isImmediate)

    def showActionMarker(self, vehicleID, vMarker='', mMarker=''):
        if vMarker and vehicleID != avatar_getter.getPlayerVehicleID():
            self.onVehicleFeedbackReceived(_EVENT_ID.VEHICLE_SHOW_MARKER, vehicleID, vMarker)
        if mMarker:
            self.onMinimapFeedbackReceived(_EVENT_ID.MINIMAP_SHOW_MARKER, vehicleID, mMarker)

    def setVehicleNewHealth(self, vehicleID, newHealth, attackerID=0, attackReasonID=0):
        self._setVehicleHealthChanged(vehicleID, newHealth, attackerID, attackReasonID)
        self._findPlayerFeedbackByAttack(vehicleID, newHealth, attackerID, attackReasonID)

    def markCellOnMinimap(self, cell):
        self.onMinimapFeedbackReceived(_EVENT_ID.MINIMAP_MARK_CELL, 0, (cell, _CELL_BLINKING_DURATION))

    def showVehicleDamagedDevices(self, vehicleID, criticalExtras, destroyedExtras):
        totalExtras = self.__arenaVisitor.vehicles.getVehicleExtras(vehicleID)
        if totalExtras is not None:
            fetcher = _DamagedDevicesExtraFetcher(totalExtras, criticalExtras, destroyedExtras)
            self.onVehicleFeedbackReceived(_EVENT_ID.SHOW_VEHICLE_DAMAGES_DEVICES, vehicleID, fetcher)
        return

    def hideVehicleDamagedDevices(self, vehicleID=0):
        self.onVehicleFeedbackReceived(_EVENT_ID.HIDE_VEHICLE_DAMAGES_DEVICES, vehicleID, None)
        return

    def setVehicleAttrs(self, vehicleID, attrs):
        self.__attrs = attrs
        self.onVehicleFeedbackReceived(_EVENT_ID.VEHICLE_ATTRS_CHANGED, vehicleID, dict(self.__attrs))

    def getVehicleAttrs(self):
        return dict(self.__attrs)

    def setTargetInFocus(self, vehicleID, isInFocus):
        self.onVehicleFeedbackReceived(_EVENT_ID.VEHICLE_IN_FOCUS, vehicleID, isInFocus)

    def setVehicleHasAmmo(self, vehicleID, hasAmmo):
        self.onVehicleFeedbackReceived(_EVENT_ID.VEHICLE_HAS_AMMO, vehicleID, hasAmmo)

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

    def __pushPlayerEvent(self, eventID, series=1):
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

    @staticmethod
    def __getSeries(vehiclesIDs):
        if hasattr(vehiclesIDs, '__len__'):
            return len(vehiclesIDs)
        else:
            return 1

    def __firePlayerEvents(self):
        LOG_DEBUG('Fires events to show ribbons', self.__queue, self.__series)
        for eventID in self.__queue:
            self.onPlayerFeedbackReceived(eventID, self.__series[eventID])

        self.__queue = []
        self.__series.clear()


class BattleFeedbackPlayer(BattleFeedbackAdaptor):

    def setPlayerShotResults(self, vehHitFlags, enemyID):
        pass

    def setPlayerAssistResult(self, assistType, vehicleID):
        pass

    def setPlayerKillResult(self, targetID):
        pass

    def setVehicleNewHealth(self, vehicleID, newHealth, attackerID=0, attackReasonID=0):
        self._setVehicleHealthChanged(vehicleID, newHealth, attackerID=attackerID, attackReasonID=attackReasonID)


def createFeedbackAdaptor(setup):
    if setup.isReplayPlaying:
        adaptor = BattleFeedbackPlayer(setup)
    else:
        adaptor = BattleFeedbackAdaptor(setup)
    return adaptor
