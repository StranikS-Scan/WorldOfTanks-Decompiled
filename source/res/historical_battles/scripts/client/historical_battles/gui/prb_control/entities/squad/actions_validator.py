# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/prb_control/entities/squad/actions_validator.py
from helpers import dependency
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.base.unit.actions_validator import CommanderValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from historical_battles.gui.prb_control.entities.pre_queue.actions_validator import FrontmanValidator as FrontmanValidatorBase, FrontValidator as FrontValidatorBase
from historical_battles.skeletons.gui.game_event_controller import IGameEventController

class FrontmanValidator(FrontmanValidatorBase):
    RESTRICTION = UNIT_RESTRICTION.VEHICLE_IS_IN_BATTLE

    def _validate(self):
        gameEventController = dependency.instance(IGameEventController)
        currentFrontman = gameEventController.frontController.getSelectedFrontman()
        return ValidationResult(False, self.RESTRICTION) if currentFrontman.isInBattle() else super(FrontmanValidator, self)._validate()


class FrontValidator(FrontValidatorBase):
    RESTRICTION = UNIT_RESTRICTION.UNDEFINED


class HistoricalBattleVehiclesValidator(SquadVehiclesValidator):
    gameEventController = dependency.descriptor(IGameEventController)

    def _validate(self):
        return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_WRONG_MODE) if not self._isValidMode() else None

    def _isValidMode(self, vehicle=None):
        return self.gameEventController.isEnabled() and self.gameEventController.isBattlesEnabled()


class HistoricalSquadSlotsValidator(CommanderValidator):

    def _validate(self):
        stats = self._entity.getStats()
        roster = self._entity.getRoster()
        pInfo = self._entity.getPlayerInfo()
        hasEmptySlots = roster.MAX_SLOTS > stats.readyCount + roster.MAX_EMPTY_SLOTS
        return ValidationResult(False, UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED) if hasEmptySlots or not pInfo.isReady else None


class HistoricalBattleSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return ActionsValidatorComposite(entity, [HistoricalBattleVehiclesValidator(entity), FrontmanValidator(entity), FrontValidator(entity)])

    def _createSlotsValidator(self, entity):
        baseValidator = super(HistoricalBattleSquadActionsValidator, self)._createSlotsValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, HistoricalSquadSlotsValidator(entity)])
