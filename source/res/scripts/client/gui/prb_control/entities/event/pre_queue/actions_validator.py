# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/pre_queue/actions_validator.py
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from gui.ranked_battles.constants import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IGameEventController

class EventBattleActionsValidator(PreQueueActionsValidator):
    __gameEventController = dependency.descriptor(IGameEventController)

    def _validate(self):
        status, _, _ = self.__gameEventController.getPrimeTimeStatus()
        if status == PrimeTimeStatus.NOT_SET:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_SET)
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_DISABLED) if status != PrimeTimeStatus.AVAILABLE else super(EventBattleActionsValidator, self)._validate()
