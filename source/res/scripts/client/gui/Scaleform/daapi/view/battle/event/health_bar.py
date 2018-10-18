# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/health_bar.py
import logging
from gui.Scaleform.daapi.view.battle.shared.formatters import formatHealthProgress, normalizeHealthPercent
from gui.Scaleform.daapi.view.meta.EventHealthBarMeta import EventHealthBarMeta
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class EventHealthBar(EventHealthBarMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EventHealthBar, self).__init__()
        self.__maxHealth = 0
        self.__initialized = False
        self.__vehicleState = None
        return

    def _populate(self):
        super(EventHealthBar, self)._populate()
        vehicleState = self.sessionProvider.shared.vehicleState
        if vehicleState is not None:
            vehicleState.onVehicleControlling += self.__onVehicleControlling
            vehicleState.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vehicle = vehicleState.getControllingVehicle()
            if vehicle is not None:
                self.__onVehicleControlling(vehicle)
            self.__vehicleState = vehicleState
        else:
            _logger.error('Vehicle state is missing!')
        return

    def _dispose(self):
        vehicleState = self.__vehicleState
        if vehicleState is not None:
            vehicleState.onVehicleControlling -= self.__onVehicleControlling
            vehicleState.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        super(EventHealthBar, self)._dispose()
        return

    def __updateHealth(self, health):
        if 0 <= health <= self.__maxHealth and self.__maxHealth > 0:
            healthStr = formatHealthProgress(health, self.__maxHealth)
            healthProgress = normalizeHealthPercent(health, self.__maxHealth)
            self.as_updateHealthS(healthStr, healthProgress)

    def __onVehicleControlling(self, vehicle):
        self.__maxHealth = vehicle.typeDescriptor.maxHealth
        self.__updateHealth(vehicle.health)

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.HEALTH:
            self.__updateHealth(value)
