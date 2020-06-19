# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/random/pre_queue/actions_validator.py
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from gui.ranked_battles.constants import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IWOTSPGController

class EventPrimeTimeValidator(BaseActionsValidator):

    def _validate(self):
        eventController = dependency.instance(IWOTSPGController)
        if eventController.isEventVehicle():
            status, _, _ = eventController.getPrimeTimeStatus()
            if status == PrimeTimeStatus.NOT_SET:
                return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_SET, None)
            if status != PrimeTimeStatus.AVAILABLE:
                return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_DISABLED, None)
        return super(EventPrimeTimeValidator, self)._validate()


class RandomActionsValidator(PreQueueActionsValidator):

    def _createStateValidator(self, entity):
        baseValidator = super(RandomActionsValidator, self)._createStateValidator(entity)
        return ActionsValidatorComposite(entity, [baseValidator, EventPrimeTimeValidator(entity)])
