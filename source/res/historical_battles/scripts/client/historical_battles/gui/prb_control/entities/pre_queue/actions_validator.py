# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/prb_control/entities/pre_queue/actions_validator.py
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.settings import PREBATTLE_RESTRICTION
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from helpers import dependency
from gui.prb_control.items import ValidationResult

class FrontmanValidator(BaseActionsValidator):
    RESTRICTION = PREBATTLE_RESTRICTION.VEHICLE_IN_BATTLE

    def _validate(self):
        gameEventController = dependency.instance(IGameEventController)
        currentFrontman = gameEventController.frontController.getSelectedFrontman()
        return ValidationResult(False, self.RESTRICTION) if currentFrontman.isInBattle() else super(FrontmanValidator, self)._validate()


class FrontValidator(BaseActionsValidator):
    RESTRICTION = PREBATTLE_RESTRICTION.UNDEFINED

    def _validate(self):
        gameEventController = dependency.instance(IGameEventController)
        currentFront = gameEventController.frontController.getSelectedFront()
        return ValidationResult(False, self.RESTRICTION) if not gameEventController.isEnabled() or not currentFront.isAvailable() or not gameEventController.isBattlesEnabled() else super(FrontValidator, self)._validate()


class HistoricalBattlesActionsValidator(ActionsValidatorComposite):

    def __init__(self, entity):
        self._frontmanValidator = FrontmanValidator(entity)
        self._frontValidator = FrontValidator(entity)
        validators = [self._frontmanValidator, self._frontValidator]
        super(HistoricalBattlesActionsValidator, self).__init__(entity, validators)
