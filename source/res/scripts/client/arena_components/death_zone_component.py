# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/arena_components/death_zone_component.py
import logging
import BigWorld
import Math
import Event
import death_zones_mapping
from arena_component_system.client_arena_component_system import ClientArenaComponent
from constants import ARENA_SYNC_OBJECTS, DEATH_ZONES
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
_INVISIBLE_RIGHT = 1
_INVISIBLE_LEFT = 2
_INVISIBLE_UP = 4
_INVISIBLE_DOWN = 8
_UPDATE_INTERVAL = 0.1
_SYNC_DATA_CB_KEY = 'activeZones'

class BRZoneData(object):
    ZONE_STATE = 0
    ZONE_ID = 1
    ZONE_BORDER_MASK = 2


class BRDeathZoneComponent(ClientArenaComponent):
    ZONE_FREE = 0
    ZONE_WAITING = 1
    ZONE_ACTIVE = 2
    __slots__ = ('__cornerPosition', '__zoneSizeX', '__zoneSizeY', '__zonePositionOffset', '__zoneScale__visualizersId', 'onDeathZoneUpdate', '__updatedZones__zoneStates', '__callbackID', '__currentZoneState', '__observedvehicleID')

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self.__inited = False
        self.__visualizersId = []
        self.__cornerPosition = None
        self.__zoneSizeX = None
        self.__zoneSizeY = None
        self.__zonePositionOffset = None
        self.__zoneScale = None
        self.__callbackID = None
        self.__currentZoneState = None
        self.__observedvehicleID = None
        self.__updatedZones = []
        self.__zoneStates = [ [ (BRDeathZoneComponent.ZONE_FREE, 0, 0) for _ in range(death_zones_mapping.ZONES_X) ] for _ in range(death_zones_mapping.ZONES_Y) ]
        self.onDeathZoneUpdate = Event.Event(self._eventManager)
        return

    def activate(self):
        super(BRDeathZoneComponent, self).activate()
        self.addSyncDataCallback(ARENA_SYNC_OBJECTS.BR_DEATH_ZONE, _SYNC_DATA_CB_KEY, self.__deathZoneUpdateCallback)

    def deactivate(self):
        self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.BR_DEATH_ZONE, _SYNC_DATA_CB_KEY, self.__deathZoneUpdateCallback)
        self.__stopTick()
        self.__inited = False
        self.__removeArenaBorders()
        super(BRDeathZoneComponent, self).deactivate()

    def destroy(self):
        try:
            self.__stopTick()
        except ValueError:
            _logger.warning('Callback has been already deleted, self.__callbackID=%s', str(self.__callbackID))

        self.__removeArenaBorders()
        self.__updatedZones = None
        super(BRDeathZoneComponent, self).destroy()
        return

    def getZonesStates(self):
        return self.__zoneStates

    def getDeathZoneCount(self):
        return (death_zones_mapping.ZONES_X, death_zones_mapping.ZONES_Y)

    def __deathZoneUpdateCallback(self, activeZones):
        if not self.__inited:
            self.__inited = True
            self.__init()
        updatedZones = []
        for zoneId, timeToClose in activeZones.iteritems():
            if timeToClose:
                zoneState = BRDeathZoneComponent.ZONE_WAITING
            else:
                zoneState = BRDeathZoneComponent.ZONE_ACTIVE
            i, j, pos = self.__addDeathZone(zoneId, zoneState)
            if pos is not None:
                updatedZones.append((i, j, zoneState))

        self.__updatedZones.extend(updatedZones)
        self.onDeathZoneUpdate(updatedZones)
        return

    def __addDeathZone(self, zoneId, state):
        i = zoneId / death_zones_mapping.ZONES_X
        j = zoneId % death_zones_mapping.ZONES_Y
        currentState = self.__zoneStates[i][j][0]
        if currentState == state:
            return (i, j, None)
        else:
            position = self.__cornerPosition + Math.Vector3(j * self.__zoneSizeX, 0, i * self.__zoneSizeY)
            position += self.__zonePositionOffset
            self.__zoneStates[i][j] = (state, zoneId, 0)
            return (i, j, position)

    def _drawZones(self):
        spaceID = BigWorld.player().spaceID
        if spaceID == 0:
            return
        for zone in self.__updatedZones:
            i, j, _ = zone
            zoneData = self.__zoneStates[i][j]
            state = zoneData[BRZoneData.ZONE_STATE]
            if state == BRDeathZoneComponent.ZONE_ACTIVE:
                color = self.__deathZoneBorderSettings['activeColor']
            else:
                color = self.__deathZoneBorderSettings['waitingColor']
            zoneID = zoneData[BRZoneData.ZONE_ID]
            position = self.__cornerPosition + Math.Vector3(j * self.__zoneSizeX, 0, i * self.__zoneSizeY)
            position += self.__zonePositionOffset
            BigWorld.ArenaBorderHelper.setBorderBounds(spaceID, zoneID, position, self.__zoneScale)
            BigWorld.ArenaBorderHelper.setBorderVisible(spaceID, zoneID, True)
            BigWorld.ArenaBorderHelper.setBorderColor(spaceID, zoneID, color)
            BigWorld.ArenaBorderHelper.setBorderMaxAlpha(spaceID, zoneID, self.__deathZoneBorderSettings['maxAlpha'])
            BigWorld.ArenaBorderHelper.setBorderHeight(spaceID, zoneID, self.__deathZoneBorderSettings['height'])
            BigWorld.ArenaBorderHelper.setBordersDistanceFadeEnabled(spaceID, False)
            self.__visualizersId.append(zoneID)
            borderMask = self.__setBoundsVisibility(i, j, state, spaceID)
            BigWorld.ArenaBorderHelper.setBorderMask(spaceID, zoneID, borderMask)
            self.__zoneStates[i][j] = (state, zoneID, borderMask)

        self.__updatedZones = []

    def __setBoundsVisibility(self, i, j, state, spaceID):
        visibilityMask = 0
        checkI = i + 1
        if checkI < death_zones_mapping.ZONES_Y:
            if self.__checkSide(checkI, j, _INVISIBLE_DOWN, state, spaceID):
                visibilityMask |= _INVISIBLE_UP
        checkI = i - 1
        if checkI >= 0:
            if self.__checkSide(checkI, j, _INVISIBLE_UP, state, spaceID):
                visibilityMask |= _INVISIBLE_DOWN
        checkJ = j - 1
        if checkJ >= 0:
            if self.__checkSide(i, checkJ, _INVISIBLE_RIGHT, state, spaceID):
                visibilityMask |= _INVISIBLE_LEFT
        checkJ = j + 1
        if checkJ < death_zones_mapping.ZONES_X:
            if self.__checkSide(i, checkJ, _INVISIBLE_LEFT, state, spaceID):
                visibilityMask |= _INVISIBLE_RIGHT
        return visibilityMask

    def __checkSide(self, i, j, mask, state, spaceID):
        zState, zId, zBorderMask = self.__zoneStates[i][j]
        if zState == BRDeathZoneComponent.ZONE_FREE:
            return False
        if state == BRDeathZoneComponent.ZONE_WAITING and zState == BRDeathZoneComponent.ZONE_ACTIVE:
            return True
        if state == zState:
            visibilityMask = zBorderMask | mask
            BigWorld.ArenaBorderHelper.setBorderMask(spaceID, zId, visibilityMask)
            self.__zoneStates[i][j] = (zState, zId, visibilityMask)
            return True
        return False

    def __tick(self):
        avatar = BigWorld.player()
        if avatar is None:
            return
        else:
            vehicle = avatar.getVehicleAttached()
            if vehicle is None:
                self.__callbackID = BigWorld.callback(_UPDATE_INTERVAL, self.__tick)
                self.__currentZoneState = None
                return
            newVehID = vehicle.id
            if newVehID != self.__observedvehicleID:
                self.__observedvehicleID = newVehID
                self.__currentZoneState = None
            if vehicle.isAlive():
                position = vehicle.position - self.__cornerPosition
                zoneJ = int(position.x / self.__zoneSizeX)
                zoneI = int(position.z / self.__zoneSizeY)
                if zoneI < death_zones_mapping.ZONES_X and zoneJ < death_zones_mapping.ZONES_Y:
                    zoneDesc = self.__zoneStates[zoneI][zoneJ]
                    zoneState = zoneDesc[0]
                    if zoneState != BRDeathZoneComponent.ZONE_FREE:
                        if self.__currentZoneState != zoneState and zoneState == BRDeathZoneComponent.ZONE_WAITING:
                            avatar.updateVehicleDeathZoneTimer(0, zoneID=DEATH_ZONES.STATIC, state='warning')
                        self.__currentZoneState = zoneState
                    elif self.__currentZoneState:
                        if self.__currentZoneState == BRDeathZoneComponent.ZONE_WAITING:
                            avatar.updateVehicleDeathZoneTimer(0, zoneID=DEATH_ZONES.STATIC)
                        self.__currentZoneState = None
            self._drawZones()
            self.__callbackID = BigWorld.callback(_UPDATE_INTERVAL, self.__tick)
            return

    def __stopTick(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __removeArenaBorders(self):
        avatar = BigWorld.player()
        if avatar is not None:
            spaceID = avatar.spaceID
            if spaceID:
                remove = BigWorld.ArenaBorderHelper.removeBorder
                for visId in self.__visualizersId:
                    remove(avatar.spaceID, visId)

        del self.__visualizersId[:]
        return

    def __init(self):
        arenaType = BigWorld.player().arena.arenaType
        boundingBox = arenaType.boundingBox
        self.__cornerPosition = Math.Vector3(boundingBox[0][0], 0, boundingBox[0][1])
        self.__zoneSizeX, self.__zoneSizeY = (boundingBox[1] - boundingBox[0]).tuple()
        self.__zoneSizeX /= death_zones_mapping.ZONES_X
        self.__zoneSizeY /= death_zones_mapping.ZONES_Y
        self.__deathZoneBorderSettings = arenaType.deathZoneBorders
        if self.__deathZoneBorderSettings is None:
            raise SoftException('Death Zone border configuration not found for given arena type')
        halfSizeX = self.__zoneSizeX * 0.5
        halfSizeY = self.__zoneSizeY * 0.5
        self.__zonePositionOffset = Math.Vector3(halfSizeX, 0, halfSizeY)
        self.__zoneScale = Math.Vector4(-halfSizeX, -halfSizeY, halfSizeX, halfSizeY)
        self.__callbackID = BigWorld.callback(_UPDATE_INTERVAL, self.__tick)
        return
