# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/ranked/pre_queue/actions_validator.py
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from gui.ranked_battles.constants import PRIME_TIME_STATUS
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.lobby_context import ILobbyContext

class RankedPrimeTimeValidator(BaseActionsValidator):

    def _validate(self):
        rankedController = dependency.instance(IRankedBattlesController)
        status, _, _ = rankedController.getPrimeTimeStatus()
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_DISABLED) if status != PRIME_TIME_STATUS.AVAILABLE else super(RankedPrimeTimeValidator, self)._validate()


class RankedVehicleValidator(BaseActionsValidator):

    def _validate(self):
        lobbyContext = dependency.instance(ILobbyContext)
        vehicle = g_currentVehicle.item
        config = lobbyContext.getServerSettings().rankedBattles
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.LIMIT_LEVEL, {'levels': range(config.minLevel, config.maxLevel + 1)}) if vehicle.level < config.minLevel or vehicle.level > config.maxLevel else super(RankedVehicleValidator, self)._validate()


class RankedActionsValidator(PreQueueActionsValidator):

    def _createStateValidator(self, entity):
        baseValidator = super(RankedActionsValidator, self)._createStateValidator(entity)
        return ActionsValidatorComposite(entity, [baseValidator, RankedPrimeTimeValidator(entity)])

    def _createVehiclesValidator(self, entity):
        baseValidator = super(RankedActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, [baseValidator, RankedVehicleValidator(entity)])
