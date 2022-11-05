# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/periodic_battles/prb_control/actions_validator.py
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator
from gui.prb_control.entities.base.unit.actions_validator import UnitStateValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION, UNIT_RESTRICTION
from gui.periodic_battles.models import PrimeTimeStatus

def _validateModeState(controller, restrictions):
    if controller is None:
        return ValidationResult(False, restrictions.UNDEFINED, None)
    elif not controller.isBattlesPossible():
        return ValidationResult(False, restrictions.MODE_NO_BATTLES, None)
    status, _, _ = controller.getPrimeTimeStatus()
    if status == PrimeTimeStatus.NOT_SET:
        return ValidationResult(False, restrictions.MODE_NOT_SET, None)
    else:
        return ValidationResult(False, restrictions.MODE_NOT_AVAILABLE, None) if status != PrimeTimeStatus.AVAILABLE else None


class PrimeTimeValidator(BaseActionsValidator):

    def _getController(self):
        raise NotImplementedError

    def _validate(self):
        validationRes = _validateModeState(self._getController(), PRE_QUEUE_RESTRICTION)
        return validationRes if validationRes is not None else super(PrimeTimeValidator, self)._validate()


class SquadPrimeTimeValidator(UnitStateValidator):

    def _getController(self):
        raise NotImplementedError

    def _validate(self):
        validationRes = _validateModeState(self._getController(), UNIT_RESTRICTION)
        return validationRes if validationRes is not None else super(SquadPrimeTimeValidator, self)._validate()
