# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/prb_control/entities/pre_queue/actions_validator.py
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite

class PortalBattleVehicleValidator(BaseActionsValidator):

    def _validate(self):
        vehicle = g_currentVehicle.item
        return ValidationResult(False) if vehicle is None else super(PortalBattleVehicleValidator, self)._validate()


class PortalBattleActionsValidator(PreQueueActionsValidator):

    def __init__(self, entity):
        self._vehicleValidatorExt = PortalBattleVehicleValidator(entity)
        super(PortalBattleActionsValidator, self).__init__(entity)

    def _createVehiclesValidator(self, entity):
        baseValidator = super(PortalBattleActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, [self._vehicleValidatorExt, baseValidator])
