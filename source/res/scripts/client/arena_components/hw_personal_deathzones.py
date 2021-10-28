# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/arena_components/hw_personal_deathzones.py
import BigWorld
from arena_component_system.client_arena_component_system import ClientArenaComponent
from shared_utils import first

class PersonalDeathZonesComponent(ClientArenaComponent):

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self.__zoneEntities = {}
        self.__currentZone = None
        self.__callbackId = None
        return

    def addZone(self, zone):
        self.__zoneEntities[zone.id] = zone
        self.__updateTimer()

    def removeZone(self, zone):
        if zone.id in self.__zoneEntities:
            del self.__zoneEntities[zone.id]
            self.__updateTimer()

    def deactivate(self):
        self.__clearCallback()
        self.__zoneEntities.clear()
        self.__currentZone = None
        super(PersonalDeathZonesComponent, self).deactivate()
        return

    def __hideTimer(self):
        self.__callbackId = None
        if self.__currentZone is not None:
            del self.__zoneEntities[self.__currentZone.id]
            self.__updateTimer()
        return

    def __clearCallback(self):
        if self.__callbackId is not None:
            BigWorld.cancelCallback(self.__callbackId)
            self.__callbackId = None
        return

    def __updateTimer(self):
        actualZone = first(sorted(self.__zoneEntities.itervalues(), key=lambda item: item.strikeTime))
        if actualZone is None:
            self.__currentZone = None
            self.__clearCallback()
            BigWorld.player().updatePersonalDeathZoneWarningNotification(False, 0, 0)
        elif actualZone != self.__currentZone:
            self.__currentZone = actualZone
            totalTime = actualZone.strikeTime - actualZone.launchTime
            BigWorld.player().updatePersonalDeathZoneWarningNotification(True, totalTime, actualZone.strikeTime)
            self.__clearCallback()
            self.__callbackId = BigWorld.callback(actualZone.strikeTime - BigWorld.serverTime(), self.__hideTimer)
        return
