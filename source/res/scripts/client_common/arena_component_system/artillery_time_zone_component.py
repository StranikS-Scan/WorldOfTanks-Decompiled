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
        self.__timeZones = dict()
        self.onTimeZoneAdded = Event.Event(self._eventManager)
        self.onTimeZoneRemoved = Event.Event(self._eventManager)
        self.onTimeZoneTimerUpdated = Event.Event(self._eventManager)

    def destroy(self):
        ClientArenaComponent.destroy(self)

    def addTimeZone(self, shotId, duration, pos, radius, zoneType):
        startTime = BigWorld.serverTime()
        self.__timeZones[shotId] = (startTime,
         duration,
         pos,
         radius,
         zoneType)
        self.onTimeZoneAdded(shotId, startTime, duration, pos, radius, zoneType)
        self.__startCountdownTimer(shotId)

    def removeTimeZone(self, shotId):
        self.__timeZones.pop(shotId, None)
        self.onTimeZoneRemoved(shotId)
        return

    def __startCountdownTimer(self, shotId):
        _, diffTime, _, _, _ = self.__timeZones[shotId]
        if diffTime >= 0:
            self.onTimeZoneTimerUpdated(shotId, diffTime)
            self.delayCallback(0.1, self.__tick)

    def __tick(self):
        serverTime = BigWorld.serverTime()
        for shotId, values in self.__timeZones.iteritems():
            startTime, duration, _, _, _ = values
            diffTime = duration - (serverTime - startTime)
            if diffTime >= 0:
                self.onTimeZoneTimerUpdated(shotId, diffTime)
            self.onTimeZoneTimerUpdated(shotId, -1)

        return 0.1 if self.__timeZones else None
