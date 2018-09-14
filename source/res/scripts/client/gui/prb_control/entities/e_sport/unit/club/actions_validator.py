# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/e_sport/unit/club/actions_validator.py
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite, BaseActionsValidator
from gui.prb_control.entities.base.unit.actions_validator import UnitActionsValidator, UnitVehiclesValidator
from gui.prb_control.entities.e_sport.unit.public.actions_validator import ESportLevelsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION

class ClubStateValidator(BaseActionsValidator):
    """
    Club state validation
    """

    def _validate(self):
        flags = self._entity.getFlags()
        return ValidationResult(False, UNIT_RESTRICTION.IS_IN_PRE_ARENA) if flags.isInPreArena() else super(ClubStateValidator, self)._validate()

    def _isEnabled(self):
        return not self._entity.isCommander()


class ClubVehiclesValidator(UnitVehiclesValidator):
    """
    Club vehicles validation
    """

    def _isCheckForRent(self):
        flags = self._entity.getFlags()
        return False if flags.isInPreArena() else super(ClubVehiclesValidator, self)._isCheckForRent()


class ClubLevelsValidator(ESportLevelsValidator):
    """
    Club levels validation
    """
    pass


class ClubsActionsValidator(UnitActionsValidator):
    """
    Club actions validation class
    """

    def validateStateToStartBattle(self):
        flags = self._entity.getFlags()
        return ValidationResult(False, UNIT_RESTRICTION.NOT_READY_IN_SLOTS) if not flags.isReady() and not flags.isInPreArena() else super(ClubsActionsValidator, self).validateStateToStartBattle()

    def _createStateValidator(self, entity):
        baseValidator = super(ClubsActionsValidator, self)._createStateValidator(entity)
        return ActionsValidatorComposite(entity, [baseValidator, ClubStateValidator(entity)])

    def _createLevelsValidator(self, entity):
        baseValidator = super(ClubsActionsValidator, self)._createLevelsValidator(entity)
        return ActionsValidatorComposite(entity, validators=[ClubLevelsValidator(entity), baseValidator])

    def _createVehiclesValidator(self, entity):
        return ClubVehiclesValidator(entity)
