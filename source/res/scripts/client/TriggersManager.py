# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TriggersManager.py
import math
import BigWorld
import Math
import PlayerEvents
from constants import ARENA_PERIOD
from debug_utils import LOG_CURRENT_EXCEPTION
from helpers import isPlayerAvatar

class TRIGGER_TYPE(object):
    AIM = 0
    AREA = 1
    AIM_AT_VEHICLE = 3
    AUTO_AIM_AT_VEHICLE = 4
    VEHICLE_DESTROYED = 5
    PLAYER_VEHICLE_ON_SOFT_TERRAIN = 6
    PLAYER_VEHICLE_TRACKS_DAMAGED = 7
    PLAYER_SHOT_MISSED = 8
    PLAYER_SHOT_RICOCHET = 9
    PLAYER_SHOT_NOT_PIERCED = 10
    PLAYER_SHOT_MADE_NONFATAL_DAMAGE = 11
    SNIPER_MODE = 12
    PLAYER_TANKMAN_SHOOTED = 13
    PLAYER_VEHICLE_IN_FIRE = 14
    PLAYER_VEHICLE_OBSERVED = 15
    PLAYER_RECEIVE_DAMAGE = 16
    PLAYER_DISCRETE_SHOOT = 17
    PLAYER_DETECT_ENEMY = 18
    VEHICLE_VISUAL_VISIBILITY_CHANGED = 19
    PLAYER_DEVICE_CRITICAL = 20
    PLAYER_MOVE = 21
    SHOW_TRACER = 22
    PLAYER_SHOT_HIT = 23
    STUN = 24
    SIXTH_SENSE = 25
    PLAYER_ENTER_SPG_STRATEGIC_MODE = 26
    PLAYER_ENTER_SPG_SNIPER_MODE = 27
    PLAYER_LEAVE_SPG_MODE = 28
    CTRL_MODE_CHANGE = 29
    PLAYER_USED_AOE_EQUIPMENT = 30
    PLAYER_CONTINUOUS_BURST_START = 31
    PLAYER_CONTINUOUS_BURST_STOP = 32


class ITriggerListener(object):

    def onTriggerActivated(self, args):
        pass

    def onTriggerDeactivated(self, args):
        pass


class TriggersManager(object):
    UPDATE_PERIOD = 0.05
    isActive = property(lambda self: self.__isEnabled and self.__isOnArena)

    def __init__(self):
        self.__autoTriggers = {}
        self.__activeAutoTriggers = set()
        self.__pendingManualTriggers = {}
        self.__activeManualTriggers = {}
        self.__listeners = set()
        self.__nextTriggerId = 1
        self.__cbID = None
        self.__isOnArena = False
        self.__isEnabled = False
        self.__shotPoints = []
        self.__explodePoints = []
        PlayerEvents.g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        return

    def isEnabled(self):
        return self.__isEnabled

    def destroy(self):
        if self.__cbID is not None:
            BigWorld.cancelCallback(self.__cbID)
            self.__cbID = None
        self.clearTriggers(False)
        self.__listeners = None
        self.__isOnArena = False
        self.__isEnabled = False
        PlayerEvents.g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        return

    def enable(self, enable):
        self.__isEnabled = enable
        if not enable:
            self.clearTriggers(True)
            if self.__cbID is not None:
                BigWorld.cancelCallback(self.__cbID)
                self.__cbID = None
        else:
            self.__cbID = BigWorld.callback(self.UPDATE_PERIOD, self.update)
        return

    def clearTriggers(self, keepTriggersFromMap):
        self.__pendingManualTriggers = {}
        self.__activeManualTriggers = {}
        if not keepTriggersFromMap:
            self.__autoTriggers = {}
            self.__activeAutoTriggers = set()
        else:
            autoTriggers = self.__autoTriggers.copy()
            for k, v in autoTriggers.iteritems():
                tType = v['type']
                if tType != TRIGGER_TYPE.AIM and tType != TRIGGER_TYPE.AREA:
                    del self.__autoTriggers[k]
                    self.__activeAutoTriggers.discard(k)

    def addListener(self, listener):
        if listener in self.__listeners:
            return
        self.__listeners.add(listener)
        if self.isActive:
            for tID in self.__activeAutoTriggers:
                listener.onTriggerActivated(self.__autoTriggers[tID])

            for _, trigger in self.__activeManualTriggers.iteritems():
                listener.onTriggerActivated(trigger)

    def delListener(self, listener):
        self.__listeners.discard(listener)

    def addTrigger(self, tType, **params):
        params = dict(params) if params is not None else {}
        params['type'] = tType
        self.__autoTriggers[self.__nextTriggerId] = params
        self.__nextTriggerId = self.__nextTriggerId + 1
        return self.__nextTriggerId - 1

    def delTrigger(self, triggerID):
        if triggerID in self.__autoTriggers:
            del self.__autoTriggers[triggerID]
            self.__activeAutoTriggers.discard(triggerID)

    def fireTrigger(self, tType, **kwargs):
        params = dict(kwargs) if kwargs is not None else {}
        params['type'] = tType
        if tType not in self.__pendingManualTriggers:
            self.__pendingManualTriggers[tType] = []
        self.__pendingManualTriggers[tType].append((False, params))
        return

    def fireTriggerInstantly(self, tType, **kwargs):
        kwargs['type'] = tType
        for listener in self.__listeners:
            listener.onTriggerActivated(kwargs)

    def activateTrigger(self, triggerType, **kwargs):
        params = dict(kwargs) if kwargs is not None else {}
        params['type'] = triggerType
        if triggerType in self.__activeManualTriggers:
            self.deactivateTrigger(triggerType)
        if triggerType not in self.__pendingManualTriggers:
            self.__pendingManualTriggers[triggerType] = []
        self.__pendingManualTriggers[triggerType].append((True, params))
        return

    def deactivateTrigger(self, triggerType):
        if triggerType in self.__pendingManualTriggers:
            del self.__pendingManualTriggers[triggerType]
        if triggerType in self.__activeManualTriggers:
            if self.isActive:
                params = self.__activeManualTriggers[triggerType]
                for listener in self.__listeners:
                    listener.onTriggerDeactivated(params)

            del self.__activeManualTriggers[triggerType]

    def update(self):
        self.__cbID = BigWorld.callback(self.UPDATE_PERIOD, self.update)
        if not self.isActive:
            return
        else:
            player = BigWorld.player()
            if not isPlayerAvatar():
                return
            camPos = BigWorld.camera().position
            camDir = BigWorld.camera().direction
            vehicle = BigWorld.entities.get(player.playerVehicleID)
            try:
                for tType, data in self.__pendingManualTriggers.iteritems():
                    for isTwoState, args in data:
                        params = dict(args)
                        params['type'] = tType
                        for listener in self.__listeners:
                            listener.onTriggerActivated(params)

                        if isTwoState:
                            self.__activeManualTriggers[tType] = params

                self.__pendingManualTriggers = {}
                for tID, params in self.__autoTriggers.iteritems():
                    wasActive = tID in self.__activeAutoTriggers
                    isActive = False
                    distance = -1.0
                    tType = params['type']
                    if tType == TRIGGER_TYPE.AREA and vehicle is not None:
                        scale = Math.Vector3(params['scale'])
                        if scale == Math.Vector3(1, 1, 1):
                            triggerRadius = params['radius']
                            if wasActive:
                                triggerRadius = triggerRadius + params['exitInterval']
                            offset = vehicle.position - Math.Vector3(params['position'])
                            offset.y = 0
                            distance = offset.length
                            isActive = distance < triggerRadius
                        else:
                            targetMatrix = Math.Matrix()
                            targetMatrix.setRotateY(-params['direction'].z)
                            offset = vehicle.position - Math.Vector3(params['position'])
                            offset.y = 0
                            offset = targetMatrix.applyPoint(offset)
                            originalSize = 5.0
                            isActive = -scale.x * originalSize < offset.x < scale.x * originalSize and -scale.z * originalSize < offset.z < scale.z * originalSize
                    if tType == TRIGGER_TYPE.AIM:
                        camToTrigger = Math.Vector3(params['position']) - camPos
                        vehicleToTrigger = Math.Vector3(params['position']) - vehicle.position
                        distance = camToTrigger.length
                        if distance <= params['maxDistance'] and vehicleToTrigger.dot(camToTrigger) > 0.0:
                            camToTrigger.normalise()
                            dp = camToTrigger.dot(camDir)
                            if dp > 0.0:
                                sinAngle = math.sqrt(1.0 - dp * dp)
                                isActive = sinAngle * distance < params['radius']
                    params['distance'] = distance
                    if wasActive != isActive:
                        if isActive:
                            self.__activeAutoTriggers.add(tID)
                            for listener in self.__listeners:
                                listener.onTriggerActivated(params)

                        else:
                            self.__activeAutoTriggers.discard(tID)
                            for listener in self.__listeners:
                                listener.onTriggerDeactivated(params)

                self.__explodePoints = []
                self.__shotPoints = []
            except Exception:
                LOG_CURRENT_EXCEPTION()

            return

    def getTriggerPosition(self, tType, name):
        for params in self.__autoTriggers.itervalues():
            if params['type'] == tType and params['name'] == name:
                return params.get('position')

        return None

    def getDistanceToTrigger(self, tType, name):
        for params in self.__autoTriggers.itervalues():
            if params['type'] == tType and params['name'] == name:
                return params.get('distance')

        return None

    def isAutoTriggerActive(self, tType, name):
        for tID, params in self.__autoTriggers.iteritems():
            if params['type'] == tType and params['name'] == name:
                return tID in self.__activeAutoTriggers

        return None

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        isOnArena = period == ARENA_PERIOD.BATTLE
        if not isOnArena and self.__isOnArena:
            self.clearTriggers(False)
        self.__isOnArena = isOnArena


g_manager = None

def init():
    global g_manager
    g_manager = TriggersManager()
