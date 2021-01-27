# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/bob/pre_queue/actions_validator.py
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION, PREBATTLE_RESTRICTION
from gui.shared.prime_time_constants import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IBobController

class BobValidator(BaseActionsValidator):
    bobCtrl = dependency.descriptor(IBobController)

    def _validate(self):
        status, _, _ = self.bobCtrl.getPrimeTimeStatus()
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_DISABLED) if status != PrimeTimeStatus.AVAILABLE else super(BobValidator, self)._validate()


class BobVehicleValidator(BaseActionsValidator):
    bobCtrl = dependency.descriptor(IBobController)

    def _validate(self):
        levels = self.bobCtrl.getConfig().levels
        forbiddenClassTags = self.bobCtrl.getConfig().forbiddenClassTags
        forbiddenVehTypes = self.bobCtrl.getConfig().forbiddenVehTypes
        if not g_currentVehicle.isPresent():
            return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_NOT_PRESENT)
        vehicle = g_currentVehicle.item
        if vehicle.level not in levels:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.LIMIT_LEVEL, {'levels': levels})
        if vehicle.type in forbiddenClassTags:
            return ValidationResult(False, PREBATTLE_RESTRICTION.LIMIT_VEHICLES, {})
        return ValidationResult(False, PREBATTLE_RESTRICTION.LIMIT_VEHICLES, {}) if vehicle.intCD in forbiddenVehTypes else super(BobVehicleValidator, self)._validate()


class BobActionsValidator(PreQueueActionsValidator):

    def _createStateValidator(self, entity):
        baseValidator = super(BobActionsValidator, self)._createStateValidator(entity)
        return ActionsValidatorComposite(entity, [baseValidator, BobValidator(entity)])

    def _createVehiclesValidator(self, entity):
        baseValidator = super(BobActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, [BobVehicleValidator(entity), baseValidator])
