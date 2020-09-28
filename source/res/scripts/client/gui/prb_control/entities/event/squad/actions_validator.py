# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/actions_validator.py
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.random.squad.actions_validator import BalancedSquadSlotsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from gui.ranked_battles.constants import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IGameEventController

class _EventBattleVehiclesValidator(SquadVehiclesValidator):

    def _isValidMode(self, vehicle):
        return vehicle.isEvent and not vehicle.isOnlyForEpicBattles and not vehicle.isOnlyForBob


class EventBattleSquadActionsValidator(SquadActionsValidator):
    __gameEventController = dependency.descriptor(IGameEventController)

    def _createVehiclesValidator(self, entity):
        return _EventBattleVehiclesValidator(entity)

    def _createSlotsValidator(self, entity):
        baseValidator = super(EventBattleSquadActionsValidator, self)._createSlotsValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, BalancedSquadSlotsValidator(entity)])

    def _validate(self):
        status, _, _ = self.__gameEventController.getPrimeTimeStatus()
        if status == PrimeTimeStatus.NOT_SET:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_SET)
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_DISABLED) if status != PrimeTimeStatus.AVAILABLE else super(EventBattleSquadActionsValidator, self)._validate()
