# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/pre_queue/actions_validator.py
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite, CurrentVehicleActionsValidator
from gui.prb_control.items import ValidationResult

class InQueueValidator(BaseActionsValidator):
    """
    Is player in queue validator.
    """

    def _validate(self):
        return ValidationResult(False) if self._entity.isInQueue() else super(InQueueValidator, self)._validate()


class PreQueueActionsValidator(ActionsValidatorComposite):
    """
    Pre queue actions validator base class.
    """

    def __init__(self, entity):
        validators = [InQueueValidator(entity), CurrentVehicleActionsValidator(entity)]
        super(PreQueueActionsValidator, self).__init__(entity, validators)
