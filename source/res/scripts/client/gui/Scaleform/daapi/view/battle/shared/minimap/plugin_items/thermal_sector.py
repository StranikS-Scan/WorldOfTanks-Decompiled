# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/minimap/plugin_items/thermal_sector.py
import logging
import math
import typing
import BigWorld
from WeakMethod import WeakMethodProxy
from cache import cached_property
from constants import THERMAL_VISION_STATE
from gui.Scaleform.daapi.view.battle.shared.minimap.plugin_items.base_sector import BaseSectorPlugin
from gui.battle_control import matrix_factory
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
if typing.TYPE_CHECKING:
    from items.components.shared_components import ThermalVisionParams
_logger = logging.getLogger(__name__)

class ThermalSectorPlugin(BaseSectorPlugin):
    NAME = 'thermalSector'

    @property
    def matrixProvider(self):
        return matrix_factory.makeVehicleTurretMatrixMP()

    @property
    def isEnabled(self):
        player = BigWorld.player()
        return player and player.vehicle and player.vehicle.typeDescriptor.hasThermalVision

    @cached_property
    def __statesMapping(self):
        return {THERMAL_VISION_STATE.IDLE: WeakMethodProxy(self.__onIdleReceived),
         THERMAL_VISION_STATE.ACTIVE: WeakMethodProxy(self.__onActivationReceived),
         THERMAL_VISION_STATE.RELOADING: WeakMethodProxy(self.__onIdleReceived),
         THERMAL_VISION_STATE.DISABLED: WeakMethodProxy(self.__onDisabledReceived)}

    def _onMinimapFeedbackReceived(self, eventID, entityID, value):
        if eventID == FEEDBACK_EVENT_ID.THERMAL_VISION_STATE_CHANGED:
            if value not in self.__statesMapping:
                _logger.error('Received unknown state - %s', value)
                return
            self.__statesMapping[value]()
        elif eventID == FEEDBACK_EVENT_ID.THERMAL_VISION_UPDATE_SETTINGS:
            self.__updateSettings(value)

    def __onActivationReceived(self):
        self.show()
        self._toggleActive(True)

    def __onIdleReceived(self):
        self.show()
        self._toggleActive(False)

    def __onDisabledReceived(self):
        self.hide()

    def __updateSettings(self, params):
        if not self.isEnabled:
            self.hide()
        fov = math.degrees(params.hSectorAngle * 2.0)
        self.setSectorSettings(fov, params.distance)
