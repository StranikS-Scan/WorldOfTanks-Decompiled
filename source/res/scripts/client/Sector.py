# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Sector.py
from functools import partial
import BigWorld
import MapActivities
from constants import SECTOR_STATE
from debug_utils import LOG_DEBUG
import Math
import items
from ReplayEvents import g_replayEvents
SECTOR_LOCATION_TO_MAP_ACTIVITY = {(1, 1): 'zone_destr_WZ1_planes',
 (1, 2): 'zone_destr_WZ2_planes',
 (1, 3): 'zone_destr_WZ3_planes',
 (2, 1): 'zone_destr_CZ1_planes',
 (2, 2): 'zone_destr_CZ2_planes',
 (2, 3): 'zone_destr_CZ3_planes',
 (3, 1): 'zone_destr_EZ1_planes',
 (3, 2): 'zone_destr_EZ2_planes',
 (3, 3): 'zone_destr_EZ3_planes'}
ID_IN_PLAYER_GROUP_TO_MAP_ACTIVITY_LEAD_TIME = {1: 2.0,
 2: 2.0,
 3: 23.0}
BORDER_VISUALISATION_DASH_DIMENSIONS = (10, 1, 1)
BORDER_VISUALISATION_GAP_LENGTH = 5

class Sector(BigWorld.Entity):

    def __init__(self):
        self.__startDestructionCallback = None
        return

    def onEnterWorld(self, prereqs):
        g_replayEvents.onTimeWarpStart += self.__cancelCallback
        sectorComponent = BigWorld.player().arena.componentSystem.sectorComponent
        if sectorComponent is not None:
            sectorComponent.addSector(self)
        self.model = model = BigWorld.Model('')
        model.addMotor(BigWorld.Servo(self.matrix))
        model.visible = True
        return

    def onLeaveWorld(self):
        g_replayEvents.onTimeWarpStart -= self.__cancelCallback
        self.__cancelCallback()
        sectorComponent = BigWorld.player().arena.componentSystem.sectorComponent
        if sectorComponent is not None:
            sectorComponent.removeSector(self)
        return

    def set_lengthX(self, oldValue):
        sectorComponent = BigWorld.player().arena.componentSystem.sectorComponent
        if sectorComponent is not None:
            sectorComponent.updateSector(self)
        return

    def set_lengthZ(self, oldValue):
        sectorComponent = BigWorld.player().arena.componentSystem.sectorComponent
        if sectorComponent is not None:
            sectorComponent.updateSector(self)
        return

    def set_state(self, oldValue):
        sectorComponent = BigWorld.player().arena.componentSystem.sectorComponent
        if sectorComponent is not None:
            sectorComponent.updateSector(self, oldValue)
        if self.state is SECTOR_STATE.TRANSITION:
            leadTime = ID_IN_PLAYER_GROUP_TO_MAP_ACTIVITY_LEAD_TIME[self.IDInPlayerGroup]
            delay = max(0, self.transitionTime - leadTime)
            self.__startDestructionCallback = BigWorld.callback(delay, partial(self.startSectorBombingMapActivities, MapActivities.Timer.getTime() + delay))
        return

    def startSectorBombingMapActivities(self, actualTargetTime):
        self.__cancelCallback()
        actualTime = MapActivities.Timer.getTime()
        timeOffset = actualTargetTime - actualTime
        if actualTime < actualTargetTime:
            self.__startDestructionCallback = BigWorld.callback(timeOffset, partial(self.startSectorBombingMapActivities, actualTargetTime))
            return
        mapActivityName = SECTOR_LOCATION_TO_MAP_ACTIVITY[self.playerGroup, self.IDInPlayerGroup]
        LOG_DEBUG('mapActivityName ', mapActivityName)
        MapActivities.startActivity(mapActivityName, timeOffset)

    def showBomb(self, position):
        largeEffectsIndex = items.vehicles.g_cache.shotEffectsIndexes.get('largeHighExplosive')
        dir_ = Math.Vector3(0.5, 1.0, -0.5)
        self.setSectorBombing(position, dir_, largeEffectsIndex)

    def setSectorBombing(self, position, dir_, effectsIndex):
        LOG_DEBUG('sector bombing started ', position, effectsIndex)
        effectsList = items.vehicles.g_cache.shotEffects[effectsIndex].get('groundHit', None)
        if not effectsList:
            return
        else:
            BigWorld.player().terrainEffects.addNew(position, effectsList[1], effectsList[0], self.__explosionFinished, dir=dir_, start=position + dir_.scale(-1.0), end=position + dir_.scale(1.0))
            return

    def __explosionFinished(self):
        LOG_DEBUG('explosion finished')

    def __cancelCallback(self):
        if self.__startDestructionCallback is not None:
            BigWorld.cancelCallback(self.__startDestructionCallback)
            self.__startDestructionCallback = None
        return
