# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/pre_queue/actions_validator.py
from helpers import dependency
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite, BaseActionsValidator, TutorialActionsValidator
from gui.prb_control.entities.base.pre_queue.actions_validator import InQueueValidator
from skeletons.gui.game_event_controller import IGameEventController
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PREBATTLE_RESTRICTION

class PreQueueEventActionsValidator(ActionsValidatorComposite):

    def __init__(self, entity):
        self._stateValidator = self._createStateValidator(entity)
        self._energyValidator = self._createEnergyValidator(entity)
        self._tutorialValidator = self._createTutorialValidator(entity)
        self._commanderValidator = self._createCommanderValidator(entity)
        validators = [self._stateValidator,
         self._energyValidator,
         self._tutorialValidator,
         self._commanderValidator]
        super(PreQueueEventActionsValidator, self).__init__(entity, validators)

    def _createStateValidator(self, entity):
        return InQueueValidator(entity)

    def _createEnergyValidator(self, entity):
        return GameEnergyValidator(entity)

    def _createTutorialValidator(self, entity):
        return TutorialActionsValidator(entity)

    def _createCommanderValidator(self, entity):
        return CommanderAvailableValidator(entity)


class GameEnergyValidator(BaseActionsValidator):
    gameEventController = dependency.descriptor(IGameEventController)

    def _validate(self):
        commander = self.gameEventController.getSelectedCommander()
        return ValidationResult(False, PREBATTLE_RESTRICTION.EVENT_NOT_ENOUGH_ENERGY) if commander.isBlockedByEnergy() else super(GameEnergyValidator, self)._validate()


class CommanderAvailableValidator(BaseActionsValidator):
    gameEventController = dependency.descriptor(IGameEventController)

    def _validate(self):
        commander = self.gameEventController.getSelectedCommander()
        return ValidationResult(False, PREBATTLE_RESTRICTION.EVENT_COMMANDER_LOCKED) if commander.isLocked() else super(CommanderAvailableValidator, self)._validate()
