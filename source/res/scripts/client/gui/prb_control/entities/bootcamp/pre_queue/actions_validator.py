# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/bootcamp/pre_queue/actions_validator.py
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from helpers import dependency
from skeletons.gui.game_control import IDemoAccCompletionController

class BootcampStateValidator(BaseActionsValidator):

    def _validate(self):
        demoAccController = dependency.instance(IDemoAccCompletionController)
        return ValidationResult(False) if demoAccController.isInDemoAccRegistration else super(BootcampStateValidator, self)._validate()


class BootcampActionsValidator(PreQueueActionsValidator):

    def _createStateValidator(self, entity):
        baseValidator = super(BootcampActionsValidator, self)._createStateValidator(entity)
        return ActionsValidatorComposite(entity, [baseValidator, BootcampStateValidator(entity)])
