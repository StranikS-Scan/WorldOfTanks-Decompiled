# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/weekend_brawl/squad/actions_validator.py
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.base.unit.actions_validator import CommanderValidator
from gui.prb_control.entities.random.squad.actions_validator import BalancedSquadVehiclesValidator, SPGForbiddenSquadVehiclesValidator, BalancedSquadSlotsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.ranked_battles.constants import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IWeekendBrawlController

class WeekendBrawllVehiclesValidator(SquadVehiclesValidator):
    wBrawlCtrl = dependency.descriptor(IWeekendBrawlController)

    def _isValidMode(self, vehicle):
        return not vehicle.isEvent

    def _isVehicleSuitableForMode(self, vehicle):
        levels = self.wBrawlCtrl.getConfig().levels
        forbiddenClassTags = self.wBrawlCtrl.getConfig().forbiddenClassTags
        forbiddenVehTypes = self.wBrawlCtrl.getConfig().forbiddenVehTypes
        if vehicle.level not in levels:
            return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_INVALID_LEVEL, {'levels': levels})
        if vehicle.type in forbiddenClassTags:
            return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_WRONG_MODE, {})
        return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_WRONG_MODE, {}) if vehicle.intCD in forbiddenVehTypes else None


class WeekendBrawlValidator(CommanderValidator):
    wBrawlCtrl = dependency.descriptor(IWeekendBrawlController)

    def _validate(self):
        status, _, _ = self.wBrawlCtrl.getPrimeTimeStatus()
        return ValidationResult(False, UNIT_RESTRICTION.CURFEW) if status != PrimeTimeStatus.AVAILABLE else super(WeekendBrawlValidator, self)._validate()


class WeekendBrawlSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        baseValidator = super(WeekendBrawlSquadActionsValidator, self)._createLevelsValidator(entity)
        validators = [baseValidator,
         WeekendBrawlValidator(entity),
         WeekendBrawllVehiclesValidator(entity),
         SPGForbiddenSquadVehiclesValidator(entity)]
        if entity.isBalancedSquadEnabled():
            validators.append(BalancedSquadVehiclesValidator(entity))
        return ActionsValidatorComposite(entity, validators=validators)

    def _createSlotsValidator(self, entity):
        baseValidator = super(WeekendBrawlSquadActionsValidator, self)._createSlotsValidator(entity)
        validators = []
        if entity.isBalancedSquadEnabled():
            validators.append(BalancedSquadSlotsValidator(entity))
        validators.append(baseValidator)
        return ActionsValidatorComposite(entity, validators=validators)
