# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/bob/squad/actions_validator.py
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.base.unit.actions_validator import CommanderValidator
from gui.prb_control.entities.random.squad.actions_validator import BalancedSquadVehiclesValidator, SPGForbiddenSquadVehiclesValidator, BalancedSquadSlotsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.ranked_battles.constants import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IBobController

class BobVehiclesValidator(SquadVehiclesValidator):
    bobCtrl = dependency.descriptor(IBobController)

    def _isValidMode(self, vehicle):
        return not vehicle.isEvent

    def _isVehicleSuitableForMode(self, vehicle):
        levels = self.bobCtrl.getConfig().levels
        forbiddenClassTags = self.bobCtrl.getConfig().forbiddenClassTags
        forbiddenVehTypes = self.bobCtrl.getConfig().forbiddenVehTypes
        if vehicle.level not in levels:
            return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_INVALID_LEVEL, {'levels': levels})
        if vehicle.type in forbiddenClassTags:
            return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_NOT_VALID_FOR_EVENT, {})
        return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_NOT_VALID_FOR_EVENT, {}) if vehicle.intCD in forbiddenVehTypes else None


class BobValidator(CommanderValidator):
    bobCtrl = dependency.descriptor(IBobController)

    def _validate(self):
        status, _, _ = self.bobCtrl.getPrimeTimeStatus()
        return ValidationResult(False, UNIT_RESTRICTION.CURFEW) if status != PrimeTimeStatus.AVAILABLE else super(BobValidator, self)._validate()


class BobSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        baseValidator = super(BobSquadActionsValidator, self)._createLevelsValidator(entity)
        validators = [baseValidator,
         BobValidator(entity),
         BobVehiclesValidator(entity),
         SPGForbiddenSquadVehiclesValidator(entity)]
        if entity.isBalancedSquadEnabled():
            validators.append(BalancedSquadVehiclesValidator(entity))
        return ActionsValidatorComposite(entity, validators=validators)

    def _createSlotsValidator(self, entity):
        baseValidator = super(BobSquadActionsValidator, self)._createSlotsValidator(entity)
        validators = []
        if entity.isBalancedSquadEnabled():
            validators.append(BalancedSquadSlotsValidator(entity))
        validators.append(baseValidator)
        return ActionsValidatorComposite(entity, validators=validators)
