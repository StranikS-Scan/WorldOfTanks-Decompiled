# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/squad/actions_validator.py
from CurrentVehicle import g_currentVehicle
from constants import VEHICLE_CLASS_INDICES
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator
from gui.prb_control.entities.base.unit.actions_validator import UnitActionsValidator, UnitVehiclesValidator
from gui.prb_control.items import ValidationResult, unit_items
from gui.prb_control.settings import UNIT_RESTRICTION
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.server_events import IEventsCache

class SquadBalanceValidator(BaseActionsValidator):
    """
    Validation for squad levels balance.
    """
    eventsCache = dependency.descriptor(IEventsCache)

    def _validate(self):
        _, unit = self._entity.getUnit()
        levels = unit.getSelectedVehicleLevels()
        distance = levels[-1] - levels[0] if len(levels) else 0
        unitHasPenalty = distance in self.eventsCache.getSquadPenaltyLevelDistance()
        return ValidationResult(True, UNIT_RESTRICTION.XP_PENALTY_VEHICLE_LEVELS) if unitHasPenalty else super(SquadBalanceValidator, self)._validate()

    def _isEnabled(self):
        return self.eventsCache.isSquadXpFactorsEnabled()


class SquadVehiclesValidator(UnitVehiclesValidator):
    """
    Validation for squad selected vehicles.
    """

    def _getVehiclesInfo(self):
        vInfos = super(SquadVehiclesValidator, self)._getVehiclesInfo()
        if not findFirst(lambda v: not v.isEmpty(), vInfos, False):
            if g_currentVehicle.isPresent():
                vehicle = g_currentVehicle.item
                vehClassIdx = VEHICLE_CLASS_INDICES[vehicle.type]
                vInfos = (unit_items.VehicleInfo(vehicle.invID, vehicle.intCD, vehicle.level, vehClassIdx),)
        return vInfos


class SquadActionsValidator(UnitActionsValidator):
    """
    Squad actions validation class.
    """

    def __init__(self, entity):
        super(SquadActionsValidator, self).__init__(entity)
        self.addWarning(SquadBalanceValidator(entity))

    def _createVehiclesValidator(self, entity):
        return SquadVehiclesValidator(entity)

    def _createSlotsValidator(self, entity):
        return BaseActionsValidator(entity)

    def _createLevelsValidator(self, entity):
        return BaseActionsValidator(entity)
