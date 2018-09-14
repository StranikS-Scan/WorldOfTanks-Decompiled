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
_RAMMING_COOLDOWN = 1

class BattleFeedbackAdaptor(object):
    __slots__ = ('onPlayerFeedbackReceived', 'onVehicleFeedbackReceived', 'onMinimapFeedbackReceived', 'onAimPositionUpdated', '__isEnabled', '__arenaDP', '__series', '__rammingCallbackID', '__queue', '__callbackID', '__aimProps', '__weakref__')

    def __init__(self):
        super(BattleFeedbackAdaptor, self).__init__()
        self.__isEnabled = False
        self.__arenaDP = None
        self.__queue = set()
        self.__series = defaultdict(lambda : 0)
        self.__callbackID = None
        self.__rammingCallbackID = None
        self.__aimProps = None
        self.onPlayerFeedbackReceived = Event.Event()
        self.onVehicleFeedbackReceived = Event.Event()
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
        self.__isEnabled = False
        self.__arenaDP = None
        self.__aimProps = None
        return

    def setPlayerVehicle(self, vID):
        if vID:
            self.__isEnabled = not self.__arenaDP.isObserver(vID)
        else:
            self.__isEnabled = False

    def setAimPositionUpdated(self, mode, x, y):
        self.__aimProps = (mode, x, y)
        self.onAimPositionUpdated(mode, x, y)

    def getAimProps(self):
        return self.__aimProps

    def setPlayerShotResults(self, vehHitFlags, _):
        if not self.__isEnabled:
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
        if not self.__isEnabled:
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
        if not self.__isEnabled:
            return
        vo = self.__arenaDP.getVehicleInfo(targetID)
        if self.__arenaDP.isEnemyTeam(vo.team):
            self.__pushPlayerEvent(_EVENT_ID.PLAYER_KILLED_ENEMY)

    def showActionMarker(self, vehicleID, vMarker = '', mMarker = ''):
        if vMarker and vehicleID != avatar_getter.getPlayerVehicleID():
            self.onVehicleFeedbackReceived(_EVENT_ID.VEHICLE_SHOW_MARKER, vehicleID, vMarker)
        if mMarker:
            self.onMinimapFeedbackReceived(_EVENT_ID.MINIMAP_SHOW_MARKER, vehicleID, mMarker)

    def setVehicleNewHealth(self, vehicleID, newHealth, attackerID = 0, attackReasonID = -1):
        if not self.__isEnabled:
            return
        elif not newHealth:
            return
        elif not attackerID or attackerID != avatar_getter.getPlayerVehicleID():
            return
        else:
            vo = self.__arenaDP.getVehicleInfo(vehicleID)
            if self.__arenaDP.isAllyTeam(vo.team):
                return
            elif attackReasonID >= len(_AR):
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

    def markCellOnMinimap(self, cell):
        self.onMinimapFeedbackReceived(_EVENT_ID.MINIMAP_MARK_CELL, 0, (cell, _CELL_BLINKING_DURATION))

    def __setRammingCooldown(self):
        self.__rammingCallbackID = BigWorld.callback(_RAMMING_COOLDOWN, self.__clearRammingCooldown)

    def __clearRammingCooldown(self):
        self.__rammingCallbackID = None
        return

    def __pushPlayerEvent(self, eventID, series = 1):
        self.__queue.add(eventID)
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

        self.__queue.clear()
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

    def setVehicleNewHealth(self, vehicleID, newHealth, attackerID = 0, attackReasonID = -1):
        pass


def createFeedbackAdaptor(isReplayPlaying):
    if isReplayPlaying:
        adaptor = BattleFeedbackPlayer()
    else:
        adaptor = BattleFeedbackAdaptor()
    return adaptor
