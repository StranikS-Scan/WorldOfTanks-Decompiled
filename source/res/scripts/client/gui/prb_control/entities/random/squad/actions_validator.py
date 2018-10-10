# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/random/squad/actions_validator.py
from CurrentVehicle import g_currentVehicle
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator
from gui.prb_control.entities.base.unit.actions_validator import CommanderValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION

class BalancedSquadVehiclesValidator(BaseActionsValidator):

    def _validate(self):
        levelsRange = self._entity.getRosterSettings().getLevelsRange()
        return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_INVALID_LEVEL) if g_currentVehicle.isPresent() and g_currentVehicle.item.level not in levelsRange else super(BalancedSquadVehiclesValidator, self)._validate()


class BalancedSquadSlotsValidator(CommanderValidator):

    def _validate(self):
        stats = self._entity.getStats()
        pInfo = self._entity.getPlayerInfo()
        return ValidationResult(False, UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED) if stats.occupiedSlotsCount > 1 and not pInfo.isReady else None


class SPGForbiddenSquadVehiclesValidator(BaseActionsValidator):

    def _validate(self):
        pInfo = self._entity.getPlayerInfo()
        if not pInfo.isReady and g_currentVehicle.isPresent():
            if g_currentVehicle.item.type == VEHICLE_CLASS_NAME.SPG:
                if self._entity.getMaxSPGCount() <= 0:
                    return ValidationResult(False, UNIT_RESTRICTION.SPG_IS_FORBIDDEN)
                return self._entity.hasSlotForSPG() or ValidationResult(False, UNIT_RESTRICTION.SPG_IS_FULL)
        return super(SPGForbiddenSquadVehiclesValidator, self)._validate()


class RandomSquadActionsValidator(SquadActionsValidator):
    pass


class BalancedSquadActionsValidator(RandomSquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        baseValidator = super(BalancedSquadActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, validators=[BalancedSquadVehiclesValidator(entity), baseValidator])

    def _createSlotsValidator(self, entity):
        baseValidator = super(BalancedSquadActionsValidator, self)._createSlotsValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, BalancedSquadSlotsValidator(entity)])


class SPGForbiddenSquadActionsValidator(RandomSquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        baseValidator = super(SPGForbiddenSquadActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, validators=[SPGForbiddenSquadVehiclesValidator(entity), baseValidator])


class SPGForbiddenBalancedSquadActionsValidator(BalancedSquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        baseValidator = super(SPGForbiddenBalancedSquadActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, SPGForbiddenSquadVehiclesValidator(entity)])
