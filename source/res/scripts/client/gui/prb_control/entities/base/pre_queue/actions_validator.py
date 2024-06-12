# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/pre_queue/actions_validator.py
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite, CurrentVehicleActionsValidator, TutorialActionsValidator, EarlyAccessActionsValidator
from gui.prb_control.items import ValidationResult

class InQueueValidator(BaseActionsValidator):

    def _validate(self):
        return ValidationResult(False) if self._entity.isInQueue() else super(InQueueValidator, self)._validate()


class PreQueueActionsValidator(ActionsValidatorComposite):

    def __init__(self, entity):
        self._stateValidator = self._createStateValidator(entity)
        self._vehiclesValidator = self._createVehiclesValidator(entity)
        self._tutorialValidator = self._createTutorialValidator(entity)
        self._earlyAccessValidator = self._createEarlyAccessValidator(entity)
        validators = [self._stateValidator,
         self._vehiclesValidator,
         self._tutorialValidator,
         self._earlyAccessValidator]
        super(PreQueueActionsValidator, self).__init__(entity, validators)

    def _createStateValidator(self, entity):
        return InQueueValidator(entity)

    def _createVehiclesValidator(self, entity):
        return CurrentVehicleActionsValidator(entity)

    def _createTutorialValidator(self, entity):
        return TutorialActionsValidator(entity)

    def _createEarlyAccessValidator(self, entity):
        return EarlyAccessActionsValidator(entity)
