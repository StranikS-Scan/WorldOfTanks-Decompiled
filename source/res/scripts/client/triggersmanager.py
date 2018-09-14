# Embedded file name: scripts/client/TriggersManager.py
import BigWorld
import Math, math
import PlayerEvents
from debug_utils import *
from constants import ARENA_PERIOD
from helpers import isPlayerAvatar

class TRIGGER_TYPE():
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


class ITriggerListener():

    def onTriggerActivated(self, args):
        pass

    def onTriggerDeactivated(self, args):
        pass


class TriggersManager():
    UPDATE_PERIOD = 0.1
    isActive = property(lambda self: self.__isEnabled and self.__isOnArena)

    def __init__(self):
        self.__autoTriggers = {}
        self.__activeAutoTriggers = set()
        self.__pendingManualTriggers = {}
        self.__activeManualTriggers = {}
        self.__listeners = set()
        self.__nextTriggerId = 1
        self.__cbID = BigWorld.callback(self.UPDATE_PERIOD, self.update)
        self.__isOnArena = False
        self.__isEnabled = False
        self.__shotPoints = []
        self.__explodePoints = []
        PlayerEvents.g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange

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

    def clearTriggers(self, keepTriggersFromMap):
        self.__pendingManualTriggers = {}
        self.__activeManualTriggers = {}
        if not keepTriggersFromMap:
            self.__autoTriggers = {}
            self.__activeAutoTriggers = set()
        else:
            for k, v in self.__autoTriggers.iteritems():
                type = v['type']
                if type != TRIGGER_TYPE.AIM and type != TRIGGER_TYPE.AREA:
                    del self.__autoTriggers[k]
                    self.__activeAutoTriggers.discard(k)

    def addListener(self, listener):
        if listener in self.__listeners:
            return
        self.__listeners.add(listener)
        if self.isActive:
            for id in self.__activeAutoTriggers:
                listener.onTriggerActivated(self.__autoTriggers[id])

            for type, trigger in self.__activeManualTriggers.iteritems():
                listener.onTriggerActivated(trigger)

    def delListener(self, listener):
        self.__listeners.discard(listener)

    def addTrigger(self, type, **params):
        params = dict(params) if params is not None else {}
        params['type'] = type
        self.__autoTriggers[self.__nextTriggerId] = params
        self.__nextTriggerId = self.__nextTriggerId + 1
        return self.__nextTriggerId - 1

    def delTrigger(self, id):
        if self.__autoTriggers.has_key(id):
            del self.__autoTriggers[id]
            self.__activeAutoTriggers.discard(id)

    def fireTrigger(self, type, **args):
        params = dict(args) if args is not None else {}
        params['type'] = type
        self.__pendingManualTriggers[type] = (False, params)
        return

    def activateTrigger(self, type, **args):
        if self.__activeManualTriggers.has_key(type):
            self.deactivateTrigger(type)
        params = dict(args) if args is not None else {}
        params['type'] = type
        self.__pendingManualTriggers[type] = (True, params)
        return

    def deactivateTrigger(self, type):
        if self.__pendingManualTriggers.has_key(type):
            del self.__pendingManualTriggers[type]
        if self.__activeManualTriggers.has_key(type):
            if self.isActive:
                params = self.__activeManualTriggers[type]
                for listener in self.__listeners:
                    listener.onTriggerDeactivated(params)

            del self.__activeManualTriggers[type]

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
                for type, (isTwoState, args) in self.__pendingManualTriggers.iteritems():
                    params = dict(args)
                    params['type'] = type
                    for listener in self.__listeners:
                        listener.onTriggerActivated(params)

                    if isTwoState:
                        self.__activeManualTriggers[type] = params

                self.__pendingManualTriggers = {}
                for id, params in self.__autoTriggers.iteritems():
                    wasActive = id in self.__activeAutoTriggers
                    isActive = False
                    distance = -1.0
                    type = params['type']
                    if type == TRIGGER_TYPE.AREA and vehicle is not None:
                        triggerRadius = params['radius']
                        if wasActive:
                            triggerRadius = triggerRadius + params['exitInterval']
                        offset = vehicle.position - Math.Vector3(params['position'])
                        offset.y = 0
                        distance = offset.length
                        isActive = distance < triggerRadius
                    if type == TRIGGER_TYPE.AIM:
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
                            self.__activeAutoTriggers.add(id)
                            for listener in self.__listeners:
                                listener.onTriggerActivated(params)

                        else:
                            self.__activeAutoTriggers.discard(id)
                            for listener in self.__listeners:
                                listener.onTriggerDeactivated(params)

                self.__explodePoints = []
                self.__shotPoints = []
            except:
                LOG_CURRENT_EXCEPTION()

            return

    def getTriggerPosition(self, type, name):
        for params in self.__autoTriggers.itervalues():
            if params['type'] == type and params['name'] == name:
                return params.get('position')

        return None

    def getDistanceToTrigger(self, type, name):
        for params in self.__autoTriggers.itervalues():
            if params['type'] == type and params['name'] == name:
                return params.get('distance')

        return None

    def isAutoTriggerActive(self, type, name):
        for id, params in self.__autoTriggers.iteritems():
            if params['type'] == type and params['name'] == name:
                return id in self.__activeAutoTriggers

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
