# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/random/squad/actions_validator.py
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator
from gui.prb_control.entities.base.unit.actions_validator import CommanderValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION

class BalancedSquadVehiclesValidator(BaseActionsValidator):

    def _validate(self):
        levelsRange = self._entity.getRosterSettings().getLevelsRange()
        pInfo = self._entity.getPlayerInfo()
        return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_INVALID_LEVEL) if not pInfo.isReady and g_currentVehicle.isPresent() and g_currentVehicle.item.level not in levelsRange else super(BalancedSquadVehiclesValidator, self)._validate()


class BalancedSquadSlotsValidator(CommanderValidator):

    def _validate(self):
        stats = self._entity.getStats()
        pInfo = self._entity.getPlayerInfo()
        return ValidationResult(False, UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED) if stats.occupiedSlotsCount > 1 and not pInfo.isReady else None


class SquadRestrictionsVehiclesValidator(BaseActionsValidator):

    def _validate(self):
        pInfo = self._entity.getPlayerInfo()
        result = super(SquadRestrictionsVehiclesValidator, self)._validate()
        if pInfo.isReady or not g_currentVehicle.isPresent():
            return result
        hasSlot, tagsWithoutSlot = self._entity.hasSlotForVehicle(g_currentVehicle.item)
        if not hasSlot:
            result = ValidationResult(False, UNIT_RESTRICTION.VEHICLES_GROUP_IS_FULL, ctx={'tags': tagsWithoutSlot})
        return result


class RandomSquadActionsValidator(SquadActionsValidator):
    pass


class BalancedSquadActionsValidator(RandomSquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        baseValidator = super(BalancedSquadActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, validators=[BalancedSquadVehiclesValidator(entity), baseValidator])

    def _createSlotsValidator(self, entity):
        baseValidator = super(BalancedSquadActionsValidator, self)._createSlotsValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, BalancedSquadSlotsValidator(entity)])


class VehTypeForbiddenSquadActionsValidator(RandomSquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        baseValidator = super(VehTypeForbiddenSquadActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, validators=[SquadRestrictionsVehiclesValidator(entity), baseValidator])


class VehTypeForbiddenBalancedSquadActionsValidator(BalancedSquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        baseValidator = super(VehTypeForbiddenBalancedSquadActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, SquadRestrictionsVehiclesValidator(entity)])
