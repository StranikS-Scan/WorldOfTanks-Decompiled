# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/artillery_time_zone_component.py
import BigWorld
from client_arena_component_system import ClientArenaComponent
import Event
from helpers.CallbackDelayer import CallbackDelayer

class ArtilleryTimeZoneComponent(ClientArenaComponent, CallbackDelayer):

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        CallbackDelayer.__init__(self)
        self.__timeZones = {}
        self.__zoneTimers = {}
        self.onTimeZoneAdded = Event.Event(self._eventManager)
        self.onTimeZoneRemoved = Event.Event(self._eventManager)
        self.onTimeZoneTimerUpdated = Event.Event(self._eventManager)

    def destroy(self):
        ClientArenaComponent.destroy(self)
        for shotId in self.__zoneTimers:
            self.__timeZones.pop(shotId, None)
            self.onTimeZoneRemoved(shotId)

        self.__zoneTimers.clear()
        return

    def addTimeZone(self, shotId, startTime, duration, pos, radius, zoneType):
        diffTime = duration - (BigWorld.serverTime() - startTime)
        if diffTime <= 0:
            return
        self.__timeZones[shotId] = (startTime,
         duration,
         pos,
         radius,
         zoneType)
        self.__zoneTimers[shotId] = duration
        self.onTimeZoneAdded(shotId, startTime, duration, pos, radius, zoneType)
        self.__startCountdownTimer(shotId)

    def removeTimeZone(self, shotId):
        self.__zoneTimers.pop(shotId, None)
        self.__timeZones.pop(shotId, None)
        self.onTimeZoneRemoved(shotId)
        return

    def __startCountdownTimer(self, shotId):
        diffTime = self.__zoneTimers[shotId]
        if diffTime >= 0:
            self.onTimeZoneTimerUpdated(shotId, diffTime)
            self.delayCallback(0.1, self.__tick)

    def __tick(self):
        serverTime = BigWorld.serverTime()
        for shotId, duration in self.__zoneTimers.iteritems():
            startTime, duration, _, _, _ = self.__timeZones[shotId]
            diffTime = duration - (serverTime - startTime)
            if diffTime >= 0:
                self.onTimeZoneTimerUpdated(shotId, diffTime)
            self.onTimeZoneTimerUpdated(shotId, -1)

        return 0 if self.__zoneTimers else None
