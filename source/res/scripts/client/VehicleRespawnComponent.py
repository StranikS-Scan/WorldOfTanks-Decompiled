# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleRespawnComponent.py
import Event
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD

class VehicleRespawnComponent(DynamicScriptComponent):
    onSetSpawnTime = Event.Event()

    def _onAvatarReady(self):
        BigWorld.player().inputHandler.onPostmortemKillerVisionExit += self.showSelector
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange

    def onDestroy(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        BigWorld.player().inputHandler.onPostmortemKillerVisionExit -= self.showSelector
        super(VehicleRespawnComponent, self).onDestroy()

    def chooseSpawnGroup(self, groupName):
        self.cell.chooseSpawnGroup(groupName)

    def showSelector(self):
        if not self.spawnTime:
            return
        self.entity.guiSessionProvider.dynamic.teleport.showSpawnPoints(self.__createSpawnPoints(), self.groupName)

    def updateSelector(self):
        if not self.spawnTime:
            return
        self.entity.guiSessionProvider.dynamic.teleport.updateSpawnPoints(self.__createSpawnPoints(), self.groupName)

    def __createSpawnPoints(self):
        points = [ {'guid': point['name'],
         'position': (point['position'].x, point['position'].y)} for point in self.spawnGroups ]
        return points

    def __onArenaPeriodChange(self, period, *_):
        if period == ARENA_PERIOD.AFTERBATTLE:
            BigWorld.player().inputHandler.onPostmortemKillerVisionExit -= self.showSelector
