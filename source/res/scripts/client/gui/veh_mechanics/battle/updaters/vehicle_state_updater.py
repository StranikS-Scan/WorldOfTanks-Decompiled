# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/vehicle_state_updater.py
import logging
import typing
from gui.veh_mechanics.battle.updaters.updaters_common import ViewUpdater
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.battle_session import BattleSessionProvider
    from gui.battle_control.controllers.vehicle_state_ctrl import VehicleStateController
_logger = logging.getLogger(__name__)

class VehicleStateUpdater(ViewUpdater):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def initialize(self):
        super(VehicleStateUpdater, self).initialize()
        vehicleStateCtrl = self.__sessionProvider.shared.vehicleState
        if vehicleStateCtrl is None:
            _logger.error('No VehicleStateController found.')
            return
        else:
            vehicleStateCtrl.onVehicleStateUpdated += self.view.onVehicleStateUpdated
            return

    def finalize(self):
        vehicleStateCtrl = self.__sessionProvider.shared.vehicleState
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onVehicleStateUpdated -= self.view.onVehicleStateUpdated
        super(VehicleStateUpdater, self).finalize()
        return
