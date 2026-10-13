# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/client/RespawnFrameworkVehicleComponent.py
from __future__ import absolute_import
from typing import TYPE_CHECKING
import logging
import BigWorld
from PlayerEvents import g_playerEvents
from VehicleRespawnComponent import VehicleRespawnComponent
from aih_constants import CTRL_MODE_NAME
from constants import ARENA_PERIOD
from gui.battle_control import avatar_getter
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from event_platform.gui.shared.events import RespawnFrameworkEvent
from event_platform_common.event_platform_constants import ARENA_BONUS_TYPE_CAPS
if TYPE_CHECKING:
    from typing import List, Dict, Any, Optional
_logger = logging.getLogger(__name__)

class RespawnFrameworkVehicleComponent(VehicleRespawnComponent):

    def __init__(self):
        super(RespawnFrameworkVehicleComponent, self).__init__()
        self._postmortem = False
        self._selectedRespawnVehicleCD = 0
        self.__spawnPoints = None
        return

    @property
    def spawnPoints(self):
        if self.__spawnPoints is None:
            self.__spawnPoints = self.__createPoints()
        return self.__spawnPoints

    @property
    def isVehicleSelectionEnabled(self):
        return BigWorld.player().hasBonusCap(ARENA_BONUS_TYPE_CAPS.RESPAWN_FRAMEWORK_VEHICLE_SELECTION)

    def _onAvatarReady(self):
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        BigWorld.player().inputHandler.onCameraChanged += self.onCameraChanged
        self.set_respawnVehicles()

    def set_respawnVehicles(self, _=None):
        if not self.respawnVehicles or not self.isVehicleSelectionEnabled:
            return
        _logger.debug('[RespawnFrameworkVehicleComponent] set_respawnVehicles received %d vehicles', len(self.respawnVehicles) if self.respawnVehicles else 0)
        g_eventBus.handleEvent(RespawnFrameworkEvent(RespawnFrameworkEvent.VEHICLES_LOADED), scope=EVENT_BUS_SCOPE.BATTLE)

    def onDestroy(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        BigWorld.player().inputHandler.onCameraChanged -= self.onCameraChanged
        super(RespawnFrameworkVehicleComponent, self).onDestroy()

    def onCameraChanged(self, controlModeName, vehicleID=None):
        if not self._postmortem and controlModeName == CTRL_MODE_NAME.POSTMORTEM:
            self._postmortem = True
            self.showPostmortem()
        elif self._postmortem and controlModeName != CTRL_MODE_NAME.POSTMORTEM:
            self._postmortem = False
            self.hidePostmortem()
            arena = avatar_getter.getArena()
            if arena and self.isVehicleSelectionEnabled:
                arena.onVehicleUpdated(self.entity.id)

    def showPostmortem(self):
        if self.entity.id != BigWorld.player().playerVehicleID:
            return
        g_eventBus.handleEvent(RespawnFrameworkEvent(RespawnFrameworkEvent.POSTMORTEM_ENTERED), scope=EVENT_BUS_SCOPE.BATTLE)

    def hidePostmortem(self):
        if self.entity.id != BigWorld.player().playerVehicleID:
            return
        g_eventBus.handleEvent(RespawnFrameworkEvent(RespawnFrameworkEvent.POSTMORTEM_LEFT), scope=EVENT_BUS_SCOPE.BATTLE)

    def __createPoints(self):
        points = [ {'guid': point['name'],
         'position': (point['position'].x, point['position'].y)} for point in self.spawnGroups ]
        return points

    def _getSelectedSetupsIndexes(self):
        vehData = self.respawnVehicles.get(self._selectedRespawnVehicleCD) if self.respawnVehicles else None
        return vehData.get('vehSetupsIndexes', {}) if vehData else {}

    def updateSelectedRespawnVehicle(self, vehicleCD):
        if not self.isVehicleSelectionEnabled:
            return
        self._selectedRespawnVehicleCD = vehicleCD
        setupsIndexes = self._getSelectedSetupsIndexes()
        _logger.debug('[FORT_RUSH][RESPAWN][CLIENT] updateLoadoutInfo: entity=%d, selectedVehicle=%d, setupsIndexes=%s, calling cell.applySelectedLoadout', self.entity.id, vehicleCD, setupsIndexes)
        setupsIndexesFixed = {'keys': [],
         'values': []}
        for key, value in setupsIndexes.iteritems():
            setupsIndexesFixed['keys'].append(key)
            setupsIndexesFixed['values'].append(value)

        self.cell.applySelectedLoadout(self._selectedRespawnVehicleCD, setupsIndexesFixed)

    def __onArenaPeriodChange(self, period, *_):
        if period == ARENA_PERIOD.AFTERBATTLE:
            BigWorld.player().inputHandler.onCameraChanged -= self.onCameraChanged
