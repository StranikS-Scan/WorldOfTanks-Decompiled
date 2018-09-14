# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/sandbox/pre_queue/actions_validator.py
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import SANDBOX_MAX_VEHICLE_LEVEL, PRE_QUEUE_RESTRICTION

class SandboxVehicleValidator(BaseActionsValidator):
    """
    Sandbox vehicle validation
    """

    def _validate(self):
        vehicle = g_currentVehicle.item
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.LIMIT_LEVEL, {'levels': range(1, SANDBOX_MAX_VEHICLE_LEVEL + 1)}) if vehicle.level > SANDBOX_MAX_VEHICLE_LEVEL or vehicle.isOnlyForEventBattles else super(SandboxVehicleValidator, self)._validate()


class SandboxActionsValidator(PreQueueActionsValidator):
    """
    Sandbox actions validation class
    """

    def _createVehiclesValidator(self, entity):
        baseValidator = super(SandboxActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, [baseValidator, SandboxVehicleValidator(entity)])
