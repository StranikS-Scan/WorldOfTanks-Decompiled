# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event_mark1/delivery_direction.py
import BigWorld
from Math import Vector3
from gui.Scaleform.daapi.view.battle.shared import indicators
from gui.shared.utils.TimeInterval import TimeInterval
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control import g_sessionProvider
from CTFManager import g_ctfManager
from constants import FLAG_TYPES
_UPDATE_INTERVAL = 0.1

class DeliveryDirection(IArenaVehiclesController):
    """
    This components shows direction and distance to Mark1 Vehicle,
    when the user captures RepairKit or Bomb.
    """
    __slots__ = ('__indicator', '__updateTimer', '__mark1VehicleID', '__playerVehicleID', '__previousMark1Position')

    def __init__(self):
        self.__indicator = indicators.createDirectIndicator()
        assert self.__indicator is not None, 'MarkI direction indicator can not be created!'
        self.__indicator.setShape('green')
        self.__indicator.setVisibility(False)
        self.__updateTimer = None
        self.__mark1VehicleID = None
        self.__playerVehicleID = g_sessionProvider.getCtx().getArenaDP().getPlayerVehicleID()
        self.__previousMark1Position = Vector3()
        self.__addListeners()
        return

    def clear(self):
        self.__destroyTimer()
        self.__indicator.remove()
        self.__indicator = None
        self.__removeListeners()
        self.__mark1VehicleID = None
        self.__previousMark1Position = None
        return

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(g_sessionProvider.getArenaDP())

    def invalidateVehiclesInfo(self, arenaDP):
        if self.__mark1VehicleID is None:
            for vInfo in arenaDP.getVehiclesInfoIterator():
                vTypeInfoVO = vInfo.vehicleType
                if vTypeInfoVO.isMark1:
                    self.__mark1VehicleID = vInfo.vehicleID
                    break

        return

    def _timerTick(self):
        position, distance = self.__getMark1PositionAndDistance()
        self.__indicator.setDistance(distance)
        self.__indicator.setPosition(position)

    def __createTimer(self):
        self.__destroyTimer()
        self.__updateTimer = TimeInterval(_UPDATE_INTERVAL, self, '_timerTick')
        self.__updateTimer.start()

    def __destroyTimer(self):
        if self.__updateTimer is not None:
            self.__updateTimer.stop()
            self.__updateTimer = None
        return

    def __createDirectionArrow(self):
        position, distance = self.__getMark1PositionAndDistance()
        self.__indicator.setDistance(distance)
        self.__indicator.track(position)
        self.__indicator.setVisibility(True)
        self.__createTimer()

    def __removeDirectionArrow(self):
        self.__indicator.setVisibility(False)
        self.__destroyTimer()

    def __getMark1PositionAndDistance(self):
        vehicle = BigWorld.entities.get(self.__mark1VehicleID)
        if vehicle is not None:
            vPosition = vehicle.position
            self.__previousMark1Position = vPosition
        else:
            positions = g_sessionProvider.arenaVisitor.getArenaPositions()
            if self.__mark1VehicleID in positions:
                vPosition = positions[self.__mark1VehicleID]
                self.__previousMark1Position = vPosition
            else:
                vPosition = self.__previousMark1Position
        return (vPosition, BigWorld.camera().position.distTo(vPosition))

    def __addListeners(self):
        g_sessionProvider.addArenaCtrl(self)
        g_ctfManager.onFlagCapturedByVehicle += self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagAbsorbed += self.__onFlagAbsorbed
        g_ctfManager.onFlagDroppedToGround += self.__onFlagDroppedToGround
        g_ctfManager.onFlagRemoved += self.__onFlagRemoved
        flagID = g_ctfManager.getVehicleCarriedFlagID(self.__playerVehicleID)
        if flagID is not None:
            self.__onFlagCapturedByVehicle(flagID, 0, self.__playerVehicleID)
        return

    def __removeListeners(self):
        g_ctfManager.onFlagCapturedByVehicle -= self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagAbsorbed -= self.__onFlagAbsorbed
        g_ctfManager.onFlagDroppedToGround -= self.__onFlagDroppedToGround
        g_ctfManager.onFlagRemoved -= self.__onFlagRemoved

    def __onFlagCapturedByVehicle(self, flagID, flagTeam, vehicleID):
        if vehicleID == self.__playerVehicleID:
            self.__createDirectionArrow()

    def __onFlagAbsorbed(self, flagID, flagTeam, vehicleID, respawnTime):
        if vehicleID == self.__playerVehicleID:
            flagType = g_ctfManager.getFlagType(flagID)
            if flagType in (FLAG_TYPES.EXPLOSIVE, FLAG_TYPES.REPAIR_KIT):
                self.__removeDirectionArrow()

    def __onFlagDroppedToGround(self, flagID, flagTeam, loserVehicleID, flagPos, respawnTime):
        if loserVehicleID == self.__playerVehicleID:
            self.__removeDirectionArrow()

    def __onFlagRemoved(self, flagID, flagTeam, vehicleID):
        if vehicleID == self.__playerVehicleID:
            self.__removeDirectionArrow()
