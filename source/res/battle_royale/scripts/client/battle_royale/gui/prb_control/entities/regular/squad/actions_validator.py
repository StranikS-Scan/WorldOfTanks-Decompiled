# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/prb_control/entities/regular/squad/actions_validator.py
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.base.unit.actions_validator import UnitSlotsValidator, CommanderValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from gui.periodic_battles.models import PrimeTimeStatus
from constants import IS_DEVELOPMENT

class _BattleRoyaleVehiclesValidator(SquadVehiclesValidator):

    def _isValidMode(self, vehicle):
        return vehicle.isOnlyForBattleRoyaleBattles

    def _isVehicleSuitableForMode(self, vehicle):
        return ValidationResult(False, UNIT_RESTRICTION.UNSUITABLE_VEHICLE) if not self._isValidMode(vehicle) else None


class _UnitSlotsValidator(UnitSlotsValidator):

    def _validate(self):
        stats = self._entity.getStats()
        return ValidationResult(False, UNIT_RESTRICTION.UNIT_NOT_FULL) if stats.freeSlotsCount > 0 else super(_UnitSlotsValidator, self)._validate()


class _BattleRoyaleValidator(CommanderValidator):

    def _validate(self):
        brController = dependency.instance(IBattleRoyaleController)
        status, _, _ = brController.getPrimeTimeStatus()
        return ValidationResult(False, UNIT_RESTRICTION.CURFEW) if status != PrimeTimeStatus.AVAILABLE else super(_BattleRoyaleValidator, self)._validate()


class BattleRoyaleSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        validators = [_BattleRoyaleVehiclesValidator(entity), _UnitSlotsValidator(entity), _BattleRoyaleValidator(entity)]
        if not IS_DEVELOPMENT:
            validators.append(_UnitSlotsValidator(entity))
        return ActionsValidatorComposite(entity, validators=validators)

    def _createSlotsValidator(self, entity):
        baseValidator = super(BattleRoyaleSquadActionsValidator, self)._createSlotsValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, BattleRoyalSquadSlotsValidator(entity)])


class BattleRoyalSquadSlotsValidator(CommanderValidator):

    def _validate(self):
        stats = self._entity.getStats()
        pInfo = self._entity.getPlayerInfo()
        return ValidationResult(False, UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED) if stats.occupiedSlotsCount > 1 and not pInfo.isReady else None
