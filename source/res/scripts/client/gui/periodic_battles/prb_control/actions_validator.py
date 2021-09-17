# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/periodic_battles/prb_control/actions_validator.py
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from gui.periodic_battles.models import PrimeTimeStatus

class PrimeTimeValidator(BaseActionsValidator):
    _controller = None

    def _validate(self):
        if not self._controller.isBattlesPossible():
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NO_BATTLES, None)
        else:
            status, _, _ = self._controller.getPrimeTimeStatus()
            if status == PrimeTimeStatus.NOT_SET:
                return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_SET, None)
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_AVAILABLE, None) if status != PrimeTimeStatus.AVAILABLE else super(PrimeTimeValidator, self)._validate()
