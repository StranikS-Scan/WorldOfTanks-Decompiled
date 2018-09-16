# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/protection_zone_component.py
from client_arena_component_system import ClientArenaComponent
import Event

class ProtectionZoneComponent(ClientArenaComponent):
    protectionZones = property(lambda self: self.__protectionZones)

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self.__protectionZones = {}
        self.__isPlayerInZone = {}
        self.onProtectionZoneAdded = Event.Event(self._eventManager)
        self.onProtectionZoneActive = Event.Event(self._eventManager)
        self.onPlayerInProtectedZoneAction = Event.Event(self._eventManager)

    def addProtectionZone(self, protZone):
        self.__protectionZones[protZone.zoneID] = protZone
        self.__isPlayerInZone[protZone.zoneID] = False
        self.onProtectionZoneAdded(protZone.zoneID, protZone.position, protZone.bound)

    def setProtectionZoneActive(self, zoneID, isActive):
        self.onProtectionZoneActive(zoneID, isActive)

    def removeProtectionZone(self, protZone):
        if protZone in self.__protectionZones:
            del self.__protectionZones[protZone.zoneID]
        self.__isPlayerInZone[protZone.zoneID] = False

    def getProtectionZoneById(self, zoneID):
        return self.__protectionZones[zoneID] if zoneID in self.__protectionZones else None

    def getOwningTeamForZone(self, zoneID):
        zone = self.getProtectionZoneById(zoneID)
        return zone.team if zone is not None else None

    def isProtectionZoneActive(self, zoneID):
        zone = self.getProtectionZoneById(zoneID)
        return zone.isActive if zone is not None else False

    def playerInProtectedZone(self, zoneID, hasPlayerEntered):
        self.__isPlayerInZone[zoneID] = hasPlayerEntered
        self.onPlayerInProtectedZoneAction(zoneID, hasPlayerEntered)

    def isPlayerInProtectedZone(self, zoneID=None):
        if zoneID is None:
            return any(self.__isPlayerInZone.values())
        else:
            return self.__isPlayerInZone[zoneID] if zoneID in self.__isPlayerInZone else False
